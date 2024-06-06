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
Add Indie DB game ID (P6717) based on Mod DB game ID (P6774), if available.

To get started, type:

    python seek_indiedb_id.py -h
"""

import re
import time
import requests
from common.seek_basis import DirectIDSeekerBot

class IndieDBSeekerBot(DirectIDSeekerBot):
    # Since Indie DB is a subset of Mod DB, we can just check whether Mod DB ID is suitable
    # and copy it into Indie DB ID property.

    def check_slug(self, slug):
        if slug is None:
            return False
        response = requests.get(f"https://www.indiedb.com/games/{slug}", headers=self.headers)
        time.sleep(2)
        if response:
            return "NOT available on IndieDB" not in response.text
        else:
            print(f"WARNING: failed to get `{slug}`")
            return False

    def __init__(self):
        super().__init__(
            database_property="P6717",
            default_matching_property="P6774",
            should_set_source=False
        )

        if self.check_slug("cyberpunk-2077"):
            raise RuntimeError("Can't detect missing Indie DB entries, script needs to be updated")

    def seek_database_entry(self):
        if self.check_slug(self.matching_value):
            return self.matching_value
        else:
            return (None, {})

if __name__ == "__main__":
    IndieDBSeekerBot().run()
