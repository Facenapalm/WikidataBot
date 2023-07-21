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
Add PCGamingWiki ID (P6337) based on matching Steam application ID (P1733).

To get started, type:

    python seek_pcgamingwiki_id.py -h
"""

import re
import requests
from common.seek_basis import DirectIDSeekerBot

class PCGamingWikiSeekerBot(DirectIDSeekerBot):
    headers = {
        'User-Agent': 'Wikidata connecting bot',
    }

    def __init__(self):
        super().__init__(
            database_property='P6337',
            qualifier_property='P9675',
            default_matching_property='P1733',
        )

    def seek_database_entry(self):
        response = requests.get('https://www.pcgamingwiki.com/api/appid.php', params={ 'appid': self.matching_value }, headers=self.headers)
        html = response.text
        if "No such AppID" in html:
            raise RuntimeError(f'no PCGamingWiki entries are linked to {self.matching_label} `{self.matching_value}`')

        match = re.match(r'https?://www\.pcgamingwiki\.com/wiki/(\S+)$', response.url)
        if not match:
            raise RuntimeError(f'unknown link format `{response.url}` (linked to {self.matching_label} `{self.matching_value}`)')
        slug = match.group(1)

        match = re.search(r'"wgArticleId":(\d+)', html)
        if not match:
            raise RuntimeError(f"can't get ID for page {slug}")
        pageid = match.group(1)

        return ([(slug, pageid)], {})

if __name__ == '__main__':
    PCGamingWikiSeekerBot().run()