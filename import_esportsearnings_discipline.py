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
Add sports discipline competed in (P2416) based on Esports Earnings player ID (P10803).
"""

import re
import requests
import pywikibot
from pywikibot.data.sparql import SparqlQuery
from common.import_basis import DataImporterBot

class EsportsEarningsBot(DataImporterBot):
    headers = {
        "User-Agent": "Wikidata bot",
        "Content-Type": "text/html; charset=utf-8",
    }

    def __init__(self):
        super().__init__(
            prop='P10803',
            description='Add sports discipline competed in (P2416) ' \
                'based on Esports Earnings player ID (P10803).',
            query_constraints=[
                '?item wdt:P106 wd:Q4379701 .',
                'FILTER NOT EXISTS { ?item p:P2416 [] }',
            ]
        )

        sparql = SparqlQuery()
        result = sparql.select("""
            SELECT ?game ?item WHERE {
                ?item wdt:P10802 ?game .
            }
        """)

        def get_item(x): return pywikibot.ItemPage(self.repo, re.match(r'^https?://www\.wikidata\.org/entity/(Q\d+)$', x).group(1))
        self.discipline_map = { entry['game']: get_item(entry['item']) for entry in result }
        self.esports = pywikibot.ItemPage(self.repo, 'Q300920')

    def parse_entry(self, entry_id):
        response = requests.get(f'https://www.esportsearnings.com/players/{entry_id}', headers=self.headers)
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
                raise RuntimeError(f'Unknown game `{game_slug}` at player entry {entry_id}')
        return { 'P641': self.esports, 'P2416': result }

if __name__ == '__main__':
    EsportsEarningsBot().run()
