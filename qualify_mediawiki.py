# Copyright (c) 2024 Facenapalm
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
Add MediaWiki page ID (P6337) qualifier to MediaWiki-based identifier

Usage:
    python qualify_mediawiki.py [identifier] [input]

For more info, type
    python qualify_mediawiki.py -h
"""

import re
import time
import requests
import pywikibot
from argparse import ArgumentParser
from pywikibot import pagegenerators
from common.utils import parse_input_source, get_best_value
from common.qualify_basis import QualifyingBot

def get_fandom_endpoint(identifier):
    wiki, pagename = identifier.split(':', maxsplit=1)
    return (f'https://{wiki}.fandom.com/api.php', pagename)

def get_huiji_wiki_endpoint(identifier):
    wiki, pagename = identifier.split(':', maxsplit=1)
    return (f'https://{wiki}.huijiwiki.com/w/api.php', pagename)

def get_liquipedia_endpoint(identifier):
    time.sleep(2)
    wiki, pagename = identifier.split('/', maxsplit=1)
    return (f'https://liquipedia.net/{wiki}/api.php', pagename)

def get_niwa_endpoint(identifier):
    mapping = {
        # 'nintendowiki': 'https://niwanetwork.org/',

        'armswiki': 'https://armswiki.org/w/api.php',
        'dragalialost': 'https://dragalialost.wiki/api.php',
        'drawntolife': 'https://drawntolife.wiki/w/api.php',
        'fewiki': 'https://fireemblemwiki.org/w/api.php',
        'fzerowiki': 'https://mutecity.org/w/api.php',
        'gsuwiki': 'https://goldensunwiki.net/w/api.php',
        'harddrop': 'https://harddrop.com/w/api.php',
        'icaruspedia': 'https://www.kidicaruswiki.org/w/api.php',
        'inkipedia': 'https://splatoonwiki.org/w/api.php',
        'kh': 'https://www.khwiki.com/api.php',
        'kovopedia': 'https://kovopedia.com/api.php',
        'lylatwiki': 'https://starfoxwiki.info/w/api.php',
        'mariowikide': 'https://mariowiki.net/w/api.php',
        'metroidwiki': 'https://www.metroidwiki.org/w/api.php',
        'miiwiki': 'https://miiwiki.org/w/api.php',
        'mysterydungeonwiki': 'https://mysterydungeonwiki.com/w/api.php',
        'nookipedia': 'https://nookipedia.com/w/api.php',
        'pikifanon': 'https://pikminfanon.com/w/api.php',
        'pikipedia': 'https://www.pikminwiki.com/api.php',
        'pikipediait': 'https://pikminitalia.it/w/api.php',
        'pokemoncentral': 'https://wiki.pokemoncentral.it/api.php',
        'rhythmheaven': 'https://rhwiki.net/w/api.php',
        'smashwiki': 'https://www.ssbwiki.com/api.php',
        'starfywiki': 'https://www.starfywiki.org/api.php',
        'supermariowikiit': 'https://www.mariowiki.it/api.php',
        'ukikipedia': 'https://ukikipedia.net/mediawiki/api.php',
        'warswiki': 'https://warswiki.org/w/api.php',
        'wikibound': 'https://wikibound.info/w/api.php',
        'wikiboundit': 'https://it.wikibound.info/w/api.php',
        'xenopediait': 'https://www.xenopedia.it/api.php',
        'xenoserieswiki': 'https://www.xenoserieswiki.org/w/api.php',
        'zeldapendium': 'https://www.zeldapendium.de/w/api.php',
        'zeldawiki': 'https://zeldawiki.wiki/w/api.php',
    }
    wiki, pagename = identifier.split(':', maxsplit=1)
    return (mapping.get(wiki), pagename)

def get_wiki_gg_endpoint(identifier):
    wiki, pagename = identifier.split(':', maxsplit=1)

    langmatch = re.match(r'^([a-z]{2}/|zh-[a-z]{2,4}/)(.+)$', pagename)
    if langmatch:
        lang, pagename = langmatch.groups()
    else:
        lang = ''

    return (f'https://{wiki}.wiki.gg/{lang}api.php', pagename)

class MediaWikiQualifyingBot(QualifyingBot):
    endpoints = {
        'P6262': get_fandom_endpoint,
        # 'P10668': get_huiji_wiki_endpoint, # 403 forbidden
        'P10918': get_liquipedia_endpoint,
        'P11988': get_wiki_gg_endpoint,
        'P12253': get_niwa_endpoint,
        # 'P12473': get_weird_gloop_endpoint, # TODO
    }

    def lookup_endpoint(self, base_property):
        """
        Get an API endpoint for given property, either as string url or as
        function(id). The latter is mandatory for properties covering several
        wikis (Fandom, Liquipedia, etc).
        """
        if base_property in self.endpoints:
            return self.endpoints[base_property]

        property_item = pywikibot.PropertyPage(self.repo, base_property)
        if 'P1629' in property_item.claims:
            database_item = get_best_value(property_item, 'P1629')
            endpoint = get_best_value(database_item, 'P6269')
        elif 'P9073' in property_item.claims:
            database_item = get_best_value(property_item, 'P9073')
            endpoint = get_best_value(database_item, 'P6269')
        else:
            endpoint = get_best_value(property_item, 'P6269')

        if endpoint is None:
            raise RuntimeError(f"Unsupported matching property `{base_property}`")
        return endpoint

    def get_mediaiki_properties(self):
        """
        Return the list of properties that require a mandatory MediaWiki page ID (P6337) qualifier.
        """
        query = """
            SELECT ?item {
                ?item p:P2302 ?statement .
                ?statement ps:P2302 wd:Q21510856 .
                ?statement pq:P2306 wd:P9675 .
            }
        """
        for item in pagegenerators.WikidataSPARQLPageGenerator(query, site=self.repo):
            print(f'Processing {item.id}...')
            yield item.id

    def __init__(self):
        self.repo = pywikibot.Site()
        self.repo.login()
        self.qualifier_property = 'P9675'
        self.endpoint = None

    def run(self):
        description = 'Add MediaWiki page ID (P9675) qualifier to given property.'
        parser = ArgumentParser(description=description)
        parser.add_argument('property', help='either a property to add qualifiers to or a keyword "all"')
        parser.add_argument('input', nargs='?', default='all', help='either a path to the file with the list of IDs of items to process (Qnnn) or a keyword "all"')
        args = parser.parse_args()

        if args.property != 'all':
            try:
                self.process_property(args.property, args.input)
            except RuntimeError as error:
                print(error)
            return

        for prop in self.get_mediaiki_properties():
            try:
                self.process_property(prop, args.input)
            except RuntimeError as error:
                print(error)

    def process_property(self, prop, input_source):
        self.endpoint = self.lookup_endpoint(prop)
        self.base_property = prop
        self.base_property_name = self.get_verbose_property_name(prop)

        query = f"""
            SELECT ?item {{
                ?item p:{self.base_property} ?s
                FILTER NOT EXISTS {{ ?s pq:{self.qualifier_property} [] }}
            }}
        """

        for item in parse_input_source(self.repo, input_source, query):
            try:
                self.process_item(item)
            except RuntimeError as error:
                print(error)

    def get_qualifier_values(self, base_value):
        if isinstance(self.endpoint, str):
            endpoint = self.endpoint
        elif callable(self.endpoint):
            endpoint, base_value = self.endpoint(base_value)
            if not endpoint:
                raise RuntimeError(f"can't find endpoint for `{base_value}`")
        else:
            raise RuntimeError('unknown endpoint encoding')

        params = {
            'action': 'query',
            'titles': base_value,
            'format': 'json',
        }
        response = requests.get(endpoint, params=params, headers=self.headers)
        if not response:
            raise RuntimeError(f"can't get info ({response.status_code})")
        pageinfo = list(response.json()['query']['pages'].values())[0]
        if 'pageid' not in pageinfo:
            raise RuntimeError(f"page `{base_value}` does not exist")
        return [str(pageinfo['pageid'])]

if __name__ == "__main__":
    MediaWikiQualifyingBot().run()
