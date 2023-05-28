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
Add Games@Mail.ru ID (P9697) based on matching Steam application ID (P1733).

To get started, type:

    python seek_mailru_id.py -h
"""

import requests
import re
from common.seek_basis import BaseSeekerBot

class MailRuSeekerBot(BaseSeekerBot):
    headers = {
        "User-Agent": "Wikidata connecting bot",
    }

    def __init__(self):
        super().__init__(
            database_prop="P9697",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733"],

            should_set_properties=False,
        )

    def search(self, query, max_results=None):
        params = [
            ( "query", query ),
        ]
        response = requests.get('https://api.games.mail.ru/pc/search_suggest/', params=params, headers=self.headers)
        if response:
            result = [item["slug"] for item in response.json()["game"]["items"]]
            if max_results:
                return result[:max_results]
            else:
                return result
        else:
            print(f"WARNING: can't get search results for query `{query}`")
            return []

    def parse_entry(self, entry_id):
        result = ""
        response = requests.get(f"https://api.games.mail.ru/pc/v2/game/{entry_id}/", headers=self.headers)
        try:
            if not response:
                raise RuntimeError("can't get info")
            for item in response.json()["game_urls"]:
                match = re.match(r"https?://store\.steampowered\.com/app/(\d+)", item["url"])
                if not match:
                    continue
                if result:
                    raise RuntimeError("several steam links found")
                result = match.group(1)
        except RuntimeError as error:
            print(f"WARNING: {error} for game `{entry_id}`")
            return {}
        return { "P1733": result }

if __name__ == "__main__":
    MailRuSeekerBot().run()
