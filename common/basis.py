# Copyright (c) 2024 Facenapalm
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

"""
This module contains dummy bot class that does nothing besides pywikibot
initialization, but has some auxiliary functions that can be useful in the
inherited classes.
"""

import functools
import pywikibot

from common.utils import get_best_value

class BaseWikidataBot:
    """
    A common ancestor for Wikidata bots.
    """

    headers = {
        'User-Agent': 'Wikidata bot'
    }

    def __init__(self):
        self.repo = pywikibot.Site()
        self.repo.login()

    def run(self) -> None:
        """Do nothing."""
        raise NotImplementedError('Direct attempt to run a dummy bot.')

    @functools.lru_cache
    def get_verbose_value(self, value):
        """If value is a Wikidata Item, return its label; otherwise return raw value."""
        if not isinstance(value, pywikibot.ItemPage):
            return value
        if "en" in value.labels:
            return value.labels["en"]
        return value.title()

    @functools.lru_cache
    def get_property_label(self, property_id):
        """Return property's label (for instance, "Steam application ID" for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, property_id)
        if "en" not in prop_page.labels:
            return property_id
        return prop_page.labels["en"]

    @functools.lru_cache
    def get_property_stated_in_value(self, property_id):
        """Return property's "stated in" value (for instance, ItemPage("Q337535") for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, property_id)
        result = get_best_value(prop_page, 'P9073')
        if result is None:
            raise RuntimeError(f"applicable 'stated in' value not set for {property_id}")
        return result
