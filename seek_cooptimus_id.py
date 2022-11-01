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
Add Co-Optimus ID (P8229) based on matching Steam application ID (P1733).

To get started, type:

    python seek_cooptimus_id.py -h
"""

import re
import requests
import pywikibot
from seek_basis import BaseSeekerBot

class CoOptimusSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q88198967",
            database_prop="P8229",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733"],

            should_set_properties=False,
        )

        get_item = lambda x: pywikibot.ItemPage(self.repo, x)

        self.platform_prop = "P400"
        self.platform_map = {
            "pc": get_item("Q16338"),
            "xbox": get_item("Q132020"),
            "xbox-360": get_item("Q48263"),
            "xbox-one": get_item("Q13361286"),
            "xbox-series": get_item("Q98973368"),
            "playstation-2": get_item("Q10680"),
            "playstation-3": get_item("Q10683"),
            "playstation-4": get_item("Q5014725"),
            "playstation-5": get_item("Q63184502"),
            "psp": get_item("Q170325"),
            "playstation-vita": get_item("Q188808"),
            "nintendo-ds": get_item("Q170323"),
            "nintendo-3ds": get_item("Q203597"),
            "wii": get_item("Q8079"),
            "nintendo-wii-u": get_item("Q56942"),
            "nintendo-switch": get_item("Q19610114"),
            "android": get_item("Q94"),
            "iphone-ipad": get_item("Q48493"),
            "ouya": get_item("Q1391641"),
            "classics-arcade": get_item("Q192851"),
            "classics-dreamcast": get_item("Q184198"),
            "classics-gamecube": get_item("Q182172"),
            "classics-nes": get_item("Q172742"),
            "classics-pc-dos": get_item("Q47604"),
            "classics-playstation": get_item("Q10677"),
            "classics-sega-genesis": get_item("Q10676"),
            "classics-sega-saturn": get_item("Q200912"),
            "classics-snes": get_item("Q183259"),
            "windows-phone": get_item("Q4885200"),
        }

        self.cached_entry = None
        self.cached_crosslinks = []

    def get_platform_item(self, platform_id):
        if platform_id in self.platform_map:
            return self.platform_map[platform_id]
        else:
            print("WARNING: unknown platform `{}`".format(platform_id))
            return None

    def set_cooptimus_id(self, item, entry_id, platform_id, summary):
        claim = pywikibot.Claim(self.repo, self.database_prop)
        claim.setTarget(entry_id)

        platform = self.get_platform_item(platform_id)
        if platform is not None:
            qualifier = pywikibot.Claim(self.repo, self.platform_prop)
            qualifier.setTarget(platform)
            claim.addQualifier(qualifier)

        item.addClaim(claim, summary=summary)
        print("{}: {} set to `{}` ({})".format(item.title(), self.database_prop_label, entry_id, platform_id))

    # implement abstract methods

    def search(self, query, max_results=None):
        query = query.replace("&", "_")
        params = [
            ( "game-title-filter", query ),
            ( "system", "4" ),
            ( "page", "1" )
        ]
        response = requests.get('https://www.co-optimus.com/ajax/ajax_games.php', params=params)
        if response:
            result = re.findall(r'<tr class="result_row" id="(\d+)"', response.text)
            if max_results:
                return result[:max_results]
            else:
                return result
        else:
            print("WARNING: can't get search results for query `{}`".format(query))
            return []

    def parse_entry(self, entry_id):
        response = requests.get("https://www.co-optimus.com/game/{}/platform/game.html".format(entry_id))
        result = None
        try:
            if not response:
                raise RuntimeError("can't get info".format(entry_id))
            html = response.text
            match = re.search(r'<a class="button" target="_new" href="https?://store\.steampowered\.com/app/(\d+)/[^"]*"', html)
            if not match:
                raise RuntimeError("no Steam application ID found".format(entry_id))
            result = match.group(1)

            # Steam ID found, now let's parse crosslinks for later

            self.cached_entry = entry_id
            self.cached_crosslinks = []

            match = re.search(r'<ul class="inline-list game-systems">.*?</ul>', html, flags=re.DOTALL)
            if not match:
                raise RuntimeError("no game systems list found")
            self.cached_crosslinks = re.findall(r'href="https?://www\.co-optimus\.com/game/(\d+)/([^/"]+)/', match.group(0))
        except RuntimeError as error:
            print("WARNING: {} for entry `{}`".format(error, entry_id))
        if result is None:
            return {}
        else:
            return { "P1733": result }

    # re-implement some methods

    def process_item(self, item):
        try:
            if item.isRedirectPage():
                raise RuntimeError("{} is a redirect page".format(item.title()))
            if self.database_prop in item.claims:
                raise RuntimeError("{} already set".format(self.database_prop_label))

            game_is_coop = False
            if "P404" in item.claims:
                # iterate through set game modes (P404) and check if
                # multiplayer video game (Q6895044) or "co-op mode" (Q1758804) is set
                for claim in item.claims["P404"]:
                    if claim.target is None:
                        continue
                    if claim.target.id in { "Q6895044", "Q1758804" }:
                        game_is_coop = True
                        break
            if not game_is_coop:
                raise RuntimeError("{} is not a multiplayer or co-op game".format(item.title()))

            entry_id, properties = self.seek_database_entry(item)

            if self.cached_entry != entry_id:
                raise RuntimeError("Internal error: cached_entry doesn't match entry_id")

            self.set_cooptimus_id(item, entry_id, "pc", "Add {} for PC based on matching {}".format(self.database_prop_label, self.matching_prop_label))

            for crosslink, platform in self.cached_crosslinks:
                if crosslink == entry_id:
                    continue
                self.set_cooptimus_id(item, crosslink, platform, "Add {} for platform `{}` (crosslinked with `{}`)".format(self.database_prop_label, platform, entry_id))
        except RuntimeError as error:
            print("{}: {}".format(item.title(), error))

    def process_all_items(self, limit=None):
        # only process items with game mode (P404) = co-op mode (Q1758804)
        query = """
            SELECT ?item {
                ?item p:P1733 [] .
                ?item wdt:P404 wd:Q1758804 .
                FILTER NOT EXISTS { ?item p:P8229 [] }
            }
        """
        if limit:
            query += "LIMIT {}".format(limit)
        generator = pywikibot.pagegenerators.WikidataSPARQLPageGenerator(query, site=self.repo)
        for item in generator:
            self.process_item(item)

if __name__ == "__main__":
    CoOptimusSeekerBot().run()
