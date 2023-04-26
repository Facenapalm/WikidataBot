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
Adventure Gamers video game ID (P7005) based on matching external idenitifiers,
for instance, Steam application ID (P1733).

To get started, type:

    python seek_adventuregamers_id.py -h
"""

import re
import requests
from common.seek_basis import BaseSeekerBot

class AdventureGamersSeekerBot(BaseSeekerBot):
    matchers = [
        {
            'regex': r'https://store\.steampowered\.com/app/(\d+)/',
            'property': 'P1733',
        },
        {
            'regex': r'https://(?:af\.)?gog\.com/(?:en/)?(game/[a-z0-9_]+?)(?:\?|$)',
            'property': 'P2725',
        },
        {
            'regex': r'https://www\.humblebundle\.com/store/([a-z0-9_\-]+?)(?:\?|$)',
            'property': 'P4477',
        },
        {
            'regex': r'(https://[a-z0-9_\-]+?\.itch\.io/[a-z0-9_\-]+?)(?:\?|$)',
            'property': 'P7294',
        }
    ]

    headers = {
        'User-Agent': 'Wikidata connecting bot',
    }

    def __init__(self):
        super().__init__(
            database_item='Q506391',
            database_prop='P7005',
            default_matching_prop='P1733',
            matching_prop_whitelist=['P1733', 'P2725', 'P4477', 'P7294'],
        )

    def search(self, query, max_results=None):
        params = [
            ( 'keywords', query ),
        ]
        response = requests.post('https://adventuregamers.com/games/search', params=params, headers=self.headers)
        if not response:
            raise RuntimeError(f'Query `{query}` resulted in {response.status_code}: {response.reason}')

        result = re.findall(r'<a href="/games/view/(\d+)">Full game details</a>', response.text)
        if max_results:
            return result[:max_results]
        else:
            return result

    def parse_entry(self, entry_id):
        response = requests.get(f'https://adventuregamers.com/games/view/{entry_id}', headers=self.headers)
        if not response:
            raise RuntimeError(f'Video game `{entry_id}` returned {response.status_code}: {response.reason}')
        html = response.text

        result = {}
        for store_link in re.findall(r'<a href="([^"]+)"[^>]+><div class="store_box">', html):
            for matcher in self.matchers:
                match = re.match(matcher['regex'], store_link)
                if match:
                    result[matcher['property']] = match.group(1)
                    break

        return result

if __name__ == '__main__':
    AdventureGamersSeekerBot().run()
