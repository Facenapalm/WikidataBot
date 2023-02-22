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
Add Mod DB game ID (P6774) based on matching Steam application ID (P1733).

To get started, type:

    python seek_moddb_id.py -h
"""

import re
import time
import requests
import pywikibot
from common.seek_basis import BaseSeekerBot

class ModDBSeekerBot(BaseSeekerBot):
    def __init__(self):
        super().__init__(
            database_item="Q2983178",
            database_prop="P6774",
            default_matching_prop="P1733",
            matching_prop_whitelist=["P1733", "P2725"],
        )

        get_item = lambda x: pywikibot.ItemPage(self.repo, x)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
            "Accept-Encoding": "none",
            "Accept-Language": "en-US,en;q=0.8",
            "Connection": "keep-alive"
        }

        self.engine_prop = "P408"
        self.engines_map = {
            "3d-game-studio": get_item("Q229443"),
            "3d-rad": get_item("Q4636302"),
            "4a-engine": get_item("Q4031580"),
            "adobe-flash-professional": get_item("Q165658"),
            "adventure-game-studio": get_item("Q379950"),
            "andengine": get_item("Q20312927"),
            "app-game-kit": get_item("Q4780806"),
            "aurora-engine": get_item("Q2716371"),
            "biengine": get_item("Q14791544"),
            "bitsquid": get_item("Q20313353"),
            "blender-game-engine": get_item("Q2536408"),
            "blitz-max": get_item("Q114731514"),
            "blitz3d": get_item("Q11605797"),
            "box2d": get_item("Q2579122"),
            "brender": get_item("Q4034737"),
            "build": get_item("Q1003003"),
            "clausewitz-engine": get_item("Q13218581"),
            "cloaknt": get_item("Q4036308"),
            "cocos2d-x": get_item("Q1525915"),
            "construct": get_item("Q1049161"),
            "construct-2": get_item("Q5164395"),
            "coppercube": get_item("Q5168683"),
            "cpal3d-engine": get_item("Q4035669"),
            "creation-engine": get_item("Q4036655"),
            "cryengine": get_item("Q21693758"),
            "cryengine-2": get_item("Q1064234"),
            "cryengine-3": get_item("Q2347849"),
            "cryengine-4": get_item("Q21653706"),
            "cryengine-v": get_item("Q30894842"),
            "crystalspace-3d": get_item("Q1142409"),
            "dagor": get_item("Q4036974"),
            "dark-engine": get_item("Q736363"),
            "darkbasic-professional": get_item("Q10986684"),
            "darkplaces-engine": get_item("Q838299"),
            "diesel-engine": get_item("Q4037333"),
            "doom-engine": get_item("Q909009"),
            "dunia": get_item("Q113073"),
            "eduke32": get_item("Q64167651"),
            "enigma-engine": get_item("Q4038075"),
            "essence-engine": get_item("Q4038228"),
            "europa-engine": get_item("Q111203019"),
            "flixel": get_item("Q2348717"),
            "forgelight-engine": get_item("Q5469616"),
            "fox-engine": get_item("Q650498"),
            "fpsc": get_item("Q107458689"),
            "frostbite": get_item("Q124514"),
            "frostbite-2": get_item("Q12809604"),
            "frostbite-3": get_item("Q20472780"),
            "gamebryo": get_item("Q1196211"),
            "gamemaker": get_item("Q243720"),
            "genie-engine": get_item("Q2981987"),
            "genome": get_item("Q71848663"),
            "geo-mod-2": get_item("Q4039342"),
            "godot-engine": get_item("Q16972633"),
            "goldsource": get_item("Q369990"),
            "hedgehog-engine": get_item("Q4040509"),
            "heroengine": get_item("Q3134308"),
            "i-novae-engine": get_item("Q5967667"),
            "id-tech-2": get_item("Q13231453"),
            "id-tech-3": get_item("Q263952"),
            "id-tech-4": get_item("Q306572"),
            "id-tech-5": get_item("Q521406"),
            "id-tech-6": get_item("Q4041255"),
            "infernal-engine": get_item("Q4041377"),
            "infinity-engine": get_item("Q602983"),
            "instead": get_item("Q4041077"),
            "iron-engine": get_item("Q4041612"),
            "irrlicht-3d-engine": get_item("Q1423300"),
            "iw-engine": get_item("Q1775450"),
            "jmonkeyengine": get_item("Q285718"),
            "leadwerks": get_item("Q28957023"),
            "libgdx": get_item("Q16321264"),
            "lightweight-java-game-library": get_item("Q940526"),
            "lithtech": get_item("Q213136"),
            "ls3d": get_item("Q2669875"),
            "lumberyard": get_item("Q22949502"),
            "lyn": get_item("Q4043279"),
            "moai": get_item("Q6886358"),
            "monogame": get_item("Q13218967"),
            "multimedia-fusion": get_item("Q1755199"),
            "neoaxis": get_item("Q10336182"),
            "odyssey": get_item("Q2072101"),
            "ogre-engine": get_item("Q1073498"),
            "openmw": get_item("Q21758353"),
            "panda3d": get_item("Q2049263"),
            "pathengine": get_item("Q4046528"),
            "phaser": get_item("Q48851432"),
            "phoenix-engine-relic-entertainment": get_item("Q7186840"),
            "phyreengine": get_item("Q834539"),
            "pyrogenesis": get_item("Q76618176"),
            "quake-engine": get_item("Q181202"),
            "quest3d": get_item("Q385875"),
            "rage": get_item("Q961461"),
            "renderware": get_item("Q1377750"),
            "renpy": get_item("Q1196014"),
            "rpg-maker-2003": get_item("Q7277472"),
            "rpg-maker-mv": get_item("Q22128818"),
            "rpg-maker-mz": get_item("Q107315313"),
            "rpg-maker-vx": get_item("Q5241236"),
            "rpg-maker-vx-ace": get_item("Q32953569"),
            "rpg-maker-xp": get_item("Q3276130"),
            "sage-strategy-action-game-engine": get_item("Q1971936"),
            "scimitar": get_item("Q282293"),
            "serious-engine": get_item("Q4049306"),
            "sfml": get_item("Q919155"),
            "source": get_item("Q643572"),
            "source-2": get_item("Q21658271"),
            "spring": get_item("Q1754264"),
            "stencyl": get_item("Q7607505"),
            "storm3d": get_item("Q114731401"),
            "stratagus": get_item("Q1936867"),
            "torque-2d": get_item("Q851402"), # create an element for this separate version ?
            "torque-3d": get_item("Q851402"), # create an element for this separate version ?
            "torque-game-engine": get_item("Q851402"),
            "treyarch-ngl": get_item("Q2688551"),
            "twine": get_item("Q15411624"),
            "tyranobuilder": get_item("Q113938826"),
            "unigine": get_item("Q2564057"),
            "unity": get_item("Q63966"),
            "unreal-development-kit": get_item("Q13156651"), # just an alias for Unreal Engine 3 ?
            "unreal-engine-1": get_item("Q84583653"),
            "unreal-engine-2": get_item("Q13156650"),
            "unreal-engine-3": get_item("Q13156651"),
            "unreal-engine-4": get_item("Q13156652"),
            "unreal-engine-5": get_item("Q94277753"),
            "visionaire-studio": get_item("Q2528330"),
            "wintermute": get_item("Q841283"),
            "wolf-rpg-editor": get_item("Q11253808"),
            "wolf3d-engine": get_item("Q4020662"),
            "x-ray-engine": get_item("Q1984445"),
            "xash3d-engine": get_item("Q20732283"),
            "xna": get_item("Q949728"),
            "zengin": get_item("Q71850046"),

            "unknown": None,
            "custom-built": None,
        }

    def search(self, query, max_results=10):
        params = [
            ( "a", "search" ),
            ( "p", "games" ),
            ( "q", query ),
            ( "l", max_results ),
        ]
        response = requests.get("https://www.moddb.com/html/scripts/autocomplete.php", params=params, headers=self.headers)
        time.sleep(2)
        if response:
            return re.findall(r'href="/games/([^"]+)"', response.text)
        else:
            raise RuntimeError("can't get search results for query `{}`. Status code: {}".format(query, response.status_code))

    def parse_entry(self, entry_id, quiet=False):
        response = requests.get("https://www.moddb.com/games/{}".format(entry_id), headers=self.headers)
        time.sleep(2)
        if not response:
            print("WARNING: can't get info for game `{}`".format(entry_id))
            return {}
        html = response.text
        result = {}

        match = re.search(r'<div class="table tablemenu tableprice">.*?</div>\s*</div>', html, flags=re.DOTALL)
        if match:
            tableprice = match.group(0)

            match = re.search(r'href="https?://store\.steampowered\.com/app/(\d+)[/"]', tableprice)
            if match:
                result["P1733"] = match.group(1)
            match = re.search(r'href="https?://www\.gog\.com/(?:en/)?(game/[a-z0-9_]+)[?"]', tableprice)
            if match:
                result["P2725"] = match.group(1)
        else:
            print("WARNING: can't get price table for game `{}`".format(entry_id))

        match = re.search(r'<h5>Engine</h5>\s*<span class="summary">\s*<a href="/engines/([a-z0-9\-]+)">([^<]+)</a>\s*</span>\s*</div>', html)
        if match:
            engine_slug = match.group(1)
            if engine_slug in self.engines_map:
                if self.engines_map[engine_slug] is not None:
                    result[self.engine_prop] = self.engines_map[engine_slug]
            else:
                print("WARNING: unknown engine `{}` for game `{}`".format(engine_slug, entry_id))
        else:
            print("WARNING: can't get engine for game `{}`".format(entry_id))

        return result

if __name__ == "__main__":
    ModDBSeekerBot().run()
