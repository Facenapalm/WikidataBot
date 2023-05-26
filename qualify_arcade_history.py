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
Add platform (P400) qualifier to Gaming-History ID (P4806) claims.

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P4806#"Mandatory_Qualifiers"_violations
"""

import re
import requests
import pywikibot
from common.qualify_basis import QualifyingBot

class ArcadeHistoryQualifyingBot(QualifyingBot):
    headers = {
        "User-Agent": "Wikidata qualifying bot",
    }

    def __init__(self):
        super().__init__(
            base_property="P4806",
            qualifier_property="P400",
        )

        get_item = lambda x: pywikibot.ItemPage(self.repo, x)

        self.platforms_table = {
            "Acorn Archimedes disk.": [ get_item("Q41357") ],
            "Acorn BBC Master cass.": [ get_item("Q795555") ],
            "Acorn BBC Micro B cass.": [ get_item("Q795555") ],
            "Acorn BBC/Electron cass.": [ get_item("Q795555"), get_item("Q342163") ],
            "Acorn Electron cass.": [ get_item("Q342163") ],
            "Amstrad CPC 464 disk.": [ get_item("Q4862171") ],
            "Amstrad CPC cass.": [ get_item("Q478829") ],
            "Amstrad CPC type-in": [ get_item("Q478829") ],
            "Amstrad CPC/ZX Spectrum cass.": [ get_item("Q478829"), get_item("Q23882" )],
            "Amstrad GX4000 cart.": [ get_item("Q981935") ],
            "Apple II 5.25 disk.": [ get_item("Q201652") ],
            "Apple IIGS disk.": [ get_item("Q1282269") ],
            "Apple Macintosh disk.": [ get_item("Q13522376") ],
            "Arcade System": [ get_item("Q631229") ],
            "Arcade Video game": [ get_item("Q192851") ],
            "Atari 2600 cart.": [ get_item("Q206261") ],
            "Atari 400/800 cart.": [ get_item("Q249075") ],
            "Atari 400/800 disk.": [ get_item("Q249075") ],
            "Atari 5200 cart.": [ get_item("Q743222") ],
            "Atari 7800 cart.": [ get_item("Q753600") ],
            "Atari Jaguar cart.": [ get_item("Q650601") ],
            "Atari Lynx cart.": [ get_item("Q753657") ],
            "Atari ST disk.": [ get_item("Q627302") ],
            "Atari XE cart.": [ get_item("Q249075") ],
            "Bally Astrocade type-in": [ get_item("Q805385") ],
            "Bandai WonderSwan cart.": [ get_item("Q1065792") ],
            "Capcom CPS-II cart.": [ get_item("Q2981666") ],
            "Coin-op Misc. game": [ get_item("Q192851") ], # TODO: temporarily set to "arcade video game machine", find more specific platform ?
            "Coleco Adam disk.": [ get_item("Q1108054") ],
            "Colecovision cart.": [ get_item("Q1046862") ],
            "Commodore Amiga 1200 disk.": [ get_item("Q471094") ],
            "Commodore Amiga 500 disk.": [ get_item("Q384656") ],
            "Commodore Amiga CD32 disc": [ get_item("Q695161") ],
            "Commodore C16 cass.": [ get_item("Q1115913") ],
            "Commodore C16 disk.": [ get_item("Q1115913") ],
            "Commodore C64 .": [ get_item("Q99775") ],
            "Commodore C64/ZX cass.": [ get_item("Q99775"), get_item("Q23882") ],
            "Commodore MAX cart.": [ get_item("Q1115981") ],
            "Commodore VIC-20 cart.": [ get_item("Q918232") ],
            "Dragon cass.": [ get_item("Q1238768") ],
            "Dragon disk.": [ get_item("Q1238768") ],
            "DynaVision cart.": [ get_item("Q10269192") ],
            "Fairchild Channel F cart.": [ get_item("Q1053294") ],
            "Famiclones cart.": [ get_item("Q2982516") ],
            "Fruit Machine": [ get_item("Q33972") ],
            "Fujitsu FM Towns CD": [ get_item("Q531896") ],
            "Fujitsu FM-7 5.25in. disk.": [ get_item("Q2379925") ],
            "Fujitsu FM-7 cass.": [ get_item("Q2379925") ],
            "Google Play pack.": [ get_item("Q94") ],
            "IBM 1401 soft.": [ get_item("Q1066933") ],
            "Jupiter Ace cass.": [ get_item("Q1713750") ],
            "Konami Bubble System cart.": [ get_item("Q2927395") ],
            "Konami System 573 disc+cart.": [ get_item("Q20995145") ],
            "Magnavox Odyssey² cart.": [ get_item("Q576932") ],
            "Mattel Intellivision cart.": [ get_item("Q1061441") ],
            "MB MicroVision game": [ get_item("Q1475303") ],
            "Microsoft XBOX 360 disc": [ get_item("Q48263") ],
            "Microsoft XBOX disc": [ get_item("Q132020") ],
            "Microsoft XBOX One BR": [ get_item("Q13361286") ],
            "MSX 2 cart.": [ get_item("Q11232203") ],
            "MSX 2 disk.": [ get_item("Q11232203") ],
            "MSX cart.": [ get_item("Q16082754") ],
            "MSX cass.": [ get_item("Q16082754") ],
            "MSX disk.": [ get_item("Q16082754") ],
            "NEC PC-6001 type-in": [ get_item("Q2440971") ],
            "NEC PC-8801 Series cass.": [ get_item("Q1338888") ],
            "NEC PC-8801 Series disk.": [ get_item("Q1338888") ],
            "NEC PC-9801 Series 5.25in. disk.": [ get_item("Q183505") ],
            "NEC PC-Engine CD": [ get_item("Q1057377") ],
            "NEC PC-Engine HuCARD": [ get_item("Q1057377") ],
            "NEC PC-FX game": [ get_item("Q1136902") ],
            "Nintendo 64 cart.": [ get_item("Q184839") ],
            "Nintendo DS cart.": [ get_item("Q170323") ],
            "Nintendo Famicom cart.": [ get_item("Q172742") ], # TODO: should we distinguish Famicom and NES ?
            "Nintendo Famicom disk.": [ get_item("Q172742") ], # TODO: should we distinguish Famicom and NES ?
            "Nintendo Game Boy Cart.": [ get_item("Q186437") ],
            "Nintendo Game Boy Color cart.": [ get_item("Q203992") ],
            "Nintendo GameCube disc": [ get_item("Q182172") ],
            "Nintendo GBA cart.": [ get_item("Q188642") ],
            "Nintendo NES cart.": [ get_item("Q172742") ], # TODO: should we distinguish Famicom and NES ?
            "Nintendo Super Famicom cart.": [ get_item("Q183259") ], # TODO: should we distinguish Super Famicom and Super NES ?
            "Nintendo Super NES cart.": [ get_item("Q183259") ], # TODO: should we distinguish Super Famicom and Super NES ?
            "Nintendo Virtual Boy cart.": [ get_item("Q164651") ],
            "Nintendo Wii disc": [ get_item("Q8079") ],
            "Nintendo Wii U disc": [ get_item("Q56942") ],
            "Olivetti PC-128 cass.": [ get_item("Q12746387") ],
            "Pachinko": [ get_item("Q836661") ],
            "Pachislot": [ get_item("Q2156242") ],
            "Panasonic 3DO CD": [ get_item("Q229429") ],
            "PC/MS-Windows CD": [ get_item("Q1406") ],
            "Phillips CD-i disc": [ get_item("Q1023103") ],
            "Pinball": [ get_item("Q653928") ],
            "Sega Game Gear cart.": [ get_item("Q751719") ],
            "Sega Genesis 32X cart.": [ get_item("Q1063978") ],
            "Sega Genesis cart.": [ get_item("Q10676") ],
            "Sega Mark III card": [ get_item("Q209868") ], # TODO: should we distinguish Mark III and Master System ?
            "Sega Mark III cart.": [ get_item("Q209868") ], # TODO: should we distinguish Mark III and Master System ?
            "Sega Master System card": [ get_item("Q209868") ], # TODO: should we distinguish Mark III and Master System ?
            "Sega Master System cart.": [ get_item("Q209868") ], # TODO: should we distinguish Mark III and Master System ?
            "Sega Mega Drive cart.": [ get_item("Q10676") ],
            "Sega Mega Play cart.": [ get_item("Q11703690") ],
            "Sega Mega-CD": [ get_item("Q1047516") ],
            "Sega Mega-Tech cart.": [ get_item("Q388384") ],
            "Sega NAOMI cart.": [ get_item("Q16111625") ],
            "Sega NAOMI GD-ROM": [ get_item("Q16111625") ],
            "Sega Pico game": [ get_item("Q1374482") ],
            "Sega Saturn CD": [ get_item("Q200912") ],
            "Sega SG-1000 game": [ get_item("Q1136956") ],
            "Sega ST-V cart.": [ get_item("Q1067380") ],
            "Sega System 24 disk.": [ get_item("Q6147678") ],
            "Sharp MZ-2000 cass.": [ get_item("Q10370979") ],
            "Sharp X1 5.25in. disk.": [ get_item("Q2710884") ],
            "Sharp X1 cass.": [ get_item("Q2710884") ],
            "Sharp X68000 Series 5.25in. disk.": [ get_item("Q1758277") ],
            "Sinclair ZX Spectrum cass.": [ get_item("Q23882") ],
            "Sinclair ZX Spectrum+3 disk.": [ get_item("Q42294616") ],
            "Sinclair ZX-81 cass.": [ get_item("Q263250") ],
            "Slot Machine": [ get_item("Q33972") ],
            "SNK Neo-Geo AES cart.": [ get_item("Q1054350") ],
            "SNK Neo-Geo CD": [ get_item("Q1054350") ],
            "SNK Neo-Geo MVS cart.": [ get_item("Q1054350") ],
            "SNK Neo-Geo Pocket Color cart.": [ get_item("Q1977455") ],
            "Sony PlayStation 2 disc": [ get_item("Q10680") ],
            "Sony PlayStation 3 disc": [ get_item("Q10683") ],
            "Sony PlayStation 4 BR": [ get_item("Q5014725") ],
            "Sony PlayStation CD": [ get_item("Q10677") ],
            "Sony PS Vita game": [ get_item("Q188808") ],
            "Sony PSN: PS4 pack.": [ get_item("Q5014725") ],
            "Sony PSP UMD": [ get_item("Q170325") ],
            "Strength Tester": [ get_item("Q7623251") ],
            "Taito F3 cart.": [ get_item("Q909002") ],
            "Texas instrument TI-99/4A cart.": [ get_item("Q454390") ],
            "Thomson MO5 cass.": [ get_item("Q2396081") ],
            "Thomson MO5/TO7 cass.": [ get_item("Q2396081"), get_item("Q1887775") ],
            "Thomson MO6 cass.": [ get_item("Q3525757") ],
            "Thomson MO6/TO8 cass.": [ get_item("Q3525757"), get_item("Q3525762") ],
            "Thomson MO6/TO8 disk.": [ get_item("Q3525757"), get_item("Q3525762") ],
            "Thomson TO7 cart.": [ get_item("Q1887775") ],
            "Thomson TO7 cass.": [ get_item("Q1887775") ],
            "Thomson TO7 Quick Disk": [ get_item("Q1887775") ],
            "Tomy Tutor cart.": [ get_item("Q7820426") ],
            "TRS-80 CoCo cart.": [ get_item("Q1411846") ],
            "Videoton TVC disk.": [ get_item("Q832692") ],

            # TODO:
            # "Alice 32 cass.": [ get_item("") ],
            # "Arcadia Super Select board": [ get_item("") ],
            # "Bowler": [ get_item("") ],
            # "Calculator": [ get_item("") ],
            # "Commodore VIC-10 cart.": [ get_item("") ],
            # "Computer": [ get_item("") ],
            # "Console": [ get_item("") ],
            # "Dedicated Console": [ get_item("") ],
            # "Exidy Max-A-Flex cart.": [ get_item("") ],
            # "Fortune Teller": [ get_item("") ],
            # "Gun game": [ get_item("") ],
            # "Handheld game": [ get_item("") ],
            # "IBM PC 3.5in. disk.": [ get_item("") ],
            # "IBM PC 5.25+3.5in. disk.": [ get_item("") ],
            # "IBM PC 5.25in. disk.": [ get_item("") ],
            # "IBM PC/AT DOS 5.25in. disk.": [ get_item("") ],
            # "IBM PC/AT DOS CD": [ get_item("") ],
            # "Jukebox": [ get_item("") ],
            # "Kiddie Ride": [ get_item("") ],
            # "Magnet System disk.": [ get_item("") ],
            # "Medal video game": [ get_item("") ],
            # "Mobile Phone": [ get_item("") ],
            # "NEC PC-98/MS-Windows CD": [ get_item("") ],
            # "NEC Supergraphx HuCARD": [ get_item("") ],
            # "NEC TurboGrafx-16 cart.": [ get_item("") ],
            # "NEC TurboGrafx-CD": [ get_item("") ],
            # "Nintendo NES Aladdin cart.": [ get_item("") ],
            # "Nintendo PlayChoice-10 cart.": [ get_item("") ],
            # "Nintendo Super System cart.": [ get_item("") ],
            # "Olivetti PC-128s disk.": [ get_item("") ],
            # "Phillips Videopac cart.": [ get_item("") ],
            # "Redemption mechanical game": [ get_item("") ],
            # "Samsung Gam*Boy cart.": [ get_item("") ],
            # "Samsung Super Gam*Boy cart.": [ get_item("") ],
            # "Sega CD": [ get_item("") ],
            # "Sega Meganet game": [ get_item("") ],
            # "Sega SPC-1000 soft.": [ get_item("") ],
            # "Starpath Supercharger cass.": [ get_item("") ],
            # "Tabletop game": [ get_item("") ],
            # "Taito G-Net card": [ get_item("") ],
            # "Takara e-Kara GK series cart.": [ get_item("") ],
            # "Thomson TO disk.": [ get_item("") ],
            # "V.R. game": [ get_item("") ],
            # "Vending Machine": [ get_item("") ],
            # "Video Slot Machine": [ get_item("") ],
            # "Wall game": [ get_item("") ],
            # "Watch game": [ get_item("") ],
        }

    def get_qualifier_values(self, base_value):
        params = [
            ( "page", "detail" ),
            ( "id", base_value ),
        ]
        response = requests.get("https://www.arcade-history.com/", params=params, headers=self.headers)
        if not response:
            raise RuntimeError(f"can't get info ({response.status_code})")
        media_type = re.search(r"<h2>.*?<span style='color:lightgrey'>(.+?)</span>", response.text).group(1)

        if media_type not in self.platforms_table:
            raise RuntimeError(f"unknown media type `{media_type}`")

        return self.platforms_table[media_type]

if __name__ == "__main__":
    ArcadeHistoryQualifyingBot().run()
