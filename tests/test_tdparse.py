from datetime import datetime
from dateutil.relativedelta import relativedelta
from throttleandcache.tdparse import parse


def test_seconds():
    assert parse('1s') == relativedelta(seconds=1)
    assert parse('1 second') == relativedelta(seconds=1)
    assert parse('2 seconds') == relativedelta(seconds=2)


def test_minutes():
    assert parse('1m') == relativedelta(minutes=1)
    assert parse('1min') == relativedelta(minutes=1)
    assert parse('1 minute') == relativedelta(minutes=1)
    assert parse('2 minutes') == relativedelta(minutes=2)


def test_hours():
    assert parse('1h') == relativedelta(hours=1)
    assert parse('1hr') == relativedelta(hours=1)
    assert parse('1 hour') == relativedelta(hours=1)
    assert parse('2 hours') == relativedelta(hours=2)


def test_mixed():
    assert parse('3 minutes, 2 seconds') == relativedelta(minutes=3, seconds=2)


def test_number():
    """
    Seconds should be assumed when a number is passed.

    """
    assert parse(1) == relativedelta(seconds=1)


def test_offset():
    # Make sure the parsed value can be added to a datetime. This is important
    # because it's possible to create valid relativedeltas that can't be added
    # to datetimes. (e.g. with a float value for "year")
    datetime.now() + parse('1s')
