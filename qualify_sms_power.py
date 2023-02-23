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
Add platform (P400) qualifier to SMS Power identifier (P5585) claims.

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P5585#"Mandatory_Qualifiers"_violations
"""

import pywikibot
from common.qualify_basis import QualifyingBot

class SMSPowerQualifyingBot(QualifyingBot):
    def __init__(self):
        super().__init__(
            base_property="P5585",
            qualifier_property="P400",
        )

    def get_qualifier_values(self, base_value):
        if base_value.endswith("-SMS"):
            return [pywikibot.ItemPage(self.repo, "Q209868")]
        if base_value.endswith("-GG"):
            return [pywikibot.ItemPage(self.repo, "Q751719")]
        if base_value.endswith("-SG"):
            return [pywikibot.ItemPage(self.repo, "Q1136956")]
        if base_value.endswith("-SC"):
            return [pywikibot.ItemPage(self.repo, "Q1322287")]
        print(f"{base_value}: unknown platform")
        return []

if __name__ == "__main__":
    SMSPowerQualifyingBot().run()
