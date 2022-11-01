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
Extract Country of origin (P495) based on OGDB ID (P7564).

See also:

   https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P7564#Item_P495
"""

import pywikibot
from pywikibot import pagegenerators as pg
import urllib.request
import time
import sys
import re
import random
from datetime import datetime

QUERY = """
SELECT DISTINCT ?item {
    ?item p:P7564 []
    FILTER NOT EXISTS { ?item p:P495 [] }
}
"""

def get_current_wbtime():
    timestamp = datetime.utcnow()
    return pywikibot.WbTime(year=timestamp.year, month=timestamp.month, day=timestamp.day)

def get_country(ogdb_id):
    attempts = 3
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }
    url = "https://ogdb.eu/index.php?section=title&titleid={}".format(ogdb_id)
    for attempt_no in range(attempts):
        try:
            # time.sleep(random.randint(1, 3))
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8")
        except Exception as error:
            if attempt_no == (attempts - 1):
                raise error

    # <tr>
    # <td class="tboldc" width="140">&nbsp; Herkunftsland:</td>
    # 
    # <td class="tnormg" width="*">&nbsp;England</td>
    # </tr>
    match = re.search(r"<td class=\"tboldc\" width=\"140\">\&nbsp; Herkunftsland:</td>\s+<td class=\"tnormg\" width=\"\*\">\&nbsp;(.*?)</td>", html)
    if match:
        return match.group(1)
    else:
        return ""

def main():
    repo = pywikibot.Site()
    OGDB = pywikibot.ItemPage(repo, "Q60315954")
    country_items = {
        "Kanada": pywikibot.ItemPage(repo, "Q16"),
        "Japan": pywikibot.ItemPage(repo, "Q17"),
        "Norwegen": pywikibot.ItemPage(repo, "Q20"),
        "England": pywikibot.ItemPage(repo, "Q21"),
        "Schottland": pywikibot.ItemPage(repo, "Q22"),
        "Wales": pywikibot.ItemPage(repo, "Q25"),
        "Nordirland": pywikibot.ItemPage(repo, "Q26"),
        "Ungarn": pywikibot.ItemPage(repo, "Q28"),
        "Spanien": pywikibot.ItemPage(repo, "Q29"),
        "USA": pywikibot.ItemPage(repo, "Q30"),
        "Belgien": pywikibot.ItemPage(repo, "Q31"),
        "Luxemburg": pywikibot.ItemPage(repo, "Q32"),
        "Finnland": pywikibot.ItemPage(repo, "Q33"),
        "Schweden": pywikibot.ItemPage(repo, "Q34"),
        "Dänemark": pywikibot.ItemPage(repo, "Q35"),
        "Polen": pywikibot.ItemPage(repo, "Q36"),
        "Litauen": pywikibot.ItemPage(repo, "Q37"),
        "Italien": pywikibot.ItemPage(repo, "Q38"),
        "Schweiz": pywikibot.ItemPage(repo, "Q39"),
        "Österreich": pywikibot.ItemPage(repo, "Q40"),
        "Griechenland": pywikibot.ItemPage(repo, "Q41"),
        "Türkei": pywikibot.ItemPage(repo, "Q43"),
        "Portugal": pywikibot.ItemPage(repo, "Q45"),
        "Niederlande": pywikibot.ItemPage(repo, "Q55"),
        "Mexiko": pywikibot.ItemPage(repo, "Q96"),
        "Frankreich": pywikibot.ItemPage(repo, "Q142"),
        "China": pywikibot.ItemPage(repo, "Q148"),
        "Brasilien": pywikibot.ItemPage(repo, "Q155"),
        "Russland": pywikibot.ItemPage(repo, "Q159"),
        "Deutschland": pywikibot.ItemPage(repo, "Q183"),
        "Belarus": pywikibot.ItemPage(repo, "Q184"),
        "Island": pywikibot.ItemPage(repo, "Q189"),
        "Estland": pywikibot.ItemPage(repo, "Q191"),
        "Lettland": pywikibot.ItemPage(repo, "Q211"),
        "Ukraine": pywikibot.ItemPage(repo, "Q212"),
        "Tschechien": pywikibot.ItemPage(repo, "Q213"),
        "Slowakei": pywikibot.ItemPage(repo, "Q214"),
        "Slowenien": pywikibot.ItemPage(repo, "Q215"),
        "Moldawien": pywikibot.ItemPage(repo, "Q217"),
        "Rumänien": pywikibot.ItemPage(repo, "Q218"),
        "Bulgarien": pywikibot.ItemPage(repo, "Q219"),
        "Kroatien": pywikibot.ItemPage(repo, "Q224"),
        "Zypern": pywikibot.ItemPage(repo, "Q229"),
        "Georgien": pywikibot.ItemPage(repo, "Q230"),
        "Kasachstan": pywikibot.ItemPage(repo, "Q232"),
        "Malta": pywikibot.ItemPage(repo, "Q233"),
        "Indonesien": pywikibot.ItemPage(repo, "Q252"),
        "Südafrika": pywikibot.ItemPage(repo, "Q258"),
        "Chile": pywikibot.ItemPage(repo, "Q298"),
        "Singapur": pywikibot.ItemPage(repo, "Q334"),
        "Serbien": pywikibot.ItemPage(repo, "Q403"),
        "Australien": pywikibot.ItemPage(repo, "Q408"),
        "Argentinien": pywikibot.ItemPage(repo, "Q414"),
        "Nordkorea": pywikibot.ItemPage(repo, "Q423"),
        "Neuseeland": pywikibot.ItemPage(repo, "Q664"),
        "Indien": pywikibot.ItemPage(repo, "Q668"),
        "Venezuela": pywikibot.ItemPage(repo, "Q717"),
        "Kolumbien": pywikibot.ItemPage(repo, "Q739"),
        "El Salvador": pywikibot.ItemPage(repo, "Q792"),
        "Iran": pywikibot.ItemPage(repo, "Q794"),
        "Costa Rica": pywikibot.ItemPage(repo, "Q800"),
        "Israel": pywikibot.ItemPage(repo, "Q801"),
        "Malaysia": pywikibot.ItemPage(repo, "Q833"),
        "Taiwan": pywikibot.ItemPage(repo, "Q865"),
        "Thailand": pywikibot.ItemPage(repo, "Q869"),
        "Vietnam": pywikibot.ItemPage(repo, "Q881"),
        "Libanon": pywikibot.ItemPage(repo, "Q882"),
        "Südkorea": pywikibot.ItemPage(repo, "Q884"),
        "Philippinen": pywikibot.ItemPage(repo, "Q928"),
        "Marokko": pywikibot.ItemPage(repo, "Q1028"),
        "U.d.S.S.R.": pywikibot.ItemPage(repo, "Q15180"),
        "Irland": pywikibot.ItemPage(repo, "Q22890"),
    }
    generator = pg.WikidataSPARQLPageGenerator(QUERY, site=repo)
    for item in generator:
        if "P495" in item.claims:
            print("{}: country already set".format(item.title()))
            continue
        if "P7564" not in item.claims:
            print("{}: OGDB ID not found".format(item.title()))
            continue
        if len(item.claims["P7564"]) > 1:
            print("{}: several OGDB IDs found".format(item.title()))
            continue
        ogdb_id = item.claims["P7564"][0].getTarget()
        countries = get_country(ogdb_id)
        if not countries:
            print("{}: can't get country for `{}`".format(item.title(), ogdb_id))
            continue
        countries = countries.split(", ")
        skip = False
        for country in countries:
            if country not in country_items:
                print("{}: unknown country `{}`".format(item.title(), country))
                skip = True
        if skip:
            continue

        for country in countries:
            claim = pywikibot.Claim(repo, "P495")
            claim.setTarget(country_items[country])

            statedin = pywikibot.Claim(repo, "P248")
            statedin.setTarget(OGDB)
            source_id = pywikibot.Claim(repo, "P7564")
            source_id.setTarget(ogdb_id)
            retrieved = pywikibot.Claim(repo, 'P813')
            retrieved.setTarget(get_current_wbtime())
            claim.addSources([statedin, source_id, retrieved], summary="Adding OGDB as a source.")

            item.addClaim(claim, summary="Add country of origin based on OGDB database.")
            print("{}: added country `{}`".format(item.title(), country))

if __name__ == "__main__":
    main()
