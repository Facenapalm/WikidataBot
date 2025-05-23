# Copyright (c) 2025 Facenapalm
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
Process headers (labels & descriptions) of the video game items: add mul labels,
remove redundant labels, fill in missing descriptions.

Usage:

    python edit_vg_headers.py
"""

import pywikibot
from pywikibot import pagegenerators as pg
from common.basis import BaseWikidataBot
from common.data import vg_descriptions_data

def has_early_access_qualifier(claim):
    if 'P3831' not in claim.qualifiers:
        return False
    for qualifier in claim.qualifiers['P3831']:
        try:
            if qualifier.getTarget().getID() == 'Q17042291':
                return True
        except:
            pass
    return False

def get_release_year(item):
    result = None
    if 'P577' not in item.claims:
        return result
    for date in item.claims['P577']:
        if date.rank == 'deprecated':
            continue
        if has_early_access_qualifier(date):
            continue
        try:
            year = date.getTarget().year
        except:
            continue
        if result is None:
            result = year
        elif year < result:
            result = year
    return result

class HeaderMaintainerBot(BaseWikidataBot):
    query = """
    SELECT ?item WHERE {
      ?item wdt:P31 wd:Q7889 .
      MINUS {
        ?item rdfs:label ?label .
        FILTER( LANG(?label) = "mul" )
      }
    }
    """

    supported_instances = {
        'Q7397', # program
        'Q166142', # application
        'Q620615', # mobile app
        'Q1121542', # mobile game
        'Q56273712', # source-available software
        'Q1395577', # fangame
        'Q2568454', # reissue
        'Q178285', # freeware
        'Q116634', # online game

        'Q7889', # video game
        'Q848991', # browser game
        'Q865493', # video game mod
        'Q1755420', # game demo
        'Q4393107', # video game remake
        'Q61475894', # cancelled/unreleased video game
        'Q65963104', # video game remaster
        'Q21125433', # free or open-source video game
        'Q60997816', # video game edition
        'Q61456428', # total conversion mod
        'Q64170203', # video game project
        'Q64170508', # unfinished or abandoned video game project
        'Q111223304', # video game reboot

        'Q112144412', # esports discipline
    }

    def check_instance_of(self, item):
        """
        Check if the item is an instance of video game.
        If not, throw RuntimeError.
        """
        if 'P31' not in item.claims:
            raise RuntimeError('instance of is not set')

        for claim in item.claims['P31']:
            instance = claim.getTarget()
            if instance is None:
                continue
            if instance.getID() not in self.supported_instances:
                raise RuntimeError(f'unsupported instance of (`{instance.getID()}`)')

    def process_labels(self, item):
        try:
            labels = item.labels
            result = {}

            # set up mul label
            if 'mul' not in labels:
                if 'en' not in labels:
                    raise RuntimeError('neither mul or en label set')
                mul_label = labels['en']
                for lang in labels:
                    if labels[lang] != mul_label:
                        raise RuntimeError(f'mismatch between en and {lang} label')
                result['mul'] = mul_label
            else:
                mul_label = labels['mul']

            # clear up duplicating labels
            for lang in labels:
                if lang in { 'mul', 'en' }:
                    continue
                if labels[lang] == mul_label:
                    result[lang] = ''

            return result
        except RuntimeError as error:
            print(f'{item.title()}: {error}')
            return {}

    def process_descriptions(self, item):
        try:
            year = get_release_year(item)
            if year is None:
                raise RuntimeError('release year is not specified')

            descriptions = item.descriptions
            result = {}

            for lang, short_description, full_description in vg_descriptions_data:
                if lang not in descriptions or descriptions[lang] == short_description:
                    result[lang] = full_description.format(year)

            return result
        except RuntimeError as error:
            print(f'{item.title()}: {error}')
            return {}

    def process_item(self, item):
        labels = self.process_labels(item)
        descriptions = self.process_descriptions(item)
        item.editEntity(
            { 'labels': labels, 'descriptions': descriptions },
            summary='maintain headers: set mul label, clear duplicating labels, add missing descriptions'
        )

    def run(self):
        for item in pg.WikidataSPARQLPageGenerator(self.query, site=self.repo):
            try:
                self.check_instance_of(item)
                self.process_item(item)
                print(f'{item.title()} processed')
            except RuntimeError as error:
                print(f'{item.title()}: {error}')

if __name__ == '__main__':
    HeaderMaintainerBot().run()
