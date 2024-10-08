# Copyright (c) 2023 Facenapalm
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Some useful functions that are used in several bots."""

import re
import pywikibot
from datetime import datetime, UTC
from pywikibot import pagegenerators as pg

def get_first_key(dictionary):
    """Return first iterable key of the dictionary."""
    return next(iter(dictionary))

def get_current_wbtime():
    """Return current UTC time as an pywikibot.WbTime object."""
    timestamp = datetime.now(UTC)
    return pywikibot.WbTime(year=timestamp.year, month=timestamp.month, day=timestamp.day)

def get_only_value(item, prop, label='claim'):
    """
    Assert that given property has only one non-None non-deprecated claim and
    return such claim.
    In case of failure, raise RuntimeError.
    """
    if item.isRedirectPage():
        raise RuntimeError("Item is a redirect page")
    result = None
    for claim in item.claims.get(prop, []):
        if claim.rank == 'deprecated':
            continue
        value = claim.getTarget()
        if value is None:
            continue
        if result is not None:
            raise RuntimeError(f"Several {label}s found")
        result = value
    if result is None:
        raise RuntimeError(f"No {label} found")
    return result

def get_best_value(item, prop):
    """
    Find the best claim for given property and return its value.
    Prefer set values over None, then preferred claims over normal.
    If there is no such values, return None.
    """
    if item is None or prop not in item.claims:
        return None

    result = None
    for claim in item.claims[prop]:
        if claim.rank == 'preferred':
            value = claim.getTarget()
            if value is not None:
                return value
        if result is None and claim.rank == 'normal':
            result = claim.getTarget()
    return result

def parse_input_source(repo, source, query):
    """
    If source equals "all", make a SPARQL query passed as a third parameter. Otherwise treat it as
    a name of file with the list of item IDs to process (Qnnn).

    Yield through pywikibot.ItemPage objects.
    """
    if source == "all":
        for item in pg.WikidataSPARQLPageGenerator(query, site=repo):
            yield item
    elif re.match(r'^Q\d+$', source):
        yield pywikibot.ItemPage(repo, source)
    else:
        with open(source, encoding="utf-8") as listfile:
            for line in listfile:
                yield pywikibot.ItemPage(repo, line)
