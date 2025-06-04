# Copyright (c) 2025 Facenapalm
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
Add platform (P400) qualifier to The Models Resource entity ID (P12373) claims.

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P12373#"Mandatory_Qualifiers"_violations
"""

import pywikibot
from common.qualify_basis import QualifyingBot

class GameTDBQualifyingBot(QualifyingBot):
    platforms_map = {
        '3ds': 'Q203597',
        'arcade': 'Q192851',
        'browser_games': 'Q6368',
        'custom_edited': None,
        'dreamcast': 'Q184198',
        'ds_dsi': 'Q170323',
        'game_boy_advance': 'Q188642',
        'gamecube': 'Q182172',
        'mobile': 'Q193828',
        'ms_dos': 'Q47604',
        'nintendo_64': 'Q184839',
        'nintendo_switch': 'Q19610114',
        'pc_computer': 'Q16338',
        'playstation': 'Q10677',
        'playstation_2': 'Q10680',
        'playstation_3': 'Q10683',
        'playstation_4': 'Q5014725',
        'playstation_5': 'Q63184502',
        'playstation_vita': 'Q188808',
        'psp': 'Q170325',
        'saturn': 'Q200912',
        'wii': 'Q8079',
        'wii_u': 'Q56942',
        'xbox': 'Q132020',
        'xbox_360': 'Q48263',

        'atari_jaguar': 'Q650601',
        'meta_quest': None,
        'n_gage': 'Q336434',
        'sega_genesis_32x': 'Q1063978',
        'snes': 'Q183259',
        'zeebo': 'Q184372',
    }

    def __init__(self):
        super().__init__(
            base_property='P12373',
            qualifier_property='P400',
        )

    def get_qualifier_values(self, base_value):
        if '/' not in base_value:
            raise RuntimeError("can't extract platform from ID")
        platform, _ = base_value.split('/', maxsplit=1)
        platform_qid = self.platforms_map.get(platform.lower())
        if platform_qid is None:
            raise RuntimeError('unknown platform')
        return [pywikibot.ItemPage(self.repo, platform_qid)]

if __name__ == '__main__':
    GameTDBQualifyingBot().run()
