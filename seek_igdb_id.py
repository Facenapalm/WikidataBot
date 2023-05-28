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
Add Internet Game Database game ID (P5794) based on matching Steam application ID (P1733).

To get started, type:

    python seek_igdb_id.py -h
"""

import pywikibot
from common.igdb_wrapper import IGDB
from common.seek_basis import BaseSeekerBot

class IGDBSeekerBot(BaseSeekerBot):
    # Unlike most databases, IGDB allows user to directly fetch games that have a link to certain
    # video game distribution platforms like Steam and GOG. That means our standard algorithm
    # based on search() and parse_entry() is not required. We'll just re-implement process_item()
    # instead.

    queries = {
        "P1733": [
            # https://store.steampowered.com/app/220
            ("websites", 'fields game; where url = *"/app/{}" & category = 13;'),

            # https://store.steampowered.com/app/220/HalfLife_2/
            ("websites", 'fields game; where url = *"/app/{}/"* & category = 13;'),
        ],
        "P2725": [
            # https://www.gog.com/game/cyberpunk_2077
            ("websites", 'fields game; where url = *"/{}" & category = 17;'),
        ],
        "P6278": [
            # https://store.epicgames.com/ru/p/kena-bridge-of-spirits
            ("websites", 'fields game; where url = *"/{}" & category = 16;'),
        ]
    }

    def __init__(self):
        super().__init__(
            database_prop="P5794",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733", "P2725", "P6278"],

            should_set_properties=False,
        )
        self.numeric_prop = "P9043"
        self.wrapper = IGDB()

    def seek_database_entry(self, item):
        if self.matching_prop not in item.claims:
            raise RuntimeError(f"{self.matching_prop_label} not found in the item")
        if len(item.claims[self.matching_prop]) > 1:
            raise RuntimeError(f"several {self.matching_prop_label}s found")
        self.matching_value = item.claims[self.matching_prop][0].getTarget()

        result = []
        for endpoint, query in self.queries[self.matching_prop]:
            result += self.wrapper.request(endpoint, query.format(self.matching_value))

        if len(result) == 0:
            raise RuntimeError(f"no IGDB entries are linked to {self.matching_prop_label} `{self.matching_value}`")
        if len(result) > 1:
            raise RuntimeError(f"several IGDB entries are linked to {self.matching_prop_label} `{self.matching_value}`")

        igdb_id = str(result[0]["game"])
        igdb_slug = self.wrapper.get_slug_by_id(igdb_id)

        return (igdb_slug, igdb_id)

    def process_item(self, item):
        try:
            if item.isRedirectPage():
                raise RuntimeError("item is a redirect page")
            if self.database_prop in item.claims:
                raise RuntimeError(f"{self.database_prop_label} already set")

            igdb_slug, igdb_id = self.seek_database_entry(item)

            claim = pywikibot.Claim(self.repo, self.database_prop)
            claim.setTarget(igdb_slug)
            qualifier = pywikibot.Claim(self.repo, self.numeric_prop)
            qualifier.setTarget(igdb_id)
            claim.addQualifier(qualifier)
            claim.addSources(self.generate_matched_by_source())
            item.addClaim(claim, summary=f"Add {self.database_prop_label} based on matching {self.matching_prop_label}")
            print(f"{item.title()}: IGDB ID set to `{igdb_slug}` (numeric id `{igdb_id}`)")
        except RuntimeError as error:
            print(f"{item.title()}: {error}")

if __name__ == "__main__":
    IGDBSeekerBot().run()
