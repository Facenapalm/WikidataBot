# Copyright (c) 2022 Facenapalm
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

"""A basis for qualify_xxx.py scripts."""

import pywikibot
from argparse import ArgumentParser
from common.utils import parse_input_source

class QualifyingBot:
    """
    A skeleton class for a simple bot that adds qualifiers to the claims of
    given property.
    """

    def __init__(self, base_property, qualifier_property):
        self.repo = pywikibot.Site()
        self.repo.login()
        self.base_property = base_property
        self.base_property_name = self.get_verbose_property_name(base_property)
        self.qualifier_property = qualifier_property

    def process_item(self, item):
        """Process one item by adding qualifiers to all claims of given property."""
        if item.isRedirectPage():
            print(f"{item.title()} is a redirect page")
            return
        if self.base_property not in item.claims:
            print(f"{item.title()}: no {self.base_property_name}s set")
            return
        for claim in item.claims[self.base_property]:
            base_value = claim.getTarget()
            try:
                if self.qualifier_property in claim.qualifiers:
                    raise RuntimeError("already has a qualifier")
                qualifier_values = self.get_qualifier_values(base_value)
                if not qualifier_values:
                    raise RuntimeError("can't get qualifier values")

                for qualifier_value in qualifier_values:
                    qualifier = pywikibot.Claim(self.repo, self.qualifier_property)
                    qualifier.setTarget(qualifier_value)
                    claim.addQualifier(qualifier, summary=f"Add qualifier to {self.base_property_name} `{base_value}`")
                    print(f"{base_value}: qualifier set to `{self.get_verbose_value(qualifier_value)}`")
            except NotImplementedError as error:
                raise error
            except RuntimeError as error:
                print(f"{base_value}: {error}")

    def run(self):
        """Parse command line arguments and process items accordingly."""
        description = "Add {} ({}) qualifier to {} ({}).".format(
            self.get_verbose_property_name(self.qualifier_property),
            self.qualifier_property,
            self.base_property_name,
            self.base_property
        )
        parser = ArgumentParser(description=description)
        parser.add_argument("input", nargs="?", default="all", help="either a path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"")
        args = parser.parse_args()

        query = f"""
            SELECT ?item {{
                ?item p:{self.base_property} ?s
                FILTER NOT EXISTS {{ ?s pq:{self.qualifier_property} [] }}
            }}
        """

        for item in parse_input_source(self.repo, args.input, query):
            self.process_item(item)

    # Virtual method to be implemented in inherited classes.

    def get_qualifier_values(self, base_value):
        """Use the property value to return the list of qualifier values to add."""
        raise NotImplementedError(f"{self.__class__.__name__}.get_qualifier_value() is not implemented")

    # Private methods.

    def get_verbose_property_name(self, prop):
        """Return property's label (for instance, "Steam application ID" for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, prop)
        if "en" in prop_page.labels:
            return prop_page.labels["en"]
        return prop

    def get_verbose_value(self, value):
        """If value is a Wikidata Item, return its label; otherwise return raw value."""
        if not isinstance(value, pywikibot.ItemPage):
            return value
        if "en" not in value.labels:
            return value.labels["en"]
        return value.title()
