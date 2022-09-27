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

# Add Lutris ID (P7597) based on matching external identifier (for instance,
# Steam application ID, P1733) and/or fill the item with other external IDs
# stated in Lutris database - for instance, IGDB, MobyGames or PCGamingWiki.
# 
# Usage:
# 
#     python lutris_seek_id.py input [base_property]
# 
# Input should a path to file with list of items (Qnnn, one per line).
# Base property is an external ID to seek a match for. If ommitted, it defaults
# to "P1733" (Steam application ID).

import pywikibot
import urllib.parse
import urllib.request
import time
import sys
import re
import random
from datetime import datetime

LUTRIS_PROPERTY = "P7597"
LUTRIS_ITEM = "Q75129027"

IDS_DATA = {
    "igdb": {
        "property": "P5794",
        "mask": r"^https?://www\.igdb\.com/games/([a-z0-9\-]+)",
        "urldecode": False,
    },
    "steam": {
        "property": "P1733",
        "mask": r"^https?:\/\/(?:store\.)?steam(?:community|powered)\.com\/app\/(\d+)",
        "urldecode": False,
    },
    "mobygames": {
        "property": "P1933",
        "mask": r"^https?://www\.mobygames\.com/game/([a-z0-9_\-]+)",
        "urldecode": False,
    },
    "pcgamingwiki": {
        "property": "P6337",
        "mask": r"^https?://(?:www\.)?pcgamingwiki\.com/wiki/([^\s]+)",
        "urldecode": True,
    },
    "winehq appdb": {
        "property": "P600",
        "mask": r"^https?://appdb\.winehq\.org/objectManager\.php\?sClass=application&amp;iId=([1-9][0-9]*)",
        "urldecode": False,
    },
    # TODO: GOG DB (for example: https://lutris.net/games/the-chaos-engine/ ) ?
}

VERBOSE_NAMES = {
    "P600": "Wine AppDB ID",
    "P1733": "Steam application ID",
    "P1933": "MobyGames game ID",
    "P5794": "IGDB game ID",
    "P6337": "PCGamingWiki ID",
}

def get_verbose_name(prop):
    if prop in VERBOSE_NAMES:
        return VERBOSE_NAMES[prop]
    else:
        return prop

def get_current_wbtime():
    timestamp = datetime.utcnow()
    return pywikibot.WbTime(year=timestamp.year, month=timestamp.month, day=timestamp.day)

def get_html(url, attempts=3):
    attempts = 3
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
        "Accept-Encoding": "none",
        "Accept-Language": "en-US,en;q=0.8",
        "Connection": "keep-alive"
    }
    for attempt_no in range(attempts):
        try:
            time.sleep(random.randint(1, 3))
            request = urllib.request.Request(url, None, headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            if error.code == 404:
                html = ""
            else:
                raise error
        except Exception as error:
            if attempt_no == (attempts - 1):
                raise error
            else:
                time.sleep(random.randint(2, 3))
    return html

def get_external_ids(lutris_id):
    html = get_html("https://lutris.net/games/{}".format(lutris_id))
    result = {}
    for link in re.findall(r"<a [^>]*class=[\"']external-link[\"'].*?</a>", html, flags=re.DOTALL):
        href = re.search(r"href=[\"'](.*?)[\"']", link).group(1)
        span = re.search(r"<span>(.*?)</span>", link).group(1).lower()
        if span in IDS_DATA:
            data = IDS_DATA[span]
            match = re.match(data["mask"], href)
            if match:
                if data["urldecode"]:
                    result[data["property"]] = urllib.parse.unquote(match.group(1))
                else:
                    result[data["property"]] = match.group(1)
            else:
                print("WARNING: {} found, but `{}` doesn't match a mask".format(data["property"], href))

    return result

def get_search_results(query):
    params = {
        "q": query,
        "unpublished-filter": "on"
    }
    html = get_html("https://lutris.net/games?" + urllib.parse.urlencode(params))
    return re.findall(r"<div class=[\"']game-preview[\"']>\s+<a href=[\"']/games/([^\"']+)/\"", html)

def seek_lutris_id(repo, item, base_property=None):
    """
    For a given item, use base_property to seek a corresponding Lutris ID.
    If found, set Lutris ID (P7597) and return (lutris_id, external_ids) tuple.
    If not, return None
    """
    if base_property is None:
        return None
    if LUTRIS_PROPERTY in item.claims:
        print("{}: Lutris ID already set".format(item.title()))
        return None
    if base_property not in item.claims:
        print("{}: base property not found".format(item.title()))
        return None
    if len(item.claims[base_property]) > 1:
        print("{}: several base properties found".format(item.title()))
        return None
    steam_id = item.claims[base_property][0].getTarget()

    if "en" in item.labels:
        lang = "en"
    else:
        # any language is better than none
        lang = [x for x in item.labels][0]

    for lutris_id in get_search_results(item.labels[lang]):
        external_ids = get_external_ids(lutris_id)
        if base_property not in external_ids:
            continue
        if external_ids[base_property] != steam_id:
            continue
        del external_ids[base_property]

        claim = pywikibot.Claim(repo, LUTRIS_PROPERTY)
        claim.setTarget(lutris_id)
        item.addClaim(claim, summary="Add Lutris ID based on matching Steam application ID")
        print("{}: added Lutris ID `{}`".format(item.title(), lutris_id))

        return (lutris_id, external_ids)

    return None


def fill_item_ids(repo, item, lutris_id, external_ids):
    for key, value in external_ids.items():
        if key in item.claims:
            print("{}: {} already set, skipped".format(item.title(), get_verbose_name(key)))
            continue

        claim = pywikibot.Claim(repo, key)
        claim.setTarget(value)

        statedin = pywikibot.Claim(repo, "P248")
        statedin.setTarget(pywikibot.ItemPage(repo, LUTRIS_ITEM))
        source_id = pywikibot.Claim(repo, LUTRIS_PROPERTY)
        source_id.setTarget(lutris_id)
        retrieved = pywikibot.Claim(repo, "P813")
        retrieved.setTarget(get_current_wbtime())
        claim.addSources([statedin, source_id, retrieved], summary="Adding Lutris as a source.")

        item.addClaim(claim, summary="Add external identifier based on Lutris database.")
        print("{}: added {} = `{}`".format(item.title(), get_verbose_name(key), value))

def process_item(repo, item, base_property=None):
    if item.isRedirectPage():
        print("{}: redirect page".format(item.title()))
        return
    if LUTRIS_PROPERTY in item.claims:
        if len(item.claims[LUTRIS_PROPERTY]) > 1:
            print("{}: several Lutris IDs found".format(item.title()))
            return
        lutris_id = item.claims[LUTRIS_PROPERTY][0].getTarget()
        fill_item_ids(repo, item, lutris_id, get_external_ids(lutris_id))
    else:
        if base_property is None:
            return
        result = seek_lutris_id(repo, item, base_property)
        if result is None:
            print("{}: failed to find Lutris ID".format(item.title()))
            return
        (lutris_id, external_ids) = result
        fill_item_ids(repo, item, lutris_id, external_ids)

if __name__ == "__main__":
    repo = pywikibot.Site()
    if len(sys.argv) == 3:
        base_property = sys.argv[2]
    else:
        base_property = "P1733"
    for item_id in open(sys.argv[1]):
        item = pywikibot.ItemPage(repo, item_id)
        process_item(repo, item, base_property)
