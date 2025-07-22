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
Add MobyGames game ID (P11688) based on matching Steam application ID (P1733).

To get started, type:

    python seek_mobygames_id.py -h

Script requires API key, place it at ./keys/mobygames.key file.
"""

import re
import requests
from time import sleep
from os.path import isfile
from common.seek_basis import DirectIDSeekerBot

class MobyGamesSeekerBot(DirectIDSeekerBot):
    headers = {
        'User-Agent': 'Wikidata connecting bot',
        'Content-Type': 'application/json',
    }

    query = '''\
    query gamepickq {{
      games(identifier_source_id: {source}, identifier: {identifier}) {{
        id,
        title,
        moby_url,
        identifiers {{
          source {{ id, name }},
          identifier,
          url
        }}
      }}
    }}
    '''

    def __init__(self):
        super().__init__(
            database_property='P11688',
            default_matching_property='P1733',
            allowed_matching_properties=['P1733', 'P5944'],
            additional_query_lines=['FILTER NOT EXISTS { ?item p:P1933 [] }'],
        )

        filename = 'keys/mobygames.key'
        if isfile(filename):
            self.api_key = open(filename).read().strip()
        else:
            raise RuntimeError('MobyGames API key unspecified')

    def make_query(self):
        if self.matching_property == 'P1733':
            result = self.query.format(source=1, identifier=self.matching_value)
        elif self.matching_property == 'P5944':
            result = self.query.format(source=11, identifier=f'"en-us/{self.matching_value}"')
        else:
            raise NotImplementedError(f'unknown matching property {self.matching_propery}')
        return { 'query': result }

    def seek_database_entry(self):
        sleep(1)
        try:
            response = requests.post(
                f'https://api.mobygames.com/v2/graphql?api_key={self.api_key}',
                headers=self.headers,
                json=self.make_query(),
                timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            raise RuntimeError(f"can't get info for game `{self.matching_value}`. Status code: {response.status_code}")
        games = response.json()['data']['games']
        if not games:
            raise RuntimeError(f"no MobyGames entries are linked to {self.matching_label} `{self.matching_value}`")
        if len(games) > 1:
            raise RuntimeError(f'several MobyGames entries are linked to {self.matching_label} `{self.matching_value}`')

        return str(games[0]['id'])

if __name__ == '__main__':
    MobyGamesSeekerBot().run()
