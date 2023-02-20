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
Extract IGDB numeric ID (P9043) based on IGDB ID (P5794).

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P5794#"Mandatory_Qualifiers"_violations

Script requires Twitch Developer Client ID and Client Secret. Place them at
./keys/igdb-id.key and ./keys/igdb-secret.key files respectively.
"""

import requests
import json
from time import sleep
from igdb.wrapper import IGDBWrapper
from qualify_basis import QualifyingBot

class IGDBQualifyingBot(QualifyingBot):
    def __init__(self):
        super().__init__(
            base_property="P5794",
            qualifier_property="P9043",
        )

        client_id = open("keys/igdb-id.key").read()
        client_secret = open("keys/igdb-secret.key").read()
        access_token = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials").json()["access_token"]
        self.wrapper = IGDBWrapper(client_id, access_token)

    def request(self, endpoint, query):
        sleep(.25)
        result = self.wrapper.api_request(endpoint, query).decode("utf-8")
        return json.loads(result)

    def get_qualifier_values(self, base_value):
        try:
            return [str(self.request("games", f'fields id; where slug="{base_value}";')[0]["id"])]
        except:
            return None

if __name__ == "__main__":
    IGDBQualifyingBot().run()
