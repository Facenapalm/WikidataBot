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
Add Internet Game Database game ID (P5794) based on matching Steam application ID (P1733).

To get started, type:

    python seek_igdb_id.py -h
"""

from common.igdb_wrapper import IGDB
from common.seek_basis import DirectIDSeekerBot

class IGDBSeekerBot(DirectIDSeekerBot):

    queries = {
        "P1733": [
            # https://store.steampowered.com/app/220
            ("websites", 'fields game; where url = *"/app/{}" & category = 13;'),

            # https://store.steampowered.com/app/220/HalfLife_2/
            ("websites", 'fields game; where url = *"/app/{}/"* & category = 13;'),
        ],
        "P2725": [
            # https://www.gog.com/game/cyberpunk_2077
            ("websites", 'fields game; where url = *"/{}" & category = 17;'),
        ],
        "P6278": [
            # https://store.epicgames.com/ru/p/kena-bridge-of-spirits
            ("websites", 'fields game; where url = *"/{}" & category = 16;'),
        ]
    }

    def __init__(self):
        super().__init__(
            database_property="P5794",
            qualifier_property="P9043",
            default_matching_property="P1733",
            allowed_matching_properties=["P1733", "P2725", "P6278"],
        )
        self.wrapper = IGDB()

    def seek_database_entry(self):
        result = []
        for endpoint, query in self.queries[self.matching_property]:
            result += self.wrapper.request(endpoint, query.format(self.matching_value))

        if len(result) == 0:
            raise RuntimeError(f"no IGDB entries are linked to {self.matching_label} `{self.matching_value}`")
        if len(result) > 1:
            raise RuntimeError(f"several IGDB entries are linked to {self.matching_label} `{self.matching_value}`")

        igdb_id = str(result[0]["game"])
        igdb_slug = self.wrapper.get_slug_by_id(igdb_id)

        return ( [(igdb_slug, igdb_id)], {} )

if __name__ == "__main__":
    IGDBSeekerBot().run()
