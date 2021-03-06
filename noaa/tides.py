"""The tides module defines exposes an API for the NOAA Tides and Currents API."""
from typing import Mapping, Optional, List, Union

import datetime
import enum
import typing

import requests


class ApiError(Exception):
    """Exception raised when a well-formed NoaaRequest causes a server error.

    Not every error can be detected by the client. It is possible for the server
    to raise an error if something goes wrong or if something is wrong with
    the request other than its syntax.
    """


class TimeZone(enum.Enum):
    """Enumeration of timezones available to the API.

    Returned data is time-stamped and those time stamps may be in one of the
    time zones enumerated by this class.

    GMT specifies the GMT time zone.
    LOCAL specifies the local standard time, which does not change throughout
        the year normally.
    LOCAL_DST specifies the current local timezone which may be local standard
        time or local daylight time depending on whether daylight savings
        time is being observed.
    """
    GMT = 'gmt'
    LOCAL = 'lst'
    LOCAL_DST = 'lst_ldt'


class Interval(enum.Enum):
    """Enumeration of data intervals available to the API.

    By default, the API will return data for every six minutes.
    Alternatively, one may specify one of the values enumerated below.

    HILO returns data at high tide and low tide.
    HOUR returns data at an interval of one hour.

    """
    HILO = 'hilo'
    HOUR = 'h'


class Datum(enum.Enum):
    """Enumeration of NOAA water level data available to this API.

    A complete listing of valid data is available at the link below:
        https://tidesandcurrents.noaa.gov/api/#datum
    """
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
    """Enumeration of NOAA Products available to the Tides and Currents API.

    Full documentation is available at the link below:
        https://tidesandcurrents.noaa.gov/api/#products
    """
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


class Unit(enum.Enum):
    """Enumeration of the unit systems available to this API.

    ENGLISH will return data in feet, knots, and degrees fahrenheit.
    METRIC will return dat in meters, cm/s, and degrees celsius.
    """
    ENGLISH = 'english'
    METRIC = 'metric'


class NoaaDate(enum.Enum):
    """Magic number time range specifiers.

    TODAY refers to the 24-hour period beginning at the most recent midnight.
    LATEST refers to the latest data point available.
    RECENT refers to the 72-hour period ending at the most recent data-point.
    """
    TODAY = 'today'
    LATEST = 'latest'
    RECENT = 'recent'


class DataRow(typing.NamedTuple):
    """A single data point from a standard NOAA data product."""
    time: datetime.datetime
    value: float
    stdev: float
    flags: List[bool]
    quality: str


class DataResult:
    """An immutable wrapper for a list of DataRow objects."""
    _DATE_FORMAT = '%Y-%m-%d %H:%M'

    def __init__(self, data):
        self._rows = []
        for row in data:
            time = datetime.datetime.strptime(
                row['t'],
                DataResult._DATE_FORMAT)
            value = float(row['v'])
            stdev = float(row['s'])
            flags = [int(x) == 1 for x in row['f'].split(',')]
            quality = row['q']
            self._rows.append(DataRow(time, value, stdev, flags, quality))

    def __iter__(self):
        for row in self._rows:
            yield row

    def __getitem__(self, item: int) -> DataRow:
        return self._rows[item]

    def __len__(self):
        return len(self._rows)


class PredictionsRow(typing.NamedTuple):
    """A single data point for a NOAA tide predictions response."""
    time: datetime.datetime
    value: float
    type: str


class PredictionsResult:
    """An immutable wrapper for a list of PredictionsRow objects."""
    _DATE_FORMAT = '%Y-%m-%d %H:%M'

    def __init__(self, data):
        self._rows = []
        for row in data:
            time = datetime.datetime.strptime(
                row['t'],
                PredictionsResult._DATE_FORMAT)
            value = float(row['v'])
            row_type = row['type'] if 'type' in row else None
            self._rows.append(PredictionsRow(time, value, row_type))

    def __iter__(self):
        for row in self._rows:
            yield row

    def __getitem__(self, item: int) -> PredictionsRow:
        return self._rows[item]

    def __len__(self):
        return len(self._rows)


