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



# Extract IGDB numeric ID (P9043) based on IGDB ID (P5794).
# 
# See also:
# 
#    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P5794#"Mandatory_Qualifiers"_violations

import pywikibot
from pywikibot import pagegenerators as pg
import urllib.request
import time
import sys
import re
import random

QUERY = """
SELECT DISTINCT ?item {
    ?item p:P5794 ?s
    FILTER NOT EXISTS { ?s pq:P9043 [] }
}
"""

def get_numeric_id_html(igdb_id):
    attempts = 3
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }
    url = "https://www.igdb.com/games/{}".format(igdb_id)
    for attempt_no in range(attempts):
        try:
            # Caution: reducing delay may result in 24h IP ban on IGDB website.
            time.sleep(random.randint(3, 7))
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8")
        except Exception as error:
            if attempt_no == (attempts - 1):
                raise error

    # <label>IGDB ID:</label>&nbsp;<span>119469</span>
    match = re.search(r"<label>IGDB ID:</label>&nbsp;<span>(\d+)</span>", html)
    if match:
        return match.group(1)
    else:
        return ""

def get_numeric_id_api(igdb_id):
    pass # TODO

def get_numeric_id(igdb_id):
    return get_numeric_id_html(igdb_id)

def main():
    repo = pywikibot.Site()
    generator = pg.WikidataSPARQLPageGenerator(QUERY, site=repo)
    for item in generator:
        if "P5794" not in item.claims:
            continue

        for i, claim in enumerate(item.claims["P5794"]):
            str_id = claim.getTarget()
            if "P9043" in claim.qualifiers:
                print("{}: already has a qualifier".format(str_id))
                continue
            numeric_id = get_numeric_id(str_id)
            if numeric_id == "":
                print("{}: can't get a numeric id".format(str_id))
                continue

            qualifier = pywikibot.Claim(repo, "P9043")
            qualifier.setTarget(numeric_id)
            claim.addQualifier(qualifier, summary="Adding IGDB numeric ID to `{}`".format(str_id))
            print("{}: numeric id set to {}".format(str_id, numeric_id))

if __name__ == "__main__":
    main()
