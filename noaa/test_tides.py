# pylint: disable=C0103
import datetime

from . import tides


class TestNoaaTimeRange:
    def test_is_valid_beginAndEnd(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.end = datetime.datetime.fromisoformat('2019-10-21')
        assert time_range.is_valid()

    def test_is_valid_endpointAndRange(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.range = 10
        assert time_range.is_valid()

        time_range.begin = None
        time_range.end = datetime.datetime.fromisoformat('2019-10-21')
        assert time_range.is_valid()

    def test_is_valid_date(self):
        time_range = tides.NoaaTimeRange()
        time_range.date = tides.NoaaTimeRange.RECENT
        assert time_range.is_valid()

        time_range.date = tides.NoaaTimeRange.TODAY
        assert time_range.is_valid()

        time_range.date = tides.NoaaTimeRange.LATEST
        assert time_range.is_valid()

        time_range.date = 'foo'
        assert not time_range.is_valid()

    def test_is_valid_tooManyFields(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-01-01')
        time_range.date = tides.NoaaTimeRange.TODAY
        assert not time_range.is_valid()

        time_range.date = None
        time_range.end = datetime.datetime.fromisoformat('2019-01-02')
        time_range.range = 32
        assert not time_range.is_valid()

    def test_is_valid_endBeforeStart(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-01-02')
        time_range.end = datetime.datetime.fromisoformat('2019-01-01')
        assert not time_range.is_valid()

    def test_str(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.end = datetime.datetime.fromisoformat('2019-10-21')

        assert str(time_range) == 'begin_date=20190415 ' \
                                  '00:00&end_date=20191021 00:00'
