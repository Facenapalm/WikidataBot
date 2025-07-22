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
Add Lutris ID (P7597) based on matching external identifier (for instance,
Steam application ID, P1733) and/or fill the item with other external IDs
stated in Lutris database - for instance, IGDB, MobyGames or PCGamingWiki.

To get started, type:

    python seek_lutris_id.py -h
"""

import re
import time
import requests
from urllib.parse import unquote
from common.seek_basis import SearchIDSeekerBot

class LutrisBot():
    ids_data = {
        "igdb": {
            "property": "P5794",
            "mask": r"^https?://www\.igdb\.com/games/([a-z0-9\-]+)",
            "urldecode": False,
        },
        "steam": {
            "property": "P1733",
            "mask": r"^https?:\/\/(?:store\.)?steam(?:community|powered)\.com\/app\/(\d+)",
            "urldecode": False,
        },
        "mobygames": {
            "property": "P1933",
            "mask": r"^https?://www\.mobygames\.com/game/(?:windows/|dos/|gameboy-color/|macintoshxbox-one/|ps2/|ps1/|ps2/|ps3/|playstation/|playstation-4/|xbox/|xbox-one/|xbox-series/|switch/|n64/|android/|iphone/|ipad/|wii/|oculus-quest/|gameboy/)?([a-z0-9_\-]+)",
            "urldecode": False,
        },
        "pcgamingwiki": {
            "property": "P6337",
            "mask": r"^https?://(?:www\.)?pcgamingwiki\.com/wiki/([^\s]+)",
            "urldecode": True,
        },
        "winehq appdb": {
            "property": "P600",
            "mask": r"^https?://appdb\.winehq\.org/objectManager\.php\?sClass=application&amp;iId=([1-9][0-9]*)",
            "urldecode": False,
        },
        # TODO: GOG DB (for example: https://lutris.net/games/the-chaos-engine/ ) ?
    }

    def parse_entry(self, entry_id):
        try:
            response = requests.get(f"https://lutris.net/games/{entry_id}", headers=self.headers, timeout=20)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        time.sleep(1)
        if not response:
            raise RuntimeError(f"can't get info for `{entry_id}` ({response.status_code})")

        result = {}
        for link in re.findall(r"<a [^>]*class=[\"']external-link[\"'].*?</a>", response.text, flags=re.DOTALL):
            href = re.search(r"href=[\"'](.*?)[\"']", link).group(1)
            span = re.search(r"<span>(.*?)</span>", link).group(1).lower()
            if span in self.ids_data:
                data = self.ids_data[span]
                match = re.match(data["mask"], href)
                if match:
                    if data["urldecode"]:
                        result[data["property"]] = unquote(match.group(1))
                    else:
                        result[data["property"]] = match.group(1)
                else:
                    print(f"WARNING: {data['property']} found, but `{href}` doesn't match a mask")
        return result

class LutrisSeekerBot(LutrisBot, SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property="P7597",
            default_matching_property="P1733",
            allowed_matching_properties=[entry["property"] for entry in self.ids_data.values()],
        )

    def search(self, query, max_results=None):
        params = {
            "q": query,
            "unpublished-filter": "on"
        }
        try:
            response = requests.get("https://lutris.net/games", params=params, headers=self.headers, timeout=20)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        time.sleep(1)
        if not response:
            raise RuntimeError(f"can't get search results for query `{query}`. Status code: {response.status_code}")

        return re.findall(r"<div class=[\"']game-preview[\"']>\s+<a href=[\"']/games/([^\"']+)/\"", response.text)

if __name__ == "__main__":
    LutrisSeekerBot().run()
