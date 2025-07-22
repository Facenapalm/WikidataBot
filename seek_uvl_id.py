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
Add UVL game ID (P7555) based on Steam application ID (P1733).

To get started, type:

    python seek_uvl_id.py -h
"""

import re
import requests
from common.seek_basis import SearchIDSeekerBot

class UVLSeeker(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property='P7555',
            default_matching_property='P1733',
        )

    def preprocess_query(self, query):
        return query.lower()

    def search(self, query, max_results=None):
        params = [
            ( 'fname', query ),
            ( 'ftag', 'steampowered' )
        ]
        try:
            response = requests.post('https://www.uvlist.net/gamesearch/', params=params, headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            raise RuntimeError(f'Query `{query}` resulted in {response.status_code}: {response.reason}')

        return re.findall(r'<td><a href=[\'"]/game-(\d+)-', response.text)

    def parse_entry(self, entry_id):
        try:
            response = requests.get(f'https://www.uvlist.net/game-{entry_id}', headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            # print(f'WARNING: video game `{entry_id}` returned {response.status_code}: {response.reason}')
            return {}
        html = response.text

        match = re.search(r'<h2 class=[\'"]acc_head[\'"] id=[\'"]acc_xrefs[\'"]>([\s\S]+?)</div>', html)
        if not match:
            # print(f'WARNING: no xref section found for video game `{entry_id}`')
            return {}
        xrefs = match.group(1)

        properties = {}
        match = re.search(r'href=[\'"]https?://store\.steampowered\.com/app/(\d+)[/\'"]', xrefs)
        if match:
            properties['P1733'] = match.group(1)
        match = re.search(r'href=[\'"]https?://www\.gog\.com/(?:en/)?(game/[a-z0-9_]+)[?\'"]', xrefs)
        if match:
            properties['P2725'] = match.group(1)

        crosslinks = [ (entry_id, None) ]

        def parse_crosslinks(section_matcher):
            match = re.search(section_matcher, html)
            if match:
                nonlocal crosslinks
                crosslinks.extend([(crosslink, None) for crosslink in re.findall(r'/game-(\d+)-', match.group(0))])

        parse_crosslinks(r'version of(?:\s*(?:<br */?>|<a .*?</a>))+')
        parse_crosslinks(r'ported to(?:\s*(?:<br */?>|<a .*?</a>))+')
        parse_crosslinks(r'port of(?:\s*(?:<br */?>|<a .*?</a>))+')

        return (crosslinks, properties)

if __name__ == '__main__':
    UVLSeeker().run()
