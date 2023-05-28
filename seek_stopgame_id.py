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
Add StopGame ID (P10030) based on matching Steam application ID (P1733).

To get started, type:

    python seek_stopgame_id.py -h
"""

import requests
import re
from common.seek_basis import BaseSeekerBot

class StopGameSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_prop="P10030",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733"],

            should_set_properties=False,
        )

        self.headers = {
            "User-Agent": "Wikidata connecting bot",
        }

    def search(self, query, max_results=None):
        params = [
            ( "term", query ),
        ]
        response = requests.get('https://stopgame.ru/ajax/search/games', params=params, headers=self.headers)
        if response:
            result = [x["url"][6:] for x in response.json()["results"] if x["url"].startswith("/game/")]
            if max_results:
                return result[:max_results]
            else:
                return result
        else:
            print(f"WARNING: can't get search results for query `{query}`")
            return []

    def parse_entry(self, entry_id):
        response = requests.get('https://stopgame.ru/game/' + entry_id, headers=self.headers)
        if not response:
            print(f"WARNING: can't get info for game `{entry_id}`")
            return {}
        html = response.text
        match = re.search(r"<div[^>]*>\s*Сайт игры\s*</div>\s*<div[^>]*>(?:(?!</div>)[\s\S])*<a href='https://store\.steampowered\.com/app/(\d+)' target='_blank' rel='nofollow'>Steam</a>", html)
        if not match:
            return {}
        return { "P1733": match.group(1) }

if __name__ == "__main__":
    StopGameSeekerBot().run()
