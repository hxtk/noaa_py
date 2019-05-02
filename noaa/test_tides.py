# pylint: disable=C0103
import datetime
from urllib import parse

from . import tides


class TestNoaaRequest:
    def test_str(self):
        req = tides.NoaaRequest()\
            .station(8720211)\
            .product('predictions')\
            .interval('hilo')\
            .begin_date(datetime.datetime.fromisoformat('2019-05-01'))\
            .end_date(datetime.datetime.fromisoformat('2019-05-02'))\
            .units('english')\
            .datum('MLLW')\
            .timezone('gmt')
        query = parse.parse_qs(parse.urlparse(str(req)).query)
        assert query['product'] == ['predictions']
        assert query['station'] == ['8720211']
        assert query['interval'] == ['hilo']
        assert query['begin_date'] == ['20190501 00:00']
        assert query['end_date'] == ['20190502 00:00']
        assert query['units'] == ['english']
        assert query['datum'] == ['MLLW']
        assert query['time_zone'] == ['gmt']

    def test_ready(self):
        req = tides.NoaaRequest()\
            .station(8720211)\
            .product('predictions')\
            .interval('hilo')\
            .begin_date(datetime.datetime.fromisoformat('2019-05-01'))\
            .end_date(datetime.datetime.fromisoformat('2019-05-02'))\
            .units('english')\
            .datum('MLLW')
        assert not req._ready()
        req.timezone('gmt')
        assert req._ready()



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

    def test_is_valid_rangeOnly(self):
        time_range = tides.NoaaTimeRange()
        time_range.range = 10
        assert time_range.is_valid()

        time_range.range = -10
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

    def test_str_startAndEnd(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.end = datetime.datetime.fromisoformat('2019-10-21')

        assert str(time_range) == 'begin_date=20190415 00:00&' \
                                  'end_date=20191021 00:00'

    def test_str_startAndRange(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.range = 10

        assert str(time_range) == 'begin_date=20190415 00:00&' \
                                  'range=10'

    def test_str_date(self):
        time_range = tides.NoaaTimeRange()
        time_range.date = tides.NoaaTimeRange.TODAY

        assert str(time_range) == 'date=today'
