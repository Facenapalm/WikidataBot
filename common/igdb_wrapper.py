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

"""IGDB API re-wrapper."""

from time import sleep
import requests
import json
from igdb.wrapper import IGDBWrapper

class IGDB():
    def __init__(self):
        client_id = open("keys/igdb-id.key").read()
        client_secret = open("keys/igdb-secret.key").read()
        access_token = requests.post(f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials").json()["access_token"]
        self.wrapper = IGDBWrapper(client_id, access_token)

    def request(self, endpoint, query):
        """Get query result as parsed json."""
        sleep(.25)
        result = self.wrapper.api_request(endpoint, query).decode("utf-8")
        return json.loads(result)

    def get_slug_by_id(self, igdb_id):
        """Get IGDB ID by IGDB numeric ID."""
        response = self.request("games", f"fields slug; where id = {igdb_id};")
        if len(response) == 0:
            return None
        return response[0]["slug"]

    def get_id_by_slug(self, igdb_slug):
        """Get IGDB numeric ID by IGDB ID."""
        response = self.request("games", f'fields id; where slug = "{igdb_slug}";')
        if len(response) == 0:
            return None
        return str(response[0]["id"])
