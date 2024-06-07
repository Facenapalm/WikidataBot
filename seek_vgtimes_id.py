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
Add VGTimes ID (P10453) based on matching Steam application ID (P1733).

To get started, type:

    python seek_vgtimes_id.py -h
"""

import requests
import re
from common.seek_basis import SearchIDSeekerBot

class VGTimesSeekerBot(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property='P10453',
            default_matching_property='P1733',
        )

    def preprocess_query(self, query):
        return query.replace('<', '').replace('>', '')

    def search(self, query, max_results=None):
        params = {
            'action': 'search2',
            'query': query,
            'ismobile': '1',
            'what': '1',
        }
        response = requests.post('https://vgtimes.ru/engine/ajax/search.php', params=params, headers=self.headers)
        if not response:
            raise RuntimeError(f"can't get search results for query `{query}`. Status code: {response.status_code}")
        json = response.json()
        if 'results' not in json or 'games' not in json['results']:
            return
        html = json['results']['games']
        if not html:
            return []
        result = re.findall(r'<a href="/games/([^"]+)/" class="game_click">', html)
        if max_results is not None:
            result = result[:max_results]
        return result

    def parse_entry(self, entry_id):
        response = requests.get(f'https://vgtimes.ru/games/{entry_id}/', headers=self.headers)
        if not response:
            print(f"WARNING: can't get info for game `{entry_id}`")
            return {}
        html = response.text
        match = re.search(r'<a href="https://store\.steampowered\.com/app/(\d+)/?" target="_blank" class="l_ks">', html)
        if not match:
            return {}
        return { 'P1733': match.group(1) }

if __name__ == '__main__':
    VGTimesSeekerBot().run()
