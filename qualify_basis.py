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
from pywikibot import pagegenerators as pg

class QualifyingBot:
    def __init__(self, base_property, qualifier_property):
        self.repo = pywikibot.Site()
        self.base_property = base_property
        self.base_property_name = self.get_verbose_property_name(base_property)
        self.qualifier_property = qualifier_property

    def process_item(self, item):
        """Process one item by adding qualifiers to all claims of given property."""
        if item.isRedirectPage():
            print("{} is a redirect page".format(item.title()))
            return
        if self.base_property not in item.claims:
            print("{}: no {}s set".format(item.title(), self.base_property_name))
            return
        for claim in item.claims[self.base_property]:
            base_value = claim.getTarget()
            try:
                if self.qualifier_property in claim.qualifiers:
                    raise RuntimeError("already has a qualifier")
                qualifier_values = self.get_qualifier_value(base_value)
                if not qualifier_values:
                    raise RuntimeError("can't get qualifier values")

                for qualifier_value in qualifier_values:
                    qualifier = pywikibot.Claim(self.repo, self.qualifier_property)
                    qualifier.setTarget(qualifier_value)
                    claim.addQualifier(qualifier, summary="Add qualifier to {} `{}`".format(self.base_property_name, base_value))
                    print("{}: qualifier set to `{}`".format(base_value, qualifier_value))
            except Exception as error:
                print("{}: {}".format(base_value, error))

    def run(self):
        """Parse command line arguments and process items accordingly."""
        description = "Add {} ({}) qualifier to {} ({}).".format(
            self.get_verbose_property_name(self.qualifier_property),
            self.qualifier_property,
            self.base_property_name,
            self.base_property
        )
        parser = ArgumentParser(description=description)
        parser.add_argument("input", nargs="?", default="all", help="A path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"")
        args = parser.parse_args()

        if args.input == "all":
            query = """
                SELECT ?item {{
                    ?item p:{} ?s
                    FILTER NOT EXISTS {{ ?s pq:{} [] }}
                }}
            """.format(self.base_property, self.qualifier_property)
            generator = pg.WikidataSPARQLPageGenerator(query, site=self.repo)
            for item in generator:
                self.process_item(item)
        else:
            for line in open(args.input):
                item = pywikibot.ItemPage(self.repo, line)
                self.process_item(item)

    # Virtual method to be implemented in inherited classes.

    def get_qualifier_values(self, base_value):
        raise NotImplementedError("SeekerBot.get_qualifier_value() is not implemented")

    # Private methods.

    def get_verbose_property_name(self, prop):
        """Return property's label (for instance, "Steam application ID" for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, prop)
        if "en" in prop_page.labels:
            return prop_page.labels["en"]
        else:
            return prop
