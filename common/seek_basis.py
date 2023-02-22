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

"""A basis for seek_xxx_id.py scripts."""

from argparse import ArgumentParser
from datetime import datetime

import pywikibot
from pywikibot import pagegenerators as pg

def get_first_key(dictionary):
    """Return first iterable key of the dictionary."""
    return next(iter(dictionary))

def get_current_wbtime():
    """Get pywikibot.WbTime object describing the current date in UTC."""
    timestamp = datetime.utcnow()
    return pywikibot.WbTime(year=timestamp.year, month=timestamp.month, day=timestamp.day)


class BaseSeekerBot:
    """
    A skeleton class for a bot that connects Wikidata items with given external
    database based on matching values.

    General algorithm for a given item is the following:
    1. Make a search request to a database using item label or alias as a query.
    2. Parse each found entry and get properties that can help identifying this
       entry (for instance, a link to yet another external database).
    3. If there is a matching property (for instance, both parsed entry and
       Wikidata item are describing Steam game with id "220"), connect this
       entry with the item.
    4. Optinally, if some of the parsed properties are missing in Wikidata item,
       add them as well.

    This class implements the whole algorithm but search() and parse_entry()
    methods, which would have a different implementation for different external
    databases.
    """

    def __init__(self, database_item, database_prop, default_matching_prop,
                 matching_prop_whitelist=None, should_check_aliases=True,
                 should_set_properties=True):
        """
        database_item - Wikidata item ID (Qnnn) that describes this database to
            use in "stated in" references.
        database_prop - Wikidata property (Pnnn) that links to the database.
        default_matching_prop - Wikidata property to use as a matching property
            by default.
        matching_prop_whitelist - Wikidata properties that are allowed to use as
            a matching property. If set, it must include default_matching_prop.
        should_check_aliases - if False, bot would seek a database entry using
            item label only. If True, bot would also use item aliases.
        should_set_properties - if set, bot would also upload the properties
            parsed by parse_entry() method to Wikidata.
        """
        self.repo = pywikibot.Site()
        self.repo.login()

        self.verbose_names_cache = {}
        self.database_item = pywikibot.ItemPage(self.repo, database_item)
        self.database_prop = database_prop
        self.database_prop_label = self.get_verbose_name(database_prop)

        self.matching_prop_whitelist = matching_prop_whitelist
        self.change_matching_property(default_matching_prop)

        self.should_check_aliases = should_check_aliases
        self.should_set_properties = should_set_properties

    def change_matching_property(self, matching_prop):
        """Set a property to use to match database entries with Wikidata items."""
        if self.matching_prop_whitelist:
            if matching_prop not in self.matching_prop_whitelist:
                raise RuntimeError(f"Unsupported matching property `{matching_prop}`")

        self.matching_prop = matching_prop
        self.matching_prop_label = self.get_verbose_name(matching_prop)

    def process_item(self, item):
        """
        Fully process one item: seek database entry matching to current item,
        set external ID linking to this item, then optionally set other
        properties based on this entry.
        """
        try:
            if item.isRedirectPage():
                raise RuntimeError(f"item is a redirect page")
            if self.database_prop in item.claims:
                raise RuntimeError(f"{self.database_prop_label} already set")

            entry_id, properties = self.seek_database_entry(item)

            claim = pywikibot.Claim(self.repo, self.database_prop)
            claim.setTarget(entry_id)
            item.addClaim(claim, summary=f"Add {self.database_prop_label} based on matching {self.matching_prop_label}")
            print(f"{item.title()}: {self.database_prop_label} set to `{entry_id}`")

            if not self.should_set_properties:
                return

            for key, value in properties.items():
                if key == self.matching_prop:
                    continue
                key_verbose = self.get_verbose_name(key)
                if key in item.claims:
                    print(f"{item.title()}: {key_verbose} already set")
                    continue
                claim = pywikibot.Claim(self.repo, key)
                claim.setTarget(value)
                claim.addSources(self.generate_source(entry_id))
                item.addClaim(claim, summary=f"Add {key_verbose} based on {self.database_prop_label}")
                print(f"{item.title()}: {key_verbose} set to `{value}`")

        except RuntimeError as error:
            print(f"{item.title()}: {error}")

    def process_file(self, filename):
        """
        Process all items from the file.
        Given file should contain a list of items to process (Qnnn), one per line.
        """
        with open(filename, encoding="utf-8") as listfile:
            for line in listfile:
                item = pywikibot.ItemPage(self.repo, line)
                self.process_item(item)

    def process_all_items(self, limit=None):
        """Process items that have matching property, but no link to this database."""
        query = f"""
            SELECT ?item {{
                ?item p:{self.matching_prop} [] .
                FILTER NOT EXISTS {{ ?item p:{self.database_prop} [] }}
            }}
        """
        if limit:
            query += f"LIMIT {limit}"
        generator = pg.WikidataSPARQLPageGenerator(query, site=self.repo)
        for item in generator:
            self.process_item(item)

    def run(self):
        """Parse command line arguments and process items accordingly."""
        parser_arguments = {}
        parser_arguments["description"] = f"Add {self.database_prop_label} ({self.database_prop}) based on matching property (second positional argument)."
        if self.should_set_properties:
            parser_arguments["description"] += f" Then import data based on {self.database_prop_label}."
        if self.matching_prop_whitelist:
            parser_arguments["epilog"] = "Supported base properties: {}".format(", ".join(sorted(self.matching_prop_whitelist)))

        parser = ArgumentParser(**parser_arguments)
        parser.add_argument("input", help="A path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"")
        parser.add_argument("base", nargs="?", help=f"A property to use to match Wikidata items with database entries. If ommited, defaults to \"{self.matching_prop}\" ({self.matching_prop_label})")
        parser.add_argument("-limit", "-l", type=int, default=0, help="A number of items to process (optional, only works with keyword \"all\")")
        args = parser.parse_args()

        try:
            if args.base:
                self.change_matching_property(args.base)
            if args.input == "all":
                self.process_all_items(limit=args.limit)
            else:
                self.process_file(args.input)
        except Exception as error:
            print(error)

    # Virtual methods to be implemented in inherited classes.

    def search(self, query, max_results=None):
        """Search in given database and return a list of entry IDs."""
        raise NotImplementedError("SeekerBot.search() is not implemented")

    def parse_entry(self, entry_id):
        """Parse entry and return { property: value } dict."""
        raise NotImplementedError("SeekerBot.parse_entry() is not implemented")

    # Private methods.

    def get_verbose_name(self, prop):
        """Return property's label (for instance, "Steam application ID" for P1733)."""
        if prop in self.verbose_names_cache:
            return self.verbose_names_cache[prop]

        prop_page = pywikibot.PropertyPage(self.repo, prop)
        if "en" in prop_page.labels:
            verbose_name = prop_page.labels["en"]
        else:
            verbose_name = prop

        self.verbose_names_cache[prop] = verbose_name
        return verbose_name

    def generate_source(self, database_id):
        """Create a Wikidata "stated in" source linking to this database page."""
        statedin = pywikibot.Claim(self.repo, "P248")
        statedin.setTarget(self.database_item)
        databaselink = pywikibot.Claim(self.repo, self.database_prop)
        databaselink.setTarget(database_id)
        retrieved = pywikibot.Claim(self.repo, "P813")
        retrieved.setTarget(get_current_wbtime())
        return [statedin, databaselink, retrieved]

    def seek_database_entry(self, item):
        """
        Try to find a database entry to connect with given Wikidata item.
        If found, return (entry_id, properties) tuple.
        If not found, throw RuntimeException.
        """
        if self.matching_prop not in item.claims:
            raise RuntimeError(f"{self.matching_prop_label} not found in the item")
        if len(item.claims[self.matching_prop]) > 1:
            raise RuntimeError(f"several {self.matching_prop_label}s found")
        matching_value = item.claims[self.matching_prop][0].getTarget()

        if "en" in item.labels:
            lang = "en"
        else:
            # any language is better than none
            lang = get_first_key(item.labels)

        checked_candidates = set()

        for candidate in self.search(item.labels[lang]):
            checked_candidates.add(candidate)
            properties = self.parse_entry(candidate)
            if self.matching_prop in properties:
                if properties[self.matching_prop] == matching_value:
                    return (candidate, properties)

        if self.should_check_aliases and lang in item.aliases:
            for alias in item.aliases[lang]:
                for candidate in self.search(alias, max_results=1):
                    if candidate in checked_candidates:
                        continue
                    checked_candidates.add(candidate)
                    properties = self.parse_entry(candidate)
                    if self.matching_prop in properties:
                        if properties[self.matching_prop] == matching_value:
                            return (candidate, properties)

        raise RuntimeError(f"no suitable {self.database_prop_label} found")
