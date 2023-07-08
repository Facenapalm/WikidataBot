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
from common.seek_basis import SearchIDSeekerBot

class CoOptimusSeekerBot(SearchIDSeekerBot):
    headers = {
        "User-Agent": "Wikidata connecting bot",
    }

    def __init__(self):
        super().__init__(
            database_property="P8229",
            qualifier_property="P400",
            default_matching_property="P1733",
            additional_query_lines=["?item wdt:P404 wd:Q1758804 ."], # co-op games only
        )

        get_item = lambda x: pywikibot.ItemPage(self.repo, x)

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

    def get_platform_item(self, entry_id, platform_id):
        if platform_id not in self.platform_map:
            print(f"WARNING: unknown platform `{platform_id}`")
        return (entry_id, self.platform_map.get(platform_id))

    def search(self, query, max_results=None):
        query = query.replace("&", "_")
        params = [
            ( "game-title-filter", query ),
            ( "system", "4" ),
            ( "page", "1" )
        ]
        response = requests.get('https://www.co-optimus.com/ajax/ajax_games.php', params=params, headers=self.headers)
        if response:
            return re.findall(r'<tr class="result_row" id="(\d+)"', response.text)
        else:
            raise RuntimeError(f"can't get search results for query `{query}`. Status code: {response.status_code}")

    def parse_entry(self, entry_id):
        response = requests.get(f"https://www.co-optimus.com/game/{entry_id}/platform/game.html", headers=self.headers)
        result = None
        try:
            if not response:
                raise RuntimeError(f"can't get info")
            html = response.text
            match = re.search(r'<a class="button" target="_new" href="https?://store\.steampowered\.com/app/(\d+)/[^"]*"', html)
            if not match:
                raise RuntimeError(f"no Steam application ID found")
            result = match.group(1)

            # Steam ID found, now let's parse crosslinks for later

            crosslinks = [self.get_platform_item(entry_id, "pc")]

            match = re.search(r'<ul class="inline-list game-systems">.*?</ul>', html, flags=re.DOTALL)
            if not match:
                raise RuntimeError("no game systems list found")
            for entry_id, platform_id in re.findall(r'href="https?://www\.co-optimus\.com/game/(\d+)/([^/"]+)/', match.group(0)):
                crosslinks.append(self.get_platform_item(entry_id, platform_id))
        except RuntimeError as error:
            print(f"WARNING: {error} for entry `{entry_id}`")
        if result is None:
            return {}
        else:
            return ( crosslinks, { "P1733": result } )

if __name__ == "__main__":
    CoOptimusSeekerBot().run()
