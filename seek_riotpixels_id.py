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
Add Riot Pixels ID (P10393) based on matching external identifier (for
instance, Steam application ID, P1733).

To get started, type:

    python riotpixels_seek_id.py -h
"""

import re
import urllib.request
from urllib.parse import quote
from common.seek_basis import BaseSeekerBot

IDS_DATA = [
    {
        "regex": r"<a rel=\"nofollow\" class=\"inline\" href=\"https?://store\.steampowered\.com/app/(\d+)(?:/[^\"]*)?\" target=_blank>Страница в Steam</a>",
        "property": "P1733",
    },
    {
        "regex": r"<a rel=\"nofollow\" class=\"inline\" href=\"https?://www\.gog\.com/(game/[^\"]+)\" target=_blank>Страница в GOG</a>",
        "property": "P2725",
    },
    {
        "regex": r"<a rel=\"nofollow\" class=\"inline\" href=\"https?://www\.epicgames\.com/store/product/([^\"]+)/\" target=_blank>Страница в магазине Epic Games</a>",
        "property": "P6278",
    },
]

class RiotPixelsSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q19612893",
            database_prop="P10393",
            default_matching_prop="P1733",
            matching_prop_whitelist=[entry["property"] for entry in IDS_DATA],
        )

    def __get_html(self, url, attempts=10):
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
                request = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(request, timeout=20)
                html = response.read().decode("utf-8")
            except Exception as error:
                if attempt_no == (attempts - 1):
                    raise error
        return html

    def search(self, query, max_results=20):
        html = self.__get_html("https://ru.riotpixels.com/search/{}".format(quote(query)))
        return re.findall(r"\"id\": \"games-([a-z0-9\-]+)\"", html)[:max_results]

    def parse_entry(self, entry_id):
        html = self.__get_html("https://ru.riotpixels.com/games/{}/".format(entry_id))
        result = {}
        for id_data in IDS_DATA:
            match = re.search(id_data["regex"], html)
            if match:
                result[id_data["property"]] = match.group(1)
        return result

if __name__ == "__main__":
    RiotPixelsSeekerBot().run()
