# Copyright (c) 2024 Facenapalm
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
Add SteamGridDB ID (P12561) based on matching Steam application application ID (P1733).
To get started, type:
    python seek_pcgamingwiki_id.py -h

Script requires SteamGridDB API key, place it at ./keys/steamgriddb.key file.
"""

import re
import requests
from common.seek_basis import DirectIDSeekerBot

class SteamGridDBSeekerBot(DirectIDSeekerBot):
    headers = {
        "User-Agent": "Wikidata connecting bot",
    }

    def __init__(self):
        super().__init__(
            database_property='P12561',
            default_matching_property='P1733',
        )

        try:
            with open("keys/steamgriddb.key") as keyfile:
                self.api_key = keyfile.read().strip()
                self.headers["Authorization"] = "Bearer " + self.api_key
                print(self.headers)
        except FileNotFoundError as error:
            raise RuntimeError("SteamGridDB API key unspecified") from error

    def seek_database_entry(self):
        response = requests.get('https://www.steamgriddb.com/api/v2/games/steam/' + self.matching_value, headers=self.headers)
        if not response:
            raise RuntimeError(f"can't get info for game `{self.matching_value}`. Status code: {response.status_code}")
        hits = response.json()
        if not hits["success"]:
            raise RuntimeError(f"can't get info for game {self.matching_label} `{self.matching_value}`")
        
        gameid = str(hits["data"]["id"])

        return (gameid, {})

if __name__ == "__main__":
    SteamGridDBSeekerBot().run()
