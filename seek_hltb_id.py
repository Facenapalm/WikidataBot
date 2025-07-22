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

To get started, type:

    python seek_hltb_id.py -h
"""

import re
import requests
from howlongtobeatpy import HowLongToBeat
from common.seek_basis import SearchIDSeekerBot

class HLTBSeekerBot(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property="P2816",
            default_matching_property="P1733",
        )

        self.hltb = HowLongToBeat(0.5)

    def preprocess_query(self, query):
        return re.sub(" [–—] ", " ", query)

    def search(self, query, max_results=5):
        search_results = self.hltb.search(query)
        if search_results is None:
            return []
        else:
            return [str(entry.game_id) for entry in search_results][:max_results]

    def parse_entry(self, entry_id):
        try:
            response = requests.get(f"https://howlongtobeat.com/game/{entry_id}", headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            raise RuntimeError(f"can't get info for entry `{entry_id}`")

        # <strong><a class="text_red" href="https://store.steampowered.com/app/620/" rel="noreferrer" target="_blank">Steam</a></strong>
        matches = re.findall(r"href=\"https://store\.steampowered\.com/app/(\d+)[/\"]", response.text)
        if len(matches) == 1:
            return { "P1733": matches[0] }
        else:
            return {}

if __name__ == "__main__":
    HLTBSeekerBot().run()
