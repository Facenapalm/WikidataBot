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
    LIMIT 5
    """

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
            self.process_item(item)
            print(f"{item.title()} processed")

if __name__ == '__main__':
    HeaderMaintainerBot().run()
