from dateutil.relativedelta import relativedelta
import re


class ParseError(Exception):
    pass


PATTERN = r"""
    (.*?(?P<years>\d+(\.\d+)?)\s*y)?
    (.*?(?P<months>\d+(\.\d+)?)\s*(mon|mos))?
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
    return relativedelta(**kwargs)