class NoaaRequest:
    """Builder for a request against the NOAA Tides and Currents API."""
    URL_FORMAT = 'https://tidesandcurrents.noaa.gov/api/datagetter?' \
                 '&application=noaa_py&format=json&{}'

    def __init__(self):
        self._time_range = NoaaTimeRange()
        self._product: Product = None
        self._datum: Datum = None
        self._units: Unit = None
        self._station: int = None
        self._interval: Optional[Interval] = None
        self._timezone: TimeZone = None

    def execute(self) -> Union['PredictionsResult', 'DataResult']:
        """Executes the built request.

        Returns:
            NoaaResult containing the data returned, if successful.

        Raises:
            ApiError: if the request returns from the server with an error or if
                the request could not be sent because the parameters were
                malformed such that the server could be guaranteed to return
                error.
        """
        self._ready(error=True)
        data = requests.get(str(self)).json()
        if 'error' in data:
            raise ApiError(data['error']['message'])

        if self._product == Product.PREDICTIONS:
            return PredictionsResult(data['predictions'])
        return DataResult(data['data'])

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
        self._time_range.begin = begin
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
        self._time_range.end = end
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
        self._time_range.hours = hours
        return self

    def date(self, date: Union[NoaaDate, str]) -> 'NoaaRequest':
        """Set the named time range for the result.

        NOAA specifies three named time ranges, which are documented in
        NoaaDate's documentation.

        This time specification cannot be used in conjunction with any other
        specification.

        Args:
            date: The Date constant to be used. This may be specified using a
                NoaaDate enum or by specifying the string value of a valid enum.

        Returns:
            The NoaaRequest object it is called on, for chaining.

        See Also: NoaaDate
        """
        if isinstance(date, NoaaDate):
            self._time_range.date = date
        else:
            self._time_range.date = NoaaDate(date)
        return self

    def product(self, product: Union[Product, str]) -> 'NoaaRequest':
        """Sets the NOAA product to be queried.

        Args:
            product: the string specifying the product to be used. This may be
                passed as a Product enum or as a string specifying a product.

        Returns:
            The NoaaRequest object it is called on, for chaining.

        See Also: NoaaProduct
        """
        if isinstance(product, Product):
            self._product = product
        else:
            self._product = Product(product)
        return self

    def datum(self, datum: Union[Datum, str]) -> 'NoaaRequest':
        """Specify NOAA Datum.

        This is a required argument required if the specified product is a
        water level product.

        Args:
            datum: The NOAA datum to be requested. This may be given as a Datum
                enum or as the string specifying a valid datum.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        if isinstance(datum, Datum):
            self._datum = datum
        else:
            self._datum = Datum(datum)
        return self

    def units(self, units: Union[Unit, str]) -> 'NoaaRequest':
        """Specify the unit system to be used.

        One must use a `tides.Unit` to specify one of the two available unit
        systems.

        Args:
            units: The unit system in which the results should be provided.
                This may use the `Unit.ENGLISH` or `Unit.METRIC` enums or their
                corresponding string values.

        Returns:
            The NoaaRequest object it is called on, for chaining.

        See Also:
            tides.Unit
        """
        if isinstance(units, Unit):
            self._units = units
        else:
            self._units = Unit(units)
        return self

    def station(self, station_id: int) -> 'NoaaRequest':
        """Specify ID of the station to be queried.

        Args:
            station_id: A station ID.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        self._station = station_id
        return self

    def interval(self, interval: Union[Interval, str]) -> 'NoaaRequest':
        """Specify the time interval to be used.

        Time interval is an optional parameter. If it is not specified,
        a time interval of six minutes will be used. If it is specified,
        it may be Interval.HOUR, which will return data for every hour,
        or Interval.HILO, which will return data at high and low tides.

        Args:
            interval: The time interval to be used, specified by an Interval
                enum or a corresponding string value.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        if isinstance(interval, Interval):
            self._interval = interval
        else:
            self._interval = Interval(interval)
        return self

    def timezone(self, timezone: Union[TimeZone, str]) -> 'NoaaRequest':
        """Specify the timezone to be used.

        The timezone may be TimeZone.GMT, specifying the GMT timezone,
        TimeZone.LOCAL, specifying the local standard time of the station being
        queried but not accounting for DST, or LOCAL_DST, specifying the local
        standard time of the station being queried and accounting for DST.

        Args:
            timezone: The timezone to be used, as an enum or a corresponding string.

        Returns:
            The NoaaRequest object it is called on, for chaining.
        """
        if isinstance(timezone, TimeZone):
            self._timezone = timezone
        else:
            self._timezone = TimeZone(timezone)
        return self

    def __str__(self) -> str:
        """Return the URL associated with this request."""
        interval = self._interval.value if self._interval else ''
        args = '&'.join([
            str(self._time_range),
            'product=' + self._product.value,
            'datum=' + self._datum.value,
            'units=' + self._units.value,
            'time_zone=' + self._timezone.value,
            'interval=' + interval,
            'station=' + str(self._station),
        ])
        return NoaaRequest.URL_FORMAT.format(args)

    def _ready(self, error=False) -> bool:
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
        if not self._time_range.is_valid():
            res = False
            if error:
                raise ApiError('Invalid time range specification.')
        if not isinstance(self._product, Product):
            res = False
            if error:
                raise ApiError('Invalid or absent NOAA Product.')
        if not isinstance(self._datum, Datum):
            res = False
            if error:
                raise ApiError('Invalid or absent NOAA Datum.')
        if not isinstance(self._units, Unit):
            res = False
            if error:
                raise ApiError('Invalid or absent Unit specification.')
        if not isinstance(self._timezone, TimeZone):
            res = False
            if error:
                raise ApiError('Invalid or absent Timezone.')
        if not self._station:
            res = False
            if error:
                raise ApiError('Absent Station ID.')

        return res


class NoaaTimeRange:
    """Time range of a NOAA API request.

    This is a group of several parameters for the time range of the API request
    that will error-check their interactions and ensure that a valid date and
    time string results.

    """
    _FORMAT_STRING = '%Y%m%d %H:%M'

    def __init__(self):
        self.begin: datetime.datetime = None
        self.end: datetime.datetime = None
        self.hours: int = None
        self.date: NoaaDate = None

    def is_valid(self) -> bool:
        """Checks if this is a well-formed range for NOAA's API.

        Noaa specifies five valid formats:
            A beginning and an end, explicitly specifying the date range;
            A beginning and a duration;
            An end and a duration;
            A duration (this implicitly uses the current time as the end); or
            A magic word 'today', 'latest' (most recent data), or 'recent'
                (last 72 hours), represented here as a NoaaDate.

        Above, duration is measured in hours.

        Returns:
            True if this time range is in one of the formats specified above.
            False otherwise.

        """
        # Beginning and an end:
        if self.begin and self.end and not (self.hours or self.date):
            return self.begin < self.end

        # Endpoint and duration:
        if self.begin and self.hours and not (self.end or self.date):
            return self.hours > 0
        if self.end and self.hours and not (self.begin or self.date):
            return self.hours > 0

        # Duration and implicit endpoint:
        if self.hours and not (self.begin or self.end or self.date):
            return self.hours > 0

        # Date constant from enum
        if self.date and not (self.begin or self.end or self.hours):
            return isinstance(self.date, NoaaDate)

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
        if self.hours:
            res['range'] = str(self.hours)
        if self.date:
            res['date'] = self.date.value
        return res

    def __str__(self) -> str:
        """URL-encoded string representing this time range."""
        return '&'.join(map(
            lambda x: '{}={}'.format(*x),
            self.as_dict().items()))
