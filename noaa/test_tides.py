# pylint: disable=C0103
import datetime
from urllib import parse

import pytest

from . import tides


class TestNoaaRequest:
    def test_str(self):
        req = tides.NoaaRequest()\
            .station(8720211)\
            .product(tides.Product.PREDICTIONS)\
            .interval(tides.Interval.HILO)\
            .begin_date(datetime.datetime.fromisoformat('2019-05-01'))\
            .end_date(datetime.datetime.fromisoformat('2019-05-02'))\
            .units(tides.Unit.ENGLISH)\
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER)\
            .timezone(tides.TimeZone.GMT)
        query = parse.parse_qs(parse.urlparse(str(req)).query)
        assert query['product'] == ['predictions']
        assert query['station'] == ['8720211']
        assert query['interval'] == ['hilo']
        assert query['begin_date'] == ['20190501 00:00']
        assert query['end_date'] == ['20190502 00:00']
        assert query['units'] == ['english']
        assert query['datum'] == ['MLLW']
        assert query['time_zone'] == ['gmt']

    def test_str_no_interval(self):
        req = tides.NoaaRequest()\
            .station(8720211)\
            .product(tides.Product.PREDICTIONS)\
            .begin_date(datetime.datetime.fromisoformat('2019-05-01'))\
            .end_date(datetime.datetime.fromisoformat('2019-05-02'))\
            .units(tides.Unit.ENGLISH)\
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER)\
            .timezone(tides.TimeZone.GMT)
        query = parse.parse_qs(parse.urlparse(str(req)).query)
        assert query['product'] == ['predictions']
        assert query['station'] == ['8720211']
        assert query['begin_date'] == ['20190501 00:00']
        assert query['end_date'] == ['20190502 00:00']
        assert query['units'] == ['english']
        assert query['datum'] == ['MLLW']
        assert query['time_zone'] == ['gmt']
        assert 'interval' not in query

    def test_ready(self):
        req = tides.NoaaRequest()\
            .station(8720211)\
            .product(tides.Product.PREDICTIONS)\
            .interval(tides.Interval.HILO)\
            .begin_date(datetime.datetime.fromisoformat('2019-05-01'))\
            .end_date(datetime.datetime.fromisoformat('2019-05-02'))\
            .units(tides.Unit.ENGLISH)\
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER)
        assert not req._ready()
        req.timezone(tides.TimeZone.GMT)
        assert req._ready()

        req = tides.NoaaRequest() \
            .station(8720211) \
            .product(tides.Product.PREDICTIONS) \
            .interval(tides.Interval.HILO) \
            .begin_date(datetime.datetime.fromisoformat('2019-05-01')) \
            .range(30) \
            .units(tides.Unit.ENGLISH) \
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER)\
            .timezone(tides.TimeZone.GMT)
        assert req._ready()

    def test_execute_predictions_request(self, requests_mock):
        req = tides.NoaaRequest() \
            .station(8720211) \
            .product(tides.Product.PREDICTIONS) \
            .interval(tides.Interval.HILO) \
            .begin_date(datetime.datetime.fromisoformat('2019-05-01')) \
            .end_date(datetime.datetime.fromisoformat('2019-05-02')) \
            .units(tides.Unit.ENGLISH) \
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER) \
            .timezone(tides.TimeZone.GMT)
        requests_mock.get(
            str(req),
            text='{ "predictions" : '
                 '[ {"t":"2019-05-01 04:20", "v":"0.633", "type":"L"},'
                 '{"t":"2019-05-01 10:50", "v":"4.453", "type":"H"},'
                 '{"t":"2019-05-01 16:41", "v":"0.363", "type":"L"},'
                 '{"t":"2019-05-01 23:12", "v":"4.776", "type":"H"} ]}')
        res = req.execute()
        assert len(res) == 4

    def test_execute_bad_request(self, requests_mock):
        req = tides.NoaaRequest() \
            .station(8720211) \
            .product(tides.Product.PREDICTIONS) \
            .interval(tides.Interval.HILO) \
            .begin_date(datetime.datetime.fromisoformat('2019-05-01')) \
            .end_date(datetime.datetime.fromisoformat('2019-05-02')) \
            .units(tides.Unit.ENGLISH) \
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER) \
            .timezone(tides.TimeZone.GMT)
        requests_mock.get(
            str(req),
            text='{"error": {"message":"No Predictions data was found. This '
                 'product may not be offered at this station at the requested '
                 'time."}} ')
        with pytest.raises(tides.ApiError):
            res = req.execute()

    def test_execute_waterlevel_request(self, requests_mock):
        req = tides.NoaaRequest() \
            .station(8735180) \
            .product(tides.Product.WATER_LEVEL) \
            .range(1) \
            .units(tides.Unit.ENGLISH) \
            .datum(tides.Datum.MEAN_LOWER_LOW_WATER) \
            .timezone(tides.TimeZone.GMT)
        requests_mock.get(
            str(req),
            text='{"metadata":{"id":"8735180","name":"Dauphin Island",'
                 '"lat":"30.2500","lon":"-88.0750"}, "data": [{'
                 '"t":"2019-05-07 18:24", "v":"1.669", "s":"0.023", "f":"0,0,'
                 '0,0", "q":"p"},{"t":"2019-05-07 18:30", "v":"1.674", '
                 '"s":"0.023", "f":"0,0,0,0", "q":"p"},{"t":"2019-05-07 '
                 '18:36", "v":"1.674", "s":"0.033", "f":"0,0,0,0", "q":"p"},'
                 '{"t":"2019-05-07 18:42", "v":"1.655", "s":"0.030", "f":"1,'
                 '0,0,0", "q":"p"},{"t":"2019-05-07 18:48", "v":"1.574", '
                 '"s":"0.026", "f":"1,0,0,0", "q":"p"},{"t":"2019-05-07 '
                 '18:54", "v":"1.564", "s":"0.033", "f":"1,0,0,0", "q":"p"},'
                 '{"t":"2019-05-07 19:00", "v":"1.502", "s":"0.026", "f":"1,'
                 '0,0,0", "q":"p"},{"t":"2019-05-07 19:06", "v":"1.483", '
                 '"s":"0.030", "f":"1,0,0,0", "q":"p"},{"t":"2019-05-07 '
                 '19:12", "v":"1.459", "s":"0.026", "f":"1,0,0,0", "q":"p"}]}')
        res = req.execute()
        assert len(res) == 9


