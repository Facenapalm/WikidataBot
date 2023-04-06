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
Extract sports discipline competed in (P2416) based on Esports Earnings player ID (P10803).
"""

import re
import requests
import pywikibot
from pywikibot import pagegenerators as pg
from pywikibot.data.sparql import SparqlQuery
from argparse import ArgumentParser
from datetime import datetime

def get_current_wbtime():
    timestamp = datetime.utcnow()
    return pywikibot.WbTime(year=timestamp.year, month=timestamp.month, day=timestamp.day)

class EsportsEarningsBot():
    def __init__(self):
        self.repo = pywikibot.Site()
        self.repo.login()

        sparql = SparqlQuery()
        result = sparql.select("""
            SELECT ?game ?item WHERE {
                ?item wdt:P10802 ?game .
            }
        """)

        get_item = lambda x: pywikibot.ItemPage(self.repo, re.match(r"^https?://www\.wikidata\.org/entity/(Q\d+)$", x).group(1))
        self.discipline_map = { entry["game"]: get_item(entry["item"]) for entry in result }

    def download_game_list(self, entry_id):
        headers = {
            "User-Agent": "Wikidata bot",
            "Content-Type": "text/html; charset=utf-8",
        }
        response = requests.get(f"https://www.esportsearnings.com/players/{entry_id}", headers=headers)
        if not response:
            raise RuntimeError(f"Can't download player entry {entry_id}")

        match = re.search(r'<h2 class="detail_box_title">Earnings By Game</h2><table[\s\S]*?</table>', response.text)
        if not match:
            raise RuntimeError(f"Can't find Earnings By Game table at player entry {entry_id}")
        table = match.group(0)

        result = []
        for game_slug, game_id in re.findall(r'href="/games/((\d+)[^"]+)', table):
            if game_id in self.discipline_map:
                result.append(self.discipline_map[game_id])
            else:
                raise RuntimeError(f"Unknown game `{game_slug}` at player entry {entry_id}")
        return result

    def process_item(self, item):
        try:
            if item.isRedirectPage():
                raise RuntimeError("Item is a redirect page")
            if "P2416" in item.claims:
                raise RuntimeError("Discipline already set")
            if "P10803" not in item.claims:
                raise RuntimeError("No Esports Earnings player ID found")
            if len(item.claims["P10803"]) > 1:
                raise RuntimeError("Several Esports Earnings player IDs found")
            entry_id = item.claims["P10803"][0].getTarget()

            for discipline in self.download_game_list(entry_id):
                claim = pywikibot.Claim(self.repo, "P2416")
                claim.setTarget(discipline)

                statedin = pywikibot.Claim(self.repo, "P248")
                statedin.setTarget(pywikibot.ItemPage(self.repo, "Q112144524"))
                source_id = pywikibot.Claim(self.repo, "P10803")
                source_id.setTarget(entry_id)
                retrieved = pywikibot.Claim(self.repo, "P813")
                retrieved.setTarget(get_current_wbtime())
                claim.addSources([statedin, source_id, retrieved], summary="Adding Esports Earnings as a source.")

                item.addClaim(claim, summary="Add sports discipline competed in based on Esports Earnings database.")
                print(f"{item.title()}: added discipline `{discipline.title()}`")
        except RuntimeError as error:
            print(f"{item.title()}: {error}")

    def run(self):
        parser = ArgumentParser(description="Extract sports discipline competed in (P2416) based on Esports Earnings player ID (P10803).")
        parser.add_argument("input", nargs="?", default="all", help="A path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"")
        args = parser.parse_args()

        if args.input == "all":
            query = """
                SELECT ?item {
                    ?item wdt:P10803 [] .
                    ?item wdt:P106 wd:Q4379701 .
                    FILTER NOT EXISTS { ?item p:P2416 [] }
                }
            """
            generator = pg.WikidataSPARQLPageGenerator(query, site=self.repo)
            for item in generator:
                self.process_item(item)
        else:
            with open(args.input, encoding="utf-8") as listfile:
                for line in listfile:
                    item = pywikibot.ItemPage(self.repo, line)
                    self.process_item(item)

if __name__ == "__main__":
    EsportsEarningsBot().run()
