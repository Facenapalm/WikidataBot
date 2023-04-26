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

"""
Add Indie DB game ID (P6717) based on Mod DB game ID (P6774), if available.

To get started, type:

    python seek_indiedb_id.py -h
"""

import re
import time
import requests
import pywikibot
from common.seek_basis import BaseSeekerBot

class IndieDBSeekerBot(BaseSeekerBot):
    # Since Indie DB is a subset of Mod DB, we can just check whether Mod DB ID is suitable
    # and copy it into Indie DB ID property.

    def check_slug(self, slug):
        if slug is None:
            return False
        response = requests.get(f"https://www.indiedb.com/games/{slug}", headers=self.headers)
        time.sleep(2)
        if response:
            return "NOT available on Indie DB" not in response.text
        else:
            print(f"WARNING: failed to get `{slug}`")
            return False

    def __init__(self):
        super().__init__(
            database_item="Q60188888",
            database_prop="P6717",
            default_matching_prop="P6774",
            matching_prop_whitelist=["P6774"],

            should_set_properties=False,
        )

        self.headers = {
            "User-Agent": "Wikidata connecting bot",
        }

        if self.check_slug("cyberpunk-2077"):
            raise RuntimeError("Can't detect missing Indie DB entries, script needs to be updated")

    def process_item(self, item):
        try:
            if item.isRedirectPage():
                raise RuntimeError("item is a redirect page")
            if self.database_prop in item.claims:
                raise RuntimeError(f"{self.database_prop_label} already set")
            if self.matching_prop not in item.claims:
                raise RuntimeError(f"{self.matching_prop_label} not found in the item")

            for moddb_claim in item.claims[self.matching_prop]:
                slug = moddb_claim.getTarget()
                if not self.check_slug(slug):
                    raise RuntimeError(f"`{slug}` not found in Indie DB")
                claim = pywikibot.Claim(self.repo, self.database_prop)
                claim.setTarget(slug)
                item.addClaim(claim, summary="Add Indie DB game ID based on Mod DB game ID")
                print(f"{item.title()}: added Indie DB game ID `{slug}`")
        except RuntimeError as error:
            print(f"{item.title()}: {error}")

if __name__ == "__main__":
    IndieDBSeekerBot().run()
