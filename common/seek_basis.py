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
from typing import Optional, List
from argparse import ArgumentParser
from common.utils import get_first_key, get_current_wbtime, parse_input_source

class BaseIDSeekerBot:
    """
    Basic skeleton class for a bot that connects Wikidata items with given
    external database based on certain matching value.

    For instance, BaseIDSeekerBot("P8351", "P1733") is a bot that adds `vglist
    video game ID` (P8351), if both Wikidata item and vglist page are linked
    with the same `Steam application ID` (P1733).

    This is private class that should not be used directly. Use inherited
    DirectIDSeekerBot and SearchIDSeekerBot classes instead.
    """

    headers = {
        'User-Agent': 'Wikidata connecting bot',
    }

    def __init__(
        self,
        database_property: str,
        default_matching_property: str,
        qualifier_property: Optional[str] = None,
        allowed_matching_properties: Optional[List[str]] = None,
        additional_query_lines = None,
        should_set_source: bool = True,
        should_set_properties: bool = True
    ) -> None:
        """
        Initializer.

        :param database_property: Wikidata property ID (`Pnnn`) that links to
            the database to connect with.
        :param default_matching_property: Wikidata property ID (`Pnnn`) to use
            as a matching property by default.
        :param qualifier_property: Wikidata property ID (`Pnnn`) to add to
            database_property claims as a qualifier.
        :param allowed_matching_properties: list of Wikidata property IDs
            (`Pnnn`) that are allowed to be used as a matching property. If set,
            it must include default_matching_property.
        :param additional_query_lines: lines to add to SPARQL query while
            executing run() with "all" set as the source. For instance, you can
            add additional filters for `?item`.
        :param should_set_source: if set to False, bot would not add sources to
            database_property claims.
        :param should_set_properties: if set to False, bot would ignore additional
            information gathered by parse_item().
        """
        self.repo = pywikibot.Site()
        self.repo.login()

        self.database_property = database_property
        self.database_label = self.get_property_label(database_property)
        self.database_item = self.get_property_stated_in_value(database_property)
        self.qualifier_property = qualifier_property

        if additional_query_lines:
            self.additional_query_lines = "\n".join(additional_query_lines)
        else:
            self.additional_query_lines = ""

        self.matching_value = None

        if allowed_matching_properties:
            self.allowed_matching_properties = allowed_matching_properties
        else:
            self.allowed_matching_properties = [default_matching_property]
        self.change_matching_property(default_matching_property)

        self.should_set_source = should_set_source
        self.should_set_properties = should_set_properties

        self.output = None

    @functools.lru_cache
    def get_property_label(self, property_id: str) -> str:
        """Return property's label (for instance, "Steam application ID" for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, property_id)

        if "en" not in prop_page.labels:
            return property_id

        return prop_page.labels["en"]

    @functools.lru_cache
    def get_property_stated_in_value(self, property_id: str) -> pywikibot.ItemPage:
        """Return property's "stated in" value (for instance, ItemPage("Q337535") for P1733)."""
        prop_page = pywikibot.PropertyPage(self.repo, property_id)

        if "P9073" not in prop_page.claims:
            raise RuntimeError(f"applicable 'stated in' value not set for {property_id}")
        # TODO: check for None?
        return prop_page.claims["P9073"][0].getTarget()

    def change_matching_property(self, matching_property: str) -> None:
        """Set a property to use to match database entries with Wikidata items."""
        if matching_property not in self.allowed_matching_properties:
            raise RuntimeError(f"Unsupported matching property `{matching_property}`")

        self.matching_property = matching_property
        self.matching_label = self.get_property_label(matching_property)
        self.matching_item = self.get_property_stated_in_value(matching_property)

    def generate_matched_by_source(self) -> List[pywikibot.Claim]:
        """Create a Wikidata "matched by identifier from" source."""
        matched_by = pywikibot.Claim(self.repo, "P11797")
        matched_by.setTarget(self.matching_item)
        database_link = pywikibot.Claim(self.repo, self.matching_property)
        database_link.setTarget(self.matching_value)
        retrieved = pywikibot.Claim(self.repo, "P813")
        retrieved.setTarget(get_current_wbtime())
        return [matched_by, database_link, retrieved]

    def generate_stated_in_source(self, database_id: str) -> List[pywikibot.Claim]:
        """Create a Wikidata "stated in" source linking to this database page."""
        stated_in = pywikibot.Claim(self.repo, "P248")
        stated_in.setTarget(self.database_item)
        database_link = pywikibot.Claim(self.repo, self.database_property)
        database_link.setTarget(database_id)
        retrieved = pywikibot.Claim(self.repo, "P813")
        retrieved.setTarget(get_current_wbtime())
        return [stated_in, database_link, retrieved]

    def parse_item(self, item: pywikibot.ItemPage):
        """
        Use item claims to find a suitable database entry and return
            ( found_entries, additional_properties )
        tuple. If no database entry found, return ( None, {} ) or raise RuntimeError.

        found_entries should either be a str (in case there's only one database entry to connect
        with), or a list of ( entry_id, qualifier ) tuples. If more than one entry is specified,
        the first element of found_element is considered as matched by matching_property value,
        while the rest are considered as crosslinks stated in the first found entry. It affects
        sourcing (unless should_set_source is set to False).

        additional_properties is a { property: value_or_list_of_values } dict. First found_entries
        element would be used to source these properties.

        Example 1:
            ( "dorfromantik", {
                "P2725": "game/dorfromantik",
                "P1712": [ "game/pc/dorfromantik", "game/switch/dorfromantik" ],
            } )
        Sets database_property to "dorfromantik", GOG application ID (P2725) to "game/dorfromantik",
        Metacritic ID (P1712) to "game/pc/dorfromantik" and "game/switch/dorfromantik".

        Example 2:
            ( [ ( "minecraft", "121" ], None )
        Sets database_property to "minecraft" with qualifier_property "121". No additional
        properties set.

        Example 3:
            ( [ ( "1500", None ), ( "1501", None ), ( "1502", None ) ], None )
        Set database_property to "1500", then add crosslinks "1501" and "1502". No additional
        qualifiers or properties set.
        """

        raise NotImplementedError(f"{self.__class__.__name__}.parse_item() is not implemented")

    def process_item(self, item: pywikibot.ItemPage) -> None:
        """
        Fully process one item: seek database entry matching to current item,
        set external ID linking to this item, then optionally set other
        properties based on this entry.
        """
        try:
            if item.isRedirectPage():
                raise RuntimeError("item is a redirect page")
            if self.database_property in item.claims:
                raise RuntimeError(f"{self.database_label} already set")

            found_entries, additional_properties = self.parse_item(item)

            if not found_entries:
                raise RuntimeError(f"no suitable {self.database_label} found")

            if isinstance(found_entries, str):
                entry_id, qualifier_value = found_entries, None
                found_entries = []
            else:
                entry_id, qualifier_value = found_entries[0]
                found_entries = found_entries[1:]

            claim = pywikibot.Claim(self.repo, self.database_property)
            claim.setTarget(entry_id)
            if self.qualifier_property and qualifier_value:
                qualifier = pywikibot.Claim(self.repo, self.qualifier_property)
                qualifier.setTarget(qualifier_value)
                claim.addQualifier(qualifier)
            if self.should_set_source:
                claim.addSources(self.generate_matched_by_source())
            item.addClaim(claim, summary=f"Add {self.database_label} based on {self.matching_label}")
            print(f"{item.title()}: {self.database_label} set to `{entry_id}`")
            if self.output:
                self.output.write(f"{item.title()}\n")

            for crosslink, qualifier_value in found_entries:
                if crosslink == entry_id:
                    continue
                claim = pywikibot.Claim(self.repo, self.database_property)
                claim.setTarget(crosslink)
                if self.should_set_source:
                    claim.addSources(self.generate_stated_in_source(entry_id))
                if self.qualifier_property and qualifier_value:
                    qualifier = pywikibot.Claim(self.repo, self.qualifier_property)
                    qualifier.setTarget(qualifier_value)
                    claim.addQualifier(qualifier)

                item.addClaim(claim, summary=f"Add {self.database_label} (cross-linked with `{entry_id}`)")
                print(f"{item.title()}: {self.database_label} set to `{crosslink}` (cross-linked with `{entry_id}`)")

            if not (self.should_set_properties and additional_properties):
                return

            for key, values in additional_properties.items():
                if key == self.matching_property:
                    continue
                if key == self.database_property:
                    continue
                key_verbose = self.get_property_label(key)
                if key in item.claims:
                    print(f"{item.title()}: {key_verbose} already set")
                    continue

                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    claim = pywikibot.Claim(self.repo, key)
                    claim.setTarget(value)
                    claim.addSources(self.generate_stated_in_source(entry_id))
                    item.addClaim(claim, summary=f"Add {key_verbose} based on {self.database_label}")
                    print(f"{item.title()}: {key_verbose} set to `{value}`")

        except NotImplementedError as error:
            raise error
        except RuntimeError as error:
            print(f"{item.title()}: {error}")

    def run(self) -> None:
        """Parse command line arguments and process items accordingly."""
        if len(self.allowed_matching_properties) == 1:
            matching_property_description = f"{self.matching_label} ({self.matching_property})"
        else:
            matching_property_description = "matching property (second positional argument)"

        parser_arguments = {}
        parser_arguments["description"] = f"Add {self.database_label} ({self.database_property}) based on {matching_property_description}."
        if self.should_set_properties:
            parser_arguments["description"] += f" Then import data based on {self.database_label}."
        if self.allowed_matching_properties:
            proplist = ", ".join(sorted(self.allowed_matching_properties))
            parser_arguments["epilog"] = f"Supported base properties: {proplist}"

        parser = ArgumentParser(**parser_arguments)
        parser.add_argument("input", help="either a path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"")
        parser.add_argument("base", nargs="?", help=f"a property to use to match Wikidata items with database entries; defaults to \"{self.matching_property}\" ({self.matching_label})")
        parser.add_argument("-limit", "-l", type=int, default=0, help="a number of items to process (optional, only works with keyword \"all\")")
        parser.add_argument("-output", "-o", action="store", dest="output", help="a path to a file to fill with a list of processed items with added identifiers")
        args = parser.parse_args()

        try:
            if args.base:
                self.change_matching_property(args.base)

            if args.output:
                self.output = open(args.output, "a", encoding="utf-8")

            query = f"""
                SELECT ?item {{
                    ?item p:{self.matching_property} [] .
                    {self.additional_query_lines}
                    FILTER NOT EXISTS {{ ?item p:{self.database_property} [] }}
                }}
            """
            if args.limit:
                query += f"LIMIT {args.limit}"

            for item in parse_input_source(self.repo, args.input, query):
                self.process_item(item)
        except Exception as error:
            print(error)

class DirectIDSeekerBot(BaseIDSeekerBot):
    """
    This class should be used for databases with sophisticated API that allows
    user to request database entries by external identifiers, e. g. IGDB.

    Database-specific function seek_database_entry() should be re-implemented
    in the inherited classes.
    """
    def seek_database_entry(self):
        """
        Use self.matching_value (of self.matching_property) to retrieve database entry.
        Return value can either be a str with entry_id, or a tuple as described at
        BaseIDSeekerBot.parse_item() function.
        If no database entry found, return ( None, {} ) or raise RuntimeError.
        """
        raise NotImplementedError(f"{self.__class__.__name__}.seek_database_entry() is not implemented")

    def parse_item(self, item: pywikibot.ItemPage):
        """Straightforward implementation of BaseIDSeekerBot.parse_item()"""
        if self.matching_property not in item.claims:
            raise RuntimeError(f"{self.matching_label} not found in the item")
        if len(item.claims[self.matching_property]) > 1:
            raise RuntimeError(f"several {self.matching_label}s found")
        self.matching_value = item.claims[self.matching_property][0].getTarget()
        if self.matching_value is None:
            raise RuntimeError(f"{self.matching_label} is set to no_value or unknown_value")

        result = self.seek_database_entry()

        if isinstance(result, str):
            result = (result, {})

        return result

class SearchIDSeekerBot(BaseIDSeekerBot):
    """
    This class should be used for databases that have search API available.

    General algorithm for a given item is the following:
    1. Make a search request to a database using item label or alias as a query.
    2. Parse each found entry and get properties that can help identifying this
       entry (for instance, a link to yet another external database).
    3. If there is a matching property (for instance, both parsed entry and
       Wikidata item are describing Steam game with id "220"), connect this
       entry with the item.
    4. Optinally, if some of the parsed properties are missing in Wikidata item,
       add them as well.

    This class implements the general algorithm, but lacks database-specific
    preprocess_query(), search() and parse_entry() functions implementation.
    Those should be re-implemented in the inherited classes.
    """

    def __init__(self, *args, should_check_aliases: bool = True, **kwargs) -> None:
        """
        :param should_check_aliases: if set to False, bot would seek a database
            entry using item label only. Otherwise bot would also use item
            aliases.

        To get information about other available parameters, refer to
        BaseDirectSeekerBot.__init__() documentation.
        """
        super().__init__(*args, **kwargs)
        self.should_check_aliases = should_check_aliases

    def preprocess_query(self, query: str) -> str:
        """
        Optimize search query, for instance, remove capitalization or
        punctuation marks.
        """
        return query

    def search(self, query: str, max_results=None) -> List[str]:
        """
        Search on given database and return the list of found entry IDs.

        :param query: a search query
        :param max_results: a hint for the search engine - no more than this
            number of search results are required

        :return the list of found entry ids
        :raises RuntimeError: if bot should skip this item and continue
        """
        raise NotImplementedError(f"{self.__class__.__name__}.search() is not implemented")

    def parse_entry(self, entry_id: str):
        """
        Parse database entry and return all the data that can be either imported
        to Wikidata or used to match this entry with Wikidata item.

        Return value can either be a { property: value } dict (if no crosslinks
        and qualifiers are specified for this entry), or a tuple as described at
        BaseIDSeekerBot.parse_item() function.

        :param entry_id: an identifier or a slug of database entry to parse

        :raises RuntimeError: if bot should skip this item and continue
        """
        raise NotImplementedError(f"{self.__class__.__name__}.parse_entry() is not implemented")

    def parse_item(self, item: pywikibot.ItemPage):
        """Implementation of BaseIDSeekerBot.parse_item() using search API."""
        if self.matching_property not in item.claims:
            raise RuntimeError(f"{self.matching_label} not found in the item")
        if len(item.claims[self.matching_property]) > 1:
            raise RuntimeError(f"several {self.matching_label}s found")
        self.matching_value = item.claims[self.matching_property][0].getTarget()
        if self.matching_value is None:
            raise RuntimeError(f"{self.matching_label} is set to no_value or unknown_value")

        if "en" in item.labels:
            lang = "en"
        else:
            # any language is better than none
            lang = get_first_key(item.labels)

        processed_candidates = set()

        def process_candidate_helper(candidate):
            if candidate in processed_candidates:
                return None
            parsed_entry = self.parse_entry(candidate)
            processed_candidates.add(candidate)

            if isinstance(parsed_entry, tuple):
                crosslinks, properties = parsed_entry
            else:
                crosslinks, properties = candidate, parsed_entry

            if properties.get(self.matching_property) != self.matching_value:
                return None

            return (crosslinks, properties)

        query = self.preprocess_query(item.labels[lang])
        for candidate in self.search(query):
            result = process_candidate_helper(candidate)
            if result:
                return result

        processed_queries = { query }

        if self.should_check_aliases and lang in item.aliases:
            for alias in item.aliases[lang]:
                query = self.preprocess_query(alias)
                if query in processed_queries:
                    continue
                for candidate in self.search(query, max_results=1)[:1]:
                    result = process_candidate_helper(candidate)
                    if result:
                        return result
                processed_queries.add(query)

        raise RuntimeError(f"no suitable {self.database_label} found")
