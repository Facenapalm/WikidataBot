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
Extract IGDB numeric ID (P9043) based on IGDB ID (P5794).

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P5794#"Mandatory_Qualifiers"_violations

Script requires Twitch Developer Client ID and Client Secret. Place them at
./keys/igdb-id.key and ./keys/igdb-secret.key files respectively.
"""

from common.igdb_wrapper import IGDB
from common.qualify_basis import QualifyingBot

class IGDBQualifyingBot(QualifyingBot):
    def __init__(self):
        super().__init__(
            base_property="P5794",
            qualifier_property="P9043",
        )
        self.wrapper = IGDB()

    def get_qualifier_values(self, base_value):
        igdb_id = self.wrapper.get_id_by_slug(base_value)
        if igdb_id is not None:
            return [igdb_id]
        else:
            return []

if __name__ == "__main__":
    IGDBQualifyingBot().run()
