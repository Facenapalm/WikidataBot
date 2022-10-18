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
from seek_basis import BaseSeekerBot

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
            "adobe-flash-professional": get_item("Q165658"),
            "adventure-game-studio": get_item("Q379950"),
            "app-game-kit": get_item("Q4780806"),
            "aurora-engine": get_item("Q2716371"),
            "blender-game-engine": get_item("Q2536408"),
            "blitz-max": get_item("Q114731514"),
            "clausewitz-engine": get_item("Q13218581"),
            "cloaknt": get_item("Q4036308"),
            "cocos2d-x": get_item("Q1525915"),
            "construct": get_item("Q1049161"),
            "construct-2": get_item("Q5164395"),
            "cryengine": get_item("Q21693758"),
            "cryengine-2": get_item("Q1064234"),
            "cryengine-3": get_item("Q2347849"),
            "cryengine-4": get_item("Q21653706"),
            "cryengine-v": get_item("Q30894842"),
            "dagor": get_item("Q4036974"),
            "darkbasic-professional": get_item("Q10986684"),
            "darkplaces-engine": get_item("Q838299"),
            "doom-engine": get_item("Q909009"),
            "eduke32": get_item("Q64167651"),
            "europa-engine": get_item("Q111203019"),
            "flixel": get_item("Q2348717"),
            "fpsc": get_item("Q107458689"),
            "frostbite-3": get_item("Q20472780"),
            "gamebryo": get_item("Q1196211"),
            "gamemaker": get_item("Q16195922"),
            "godot-engine": get_item("Q16972633"),
            "goldsource": get_item("Q369990"),
            "id-tech-2": get_item("Q13231453"),
            "id-tech-3": get_item("Q263952"),
            "id-tech-4": get_item("Q306572"),
            "id-tech-5": get_item("Q521406"),
            "id-tech-6": get_item("Q4041255"),
            "infernal-engine": get_item("Q4041377"),
            "iron-engine": get_item("Q4041612"),
            "irrlicht-3d-engine": get_item("Q1423300"),
            "iw-engine": get_item("Q1775450"),
            "jmonkeyengine": get_item("Q285718"),
            "libgdx": get_item("Q16321264"),
            "lightweight-java-game-library": get_item("Q940526"),
            "moai": get_item("Q6886358"),
            "monogame": get_item("Q13218967"),
            "multimedia-fusion": get_item("Q1755199"),
            "ogre-engine": get_item("Q1073498"),
            "panda3d": get_item("Q2049263"),
            "quake-engine": get_item("Q181202"),
            "quest3d": get_item("Q385875"),
            "renpy": get_item("Q1196014"),
            "rpg-maker-2003": get_item("Q7277472"),
            "rpg-maker-mv": get_item("Q22128818"),
            "rpg-maker-mz": get_item("Q107315313"),
            "rpg-maker-vx": get_item("Q5241236"),
            "rpg-maker-vx-ace": get_item("Q32953569"),
            "rpg-maker-xp": get_item("Q3276130"),
            "sage-strategy-action-game-engine": get_item("Q1971936"),
            "serious-engine": get_item("Q4049306"),
            "sfml": get_item("Q919155"),
            "source": get_item("Q643572"),
            "source-2": get_item("Q21658271"),
            "spring": get_item("Q1754264"),
            "storm3d": get_item("Q114731401"),
            "stratagus": get_item("Q1936867"),
            "torque-2d": get_item("Q851402"), # create an element for this separate version ?
            "torque-3d": get_item("Q851402"), # create an element for this separate version ?
            "torque-game-engine": get_item("Q851402"),
            "twine": get_item("Q15411624"),
            "tyranobuilder": get_item("Q113938826"),
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
            "x-ray-engine": get_item("Q1984445"),
            "xash3d-engine": get_item("Q20732283"),
            "xna": get_item("Q949728"),

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
            raise RuntimeError("can't get search results for query `{}`: {}".format(query, response.status))

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
