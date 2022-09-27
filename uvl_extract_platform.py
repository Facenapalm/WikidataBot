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



# Add platform (P400) qualifier to UVL game ID (P7555) claims.
# 
# See also:
# 
#    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P7555#"Mandatory_Qualifiers"_violations

import pywikibot
from pywikibot import pagegenerators as pg
import urllib.request
import time
import sys
import re
import random

QUERY = """
SELECT DISTINCT ?item {
    ?item p:P7555 ?s
    FILTER NOT EXISTS { ?s pq:P400 [] }
}
"""

def extract_platform(uvl_id):
    attempts = 3
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }
    url = "https://www.uvlist.net/game-{}".format(uvl_id)
    for attempt_no in range(attempts):
        try:
            # time.sleep(random.randint(1, 2))
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            if error.code == 404:
                return ""
            else:
                raise error
        except Exception as error:
            if attempt_no == (attempts - 1):
                raise error

    match = re.search(r"<a class='bold platinfo'.*?>(.*?)</a>", html)
    if match:
        return match.group(1)
    else:
        return ""

def main():
    repo = pywikibot.Site()

    platforms = {
        "Amiga OCS": pywikibot.ItemPage(repo, "Q100047"),
        # "Amiga OCS": pywikibot.ItemPage(repo, "Q1969923"), # UVL platform ID = 1
        "Amiga AGA": pywikibot.ItemPage(repo, "Q379575"), # UVL platform ID = 2
        "PlayStation": pywikibot.ItemPage(repo, "Q10677"), # UVL platform ID = 3
        "Saturn": pywikibot.ItemPage(repo, "Q200912"), # UVL platform ID = 4
        "Nintendo Entertainment System": pywikibot.ItemPage(repo, "Q172742"), # UVL platform ID = 5
        "Super Nintendo": pywikibot.ItemPage(repo, "Q183259"), # UVL platform ID = 6
        "Nintendo 64": pywikibot.ItemPage(repo, "Q184839"), # UVL platform ID = 7
        "Game Boy": pywikibot.ItemPage(repo, "Q186437"), # UVL platform ID = 8
        "Atari 2600 VCS": pywikibot.ItemPage(repo, "Q206261"), # UVL platform ID = 9
        "Atari 5200": pywikibot.ItemPage(repo, "Q743222"), # UVL platform ID = 10
        "Atari Lynx": pywikibot.ItemPage(repo, "Q753657"), # UVL platform ID = 11
        "ColecoVision": pywikibot.ItemPage(repo, "Q1046862"), # UVL platform ID = 12
        "Intellivision": pywikibot.ItemPage(repo, "Q1061441"), # UVL platform ID = 13
        "Magnavox Odyssey2": pywikibot.ItemPage(repo, "Q576932"), # UVL platform ID = 14
        "Master System": pywikibot.ItemPage(repo, "Q209868"), # UVL platform ID = 15
        "Game Gear": pywikibot.ItemPage(repo, "Q751719"), # UVL platform ID = 16
        "Mega Drive": pywikibot.ItemPage(repo, "Q10676"), # UVL platform ID = 17
        "PC Engine": pywikibot.ItemPage(repo, "Q1057377"), # UVL platform ID = 18
        "Vectrex": pywikibot.ItemPage(repo, "Q767631"), # UVL platform ID = 19
        "Amstrad CPC": pywikibot.ItemPage(repo, "Q478829"), # UVL platform ID = 20
        "Apple II E": pywikibot.ItemPage(repo, "Q1761667"), # UVL platform ID = 21
        "Atari 400/800": pywikibot.ItemPage(repo, "Q249075"), # UVL platform ID = 22
        "Atari ST": pywikibot.ItemPage(repo, "Q627302"), # UVL platform ID = 23
        "Commodore 64": pywikibot.ItemPage(repo, "Q99775"), # UVL platform ID = 24
        "ZX Spectrum": pywikibot.ItemPage(repo, "Q23882"), # UVL platform ID = 25
        "X68000": pywikibot.ItemPage(repo, "Q1758277"), # UVL platform ID = 26
        "Atari Jaguar": pywikibot.ItemPage(repo, "Q650601"), # UVL platform ID = 27
        "Virtual Boy": pywikibot.ItemPage(repo, "Q164651"), # UVL platform ID = 28
        "Altair MITS 8800": pywikibot.ItemPage(repo, "Q223493"), # UVL platform ID = 29
        "Archimedes": pywikibot.ItemPage(repo, "Q41357"), # UVL platform ID = 30
        "Atom": pywikibot.ItemPage(repo, "Q2043357"), # UVL platform ID = 31
        "BBC Micro": pywikibot.ItemPage(repo, "Q749976"), # UVL platform ID = 32
        "BK11M": pywikibot.ItemPage(repo, "Q978980"), # UVL platform ID = 33
        "Colour Genie": pywikibot.ItemPage(repo, "Q1111889"), # UVL platform ID = 35
        "Commodore PET": pywikibot.ItemPage(repo, "Q946661"), # UVL platform ID = 37
        "Game Boy Advance": pywikibot.ItemPage(repo, "Q188642"), # UVL platform ID = 38
        "VIC-20": pywikibot.ItemPage(repo, "Q918232"), # UVL platform ID = 39
        "Dragon32": pywikibot.ItemPage(repo, "Q57741692"), # UVL platform ID = 40
        "EDSAC": pywikibot.ItemPage(repo, "Q863565"), # UVL platform ID = 41
        "Enterprise": pywikibot.ItemPage(repo, "Q989875"), # UVL platform ID = 43
        "HP 48": pywikibot.ItemPage(repo, "Q1412154"), # UVL platform ID = 45
        "Imsai": pywikibot.ItemPage(repo, "Q600988"), # UVL platform ID = 46
        "KC 85": pywikibot.ItemPage(repo, "Q351020"), # UVL platform ID = 47
        "Macintosh OS Classic": pywikibot.ItemPage(repo, "Q13522376"), # UVL platform ID = 48
        "MSX": pywikibot.ItemPage(repo, "Q853547"), # UVL platform ID = 49
        "Oric": pywikibot.ItemPage(repo, "Q17042679"), # UVL platform ID = 50
        "Sinclair QL": pywikibot.ItemPage(repo, "Q602253"), # UVL platform ID = 51
        "Sharp MZ-Series": pywikibot.ItemPage(repo, "Q1854071"), # UVL platform ID = 52
        "ZX 81": pywikibot.ItemPage(repo, "Q263250"), # UVL platform ID = 53
        "Videopac G7400 / Magnovox Odyssey3": pywikibot.ItemPage(repo, "Q7185533"), # UVL platform ID = 54
        "Creativison": pywikibot.ItemPage(repo, "Q2502670"), # UVL platform ID = 55
        "TI-99/4A": pywikibot.ItemPage(repo, "Q454390"), # UVL platform ID = 56
        "MPF II": pywikibot.ItemPage(repo, "Q16082796"), # UVL platform ID = 57
        "Magnovox Odyssey 200": pywikibot.ItemPage(repo, "Q58852339"), # UVL platform ID = 58
        "Sega 32X": pywikibot.ItemPage(repo, "Q1063978"), # UVL platform ID = 59
        "Neo-Geo": pywikibot.ItemPage(repo, "Q1054350"), # UVL platform ID = 60
        "Commodore 16/Plus 4": pywikibot.ItemPage(repo, "Q76135548"), # UVL platform ID = 61
        "Fairchild Channel F": pywikibot.ItemPage(repo, "Q1053294"), # UVL platform ID = 63
        "Magnavox Odyssey (100)": pywikibot.ItemPage(repo, "Q744987"), # UVL platform ID = 64
        "Atari 7800": pywikibot.ItemPage(repo, "Q753600"), # UVL platform ID = 65
        "Arcade": pywikibot.ItemPage(repo, "Q192851"), # UVL platform ID = 66
        "Emerson Arcadia 2001": pywikibot.ItemPage(repo, "Q1196518"), # UVL platform ID = 67
        "3DO Interactive Multiplayer": pywikibot.ItemPage(repo, "Q229429"), # UVL platform ID = 68
        "CD-I": pywikibot.ItemPage(repo, "Q1023103"), # UVL platform ID = 69
        "Tandy Color Computer": pywikibot.ItemPage(repo, "Q1411846"), # UVL platform ID = 72
        "MS-DOS": pywikibot.ItemPage(repo, "Q47604"), # UVL platform ID = 75
        "Windows": pywikibot.ItemPage(repo, "Q1406"), # UVL platform ID = 76
        "Bally Astrocade": pywikibot.ItemPage(repo, "Q805385"), # UVL platform ID = 79
        "Atari Falcon": pywikibot.ItemPage(repo, "Q753619"), # UVL platform ID = 80
        "Dreamcast": pywikibot.ItemPage(repo, "Q184198"), # UVL platform ID = 81
        "ZX Spectrum 128": pywikibot.ItemPage(repo, "Q9132410"), # UVL platform ID = 82
        "MSX 2": pywikibot.ItemPage(repo, "Q11232203"), # UVL platform ID = 83
        "Konix Multi-System": pywikibot.ItemPage(repo, "Q3816386"), # UVL platform ID = 84
        "Neo Geo Pocket": pywikibot.ItemPage(repo, "Q939881"), # UVL platform ID = 85
        "TRS-80": pywikibot.ItemPage(repo, "Q14523564"), # UVL platform ID = 86
        "PlayStation 2": pywikibot.ItemPage(repo, "Q10680"), # UVL platform ID = 87
        "Windows CE": pywikibot.ItemPage(repo, "Q488244"), # UVL platform ID = 88
        "Sega-CD/Mega-CD": pywikibot.ItemPage(repo, "Q1047516"), # UVL platform ID = 89
        "Game Boy Color": pywikibot.ItemPage(repo, "Q203992"), # UVL platform ID = 90
        "Apple IIGS": pywikibot.ItemPage(repo, "Q1282269"), # UVL platform ID = 91
        "Internet Only": pywikibot.ItemPage(repo, "Q6368"), # UVL platform ID = 92
        "Game & Watch": pywikibot.ItemPage(repo, "Q215034"), # UVL platform ID = 93
        "NEC PC9801": pywikibot.ItemPage(repo, "Q183505"), # UVL platform ID = 95
        "FM Towns": pywikibot.ItemPage(repo, "Q531896"), # UVL platform ID = 96
        "Windows 3.1": pywikibot.ItemPage(repo, "Q495432"), # UVL platform ID = 97
        "PC-FX": pywikibot.ItemPage(repo, "Q1136902"), # UVL platform ID = 98
        "Sharp X1": pywikibot.ItemPage(repo, "Q2710884"), # UVL platform ID = 99
        "NEC PC8801": pywikibot.ItemPage(repo, "Q1338888"), # UVL platform ID = 101
        "NEC PC6001": pywikibot.ItemPage(repo, "Q2440971"), # UVL platform ID = 102
        "MICRO 7 - FM7": pywikibot.ItemPage(repo, "Q2379925"), # UVL platform ID = 103
        "GameCube": pywikibot.ItemPage(repo, "Q182172"), # UVL platform ID = 104
        "Xbox": pywikibot.ItemPage(repo, "Q132020"), # UVL platform ID = 105
        "Linux": pywikibot.ItemPage(repo, "Q388"), # UVL platform ID = 106
        "Sega SG-1000": pywikibot.ItemPage(repo, "Q1136956"), # UVL platform ID = 107
        "DEC PDP-1": pywikibot.ItemPage(repo, "Q1758866"), # UVL platform ID = 108
        "GamePark 32": pywikibot.ItemPage(repo, "Q426119"), # UVL platform ID = 110
        "Adventure Vision": pywikibot.ItemPage(repo, "Q379965"), # UVL platform ID = 111
        "Tiger Game.COM": pywikibot.ItemPage(repo, "Q2498396"), # UVL platform ID = 112
        "Acorn Electron": pywikibot.ItemPage(repo, "Q342163"), # UVL platform ID = 113
        "WonderSwan": pywikibot.ItemPage(repo, "Q1065792"), # UVL platform ID = 114
        "WonderSwan Color": pywikibot.ItemPage(repo, "Q1048035"), # UVL platform ID = 115
        "Neo Geo Pocket Color": pywikibot.ItemPage(repo, "Q1977455"), # UVL platform ID = 116
        "Commodore 128": pywikibot.ItemPage(repo, "Q1115919"), # UVL platform ID = 117
        "Watara Supervision": pywikibot.ItemPage(repo, "Q732683"), # UVL platform ID = 118
        "PC Engine CD": pywikibot.ItemPage(repo, "Q10854461"), # UVL platform ID = 119
        "Famicom Disk System": pywikibot.ItemPage(repo, "Q135321"), # UVL platform ID = 120
        "DVD player": pywikibot.ItemPage(repo, "Q3783103"), # UVL platform ID = 121
        "Flash": pywikibot.ItemPage(repo, "Q165658"), # UVL platform ID = 122
        "Mobile phone": pywikibot.ItemPage(repo, "Q193828"), # UVL platform ID = 123
        "Palm": pywikibot.ItemPage(repo, "Q274582"), # UVL platform ID = 124
        "N-Gage": pywikibot.ItemPage(repo, "Q336434"), # UVL platform ID = 125
        "Newton": pywikibot.ItemPage(repo, "Q420772"), # UVL platform ID = 126
        "Nintendo DS": pywikibot.ItemPage(repo, "Q170323"), # UVL platform ID = 128
        "PlayStation Portable": pywikibot.ItemPage(repo, "Q170325"), # UVL platform ID = 129
        "RCA Studio II": pywikibot.ItemPage(repo, "Q1143954"), # UVL platform ID = 130
        "Interton VC 4000": pywikibot.ItemPage(repo, "Q302411"), # UVL platform ID = 131
        "Xbox 360": pywikibot.ItemPage(repo, "Q48263"), # UVL platform ID = 144
        "SAM Coupe": pywikibot.ItemPage(repo, "Q1188778"), # UVL platform ID = 145
        "GP2X-F100": pywikibot.ItemPage(repo, "Q907531"), # UVL platform ID = 146
        "Wii": pywikibot.ItemPage(repo, "Q8079"), # UVL platform ID = 147
        "PlayStation 3": pywikibot.ItemPage(repo, "Q10683"), # UVL platform ID = 148
        "Playdia": pywikibot.ItemPage(repo, "Q1198088"), # UVL platform ID = 150
        "Apple Pippin": pywikibot.ItemPage(repo, "Q15015195"), # UVL platform ID = 151
        "Epoch Cassette Vision": pywikibot.ItemPage(repo, "Q1140676"), # UVL platform ID = 152
        "Microvision": pywikibot.ItemPage(repo, "Q1475303"), # UVL platform ID = 153
        "APF Imagination Machine": pywikibot.ItemPage(repo, "Q648791"), # UVL platform ID = 154
        "Action Max": pywikibot.ItemPage(repo, "Q343682"), # UVL platform ID = 155
        "Supervision 8000": pywikibot.ItemPage(repo, "Q2503052"), # UVL platform ID = 156
        "Casio PV-1000": pywikibot.ItemPage(repo, "Q60407"), # UVL platform ID = 157
        "My Vision": pywikibot.ItemPage(repo, "Q6946580"), # UVL platform ID = 158
        "Super Micro / Super Micro PVS": pywikibot.ItemPage(repo, "Q58823058"), # UVL platform ID = 159
        "Thomson": pywikibot.ItemPage(repo, "Q3095025"), # UVL platform ID = 163
        "RDI Halcyon": pywikibot.ItemPage(repo, "Q5641195"), # UVL platform ID = 164
        "Gizmondo": pywikibot.ItemPage(repo, "Q909005"), # UVL platform ID = 165
        "V.Smile": pywikibot.ItemPage(repo, "Q1055215"), # UVL platform ID = 166
        "V.Flash": pywikibot.ItemPage(repo, "Q3552867"), # UVL platform ID = 167
        "Mattel Aquarius": pywikibot.ItemPage(repo, "Q968545"), # UVL platform ID = 168
        "LaserActive Mega LD": pywikibot.ItemPage(repo, "Q3276319"), # UVL platform ID = 169
        "EXL 100": pywikibot.ItemPage(repo, "Q3046263"), # UVL platform ID = 170
        "GameKing": pywikibot.ItemPage(repo, "Q3183771"), # UVL platform ID = 171
        "Super A'Can": pywikibot.ItemPage(repo, "Q2475188"), # UVL platform ID = 172
        "HP-41C": pywikibot.ItemPage(repo, "Q629522"), # UVL platform ID = 173
        "iOS": pywikibot.ItemPage(repo, "Q48493"), # UVL platform ID = 174
        "Sega Pico": pywikibot.ItemPage(repo, "Q1374482"), # UVL platform ID = 175
        "Hartung Game Master": pywikibot.ItemPage(repo, "Q5675347"), # UVL platform ID = 176
        "Tiger R-Zone": pywikibot.ItemPage(repo, "Q7273280"), # UVL platform ID = 179
        "custom platform": pywikibot.ItemPage(repo, "Q5249798"), # UVL platform ID = 180
        "PLATO": pywikibot.ItemPage(repo, "Q1755406"), # UVL platform ID = 181
        "Leapster": pywikibot.ItemPage(repo, "Q6509976"), # UVL platform ID = 182
        "Zeebo": pywikibot.ItemPage(repo, "Q184372"), # UVL platform ID = 184
        "OS/2": pywikibot.ItemPage(repo, "Q189794"), # UVL platform ID = 185
        "Philips VG5000": pywikibot.ItemPage(repo, "Q3381050"), # UVL platform ID = 186
        "Nintendo 3DS": pywikibot.ItemPage(repo, "Q203597"), # UVL platform ID = 187
        "PlayStation Vita": pywikibot.ItemPage(repo, "Q188808"), # UVL platform ID = 188
        "Android": pywikibot.ItemPage(repo, "Q94"), # UVL platform ID = 189
        "Epoch Game Pocket Computer": pywikibot.ItemPage(repo, "Q840865"), # UVL platform ID = 190
        "Casio Loopy": pywikibot.ItemPage(repo, "Q661952"), # UVL platform ID = 191
        "Sord M5": pywikibot.ItemPage(repo, "Q506908"), # UVL platform ID = 192
        "Uzebox": pywikibot.ItemPage(repo, "Q579739"), # UVL platform ID = 194
        "BeOS": pywikibot.ItemPage(repo, "Q62563"), # UVL platform ID = 195
        "Wii U": pywikibot.ItemPage(repo, "Q56942"), # UVL platform ID = 196
        "Tandy VIS": pywikibot.ItemPage(repo, "Q7682528"), # UVL platform ID = 197
        "Game Wave": pywikibot.ItemPage(repo, "Q3094980"), # UVL platform ID = 198
        "Vii": pywikibot.ItemPage(repo, "Q1206706"), # UVL platform ID = 199
        "MicroBee": pywikibot.ItemPage(repo, "Q724174"), # UVL platform ID = 200
        "HyperScan": pywikibot.ItemPage(repo, "Q3144093"), # UVL platform ID = 201
        "PlayStation 4": pywikibot.ItemPage(repo, "Q5014725"), # UVL platform ID = 202
        "Xbox One": pywikibot.ItemPage(repo, "Q13361286"), # UVL platform ID = 203
        "Nintendo Switch": pywikibot.ItemPage(repo, "Q19610114"), # UVL platform ID = 204
        "NeXTstep": pywikibot.ItemPage(repo, "Q831367"), # UVL platform ID = 205
        "Amstrad PCW": pywikibot.ItemPage(repo, "Q478833"), # UVL platform ID = 206
        "Memotech MTX": pywikibot.ItemPage(repo, "Q746047"), # UVL platform ID = 207
        "Tatung Einstein": pywikibot.ItemPage(repo, "Q1759524"), # UVL platform ID = 208
        "Camputers Lynx": pywikibot.ItemPage(repo, "Q3108233"), # UVL platform ID = 209
        "Ouya": pywikibot.ItemPage(repo, "Q1391641"), # UVL platform ID = 210
        "Exidy Sorcerer": pywikibot.ItemPage(repo, "Q2175706"), # UVL platform ID = 211
        "Xavix": pywikibot.ItemPage(repo, "Q8043186"), # UVL platform ID = 212
        "Unix": pywikibot.ItemPage(repo, "Q11368"), # UVL platform ID = 213
        "BSD": pywikibot.ItemPage(repo, "Q58636917"), # UVL platform ID = 214
        "Solaris": pywikibot.ItemPage(repo, "Q14646"), # UVL platform ID = 215
        "Minix": pywikibot.ItemPage(repo, "Q187906"), # UVL platform ID = 216
        "Nascom": pywikibot.ItemPage(repo, "Q178930"), # UVL platform ID = 217
        "Coleco Adam": pywikibot.ItemPage(repo, "Q1108054"), # UVL platform ID = 218
        "Mac OS X": pywikibot.ItemPage(repo, "Q14116"), # UVL platform ID = 219
        "NEC PC8001": pywikibot.ItemPage(repo, "Q16081092"), # UVL platform ID = 220
        "Tizen OS": pywikibot.ItemPage(repo, "Q609306"), # UVL platform ID = 221
        "Tomy Tutor": pywikibot.ItemPage(repo, "Q7820426"), # UVL platform ID = 222
        "Apple III": pywikibot.ItemPage(repo, "Q420769"), # UVL platform ID = 223
        "Advanced BASIC Computer 80": pywikibot.ItemPage(repo, "Q287115"), # UVL platform ID = 224
        "Ohio Scientific Challenger Series": pywikibot.ItemPage(repo, "Q60486815"), # UVL platform ID = 225
        "Processor Technology Sol-20": pywikibot.ItemPage(repo, "Q3964167"), # UVL platform ID = 226
        "Open Pandora": pywikibot.ItemPage(repo, "Q225009"), # UVL platform ID = 227
        "Gamate": pywikibot.ItemPage(repo, "Q2395462"), # UVL platform ID = 228
        "Sharp Zaurus": pywikibot.ItemPage(repo, "Q166841"), # UVL platform ID = 229
        "Timex Sinclair 2068": pywikibot.ItemPage(repo, "Q926446"), # UVL platform ID = 230
        "Windows Phone": pywikibot.ItemPage(repo, "Q4885200"), # UVL platform ID = 231
        "VTech Socrates": pywikibot.ItemPage(repo, "Q7907638"), # UVL platform ID = 232
        "Apple I": pywikibot.ItemPage(repo, "Q18981"), # UVL platform ID = 233
        "Terebikko": pywikibot.ItemPage(repo, "Q3518305"), # UVL platform ID = 234
        "PlayStation 5": pywikibot.ItemPage(repo, "Q63184502"), # UVL platform ID = 235
        "Xbox Series X": pywikibot.ItemPage(repo, "Q64513817"), # UVL platform ID = 236
        # "Stadia": pywikibot.ItemPage(repo, "Q60309635"), # UVL platform ID = 237
        "Xerox Alto": pywikibot.ItemPage(repo, "Q1140061"), # UVL platform ID = 249
    }

    generator = pg.WikidataSPARQLPageGenerator(QUERY, site=repo)
    for item in generator:
        if "P7555" not in item.claims:
            continue

        for claim in item.claims["P7555"]:
            uvl_id = claim.getTarget()
            if "P400" in claim.qualifiers:
                print("{}: already has a qualifier".format(uvl_id))
                continue
            platform = extract_platform(uvl_id)
            if platform == "":
                print("{}: can't extract platform".format(uvl_id))
                continue
            if platform not in platforms:
                print("{}: unknown platform {}".format(uvl_id, platform))
                continue

            qualifier = pywikibot.Claim(repo, "P400")
            qualifier.setTarget(platforms[platform])
            claim.addQualifier(qualifier, summary="Adding platform qualifier to UVL `{}`".format(uvl_id))
            print("{}: platform is set to {}".format(uvl_id, platform))

if __name__ == "__main__":
    main()
