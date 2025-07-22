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
Add tuxDB game ID (P11307) based on Steam application ID (P1733).

To get started, type:

    python seek_tuxdb_id.py -h
"""

import re
import requests
from time import sleep
from common.seek_basis import SearchIDSeekerBot

class TuxDBSeekerBot(SearchIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property="P11307",
            default_matching_property="P1733",
        )

    def search(self, query, max_results=None):
        files = {
            's': ( None, query ),
            'submit': ( None, 'Submit' ),
        }
        sleep(0.5)
        try:
            response = requests.post('https://tuxdb.com/section/db&page=0&fwd=go', files=files, headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            raise RuntimeError(f'Query `{query}` resulted in {response.status_code}: {response.reason}')

        return re.findall(r'<a href="https://tuxdb\.com/game/(\d+)"><img color="1"', response.text)

    def parse_entry(self, entry_id):
        sleep(0.5)
        try:
            response = requests.get(f'https://tuxdb.com/game/{entry_id}', headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if not response:
            raise RuntimeError(f"Video game `{entry_id}` returned {response.status_code}: {response.reason}")

        match = re.search(r'<a href="(https://store\.steampowered\.com/app/(\d+))">\1</a>', response.text)
        if match:
            return { 'P1733': match.group(2) }
        else:
            return {}

if __name__ == '__main__':
    TuxDBSeekerBot().run()
