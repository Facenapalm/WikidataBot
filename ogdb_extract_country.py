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
Add Country of origin (P495) based on OGDB ID (P7564).

See also:

   https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P7564#Item_P495
"""

import re
import requests
import pywikibot
from argparse import ArgumentParser
from common.utils import get_current_wbtime, parse_input_source

class OGDBBot():
    def __init__(self):
        self.repo = pywikibot.Site()
        self.repo.login()

        get_item = lambda x: pywikibot.ItemPage(self.repo, x)
        self.ogdb_item = get_item("Q60315954")
        self.country_items = {
            "Kanada": get_item("Q16"),
            "Japan": get_item("Q17"),
            "Norwegen": get_item("Q20"),
            "England": get_item("Q21"),
            "Schottland": get_item("Q22"),
            "Wales": get_item("Q25"),
            "Nordirland": get_item("Q26"),
            "Ungarn": get_item("Q28"),
            "Spanien": get_item("Q29"),
            "USA": get_item("Q30"),
            "Belgien": get_item("Q31"),
            "Luxemburg": get_item("Q32"),
            "Finnland": get_item("Q33"),
            "Schweden": get_item("Q34"),
            "Dänemark": get_item("Q35"),
            "Polen": get_item("Q36"),
            "Litauen": get_item("Q37"),
            "Italien": get_item("Q38"),
            "Schweiz": get_item("Q39"),
            "Österreich": get_item("Q40"),
            "Griechenland": get_item("Q41"),
            "Türkei": get_item("Q43"),
            "Portugal": get_item("Q45"),
            "Niederlande": get_item("Q55"),
            "Uruguay": get_item("Q77"),
            "Ägypten": get_item("Q79"),
            "Mexiko": get_item("Q96"),
            "Frankreich": get_item("Q142"),
            "China": get_item("Q148"),
            "Brasilien": get_item("Q155"),
            "Russland": get_item("Q159"),
            "Deutschland": get_item("Q183"),
            "Belarus": get_item("Q184"),
            "Island": get_item("Q189"),
            "Estland": get_item("Q191"),
            "Lettland": get_item("Q211"),
            "Ukraine": get_item("Q212"),
            "Tschechien": get_item("Q213"),
            "Slowakei": get_item("Q214"),
            "Slowenien": get_item("Q215"),
            "Moldawien": get_item("Q217"),
            "Rumänien": get_item("Q218"),
            "Bulgarien": get_item("Q219"),
            "Mazedonien": get_item("Q221"),
            "Kroatien": get_item("Q224"),
            "Bosnien und Herzegowina": get_item("Q225"),
            "Aserbaidschan": get_item("Q227"),
            "Andorra": get_item("Q228"),
            "Zypern": get_item("Q229"),
            "Georgien": get_item("Q230"),
            "Kasachstan": get_item("Q232"),
            "Malta": get_item("Q233"),
            "Monaco": get_item("Q235"),
            "Montenegro": get_item("Q236"),
            "Kuba": get_item("Q241"),
            "Indonesien": get_item("Q252"),
            "Südafrika": get_item("Q258"),
            "Algerien": get_item("Q262"),
            "Usbekistan": get_item("Q265"),
            "Chile": get_item("Q298"),
            "Singapur": get_item("Q334"),
            "Liechtenstein": get_item("Q347"),
            "Armenien": get_item("Q399"),
            "Serbien": get_item("Q403"),
            "Australien": get_item("Q408"),
            "Argentinien": get_item("Q414"),
            "Peru": get_item("Q419"),
            "Nordkorea": get_item("Q423"),
            "Neuseeland": get_item("Q664"),
            "Indien": get_item("Q668"),
            "Mongolien": get_item("Q711"),
            "Venezuela": get_item("Q717"),
            "Paraguay": get_item("Q733"),
            "Ecuador": get_item("Q736"),
            "Kolumbien": get_item("Q739"),
            "Trinidad und Tobago": get_item("Q754"),
            "Guatemala": get_item("Q774"),
            "El Salvador": get_item("Q792"),
            "Iran": get_item("Q794"),
            "Irak": get_item("Q796"),
            "Costa Rica": get_item("Q800"),
            "Israel": get_item("Q801"),
            "Panama": get_item("Q804"),
            "Jordanien": get_item("Q810"),
            "Nicaragua": get_item("Q811"),
            "Kuwait": get_item("Q817"),
            "Malaysia": get_item("Q833"),
            "Myanmar": get_item("Q836"),
            "Pakistan": get_item("Q843"),
            "Katar": get_item("Q846"),
            "Saudi-Arabien": get_item("Q851"),
            "Syrien": get_item("Q858"),
            "Taiwan": get_item("Q865"),
            "Thailand": get_item("Q869"),
            "Vereinigte Arabische Emirate": get_item("Q878"),
            "Vietnam": get_item("Q881"),
            "Libanon": get_item("Q882"),
            "Südkorea": get_item("Q884"),
            "Bangladesch": get_item("Q902"),
            "Philippinen": get_item("Q928"),
            "Tunesien": get_item("Q948"),
            "Kamerun": get_item("Q1009"),
            "Mauritius": get_item("Q1027"),
            "Marokko": get_item("Q1028"),
            "Namibia": get_item("Q1030"),
            "Puerto Rico": get_item("Q1183"),
            "Hong Kong": get_item("Q8646"),
            "U.d.S.S.R.": get_item("Q15180"),
            "Irland": get_item("Q22890"),
            "Jugoslawien": get_item("Q36704"),
            "Serbien und Montenegro": get_item("Q37024"),
            "Sri Lanka": get_item("Q37024"),
        }

    def get_countries(self, ogdb_id):
        headers = {
            "User-Agent": "Wikidata bot"
        }
        response = requests.get(f"https://ogdb.eu/index.php?section=title&titleid={ogdb_id}")
        if not response:
            raise RuntimeError(f"can't download game entry {ogdb_id}")
        html = response.text

        if "Keinen Titel zu dieser TitleId gefunden!" in html:
            raise RuntimeError(f"no game entry {ogdb_id} exist")

        # <tr>
        # <td class="tboldc" width="140">&nbsp; Herkunftsland:</td>
        # 
        # <td class="tnormg" width="*">&nbsp;England</td>
        # </tr>
        match = re.search(r"<td class=\"tboldc\" width=\"140\">\&nbsp; Herkunftsland:</td>\s+<td class=\"tnormg\" width=\"\*\">\&nbsp;([^<]+)</td>", html)
        if not match:
            raise RuntimeError(f"no country of origin specified for game entry {ogdb_id}")
        countries = match.group(1)

        result = []
        for country_name in countries.split(", "):
            if country_name not in self.country_items:
                raise RuntimeError(f"unknown country `{country_name}`")
            result.append(self.country_items[country_name])

        return result

    def process_item(self, item):
        try:
            if "P495" in item.claims:
                raise RuntimeError("country of origin already set")
            if "P7564" not in item.claims:
                raise RuntimeError("OGDB ID not found")
            if len(item.claims["P7564"]) > 1:
                raise RuntimeError("several OGDB IDs found")
            ogdb_id = item.claims["P7564"][0].getTarget()

            for country in self.get_countries(ogdb_id):
                claim = pywikibot.Claim(self.repo, "P495")
                claim.setTarget(country)

                statedin = pywikibot.Claim(self.repo, "P248")
                statedin.setTarget(self.ogdb_item)
                source_id = pywikibot.Claim(self.repo, "P7564")
                source_id.setTarget(ogdb_id)
                retrieved = pywikibot.Claim(self.repo, "P813")
                retrieved.setTarget(get_current_wbtime())
                claim.addSources([statedin, source_id, retrieved], summary="Adding OGDB as a source.")

                item.addClaim(claim, summary="Add country of origin based on OGDB database.")

                if "en" in country.labels:
                    country_label = country.labels["en"]
                else:
                    country_label = country.title()
                print(f"{item.title()}: added country `{country_label}`")
        except RuntimeError as error:
            print(f"{item.title()}: {error}")

    def run(self):
        parser = ArgumentParser(description="Add Country of origin (P495) based on OGDB ID (P7564).")
        parser.add_argument("input", nargs="?", default="all", help="either a path to the file with the list of IDs of items to process (Qnnn) or a keyword \"all\"; treated as \"all\" by default")
        args = parser.parse_args()

        query = """
            SELECT ?item {
                ?item p:P7564 [] .
                FILTER NOT EXISTS { ?item p:P495 [] }
            }
        """

        for item in parse_input_source(self.repo, args.input, query):
            self.process_item(item)

if __name__ == "__main__":
    OGDBBot().run()
