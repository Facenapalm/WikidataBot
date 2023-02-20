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
Add platform (P400) qualifier to Nintendo eShop ID (P8084) claims.

See also:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P8084#"Mandatory_Qualifiers"_violations
"""

import pywikibot
from qualify_basis import QualifyingBot

class EShopQualifyingBot(QualifyingBot):
    def __init__(self):
        super().__init__(
            base_property="P8084",
            qualifier_property="P400",
        )

    def get_qualifier_values(self, base_value):
        if base_value.endswith("-switch"):
            return [pywikibot.ItemPage(self.repo, "Q19610114")]
        if base_value.endswith("-wii-u"):
            return [pywikibot.ItemPage(self.repo, "Q56942")]
        if base_value.endswith("-3ds"):
            return [pywikibot.ItemPage(self.repo, "Q203597")]
        print(f"{base_value}: unknown platform")
        return []

if __name__ == "__main__":
    EShopQualifyingBot().run()