class TestNoaaTimeRange:
    def test_is_valid_beginAndEnd(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.end = datetime.datetime.fromisoformat('2019-10-21')
        assert time_range.is_valid()

    def test_is_valid_endpointAndRange(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-04-15')
        time_range.hours = 10
        assert time_range.is_valid()

        time_range.begin = None
        time_range.end = datetime.datetime.fromisoformat('2019-10-21')
        assert time_range.is_valid()

    def test_is_valid_date(self):
        time_range = tides.NoaaTimeRange()
        time_range.date = tides.NoaaDate.RECENT
        assert time_range.is_valid()

        time_range.date = tides.NoaaDate.TODAY
        assert time_range.is_valid()

        time_range.date = tides.NoaaDate.LATEST
        assert time_range.is_valid()

        time_range.date = 'foo'
        assert not time_range.is_valid()

    def test_is_valid_rangeOnly(self):
        time_range = tides.NoaaTimeRange()
        time_range.hours = 10
        assert time_range.is_valid()

        time_range.hours = -10
        assert not time_range.is_valid()

    def test_is_valid_tooManyFields(self):
        time_range = tides.NoaaTimeRange()
        time_range.begin = datetime.datetime.fromisoformat('2019-01-01')
        time_range.date = tides.NoaaDate.TODAY
        assert not time_range.is_valid()

        time_range.date = None
        time_range.end = datetime.datetime.fromisoformat('2019-01-02')
        time_range.hours = 32
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
        time_range.hours = 10

        assert str(time_range) == 'begin_date=20190415 00:00&' \
                                  'range=10'

    def test_str_date(self):
        time_range = tides.NoaaTimeRange()
        time_range.date = tides.NoaaDate.TODAY

        assert str(time_range) == 'date=today'
