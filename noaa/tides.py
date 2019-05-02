from typing import Mapping, Optional

import datetime
import enum

import requests


class ApiError(Exception):
    """Exception raised when a well-formed NoaaRequest causes a server error.

    Not every error can be detected by the client. It is possible for the server
    to raise an error if something goes wrong or if something is wrong with
    the request other than its syntax.
    """


class TimeZone(enum.Enum):
    GMT = 'gmt'
    LOCAL = 'lst'
    LOCAL_DST = 'lst_dst'


class Interval(enum.Enum):
    HILO = 'hilo'
    HOUR = 'h'


class Datum(enum.Enum):
    COLUMBIA_RIVER = 'CRD'
    GREAT_LAKES = 'IGLD'
    GREAT_LAKES_LOW_WATER = 'LWD'
    MEAN_HIGHER_HIGH_WATER = 'MHHW'
    MEAN_HIGH_WATER = 'MHW'
    MEAN_TIDE_LEVEL = 'MTL'
    MEAN_SEA_LEVEL = 'MSL'
    MEAN_LOW_WATER = 'MLW'
    MEAN_LOWER_LOW_WATER = 'MLLW'
    N_AMERICAN_VERTICAL = 'NAVD'
    STATION = 'STND'


class Product(enum.Enum):
    WATER_LEVEL = 'water_level'
    AIR_TEMP = 'air_temperature'
    WATER_TEMP = 'water_temp'
    WIND = 'wind'
    AIR_PRESSURE = 'air_pressure'
    AIR_GAP = 'air_gap'
    CONDUCT = 'conductivity'
    VIS = 'visibility'
    HUMIDITY = 'humidity'
    SALINITY = 'salinity'
    HOURLY_HEIGHT = 'hourly_height'
    HIGH_LOW = 'high_low'
    DAILY_MEAN = 'daily_mean'
    MONTHLY_MEAN = 'monthly_mean'
    ONE_MIN_WL = 'one_minute_water_level'
    PREDICTIONS = 'predictions'
    DATUMS = 'datums'
    CURRENTS = 'currents'


class NoaaResult(object):
    pass


class NoaaRequest(object):
    URL_FORMAT = 'https://tidesandcurrents.noaa.gov/api/datagetter?' \
                 '&application=noaa_py&format=json&{}'

    def __init__(self):
        self.time_range = NoaaTimeRange()
        self.noaa_product: Product = None
        self.noaa_datum: Datum = None
        self.unit_system: str = None
        self.station_id: int = None
        self.interval_: Optional[Interval] = None
        self.timezone_: TimeZone = None

    def execute(self) -> 'NoaaResult':
        """Executes the built request.

        Returns:
            NoaaResult containing the data returned, if successful.

        Raises:
            MalformedRequestException: if there is a syntax error with the
                request, such as an invalid combination of instructions.
            ApiError: if the request returns from the server with an error
        """
        if self._ready():
            raise ApiError(
                'Request was malformed. Double-check parameters.')
        data = requests.get(str(self)).json()
        if 'error' in data:
            print(data['error'])
            raise ApiError(data['error'])

        return NoaaResult(data['predictions'])

    def begin_date(self, begin: datetime.datetime) -> 'NoaaRequest':
        """Set the beginning date for the result.

        This must be used in conjunction with `NoaaRequest.end_date()` or
        `NoaaRequest.range()`, but not both.

        Args:
            begin: The beginning of the data range to be returned by the
                request when it is executed.

        Return:
            The NoaaRequest object it was called on, for chaining.

        """
        self.time_range.begin = begin
        return self

    def end_date(self, end: datetime.datetime) -> 'NoaaRequest':
        """Set the ending date for the result.

        This must be used in conjunction with `NoaaRequest.begin_date()` or
        `NoaaRequest.range()`, but not both.

        Args:
            end: The end of the data range to be returned by the
                request when it is executed.

        Return:
            The NoaaRequest object it was called on, for chaining.

        """
        self.time_range.end = end
        return self

    def range(self, hours: int) -> 'NoaaRequest':
        """Set the size of the time range for the result.

        This may be used in conjunction with `NoaaRequest.begin_date()` or
        `NoaaRequest.end_date()`, or it may be used on its own.

        Using this method by itself is equivalent to using it with
        `NoaaRequest.end_date(datetime.date.today())`, i.e., it is interpreted
        as the number of hours to look back from the present.

        Args:
            hours: The size of the range, in hours.

        Return:
            The NoaaRequest object it is called on, for chaining.

        """
        self.time_range.range = hours
        return self

    def product(self, product: Product) -> 'NoaaRequest':
        """Sets the NOAA product to be queried.

        A complete listing of valid products can be found here:
            https://tidesandcurrents.noaa.gov/api/#products

        Args:
            product: the string specifying the product to be used.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        if isinstance(product, Product):
            self.noaa_product = product
        else:
            self.noaa_product = Product(product)
        return self

    def datum(self, datum: Datum) -> 'NoaaRequest':
        """Specify NOAA Datum.

        This is an optional argument required if the specified product is a
        water level product.

        A complete listing of valid data is available at the link below:
            https://tidesandcurrents.noaa.gov/api/#datum

        Args:
            datum: The NOAA datum to be requested.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        self.noaa_datum = datum
        return self

    def units(self, units: str) -> 'NoaaRequest':
        """Specify the unit system to be used.

        One may use 'english' or 'metric' to specify either of those two unit
        systems.

        Args:
            units: The name of the unit system in which the results should be
                provided.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        self.unit_system = units
        return self

    def station(self, station_id: int) -> 'NoaaRequest':
        """Specify ID of the station to be queried.

        Args:
            station_id: A station ID.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        self.station_id = station_id
        return self

    def interval(self, interval: Interval) -> 'NoaaRequest':
        """Specify the time interval to be used.

        Time interval is an optional parameter. If it is not specified,
        a time interval of six minutes will be used. If it is specified,
        it may be "h", which will return data for every hour, or "hilo", which
        will return data at high and low tides.

        Args:
            interval: The time interval to be used.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        self.interval_ = interval
        return self

    def timezone(self, tz: TimeZone) -> 'NoaaRequest':
        """Specify the timezone to be used.

        The timezone may be 'gmt', specifying the GMT timezone, 'lst',
        specifying the local standard time of the station being queried but
        not accounting for DST, or 'lst_ldt', specifying the local standard
        time of the station being queried and accounting for DST.

        Args:
            tz: The timezone to be used.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        self.timezone_ = tz
        return self

    def __str__(self) -> str:
        """Return the URL associated with this request."""
        args = '&'.join([
            str(self.time_range),
            'product=' + self.noaa_product.value,
            'datum=' + self.noaa_datum.value,
            'units=' + self.unit_system,
            'time_zone=' + self.timezone_.value,
            'interval=' + self.interval_.value if self.interval_ else '',
            'station=' + str(self.station_id),
        ])
        return NoaaRequest.URL_FORMAT.format(args)

    def _ready(self) -> bool:
        """Check if the request is ready to be executed.

        The NOAA API documentation (https://tidesandcurrents.noaa.gov/api/)
        defines several valid ways to define a request, which are distinguished
        by the arguments passed in. This ensures that the request is valid.

        Args:
            error: If true, this method will raise an exception upon finding
                an invalid request, indicating the errors.

        Returns:
            True if the request is ready to be sent. False otherwise.

        Raises:
            If `error` is True, may raise MalformedRequestException.
        """
        res = True
        if not self.time_range.is_valid():
            res = False
        if not isinstance(self.noaa_product, Product):
            res = False
        if not isinstance(self.noaa_datum, Datum):
            res = False
        if self.unit_system not in ['english', 'metric']:
            res = False
        if self.timezone_ not in ['gmt', 'lst', 'lst_ldt']:
            res = False
        if self.interval_ and not isinstance(self.interval_, Interval):
            res = False

        return res


