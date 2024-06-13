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

"""A basis for import_xxx.py scripts."""

import pywikibot
from argparse import ArgumentParser

from common.basis import BaseWikidataBot
from common.utils import get_only_value, get_current_wbtime, parse_input_source

class DataImporterBot(BaseWikidataBot):
    """
    Basic skeleton class for a bot that imports data using certain external ID.
    """

    def __init__(self, prop, description='', query_constraints=''):
        super().__init__()

        self.database_property = prop
        self.database_label = self.get_property_label(prop)
        self.database_item = self.get_property_stated_in_value(prop)

        if description:
            self.description = description
        else:
            self.description = f'Import data from {self.database_label} ({self.database_property})'

        if query_constraints:
            self.query_constraints = '\n'.join(query_constraints)
        else:
            self.query_constraints = ''

    def process_item(self, item):
        """Fully process one item."""
        try:
            entry_id = get_only_value(item, self.database_property, self.database_label)
            data = self.parse_entry(entry_id)
            for prop, values in data.items():
                label = self.get_property_label(prop)
                if prop in item.claims:
                    continue

                if not isinstance(values, list):
                    values = [values]
                for value in values:
                    claim = pywikibot.Claim(self.repo, prop)
                    claim.setTarget(value)

                    stated_in = pywikibot.Claim(self.repo, 'P248')
                    stated_in.setTarget(self.database_item)
                    database_link = pywikibot.Claim(self.repo, self.database_property)
                    database_link.setTarget(entry_id)
                    retrieved = pywikibot.Claim(self.repo, 'P813')
                    retrieved.setTarget(get_current_wbtime())
                    claim.addSources([stated_in, database_link, retrieved])

                    item.addClaim(claim, summary=f'Add {label} based on {self.database_label}')
                    print(f'{item.title()}: added {label} `{self.get_verbose_value(value)}`')
        except RuntimeError as error:
            print(f'{item.title()}: {error}')

    def run(self):
        """Parse command line arguments and run bot."""
        parser = ArgumentParser(description=self.description)
        parser.add_argument(
            'input',
            nargs='?',
            default='all',
            help='either a path to the file with the list of IDs of items ' \
                 'to process (Qnnn) or a keyword "all"; ' \
                 'treated as "all" by default')
        args = parser.parse_args()

        query = f"""
        SELECT ?item {{
            ?item wdt:{self.database_property} [] .
            {self.query_constraints}
        }}
        """

        for item in parse_input_source(self.repo, args.input, query):
            self.process_item(item)

    def parse_entry(self, entry_id):
        """
        Download data of the given database entry and return it in { property: list_of_values } format.
        """
        raise NotImplementedError(f'{self.__class__.__name__}.parse_entry() is not implemented')
