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
Add platform (P400) qualifier to TheGamesDB game ID (P7622) claims.

Script uses TheGamesDB platform ID (P7623) to match Wikidata items with TGDB platforms.

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P7622#"Mandatory_Qualifiers"_violations
"""

import re
import requests
import pywikibot
from pywikibot.data.sparql import SparqlQuery
from common.qualify_basis import QualifyingBot

class TGDBQualifyingBot(QualifyingBot):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }

    def __init__(self):
        super().__init__(
            base_property="P7622",
            qualifier_property="P400",
        )

        sparql = SparqlQuery()
        result = sparql.select("""
            SELECT ?tgdb ?item WHERE {
                ?item wdt:P7623 ?tgdb .
            }
        """)

        get_item = lambda x: pywikibot.ItemPage(self.repo, re.match(r"^https?://www\.wikidata\.org/entity/(Q\d+)$", x).group(1))
        self.platform_map = { entry["tgdb"]: get_item(entry["item"]) for entry in result }

    def get_qualifier_values(self, base_value):
        params = [
            ( 'id', base_value )
        ]
        response = requests.get('https://thegamesdb.net/game.php', params=params, headers=self.headers)
        if not response:
            return []
        html = response.text

        match = re.search(r'<p>Platform: <a href="/platform\.php\?id=(\d+)">(.*?)</a></p>', html)
        if not match:
            return []

        platform_id = match.group(1)
        platform_name = match.group(2)
        if platform_id not in self.platform_map:
            print(f"{base_value}: platform {platform_id} ({platform_name}) isn't linked with Wikidata ")
            return []

        return [self.platform_map[platform_id]]

if __name__ == "__main__":
    TGDBQualifyingBot().run()
