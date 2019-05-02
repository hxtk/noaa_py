from typing import Mapping

import datetime

import requests


class MalformedRequestException(Exception):
    """Exception raised when a NoaaRequest is submitted with invalid arguments.

    The message should specify the missing or conflicting arguments. This
    exception specifically indicates a syntax error.
    """
    pass


class ApiError(Exception):
    """Exception raised when a well-formed NoaaRequest causes a server error.

    Not every error can be detected by the client. It is possible for the server
    to raise an error if something goes wrong or if something is wrong with
    the request other than its syntax.
    """
    pass


class NoaaResult(object):
    pass


class NoaaRequest(object):
    def __init__(self):
        self.time_range = NoaaTimeRange()

    def execute(self) -> 'NoaaResult':
        pass

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
        self.begin = begin
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
        self.end = end
        return self

    def range(self, hours: int):
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
        self.hours = hours
        return self

    def _ready(self, error: bool) -> bool:
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
        return self._date_check()


class NoaaTimeRange:
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

    def as_dict_(self) -> Mapping[str, str]:
        """Dictionary for this time range."""
        res = dict()
        if self.begin:
            res['begin_date'] = self.begin.strftime(
                NoaaTimeRange._FORMAT_STRING)
        if self.end:
            res['end_date'] = self.begin.strftime(
                NoaaTimeRange._FORMAT_STRING)
        if self.range:
            res['range'] = str(self.range)
        if self.date:
            res['date'] = self.date
        return res

    def __str__(self) -> str:
        """URL-encoded string representing this time range."""
        return '&'.join(map(
            lambda k, v: '{}={}'.format(k,v),
            self.as_dict().items))
