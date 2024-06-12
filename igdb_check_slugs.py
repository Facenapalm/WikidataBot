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

"""
Process changed and deprecate withdrawn IGDB slugs (P5794) based on IGDB numeric ID (P9043)
qualifier.

Usage:

    python igdb_check_slugs.py
"""

import re
import pywikibot
from pywikibot.data.sparql import SparqlQuery
from common.igdb_wrapper import IGDB
from argparse import ArgumentParser

class IGDBMaintainingBot():
    QUERY = """
    SELECT ?item ?id ?slug {
        ?item p:P5794 ?x .
        FILTER NOT EXISTS { ?x wikibase:rank wikibase:DeprecatedRank } .
        ?x ps:P5794 ?slug .
        ?x pq:P9043 ?id .
    }
    """

    def __init__(self):
        self.igdb = IGDB()
        self.repo = pywikibot.Site()
        self.repo.login()

        self.reset_counters()

    def reset_counters(self):
        self.deprecations = 0
        self.changes = 0

    def find_claim(self, item_id, value):
        item = pywikibot.ItemPage(self.repo, item_id)
        if "P5794" not in item.claims:
            return None
        for claim in item.claims["P5794"]:
            if claim.getTarget() == value:
                return claim
        return None

    def deprecate_slug(self, item_id, slug):
        claim = self.find_claim(item_id, slug)
        if claim is None:
            return
        if claim.rank == 'deprecated':
            return
        claim.changeRank('deprecated')
        qualifier = pywikibot.Claim(self.repo, "P2241")
        qualifier.setTarget(pywikibot.ItemPage(self.repo, "Q21441764"))
        claim.addQualifier(qualifier, summary="Identifier value was withdrawn")

        self.deprecations += 1
        print(f"{item_id}: `{slug}` -> deprecated")

    def change_slug(self, item_id, old_slug, new_slug):
        claim = self.find_claim(item_id, old_slug)
        if claim is None:
            return
        claim.changeTarget(new_slug, summary="Restore slug based on IGDB numeric ID")

        self.changes += 1
        print(f"{item_id}: `{old_slug}` -> `{new_slug}`")

    def run(self):
        parser = ArgumentParser(description="Process changed and deprecate withdrawn IGDB slugs " \
            "(P5794) based on IGDB numeric ID (P9043) qualifier. Script checks all set IGDB slugs " \
            "by using SPARQL query, no arguments required.")
        args = parser.parse_args()

        self.reset_counters()

        sparql = SparqlQuery()
        result = sparql.select(self.QUERY)
        size = len(result)

        print(f"Query complete ({size} entries to process)")
        for idx in range(0, len(result), 10):
            if idx % 1000 == 0:
                print(f"{idx} entries processed ({round(idx / size * 100, 1)} %)")

            id_list = [entry["id"] for entry in result[idx:idx+10] if re.match(r"^\d+$", entry["id"])]
            if len(id_list) == 0:
                continue

            query = 'fields id, slug; where id = (' + ', '.join(id_list) + ');'
            slug_map = { str(entry["id"]): entry["slug"] for entry in self.igdb.request("games", query) }

            for entry in result[idx:idx+10]:
                igdb_id = entry["id"]
                if igdb_id not in id_list:
                    # unknownvalue or novalue
                    continue

                item_id = re.match(r"^https?://www\.wikidata\.org/entity/(Q\d+)$", entry["item"]).group(1)
                old_slug = entry["slug"]
                if igdb_id not in slug_map:
                    self.deprecate_slug(item_id, old_slug)
                    continue

                new_slug = slug_map[igdb_id]
                if old_slug != new_slug:
                    self.change_slug(item_id, old_slug, new_slug)

        print(f"{size} entries processed, {self.deprecations} claims deprecated, {self.changes} slugs updated")

if __name__ == "__main__":
    IGDBMaintainingBot().run()
