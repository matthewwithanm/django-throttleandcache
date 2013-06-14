from dateutil.relativedelta import relativedelta
import re


class ParseError(Exception):
    pass


PATTERN = r"""
    (.*?(?P<years>\d+)\s*y)?
    (.*?(?P<months>\d+)\s*(mon|mos))?
    (.*?(?P<weeks>\d+(\.\d+)?)\s*w)?
    (.*?(?P<days>\d+(\.\d+)?)\s*d)?
    (.*?(?P<hours>\d+(\.\d+)?)\s*h)?
    (.*?(?P<minutes>\d+(\.\d+)?)\s*m)?
    (.*?(?P<seconds>\d+(\.\d+)?)\s*s)?
"""

COMPILED_PATTERN = re.compile(PATTERN, re.VERBOSE)


def parse(val):
    try:
        return relativedelta(seconds=float(val))
    except ValueError:
        pass

    match = COMPILED_PATTERN.search(val)
    if not match:
        raise ParseError("Couldn't parse %s" % val)
    kwargs = dict((k, float(v or 0)) for k, v in match.groupdict().items())
    for attr in ['years', 'months']:
        # Years and months don't work with floats. (You can create the
        # relativedelta, but it can't be successfully added to a datetime.)
        kwargs[attr] = int(kwargs[attr])
    return relativedelta(**kwargs)