class NoaaTimeRange:
    """Time range of a NOAA API request.

    This is a group of several parameters for the time range of the API request
    that will error-check their interactions and ensure that a valid date and
    time string results.

    """
    _FORMAT_STRING = '%Y%m%d %H:%M'

    TODAY = 'today'
    LATEST = 'latest'
    RECENT = 'recent'

    def __init__(self):
        self.begin: datetime.datetime = None
        self.end: datetime.datetime = None
        self.range: int = None
        self.date: str = None

    def is_valid(self) -> bool:
        """Checks if this is a well-formed range for NOAA's API.

        Noaa specifies five valid formats:
            A beginning and an end, explicitly specifying the date range;
            A beginning and a duration;
            An end and a duration;
            A duration (this implicitly uses the current time as the end); or
            A magic word 'today', 'latest' (most recent data), or 'recent'
                (last 72 hours).

        Returns:
            True if this time range is in one of the formats specified above.
            False otherwise.

        """
        # Beginning and an end:
        if self.begin and self.end and not (self.range or self.date):
            return self.begin < self.end

        # Endpoint and duration:
        if self.begin and self.range and not (self.end or self.date):
            return self.range > 0
        if self.end and self.range and not (self.begin or self.date):
            return self.range > 0

        # Duration and implicit endpoint:
        if self.range and not (self.begin or self.end or self.date):
            return self.range > 0

        # Date constant from enum
        if self.date and not (self.begin or self.end or self.range):
            return self.date in [NoaaTimeRange.TODAY,
                                 NoaaTimeRange.LATEST,
                                 NoaaTimeRange.RECENT]

        return False

    def as_dict(self) -> Mapping[str, str]:
        """Dictionary for this time range."""
        res = dict()
        if self.begin:
            res['begin_date'] = self.begin.strftime(
                NoaaTimeRange._FORMAT_STRING)
        if self.end:
            res['end_date'] = self.end.strftime(
                NoaaTimeRange._FORMAT_STRING)
        if self.range:
            res['range'] = str(self.range)
        if self.date:
            res['date'] = self.date
        return res

    def __str__(self) -> str:
        """URL-encoded string representing this time range."""
        return '&'.join(map(
            lambda x: '{}={}'.format(*x),
            self.as_dict().items()))
