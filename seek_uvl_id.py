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

import re
import requests
from common.seek_basis import BaseSeekerBot

class UVLSeeker(BaseSeekerBot):
    headers = {
        'User-Agent': 'Wikidata connecting bot',
    }

    def __init__(self):
        super().__init__(
            database_prop='P7555',
            default_matching_prop='P1733',
            matching_prop_whitelist=['P1733'],

            should_set_properties=True
        )

    def preprocess_query(self, query):
        return query.lower()

    def search(self, query, max_results=None):
        params = [
            ( 'fname', query ),
            ( 'ftag', 'steampowered' )
        ]
        response = requests.post('https://www.uvlist.net/gamesearch/', params=params, headers=self.headers)
        if not response:
            raise RuntimeError(f'Query `{query}` resulted in {response.status_code}: {response.reason}')

        result = re.findall(r"<td><a href='/game-(\d+)-", response.text)
        if max_results:
            return result[:max_results]
        else:
            return result

    def parse_entry(self, entry_id):
        response = requests.get(f'https://www.uvlist.net/game-{entry_id}', headers=self.headers)
        if not response:
            # print(f'WARNING: video game `{entry_id}` returned {response.status_code}: {response.reason}')
            return {}
        html = response.text

        match = re.search(r"<h2 class='acc_head' id='acc_xrefs'>([\s\S]+?)</div>", html)
        if not match:
            # print(f'WARNING: no xref section found for video game `{entry_id}`')
            return {}
        xrefs = match.group(1)

        result = {}
        match = re.search(r"href='https?://store\.steampowered\.com/app/(\d+)[/']", xrefs)
        if match:
            result['P1733'] = match.group(1)
        match = re.search(r"href='https?://www\.gog\.com/(?:en/)?(game/[a-z0-9_]+)[?']", xrefs)
        if match:
            result['P2725'] = match.group(1)

        crosslinks = []

        def parse_crosslinks(section_matcher):
            match = re.search(section_matcher, html)
            if match:
                nonlocal crosslinks
                crosslinks += re.findall(r'/game-(\d+)-', match.group(0))

        parse_crosslinks(r'version of(?:\s*(?:<br />|<a .*?</a>))+')
        parse_crosslinks(r'ported to(?:\s*(?:<br />|<a .*?</a>))+')
        parse_crosslinks(r'port of(?:\s*(?:<br />|<a .*?</a>))+')

        if crosslinks:
            result['P7555'] = crosslinks

        return result

if __name__ == '__main__':
    UVLSeeker().run()
