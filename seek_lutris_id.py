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

import urllib.parse
import urllib.request
import time
import random
import re
from common.seek_basis import BaseSeekerBot

IDS_DATA = {
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

class LutrisSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q75129027",
            database_prop="P7597",
            default_matching_prop="P1733",
            matching_prop_whitelist=[entry["property"] for entry in IDS_DATA.values()],
        )

    def __get_html(self, url, attempts=3):
        attempts = 3
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive"
        }
        for attempt_no in range(attempts):
            try:
                time.sleep(random.randint(1, 3))
                request = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(request)
                html = response.read().decode("utf-8")
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    html = ""
                else:
                    raise error
            except Exception as error:
                if attempt_no == (attempts - 1):
                    raise error
                else:
                    time.sleep(random.randint(2, 3))
        return html

    def search(self, query, max_results=None):
        params = {
            "q": query,
            "unpublished-filter": "on"
        }
        html = self.__get_html("https://lutris.net/games?" + urllib.parse.urlencode(params))
        results = re.findall(r"<div class=[\"']game-preview[\"']>\s+<a href=[\"']/games/([^\"']+)/\"", html)
        if max_results:
            return results[:max_results]
        else:
            return results

    def parse_entry(self, entry_id):
        html = self.__get_html(f"https://lutris.net/games/{entry_id}")
        result = {}
        for link in re.findall(r"<a [^>]*class=[\"']external-link[\"'].*?</a>", html, flags=re.DOTALL):
            href = re.search(r"href=[\"'](.*?)[\"']", link).group(1)
            span = re.search(r"<span>(.*?)</span>", link).group(1).lower()
            if span in IDS_DATA:
                data = IDS_DATA[span]
                match = re.match(data["mask"], href)
                if match:
                    if data["urldecode"]:
                        result[data["property"]] = urllib.parse.unquote(match.group(1))
                    else:
                        result[data["property"]] = match.group(1)
                else:
                    print(f"WARNING: {data['property']} found, but `{href}` doesn't match a mask")
        return result

if __name__ == "__main__":
    LutrisSeekerBot().run()
