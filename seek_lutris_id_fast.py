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
Copy Internet Game Database game ID (P5794) to Lutris ID (P7597), if both of
these database have the same game under the same ID.

This is relatively common case, because Lutris imported tens of thousands of
games from IGDB. For more sophisticated (and slower) method of connecting Lutris
IDs, use seek_lutris_id.py

To get started, type:

    python seek_lutris_id_fast.py -h
"""

from common.seek_basis import DirectIDSeekerBot
from seek_lutris_id import LutrisSeekerBot

class LutrisSeekerBotLite(DirectIDSeekerBot):
    def __init__(self):
        super().__init__(
            database_property='P7597',
            default_matching_property='P5794',
        )
        self.seeker = LutrisSeekerBot()

    def seek_database_entry(self):
        parsed_entry = self.seeker.parse_entry(self.matching_value)
        if 'P5794' not in parsed_entry:
            raise RuntimeError(f'Lutris entry `{self.matching_value}` have no backlink to IGDB')
        if parsed_entry['P5794'] != self.matching_value:
            raise RuntimeError(f'Lutris entry `{self.matching_value}` backlinks to different IGDB entry')
        del parsed_entry['P5794']

        return ( self.matching_value, parsed_entry )

if __name__ == '__main__':
    LutrisSeekerBotLite().run()
