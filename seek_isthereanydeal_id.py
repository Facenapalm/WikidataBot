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
Add IsThereAnyDeal ID (P12570) based on matching Steam application ID (P1733).333333333333

To get started, type:
    python seek_isthereanydeal_id.py -h
"""

import re
import requests
from common.seek_basis import DirectIDSeekerBot

class IsThereAnyDealSeekerBot(DirectIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property='P12570',
            default_matching_property='P1733',
        )

    def seek_database_entry(self):
        try:
            response = requests.head(f'https://isthereanydeal.com/steam/app/{self.matching_value}/', headers=self.headers, timeout=10)
        except requests.exceptions.Timeout:
            raise RuntimeError('request timed out')
        if response.status_code != 302 or 'location' not in response.headers:
            raise RuntimeError(f"can't get info for game `{self.matching_value}`. Status code: {response.status_code}")
        location = response.headers['location']
        match = re.match(r'^/game/([a-z0-9\-_]+)/info/$', location)
        if not match:
            raise RuntimeError(f"location `{location}` doesn't match the regex mask")
        return (match.group(1), {})

if __name__ == "__main__":
    IsThereAnyDealSeekerBot().run()
