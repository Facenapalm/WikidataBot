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

import functools
import pywikibot
from argparse import ArgumentParser
from datetime import datetime
from common.utils import get_current_wbtime, parse_input_source

def get_first_key(dictionary):
    """Return first iterable key of the dictionary."""
    return next(iter(dictionary))


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

    def __init__(self, database_prop, default_matching_prop,
                 matching_prop_whitelist=None, additional_query_lines=[],
                 should_check_aliases=True, should_set_properties=True):
        """
        database_prop - Wikidata property (Pnnn) that links to the database.
        default_matching_prop - Wikidata property to use as a matching property
            by default.
        matching_prop_whitelist - Wikidata properties that are allowed to use as
            a matching property. If set, it must include default_matching_prop.
        additional_query_lines - lines to add to SPARQL query while executing
            run() with "all" set as an source. For instance, you can add
            additional filters for `?item`.
        should_check_aliases - if False, bot would seek a database entry using
            item label only. If True, bot would also use item aliases.
        should_set_properties - if set, bot would also upload the properties
            parsed by parse_entry() method to Wikidata.
        """
        self.repo = pywikibot.Site()
        self.repo.login()

        self.database_prop = database_prop
        self.database_prop_label = self.get_property_label(database_prop)
        self.database_item = self.get_property_stated_in_value(database_prop)

        self.additional_query_lines = "\n".join(additional_query_lines)

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
        self.matching_prop_label = self.get_property_label(matching_prop)
        self.matching_item = self.get_property_stated_in_value(matching_prop)

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
            claim.addSources(self.generate_matched_by_source())
            item.addClaim(claim, summary=f"Add {self.database_prop_label} based on matching {self.matching_prop_label}")
            print(f"{item.title()}: {self.database_prop_label} set to `{entry_id}`")

            if not self.should_set_properties:
                return

            if self.database_prop in properties:
                crosslinks = properties[self.database_prop]
                if not isinstance(crosslinks, list):
                    crosslinks = [crosslinks]
                for crosslink in crosslinks:
                    if crosslink == entry_id:
                        continue
                    claim = pywikibot.Claim(self.repo, self.database_prop)
                    claim.setTarget(crosslink)
                    item.addClaim(claim, summary=f"Add {self.database_prop_label} (cross-linked with `{entry_id}`)")
                    print(f"{item.title()}: {self.database_prop_label} set to `{crosslink}` (cross-linked with `{entry_id}`)")

            for key, value in properties.items():
                if key == self.matching_prop:
                    continue
                if key == self.database_prop:
                    continue
                key_verbose = self.get_property_label(key)
                if key in item.claims:
                    print(f"{item.title()}: {key_verbose} already set")
                    continue
                claim = pywikibot.Claim(self.repo, key)
                claim.setTarget(value)
                claim.addSources(self.generate_stated_in_source(entry_id))
                item.addClaim(claim, summary=f"Add {key_verbose} based on {self.database_prop_label}")
                print(f"{item.title()}: {key_verbose} set to `{value}`")

        except RuntimeError as error:
            print(f"{item.title()}: {error}")

    def run(self):
        """Parse command line arguments and process items accordingly."""
        matching_property_description = "matching property (second positional argument)"
        if self.matching_prop_whitelist:
            if len(self.matching_prop_whitelist) == 1:
                matching_property_description = f"{self.matching_prop_label} ({self.matching_prop})"

        parser_arguments = {}
        parser_arguments["description"] = f"Add {self.database_prop_label} ({self.database_prop}) based on {matching_property_description}."
        if self.should_set_properties:
            parser_arguments["description"] += f" Then import data based on {self.database_prop_label}."
        if self.matching_prop_whitelist:
            parser_arguments["epilog"] = "Supported base properties: {}".format(", ".join(sorted(self.matching_prop_whitelist)))

        parser = ArgumentParser(**parser_arguments)
        parser.add_argument("input", help="either a path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"")
        parser.add_argument("base", nargs="?", help=f"a property to use to match Wikidata items with database entries; defaults to \"{self.matching_prop}\" ({self.matching_prop_label})")
        parser.add_argument("-limit", "-l", type=int, default=0, help="a number of items to process (optional, only works with keyword \"all\")")
        args = parser.parse_args()

        try:
            if args.base:
                self.change_matching_property(args.base)

            query = f"""
                SELECT ?item {{
                    ?item p:{self.matching_prop} [] .
                    {self.additional_query_lines}
                    FILTER NOT EXISTS {{ ?item p:{self.database_prop} [] }}
                }}
            """
            if args.limit:
                query += f"LIMIT {args.limit}"

            for item in parse_input_source(self.repo, args.input, query):
                self.process_item(item)
        except Exception as error:
            print(error)

    # Virtual methods to be implemented in inherited classes.

    def preprocess_query(self, query):
        """Optimize search request."""
        return query

    def search(self, query, max_results=None):
        """Search in given database and return a list of entry IDs."""
        raise NotImplementedError(f"{self.__class__.__name__}.search() is not implemented")

    def parse_entry(self, entry_id):
        """Parse entry and return { property: value } dict."""
        raise NotImplementedError(f"{self.__class__.__name__}.parse_entry() is not implemented")

    # Private methods.

    @functools.lru_cache
    def get_property_label(self, prop):
        """Return property's label (for instance, "Steam application ID" for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, prop)

        if "en" in prop_page.labels:
            return prop_page.labels["en"]
        else:
            return prop

    @functools.lru_cache
    def get_property_stated_in_value(self, prop):
        """Return property's "stated in" value (for instance, ItemPage("Q337535") for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, prop)

        if "P9073" not in prop_page.claims:
            raise RuntimeError(f"applicable 'stated in' value not set for {prop}")
        return prop_page.claims["P9073"][0].getTarget()

    def generate_matched_by_source(self):
        """Create a Wikidata "matched by identifier from" source."""
        matchedby = pywikibot.Claim(self.repo, "P11797")
        matchedby.setTarget(self.matching_item)
        databaselink = pywikibot.Claim(self.repo, self.matching_prop)
        databaselink.setTarget(self.matching_value)
        retrieved = pywikibot.Claim(self.repo, "P813")
        retrieved.setTarget(get_current_wbtime())
        return [matchedby, databaselink, retrieved]

    def generate_stated_in_source(self, database_id):
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
        self.matching_value = item.claims[self.matching_prop][0].getTarget()

        if "en" in item.labels:
            lang = "en"
        else:
            # any language is better than none
            lang = get_first_key(item.labels)

        processed_candidates = set()

        query = self.preprocess_query(item.labels[lang])
        for candidate in self.search(query):
            properties = self.parse_entry(candidate)
            if self.matching_prop in properties:
                if properties[self.matching_prop] == self.matching_value:
                    return (candidate, properties)
            processed_candidates.add(candidate)

        processed_queries = { query }

        if self.should_check_aliases and lang in item.aliases:
            for alias in item.aliases[lang]:
                query = self.preprocess_query(alias)
                if query in processed_queries:
                    continue
                for candidate in self.search(query, max_results=1):
                    if candidate in processed_candidates:
                        continue
                    properties = self.parse_entry(candidate)
                    if self.matching_prop in properties:
                        if properties[self.matching_prop] == self.matching_value:
                            return (candidate, properties)
                    processed_candidates.add(candidate)
                processed_queries.add(query)

        raise RuntimeError(f"no suitable {self.database_prop_label} found")
