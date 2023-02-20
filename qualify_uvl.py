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
Add platform (P400) qualifier to UVL game ID (P7555) claims.

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P7555#"Mandatory_Qualifiers"_violations
"""

import re
import urllib.request
import pywikibot
from qualify_basis import QualifyingBot

class UVLQualifyingBot(QualifyingBot):
    def __init__(self):
        super().__init__(
            base_property="P7555",
            qualifier_property="P400",
        )

        get_item = lambda x: pywikibot.ItemPage(self.repo, x)
        self.platform_map = {
            "Amiga OCS": get_item("Q100047"),
            # "Amiga OCS": get_item("Q1969923"), # UVL platform ID = 1
            "Amiga AGA": get_item("Q379575"), # UVL platform ID = 2
            "PlayStation": get_item("Q10677"), # UVL platform ID = 3
            "Saturn": get_item("Q200912"), # UVL platform ID = 4
            "Nintendo Entertainment System": get_item("Q172742"), # UVL platform ID = 5
            "Super Nintendo": get_item("Q183259"), # UVL platform ID = 6
            "Nintendo 64": get_item("Q184839"), # UVL platform ID = 7
            "Game Boy": get_item("Q186437"), # UVL platform ID = 8
            "Atari 2600 VCS": get_item("Q206261"), # UVL platform ID = 9
            "Atari 5200": get_item("Q743222"), # UVL platform ID = 10
            "Atari Lynx": get_item("Q753657"), # UVL platform ID = 11
            "ColecoVision": get_item("Q1046862"), # UVL platform ID = 12
            "Intellivision": get_item("Q1061441"), # UVL platform ID = 13
            "Magnavox Odyssey2": get_item("Q576932"), # UVL platform ID = 14
            "Master System": get_item("Q209868"), # UVL platform ID = 15
            "Game Gear": get_item("Q751719"), # UVL platform ID = 16
            "Mega Drive": get_item("Q10676"), # UVL platform ID = 17
            "PC Engine": get_item("Q1057377"), # UVL platform ID = 18
            "Vectrex": get_item("Q767631"), # UVL platform ID = 19
            "Amstrad CPC": get_item("Q478829"), # UVL platform ID = 20
            "Apple II E": get_item("Q1761667"), # UVL platform ID = 21
            "Atari 400/800": get_item("Q249075"), # UVL platform ID = 22
            "Atari ST": get_item("Q627302"), # UVL platform ID = 23
            "Commodore 64": get_item("Q99775"), # UVL platform ID = 24
            "ZX Spectrum": get_item("Q23882"), # UVL platform ID = 25
            "X68000": get_item("Q1758277"), # UVL platform ID = 26
            "Atari Jaguar": get_item("Q650601"), # UVL platform ID = 27
            "Virtual Boy": get_item("Q164651"), # UVL platform ID = 28
            "Altair MITS 8800": get_item("Q223493"), # UVL platform ID = 29
            "Archimedes": get_item("Q41357"), # UVL platform ID = 30
            "Atom": get_item("Q2043357"), # UVL platform ID = 31
            "BBC Micro": get_item("Q749976"), # UVL platform ID = 32
            "BK11M": get_item("Q978980"), # UVL platform ID = 33
            "Colour Genie": get_item("Q1111889"), # UVL platform ID = 35
            "Commodore PET": get_item("Q946661"), # UVL platform ID = 37
            "Game Boy Advance": get_item("Q188642"), # UVL platform ID = 38
            "VIC-20": get_item("Q918232"), # UVL platform ID = 39
            "Dragon32": get_item("Q57741692"), # UVL platform ID = 40
            "EDSAC": get_item("Q863565"), # UVL platform ID = 41
            "Enterprise": get_item("Q989875"), # UVL platform ID = 43
            "HP 48": get_item("Q1412154"), # UVL platform ID = 45
            "Imsai": get_item("Q600988"), # UVL platform ID = 46
            "KC 85": get_item("Q351020"), # UVL platform ID = 47
            "Macintosh OS Classic": get_item("Q13522376"), # UVL platform ID = 48
            "MSX": get_item("Q853547"), # UVL platform ID = 49
            "Oric": get_item("Q17042679"), # UVL platform ID = 50
            "Sinclair QL": get_item("Q602253"), # UVL platform ID = 51
            "Sharp MZ-Series": get_item("Q1854071"), # UVL platform ID = 52
            "ZX 81": get_item("Q263250"), # UVL platform ID = 53
            "Videopac G7400 / Magnovox Odyssey3": get_item("Q7185533"), # UVL platform ID = 54
            "Creativison": get_item("Q2502670"), # UVL platform ID = 55
            "TI-99/4A": get_item("Q454390"), # UVL platform ID = 56
            "MPF II": get_item("Q16082796"), # UVL platform ID = 57
            "Magnovox Odyssey 200": get_item("Q58852339"), # UVL platform ID = 58
            "Sega 32X": get_item("Q1063978"), # UVL platform ID = 59
            "Neo-Geo": get_item("Q1054350"), # UVL platform ID = 60
            "Commodore 16/Plus 4": get_item("Q76135548"), # UVL platform ID = 61
            "Fairchild Channel F": get_item("Q1053294"), # UVL platform ID = 63
            "Magnavox Odyssey (100)": get_item("Q744987"), # UVL platform ID = 64
            "Atari 7800": get_item("Q753600"), # UVL platform ID = 65
            "Arcade": get_item("Q192851"), # UVL platform ID = 66
            "Emerson Arcadia 2001": get_item("Q1196518"), # UVL platform ID = 67
            "3DO Interactive Multiplayer": get_item("Q229429"), # UVL platform ID = 68
            "CD-I": get_item("Q1023103"), # UVL platform ID = 69
            "Tandy Color Computer": get_item("Q1411846"), # UVL platform ID = 72
            "MS-DOS": get_item("Q47604"), # UVL platform ID = 75
            "Windows": get_item("Q1406"), # UVL platform ID = 76
            "Bally Astrocade": get_item("Q805385"), # UVL platform ID = 79
            "Atari Falcon": get_item("Q753619"), # UVL platform ID = 80
            "Dreamcast": get_item("Q184198"), # UVL platform ID = 81
            "ZX Spectrum 128": get_item("Q9132410"), # UVL platform ID = 82
            "MSX 2": get_item("Q11232203"), # UVL platform ID = 83
            "Konix Multi-System": get_item("Q3816386"), # UVL platform ID = 84
            "Neo Geo Pocket": get_item("Q939881"), # UVL platform ID = 85
            "TRS-80": get_item("Q14523564"), # UVL platform ID = 86
            "PlayStation 2": get_item("Q10680"), # UVL platform ID = 87
            "Windows CE": get_item("Q488244"), # UVL platform ID = 88
            "Sega-CD/Mega-CD": get_item("Q1047516"), # UVL platform ID = 89
            "Game Boy Color": get_item("Q203992"), # UVL platform ID = 90
            "Apple IIGS": get_item("Q1282269"), # UVL platform ID = 91
            "Internet Only": get_item("Q6368"), # UVL platform ID = 92
            "Game & Watch": get_item("Q215034"), # UVL platform ID = 93
            "NEC PC9801": get_item("Q183505"), # UVL platform ID = 95
            "FM Towns": get_item("Q531896"), # UVL platform ID = 96
            "Windows 3.1": get_item("Q495432"), # UVL platform ID = 97
            "PC-FX": get_item("Q1136902"), # UVL platform ID = 98
            "Sharp X1": get_item("Q2710884"), # UVL platform ID = 99
            "NEC PC8801": get_item("Q1338888"), # UVL platform ID = 101
            "NEC PC6001": get_item("Q2440971"), # UVL platform ID = 102
            "MICRO 7 - FM7": get_item("Q2379925"), # UVL platform ID = 103
            "GameCube": get_item("Q182172"), # UVL platform ID = 104
            "Xbox": get_item("Q132020"), # UVL platform ID = 105
            "Linux": get_item("Q388"), # UVL platform ID = 106
            "Sega SG-1000": get_item("Q1136956"), # UVL platform ID = 107
            "DEC PDP-1": get_item("Q1758866"), # UVL platform ID = 108
            "GamePark 32": get_item("Q426119"), # UVL platform ID = 110
            "Adventure Vision": get_item("Q379965"), # UVL platform ID = 111
            "Tiger Game.COM": get_item("Q2498396"), # UVL platform ID = 112
            "Acorn Electron": get_item("Q342163"), # UVL platform ID = 113
            "WonderSwan": get_item("Q1065792"), # UVL platform ID = 114
            "WonderSwan Color": get_item("Q1048035"), # UVL platform ID = 115
            "Neo Geo Pocket Color": get_item("Q1977455"), # UVL platform ID = 116
            "Commodore 128": get_item("Q1115919"), # UVL platform ID = 117
            "Watara Supervision": get_item("Q732683"), # UVL platform ID = 118
            "PC Engine CD": get_item("Q10854461"), # UVL platform ID = 119
            "Famicom Disk System": get_item("Q135321"), # UVL platform ID = 120
            "DVD player": get_item("Q3783103"), # UVL platform ID = 121
            "Flash": get_item("Q165658"), # UVL platform ID = 122
            "Mobile phone": get_item("Q193828"), # UVL platform ID = 123
            "Palm": get_item("Q274582"), # UVL platform ID = 124
            "N-Gage": get_item("Q336434"), # UVL platform ID = 125
            "Newton": get_item("Q420772"), # UVL platform ID = 126
            "Nintendo DS": get_item("Q170323"), # UVL platform ID = 128
            "PlayStation Portable": get_item("Q170325"), # UVL platform ID = 129
            "RCA Studio II": get_item("Q1143954"), # UVL platform ID = 130
            "Interton VC 4000": get_item("Q302411"), # UVL platform ID = 131
            "Xbox 360": get_item("Q48263"), # UVL platform ID = 144
            "SAM Coupe": get_item("Q1188778"), # UVL platform ID = 145
            "GP2X-F100": get_item("Q907531"), # UVL platform ID = 146
            "Wii": get_item("Q8079"), # UVL platform ID = 147
            "PlayStation 3": get_item("Q10683"), # UVL platform ID = 148
            "Playdia": get_item("Q1198088"), # UVL platform ID = 150
            "Apple Pippin": get_item("Q15015195"), # UVL platform ID = 151
            "Epoch Cassette Vision": get_item("Q1140676"), # UVL platform ID = 152
            "Microvision": get_item("Q1475303"), # UVL platform ID = 153
            "APF Imagination Machine": get_item("Q648791"), # UVL platform ID = 154
            "Action Max": get_item("Q343682"), # UVL platform ID = 155
            "Supervision 8000": get_item("Q2503052"), # UVL platform ID = 156
            "Casio PV-1000": get_item("Q60407"), # UVL platform ID = 157
            "My Vision": get_item("Q6946580"), # UVL platform ID = 158
            "Super Micro / Super Micro PVS": get_item("Q58823058"), # UVL platform ID = 159
            "Thomson": get_item("Q3095025"), # UVL platform ID = 163
            "RDI Halcyon": get_item("Q5641195"), # UVL platform ID = 164
            "Gizmondo": get_item("Q909005"), # UVL platform ID = 165
            "V.Smile": get_item("Q1055215"), # UVL platform ID = 166
            "V.Flash": get_item("Q3552867"), # UVL platform ID = 167
            "Mattel Aquarius": get_item("Q968545"), # UVL platform ID = 168
            "LaserActive Mega LD": get_item("Q3276319"), # UVL platform ID = 169
            "EXL 100": get_item("Q3046263"), # UVL platform ID = 170
            "GameKing": get_item("Q3183771"), # UVL platform ID = 171
            "Super A'Can": get_item("Q2475188"), # UVL platform ID = 172
            "HP-41C": get_item("Q629522"), # UVL platform ID = 173
            "iOS": get_item("Q48493"), # UVL platform ID = 174
            "Sega Pico": get_item("Q1374482"), # UVL platform ID = 175
            "Hartung Game Master": get_item("Q5675347"), # UVL platform ID = 176
            "Tiger R-Zone": get_item("Q7273280"), # UVL platform ID = 179
            "custom platform": get_item("Q5249798"), # UVL platform ID = 180
            "PLATO": get_item("Q1755406"), # UVL platform ID = 181
            "Leapster": get_item("Q6509976"), # UVL platform ID = 182
            "Zeebo": get_item("Q184372"), # UVL platform ID = 184
            "OS/2": get_item("Q189794"), # UVL platform ID = 185
            "Philips VG5000": get_item("Q3381050"), # UVL platform ID = 186
            "Nintendo 3DS": get_item("Q203597"), # UVL platform ID = 187
            "PlayStation Vita": get_item("Q188808"), # UVL platform ID = 188
            "Android": get_item("Q94"), # UVL platform ID = 189
            "Epoch Game Pocket Computer": get_item("Q840865"), # UVL platform ID = 190
            "Casio Loopy": get_item("Q661952"), # UVL platform ID = 191
            "Sord M5": get_item("Q506908"), # UVL platform ID = 192
            "Uzebox": get_item("Q579739"), # UVL platform ID = 194
            "BeOS": get_item("Q62563"), # UVL platform ID = 195
            "Wii U": get_item("Q56942"), # UVL platform ID = 196
            "Tandy VIS": get_item("Q7682528"), # UVL platform ID = 197
            "Game Wave": get_item("Q3094980"), # UVL platform ID = 198
            "Vii": get_item("Q1206706"), # UVL platform ID = 199
            "MicroBee": get_item("Q724174"), # UVL platform ID = 200
            "HyperScan": get_item("Q3144093"), # UVL platform ID = 201
            "PlayStation 4": get_item("Q5014725"), # UVL platform ID = 202
            "Xbox One": get_item("Q13361286"), # UVL platform ID = 203
            "Nintendo Switch": get_item("Q19610114"), # UVL platform ID = 204
            "NeXTstep": get_item("Q831367"), # UVL platform ID = 205
            "Amstrad PCW": get_item("Q478833"), # UVL platform ID = 206
            "Memotech MTX": get_item("Q746047"), # UVL platform ID = 207
            "Tatung Einstein": get_item("Q1759524"), # UVL platform ID = 208
            "Camputers Lynx": get_item("Q3108233"), # UVL platform ID = 209
            "Ouya": get_item("Q1391641"), # UVL platform ID = 210
            "Exidy Sorcerer": get_item("Q2175706"), # UVL platform ID = 211
            "Xavix": get_item("Q8043186"), # UVL platform ID = 212
            "Unix": get_item("Q11368"), # UVL platform ID = 213
            "BSD": get_item("Q58636917"), # UVL platform ID = 214
            "Solaris": get_item("Q14646"), # UVL platform ID = 215
            "Minix": get_item("Q187906"), # UVL platform ID = 216
            "Nascom": get_item("Q178930"), # UVL platform ID = 217
            "Coleco Adam": get_item("Q1108054"), # UVL platform ID = 218
            "Mac OS X": get_item("Q14116"), # UVL platform ID = 219
            "NEC PC8001": get_item("Q16081092"), # UVL platform ID = 220
            "Tizen OS": get_item("Q609306"), # UVL platform ID = 221
            "Tomy Tutor": get_item("Q7820426"), # UVL platform ID = 222
            "Apple III": get_item("Q420769"), # UVL platform ID = 223
            "Advanced BASIC Computer 80": get_item("Q287115"), # UVL platform ID = 224
            "Ohio Scientific Challenger Series": get_item("Q60486815"), # UVL platform ID = 225
            "Processor Technology Sol-20": get_item("Q3964167"), # UVL platform ID = 226
            "Open Pandora": get_item("Q225009"), # UVL platform ID = 227
            "Gamate": get_item("Q2395462"), # UVL platform ID = 228
            "Sharp Zaurus": get_item("Q166841"), # UVL platform ID = 229
            "Timex Sinclair 2068": get_item("Q926446"), # UVL platform ID = 230
            "Windows Phone": get_item("Q4885200"), # UVL platform ID = 231
            "VTech Socrates": get_item("Q7907638"), # UVL platform ID = 232
            "Apple I": get_item("Q18981"), # UVL platform ID = 233
            "Terebikko": get_item("Q3518305"), # UVL platform ID = 234
            "PlayStation 5": get_item("Q63184502"), # UVL platform ID = 235
            "Xbox Series X": get_item("Q64513817"), # UVL platform ID = 236
            # "Stadia": get_item("Q60309635"), # UVL platform ID = 237
            "Xerox Alto": get_item("Q1140061"), # UVL platform ID = 249
        }

    def get_qualifier_values(self, base_value):
        attempts = 3
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive"
        }
        url = "https://www.uvlist.net/game-{}".format(base_value)
        for attempt_no in range(attempts):
            try:
                request = urllib.request.Request(url, None, headers)
                response = urllib.request.urlopen(request)
                html = response.read().decode("utf-8")
            except urllib.error.HTTPError as error:
                if error.code == 404:
                    return []
                else:
                    raise error
            except Exception as error:
                if attempt_no == (attempts - 1):
                    raise error

            match = re.search(r"<a class='bold platinfo'.*?>(.*?)</a>", html)
            if not match:
                return []

            platform = match.group(1)
            if platform not in self.platform_map:
                print("{}: unknown platform {}".format(base_value, platform))
                return []

            return [self.platform_map[platform]]

if __name__ == "__main__":
    UVLQualifyingBot().run()
