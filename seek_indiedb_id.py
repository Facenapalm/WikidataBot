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
Add Indie DB game ID (P6717) based on Mod DB game ID (P6774), if available.

Usage:

    python seek_indiedb_id.py [input_filename]
"""

import re
import sys
import time
import requests
import pywikibot

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
    "Accept-Encoding": "none",
    "Accept-Language": "en-US,en;q=0.8",
    "Connection": "keep-alive"
}

INIDEDB_PROP = "P6717"
MODDB_PROP = "P6774"

def check_slug(slug):
    if slug is None:
        return False
    response = requests.get("https://www.indiedb.com/games/{}".format(slug), headers=HEADERS)
    time.sleep(2)
    if response:
        return "NOT available on Indie DB" not in response.text
    else:
        print("WARNING: failed to get `{}`".format(slug))
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python seek_indiedb_id.py [input_filename]")
        return
    if check_slug("cyberpunk-2077"):
        print("Can't detect missing Indie DB entries, script needs to be updated")
        return
    repo = pywikibot.Site()
    repo.login()
    for line in open(sys.argv[1]):
        item = pywikibot.ItemPage(repo, line)
        if INIDEDB_PROP in item.claims:
            print("{}: Indie DB game ID already set".format(item.title()))
            continue
        if MODDB_PROP not in item.claims:
            print("{}: no Mod DB game ID set".format(item.title()))
            continue
        for moddb_claim in item.claims[MODDB_PROP]:
            slug = moddb_claim.getTarget()
            if check_slug(slug):
                claim = pywikibot.Claim(repo, INIDEDB_PROP)
                claim.setTarget(slug)
                item.addClaim(claim, summary="Add Indie DB game ID based on Mod DB game ID")
                print("{}: added Indie DB game ID `{}`".format(item.title(), slug))
            else:
                print("{}: `{}` not found in Indie DB".format(item.title(), slug))

if __name__ == "__main__":
    main()
