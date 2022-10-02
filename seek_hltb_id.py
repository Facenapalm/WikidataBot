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
Add HowLongToBeat ID (P2816) based on matching Steam application ID (P1733).

Usage:

    python seek_hltb_id.py input

input should be either a path to file with list of items (Qnnn, one per line),
or a keyword "all".
"""

import re
import urllib.request
from howlongtobeatpy import HowLongToBeat
from seek_basis import BaseSeekerBot

class HLTBSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q22222506",
            database_prop="P2816",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733"],
        )

    def search(self, query, max_results=5):
        query = re.sub(" [–—] ", " ", query)
        search_results = HowLongToBeat(0.5).search(query)
        if search_results is None:
            return []
        else:
            return [str(entry.game_id) for entry in search_results][:max_results]

    def parse_entry(self, entry_id):
        attempts = 3
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive",
        }
        url = "https://howlongtobeat.com/game/{}".format(entry_id)
        for attempt_no in range(attempts):
            try:
                request = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(request)
                html = response.read().decode("utf-8", errors="ignore")
            except Exception as error:
                if attempt_no == (attempts - 1):
                    raise error

        # <strong><a class="text_red" href="https://store.steampowered.com/app/620/" rel="noreferrer" target="_blank">Steam</a></strong>
        matches = re.findall(r"href=\"https://store\.steampowered\.com/app/(\d+)[/\"]", html)
        if len(matches) == 1:
            return { "P1733": matches[0] }
        else:
            return {}

if __name__ == "__main__":
    HLTBSeekerBot().run()
