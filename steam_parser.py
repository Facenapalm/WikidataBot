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
Extract various video game data from Steam based on Steam application ID (P1733):
- platform (P400), both as a standalone claim and as a qualifier to Steam application ID (P1733)
- publication date (P577), except for unpublished and early access games
- game mode (P404), one of the following:
    singleplayer (Q208850)
    multiplayer (Q6895044)
    co-op mode (Q1758804)
- language of work or name (P407), with applies to part (P518) qualifier:
    user interface (Q47146)
    voice acting (Q22920017)
    subtitle (Q204028)

Script requires `input.txt` file with list of IDs of items to process (Qnnn)
or Steam IDs to be included in newly created items (just number).
Mixed input is supported, although the order of IDs might be altered.

A list of elements to process might be obtained from page:

    https://www.wikidata.org/wiki/Wikidata:Database_reports/Constraint_violations/P1733
"""

import requests
import re
import argparse
import os.path
from datetime import datetime, UTC

import pywikibot
from pywikibot.data.sparql import SparqlQuery

from common.utils import get_only_value

title_replacements = [
    (r"&quot;", "\""),
    (r"&reg;|®", ""),
    (r"&trade;|™", ""),
    (r"&amp;", "&"),
]

vg_descriptions_data = [
    # (lang_code, default_description, description_with_year)
    ("ast", "videoxuegu", "videoxuegu espublizáu en {}"),
    ("be", "камп’ютарная гульня", "камп’ютарная гульня {} года"),
    ("be-tarask", "кампутарная гульня", "кампутарная гульня {} року"),
    ("bg", "видеоигра", "видеоигра от {} година"),
    ("ca", "videojoc", "videojoc de {}"),
    ("cs", "videohra", "videohra z roku {}"),
    ("da", "computerspil", "computerspil fra {}"),
    ("de", "Computerspiel", "Computerspiel aus dem Jahr {}"),
    ("de-ch", "Computerspiel", "Computerspiel von {}"),
    ("en", "video game", "{} video game"),
    ("eo", "videoludo", "videoludo de {}"),
    ("es", "videojuego", "videojuego de {}"),
    ("fi", "videopeli", "videopeli vuodelta {}"),
    ("fr", "jeu vidéo", "jeu vidéo de {}"),
    ("ga", "físchluiche", "físchluiche a foilsíodh sa bhliain {}"),
    ("gl", "videoxogo", "videoxogo de {}"),
    ("gsw", "Computerspiel", "Computerspiel von {}"),
    ("hr", "videoigra", "videoigra iz {}. godine"),
    ("hy", "համակարգչային խաղ", "{} թվականի համակարգչային խաղ"),
    ("id", "permainan video", "permainan video tahun {}"),
    ("it", "videogioco", "videogioco del {}"),
    ("lt", "kompiuterinis žaidimas", "{} metų kompiuterinis žaidimas"),
    ("lv", "videospēle", "{}. gadā videospēle"),
    ("mk", "видеоигра", "видеоигра од {} година"),
    ("nb", "videospill", "videospill fra {}"),
    ("nds", "Computerspeel", "Computerspeel von {}"),
    ("nl", "computerspel", "computerspel uit {}"),
    ("nn", "dataspel", "dataspel frå {}"),
    ("oc", "videojòc", "videojòc de {}"),
    ("pl", "gra komputerowa", "gra komputerowa z {} roku"),
    ("pt", "vídeojogo", "vídeojogo de {}"),
    ("pt-br", "jogo eletrônico", "jogo eletrônico de {}"),
    ("ro", "joc video", "joc video din {}"),
    ("ru", "компьютерная игра", "компьютерная игра {} года"),
    ("sco", "video gemme", "{} video gemme"),
    ("sk", "počítačová hra", "počítačová hra z {}"),
    ("sl", "videoigra", "videoigra iz leta {}"),
    ("sq", "video lojë", "video lojë e vitit {}"),
    ("sr", "видео-игра", "видео-игра из {}. године"),
    ("sv", "datorspel", "datorspel från {}"),
    ("tr", "video oyunu", "{} video oyunu"),
    ("uk", "відеогра", "відеогра {} року"),
]

early_access_descriptions_data = [
    ("en", "early access video game", "{} early access video game"),
    ("ru", "компьютерная игра в раннем доступе", "компьютерная игра в раннем доступе {} года"),
]

dlc_descriptions_data = [
    ("en", "expansion pack", "{} expansion pack"),
    ("ru", "дополнение", "дополнение {} года"),
]

mod_descriptions_data = [
    ("en", "mod", "{} mod"),
    ("ru", "мод", "мод {} года"),
]

software_descriptions_data = [
    ("en", "software", "{} software"),
    ("ru", "программное обеспечение", "программное обеспечение {} года"),
]

descriptions_data = {
    "game": vg_descriptions_data,
    "early access": early_access_descriptions_data,
    "dlc": dlc_descriptions_data,
    "mod": mod_descriptions_data,
    "software": software_descriptions_data,
}

arguments = None
output = None

repo = pywikibot.Site()
repo.login()
def get_item(x): return pywikibot.ItemPage(repo, x)

steam = get_item("Q337535")
early_access = get_item("Q17042291")
digital_distribution = get_item("Q269415")

def find_item_for_id(steam_id):
    """
    Return Wikidata item with given steam_id set. If such item does not exist or there are several
    such items, return None.
    """
    sparql = SparqlQuery()
    result = sparql.select(f"""
        SELECT ?item WHERE {{
          ?item wdt:P1733 "{steam_id}" .
        }}
    """)
    if not result or len(result) != 1:
        return None
    match = re.match(r"^https?://www\.wikidata\.org/entity/(Q\d+)$", result[0]["item"])
    if not match:
        return None
    return pywikibot.ItemPage(repo, match.group(1))

def extract_steam_id(url):
    """Extract Steam application ID from url."""
    match = re.match(r"https?://store\.steampowered\.com/app/(\d+)/?", url)
    if match:
        steam_id = match.group(1)
    else:
        steam_id = url.strip()
    return steam_id


class SteamPage():
    """
    One parsed Steam store page related to a videogame, an expansion, a modification or
    a soundtrack.
    """

    headers = {
        "User-Agent": "Wikidata parser (https://github.com/facenapalm/wikidatabot)",
        "Cookie": "wants_mature_content=1;birthtime=470682001;lastagecheckage=1-0-1985;Steam_Language=english",
    }

    instance_map = {
        "game": get_item("Q7889"),
        "dlc": get_item("Q209163"),
        "mod": get_item("Q865493"),
        "soundtrack": get_item("Q100749465"),
        "software": get_item("Q166142"),
    }

    platform_map = {
        "pc": get_item("Q16338"),
        "win": get_item("Q1406"),
        "mac": get_item("Q14116"),
        "linux": get_item("Q388"),
    }

    gamemode_map = {
        "singleplayer": get_item("Q208850"),
        "multiplayer": get_item("Q6895044"),
        "cooperative": get_item("Q1758804"),
    }

    languages_map = {
        "Afrikaans": get_item("Q14196"),
        "Albanian": get_item("Q8748"),
        "Amharic": get_item("Q28244"),
        "Arabic": get_item("Q13955"),
        "Armenian": get_item("Q8785"),
        "Assamese": get_item("Q29401"),
        "Azerbaijani": get_item("Q9292"),
        "Bangla": get_item("Q9610"),
        "Basque": get_item("Q8752"),
        "Belarusian": get_item("Q9091"),
        "Bosnian": get_item("Q9303"),
        "Bulgarian": get_item("Q7918"),
        "Catalan": get_item("Q7026"),
        "Cherokee": get_item("Q33388"),
        "Croatian": get_item("Q6654"),
        "Czech": get_item("Q9056"),
        "Danish": get_item("Q9035"),
        "Dari": get_item("Q178440"),
        "Dutch": get_item("Q7411"),
        "English": get_item("Q1860"),
        "Estonian": get_item("Q9072"),
        "Filipino": get_item("Q33298"),
        "Finnish": get_item("Q1412"),
        "French": get_item("Q150"),
        "Galician": get_item("Q9307"),
        "Georgian": get_item("Q8108"),
        "German": get_item("Q188"),
        "Greek": get_item("Q9129"),
        "Gujarati": get_item("Q5137"),
        "Hausa": get_item("Q56475"),
        "Hebrew": get_item("Q9288"),
        "Hindi": get_item("Q1568"),
        "Hungarian": get_item("Q9067"),
        "Icelandic": get_item("Q294"),
        "Igbo": get_item("Q33578"),
        "Indonesian": get_item("Q9240"),
        "Irish": get_item("Q9142"),
        "Italian": get_item("Q652"),
        "Japanese": get_item("Q5287"),
        "K'iche'": get_item("Q36494"),
        "Kannada": get_item("Q33673"),
        "Kazakh": get_item("Q9252"),
        "Khmer": get_item("Q9205"),
        "Kinyarwanda": get_item("Q33573"),
        "Konkani": get_item("Q34239"),
        "Korean": get_item("Q9176"),
        "Kyrgyz": get_item("Q9255"),
        "Latvian": get_item("Q9078"),
        "Lithuanian": get_item("Q9083"),
        "Luxembourgish": get_item("Q9051"),
        "Macedonian": get_item("Q9296"),
        "Malay": get_item("Q9237"),
        "Malayalam": get_item("Q36236"),
        "Maltese": get_item("Q9166"),
        "Maori": get_item("Q36451"),
        "Marathi": get_item("Q1571"),
        "Mongolian": get_item("Q9246"),
        "Nepali": get_item("Q33823"),
        "Norwegian": get_item("Q9043"),
        "Odia": get_item("Q33810"),
        "Persian": get_item("Q9168"),
        "Polish": get_item("Q809"),
        "Portuguese - Brazil": get_item("Q750553"),
        "Portuguese - Portugal": get_item("Q5146"),
        "Punjabi (Gurmukhi)": get_item("Q58635"), # No item for specific writing yet?
        "Punjabi (Shahmukhi)": get_item("Q58635"), # No item for specific writing yet?
        "Quechua": get_item("Q5218"),
        "Romanian": get_item("Q7913"),
        "Russian": get_item("Q7737"),
        "Scots": get_item("Q14549"),
        "Serbian": get_item("Q9299"),
        "Simplified Chinese": get_item("Q13414913"),
        "Sindhi": get_item("Q33997"),
        "Sinhala": get_item("Q13267"),
        "Slovak": get_item("Q9058"),
        "Slovenian": get_item("Q9063"),
        "Sorani": get_item("Q36811"),
        "Sotho": get_item("Q34340"),
        "Spanish - Latin America": get_item("Q56649449"),
        "Spanish - Spain": get_item("Q1321"),
        "Swahili": get_item("Q7838"),
        "Swedish": get_item("Q9027"),
        "Tajik": get_item("Q9260"),
        "Tamil": get_item("Q5885"),
        "Tatar": get_item("Q25285"),
        "Telugu": get_item("Q8097"),
        "Thai": get_item("Q9217"),
        "Tigrinya": get_item("Q34124"),
        "Traditional Chinese": get_item("Q18130932"),
        "Tswana": get_item("Q34137"),
        "Turkish": get_item("Q256"),
        "Turkmen": get_item("Q9267"),
        "Ukrainian": get_item("Q8798"),
        "Urdu": get_item("Q1617"),
        "Uyghur": get_item("Q13263"),
        "Uzbek": get_item("Q9264"),
        "Valencian": get_item("Q32641"),
        "Vietnamese": get_item("Q9199"),
        "Welsh": get_item("Q9309"),
        "Wolof": get_item("Q34257"),
        "Xhosa": get_item("Q13218"),
        "Yoruba": get_item("Q34311"),
        "Zulu": get_item("Q10179"),
    }

    languages_qualifiers = [
        get_item("Q47146"), # inteface
        get_item("Q22920017"), # full_audio
        get_item("Q204028"), # subtitles
    ]

    month_names = {
        "Jan": 1,     "January": 1,
        "Feb": 2,     "February": 2,
        "Mar": 3,     "March": 3,
        "Apr": 4,     "April": 4,
        "May": 5,
        "Jun": 6,     "June": 6,
        "Jul": 7,     "July": 7,
        "Aug": 8,     "August": 8,
        "Sep": 9,     "September": 9,
        "Oct": 10,    "October": 10,
        "Nov": 11,    "November": 11,
        "Dec": 12,    "December": 12,
    }

    def __init__(self, steam_id, bypass_cache=False):
        steam_id = extract_steam_id(steam_id)
        filename = f"steam_cache/{steam_id}"
        if os.path.isfile(filename) and not bypass_cache:
            with open(filename, encoding="utf-8") as cache_page:
                html = cache_page.read()
            retrieve_date = datetime.utcfromtimestamp(os.path.getmtime(filename))
            print(f"{steam_id}: Cached HTML used")
            self.cache_used = True
        else:
            url = f"https://store.steampowered.com/app/{steam_id}/"
            response = requests.get(url, headers=self.headers)
            if not response:
                raise RuntimeError(f"Can't access page `{steam_id}`. Status code: {response.status_code}")
            if extract_steam_id(response.url) != steam_id:
                raise RuntimeError(f"Redirected to the different page ({steam_id})")
            html = response.text
            match = re.search(r"<span class=\"error\">(.*?)</span>", html)
            if match:
                raise RuntimeError(f"{match.group(1)} ({steam_id})")
            if "<title>Welcome to Steam</title>" in html:
                raise RuntimeError(f"Redirected to the main page ({steam_id})")
            retrieve_date = datetime.now(UTC)
            print(f"{steam_id}: HTML downloaded")
            self.cache_used = False

        self.steam_id = steam_id
        self.html = html
        self.retrieve_date = pywikibot.WbTime(year=retrieve_date.year, month=retrieve_date.month, day=retrieve_date.day)

    def cache(self):
        """
        Save html code as steam_cache/{steam_id} file. Next time it would be requested,
        __init__ would read a file instead of making a request.
        """
        if self.cache_used:
            return
        if not os.path.isdir("steam_cache"):
            os.mkdir("steam_cache")
        filename = f"steam_cache/{self.steam_id}"
        with open(filename, "w", encoding="utf-8") as cache_page:
            cache_page.write(self.html)

    def uncache(self):
        """Delete current Steam ID from cache."""
        filename = f"steam_cache/{self.steam_id}"
        if os.path.isfile(filename):
            os.remove(filename)

    def get_retrieve_date(self):
        """Get the date of downloading the HTML (handy for pages taken from cache)."""
        return self.retrieve_date

    def generate_source(self):
        """Create a Wikidata "stated in" source linking to this Steam page."""
        statedin = pywikibot.Claim(repo, "P248")
        statedin.setTarget(steam)
        steam_id = pywikibot.Claim(repo, "P1733")
        steam_id.setTarget(self.steam_id)
        retrieved = pywikibot.Claim(repo, "P813")
        retrieved.setTarget(self.retrieve_date)
        return [statedin, steam_id, retrieved]

    def get_id(self):
        """Get steam ID as string, for instance, '220'."""
        return self.steam_id

    def get_instance(self):
        """Get instance as a string: 'game', 'dlc', 'mod' or 'soundtrack'."""
        if "game_area_dlc_bubble" in self.html:
            return "dlc"
        if "game_area_mod_bubble" in self.html:
            return "mod"
        if "game_area_soundtrack_bubble" in self.html:
            return "soundtrack"
        if "<h2>About This Software</h2>" in self.html:
            return "software"
        return "game"

    def get_instance_item(self):
        """Get instance as pywikibot.ItemPage object."""
        return self.instance_map[self.get_instance()]

    def get_title(self):
        """Get title as a string, for instance, 'Half-Life 2'."""
        match = re.search(r"<div id=\"appHubAppName\" class=\"apphub_AppName\">(.*?)</div>", self.html)
        if match:
            title = match.group(1)
            for (matcher, replacer) in title_replacements:
                title = re.sub(matcher, replacer, title)
            return title.strip()

        raise RuntimeError("Can't retrieve game title")

    def get_dlc_base_game(self):
        """Get Steam ID of the base game for this DLC or expansion."""
        match = re.search(r"<h1>Downloadable Content</h1>\s*<p>[^<>]+<a href=\"https?://store\.steampowered\.com/app/(\d+)[\"/]", self.html)
        if match:
            return match.group(1)
        raise RuntimeError("Can't get DLC base game")

    def get_dlc_base_game_item(self):
        """Get base game for this DLC or expansion as pywikibot.ItemPage instance."""
        return find_item_for_id(self.get_dlc_base_game())

    def get_mod_base_game(self):
        """Get Steam ID of the base game for this modification."""
        match = re.search(r"<h1>Community-Made Mod</h1>\s*<p>[^<>]+<a href=\"https?://store\.steampowered\.com/app/(\d+)[\"/]", self.html)
        if match:
            return match.group(1)
        raise RuntimeError("Can't get modification base game")

    def get_mod_base_game_item(self):
        """Get base game for this modification as pywikibot.ItemPage instance."""
        return find_item_for_id(self.get_mod_base_game())

    def get_release_status(self):
        """Get status as a string: 'unreleased', 'early access' or 'released'."""
        if "game_area_comingsoon" in self.html:
            return "unreleased"
        if "early_access_header" in self.html:
            return "early access"
        return "released"

    def is_released(self):
        """Check if the game has been fully released."""
        return self.get_release_status() == "released"

    def parse_release_date(self, date):
        """Init pywikibot.WbTime instance."""
        date = date.strip()

        # 10 Dec, 2077
        match = re.match(r"^(\d{1,2}) ([A-Z][a-z]{2}), (\d{4})$", date)
        if match:
            month_name = match.group(2)
            if month_name not in self.month_names:
                raise RuntimeError(f"Unknown month abbreviation `{month_name}`")
            return pywikibot.WbTime(year=int(match.group(3)), month=self.month_names[month_name], day=int(match.group(1)))

        # Dec 10, 2077
        match = re.match(r"^([A-Z][a-z]{2}) (\d{1,2}), (\d{4})$", date)
        if match:
            month_name = match.group(1)
            if month_name not in self.month_names:
                raise RuntimeError(f"Unknown month abbreviation `{month_name}`")
            return pywikibot.WbTime(year=int(match.group(3)), month=self.month_names[month_name], day=int(match.group(2)))

        # December 2077
        match = re.match(r"^([A-Z][a-z]+) (\d{4})$", date)
        if match:
            month_name = match.group(1)
            if month_name not in self.month_names:
                raise RuntimeError(f"Unknown month name `{month_name}`")
            return pywikibot.WbTime(year=int(match.group(2)), month=self.month_names[month_name])

        # Q4 2077
        match = re.match(r"^Q([1-4]) (\d{4})", date)
        if match:
            # Wikidata doesn't support quarters of calendar year, so we'll shorten it to year only
            return pywikibot.WbTime(year=int(match.group(2)))

        # 2077
        match = re.match(r"^(\d{4})$", date)
        if match:
            return pywikibot.WbTime(year=int(match.group(1)))

        # Coming soon
        if date == "Coming soon":
            raise RuntimeError("No date specified")

        raise RuntimeError(f"Unknown date format: `{date}`")

    def get_release_date(self):
        """Get release date as an pywikibot.WbTime instance."""
        match = re.search(r"<div class=\"date\">(.*?)</div>", self.html)
        if match is None:
            raise RuntimeError("Release date field not found")
        return self.parse_release_date(match.group(1))

    def get_early_access_release_date(self):
        """Get early access release date as an pywikibot.WbTime instance."""
        # <b>Early Access Release Date:</b> 6 May, 2024<br>
        match = re.search(r"<b>Early Access Release Date:</b>(.*?)<br>", self.html)
        if match is None:
            return None
        return self.parse_release_date(match.group(1))

    def get_release_year(self):
        """Get release year as int, or None."""
        try:
            return self.get_release_date().year
        except RuntimeError:
            return None

    def get_developers(self):
        """Get developers as a list of strings, for instance, ['Valve']."""
        match = re.search(r"id=\"developers_list\">([\s\S]+?)</div>", self.html)
        if match:
            return [developer.strip() for developer in re.findall(r"<a[^>]+>(.*?)</a>", match.group(1))]
        return []

    def get_publishers(self):
        """Get publishers as a list of strings, for instance, ['Valve']."""
        match = re.search(r"Publisher:</div>\s*<div[^>]+>([\s\S]+?)</div>", self.html)
        if match:
            return [publisher.strip() for publisher in re.findall(r"<a[^>]+>(.*?)</a>", match.group(1))]
        return []

    def get_platforms(self):
        """Get platforms as a list of strings: 'win', 'mac' or 'linux'."""
        return re.findall(r"<div class=\"game_area_sys_req sysreq_content (?:active)?\" data-os=\"([a-z]+)\">", self.html)

    def get_platform_items(self):
        """Get platforms as a list of pywikibot.ItemPage instances."""
        return [self.platform_map[x] for x in self.get_platforms()]

    def get_gamemodes(self):
        """Get gamemodes as a list of pywikibot.ItemPage instances."""
        result = []
        if "steamstatic.com/public/images/v6/ico/ico_singlePlayer.png" in self.html:
            result.append("singleplayer")
        if "steamstatic.com/public/images/v6/ico/ico_multiPlayer.png" in self.html:
            result.append("multiplayer")
        if "steamstatic.com/public/images/v6/ico/ico_coop.png" in self.html:
            result.append("cooperative")
        return result

    def get_gamemode_items(self):
        """Get gamemodes as a list of pywikibot.ItemPage instances."""
        return [self.gamemode_map[x] for x in self.get_gamemodes()]

    def get_language_items(self):
        """
        Get languages as a list of the following tuple:
            (
                language as pywikibot.ItemPage instance,
                [`applies to part` (P518) qualifiers as a list of pywikibot.ItemPage instances]
            )
        """
        result = []
        same_checks = True
        seen_languages = set()
        for language, info in re.findall(r"class=\"ellipsis\">\s*(.*?)\s*</td>\s*(.*?)\s*</tr>", self.html, flags=re.DOTALL):
            if "Not supported" in info:
                continue

            if language not in self.languages_map:
                raise RuntimeError(f"Unknown language `{language}`")
            language_item = self.languages_map[language]

            if language_item.getID() in seen_languages:
                # For some languages, steam has more diverse classification than we do.
                # In this case, languages_map can have overlapping items, and we don't want to have
                # duplicate values in the languages list.
                continue
            seen_languages.add(language_item.getID())

            checks = re.findall(r"<td class=\"checkcol\">\s*(<span>&#10004;</span>)?\s*</td>\s*", info)
            if len(checks) != 3:
                raise RuntimeError("Can't parse language tables")
            qualifiers = [qualifier for qualifier, check in zip(self.languages_qualifiers, checks) if check]

            result.append((language_item, qualifiers))

            if qualifiers != result[0][1]:
                same_checks = False

        if same_checks:
            # Some indie titles love to ensure they have full voice acting and subtitles for every
            # language even if the games don't have any speech whatsoever.
            # Since qualifiers would give us no additional info if all of them would be equal, let's
            # only add qualifiers for games that have different qualifiers for different languages.
            result = [(language, []) for language, _ in result]
        return result

    def get_metacritic_id(self):
        """Get Metacritic slug (for instance, `game/pc/mosaic`), if stated."""
        match = re.search(r"<a href=\"https://www\.metacritic\.com/game/(?:pc/)?([\-a-z0-9!+_()]+)(?:\?[^\"]+)\" target=\"_blank\">Read Critic Reviews</a>", self.html)
        if not match:
            return None

        metacritic_id = match.group(1)
        if not re.match(r"^[a-z\d]+(\-[a-z\d]+)*$", metacritic_id):
            return None

        return metacritic_id


class ItemProcessor():
    """Processor for one (ItemPage, SteamPage) pair."""

    def __init__(self, item_page, steam_page):
        self.item_page = item_page
        self.steam_page = steam_page

    def generate_inferred_from_source(self):
        """Create a Wikidata "inferred_from" source linking to Steam item."""
        source = pywikibot.Claim(repo, "P3452")
        source.setTarget(steam)
        return [source]

    def call_safe(self, function, default_value=None):
        """
        Call function. In case of RuntimeError exception, log it and return default value instead.
        """
        try:
            return function()
        except RuntimeError as error:
            print(f"{self.steam_page.get_id()}: WARNING: {error}")
            return default_value

    def find_claim(self, prop, value):
        """Return requested prop=value claim as pywikibot.Claim."""
        if prop not in self.item_page.claims:
            return None
        for claim in self.item_page.claims[prop]:
            if claim.getTarget() == value:
                return claim
        return None

    def add_steam_qualifier(self, prop, values, typename="claim"):
        """For each value, add prop=value qualifier to the Steam ID claim."""
        steam_id = self.steam_page.get_id()
        claim = self.find_claim("P1733", steam_id)
        if prop in claim.qualifiers:
            return
        for value in values:
            qualifier = pywikibot.Claim(repo, prop)
            qualifier.setTarget(value)
            claim.addQualifier(qualifier, summary=f"Add {typename} qualifier to Steam ID `{steam_id}`")
            print(f"{steam_id}: Added {typename} qualifier")

    def add_claims(self, prop, values, typename="claim", get_source="default"):
        """If requested property is not set, add prop=value claim for each given value."""
        if not values:
            return
        if prop in self.item_page.claims:
            return
        if get_source == "default":
            get_source = self.steam_page.generate_source
        for value in values:
            if not value:
                continue
            claim = pywikibot.Claim(repo, prop)
            claim.setTarget(value)
            if get_source:
                claim.addSources(get_source())
            self.item_page.addClaim(claim, summary=f"Add {typename} based on Steam page")
            print(f"{self.steam_page.get_id()}: Added {typename}")

    def add_claims_with_update(self, prop, values, typename="claim", get_source="default", add_sources=False):
        """
        Add prop=value claim for each given value. Unlike add_claims(), this method would not ignore
        set properties, if it has new values to add.
        If add_sources is True, also add sources to uncited set values.
        """
        if not values:
            return
        if get_source == "default":
            get_source = self.steam_page.generate_source
        for value in values:
            if not value:
                continue
            claim = self.find_claim(prop, value)
            if claim:
                # claim is already set, let's add a source if it's neccessary
                if add_sources and len(claim.getSources()) == 0:
                    claim.addSources(get_source(), summary="Add source")
                    print(f"{self.steam_page.get_id()}: Added a source for {typename}")
            else:
                # there's no such claim, let's create it
                claim = pywikibot.Claim(repo, prop)
                claim.setTarget(value)
                if get_source:
                    claim.addSources(get_source())
                self.item_page.addClaim(claim, summary=f"Add {typename} based on Steam page")
                print(f"{self.steam_page.get_id()}: Added {typename}")

    def add_claims_with_qualifiers(self, prop, qualifier_prop, values, typename="claim", get_source="default"):
        """
        Add given values with given qualifiers.
        `values` is a list of the following tuple: (property_value, [list_of_qualifier_values]).
        """
        if not values:
            return
        if get_source == "default":
            get_source = self.steam_page.generate_source
        if prop in self.item_page.claims:
            return
        for prop_value, qualifier_values in values:
            claim = pywikibot.Claim(repo, prop)
            claim.setTarget(prop_value)
            for qualifier_value in qualifier_values:
                qualifier = pywikibot.Claim(repo, qualifier_prop)
                qualifier.setTarget(qualifier_value)
                claim.addQualifier(qualifier)
            if get_source:
                claim.addSources(get_source())
            self.item_page.addClaim(claim, summary=f"Add {typename} based on Steam page")
            print(f"{self.steam_page.get_id()}: Added {typename}")

    def process_release_date(self, status, date, ea_date):
        """Import release date from Steam to Wikidata."""
        prop = "P577"

        if status == "released":
            if ea_date and ea_date != date:
                # the game used to be in early access
                # if no dates are specified, let's import early access release date
                # otherwise it's too ambiguous for the bot
                data = (ea_date, [early_access])
                self.add_claims_with_qualifiers(prop, "P3831", [data], "early access release date")
                self.add_claims_with_update("P7936", [early_access], "business model")

            # set release date if no full release dates are specified (early access is okay)
            if prop in self.item_page.claims:
                for claim in self.item_page.claims[prop]:
                    is_early_access_date = False
                    for qualifier, value in claim.qualifiers.items():
                        if qualifier == "P3831" and len(value) == 1 and value[0].getTarget() == early_access:
                            is_early_access_date = True
                            break
                    if not is_early_access_date:
                        return

            claim = pywikibot.Claim(repo, prop)
            claim.setTarget(date)
            claim.addSources(self.steam_page.generate_source())
            self.item_page.addClaim(claim, summary="Add release date based on Steam page")
            print(f"{self.steam_page.get_id()}: Added release date")

        elif status == "early access":
            # the game is in early access right now to be in early access
            data = (date, [early_access])
            self.add_claims_with_qualifiers("P577", "P3831", [data], "early access release date")
            self.add_claims_with_update("P7936", [early_access], "business model")

    def process(self):
        """Import missing information from Steam to Wikidata."""
        status = self.steam_page.get_release_status()
        date = self.call_safe(self.steam_page.get_release_date)
        ea_date = self.call_safe(self.steam_page.get_early_access_release_date)
        platforms = self.steam_page.get_platform_items()
        gamemodes = self.steam_page.get_gamemode_items()
        languages = self.call_safe(self.steam_page.get_language_items)
        metacritic = self.steam_page.get_metacritic_id()

        self.add_steam_qualifier("P400", platforms, "platform")
        self.add_claims_with_update("P437", [digital_distribution], "distribution format", get_source=self.generate_inferred_from_source)
        self.add_claims_with_update("P750", [steam], "distributor")
        self.add_claims("P123", arguments.publishers, "publisher")
        self.add_claims("P178", arguments.developers, "developer")
        self.add_claims("P179", [arguments.series], "series")
        self.add_claims("P136", arguments.genres, "series")
        self.process_release_date(status, date, ea_date)
        self.add_claims_with_update("P400", platforms, "platform", add_sources=True)
        self.add_claims_with_update("P404", gamemodes, "game mode", add_sources=True)
        self.add_claims_with_qualifiers("P407", "P518", languages, "language")
        self.add_claims("P12054", [metacritic], "Metacritic ID")

        print(f"{self.steam_page.get_id()}: Item {self.item_page.title()} processed")
        if output:
            output.write(f"{self.item_page.title()}\n")

class ExistingItemProcessor(ItemProcessor):
    """
    ItemProcessor for existing Wikidata item. Item must have Steam application ID (P1733) set,
    this class would use it to get SteamPage.
    """

    def check_instance_of(self, item):
        """Check if the item is an instance of video game, DLC or expansion pack."""
        if "P31" not in item.claims:
            raise RuntimeError("Instance of is not set")
        supported_instances = {
            "Q7889", # video game
            "Q209163", # video game expansion pack
            "Q848991", # browser game
            "Q865493", # video game mod
            "Q1066707", # downloadable content
            "Q1755420", # game demo
            "Q4393107", # video game remake
            "Q61475894", # cancelled/unreleased video game
            "Q65963104", # video game remaster
            "Q16070115", # video game compilation
            "Q21125433", # free or open-source video game
            "Q55632755", # season pass
            "Q56196027", # stuff pack
            "Q60997816", # video game edition
            "Q61456428", # total conversion mod
            "Q62707668", # high resolution texture pack
            "Q64170203", # video game project
            "Q64170508", # unfinished or abandoned video game project
            "Q96604496", # GOTY edition
            "Q90181054", # video game episode
            "Q107458055", # director's cut
            "Q107636751", # cosmetic downloadable content
            "Q111223304", # video game reboot
            "Q111662771", # clothing downloadable content
        }
        for claim in item.claims["P31"]:
            instance = claim.getTarget()
            if instance is None:
                continue
            if instance.getID() in supported_instances:
                return True
        return False

    def __init__(self, item_id):
        item = pywikibot.ItemPage(repo, item_id)
        if not self.check_instance_of(item):
            raise RuntimeError("Item is not an instance of video game, DLC or expansion pack")
        steam_id = get_only_value(item, "P1733", "Steam application ID")
        super().__init__(item, SteamPage(steam_id))

class NewItemProcessor(ItemProcessor):
    """
    ItemProcessor for newly created item (NewItemProcessor would create it during initialization).
    """

    def __init__(self, steam_id):
        steam_page = SteamPage(steam_id)
        title = steam_page.get_title()
        instance = steam_page.get_instance()
        status = steam_page.get_release_status()

        base_property = None
        base_game = None
        if instance == "game" and status == "early access":
            instance = "early access"
        elif instance == "dlc":
            base_property = "P8646"
            base_game = steam_page.get_dlc_base_game_item()
        elif instance == "mod":
            base_property = "P7075"
            base_game = steam_page.get_mod_base_game_item()

        if status == "released" or instance == "early access":
            year = steam_page.get_release_year()
        else:
            year = None

        if instance not in descriptions_data:
            raise RuntimeError(f"{instance} items are not supported")

        labels = { 'mul' : title }
        if year:
            descriptions = { data[0]: data[2].format(year) for data in descriptions_data[instance] if data[2] }
        else:
            descriptions = { data[0]: data[1] for data in descriptions_data[instance] if data[1] }

        item = pywikibot.ItemPage(repo)
        item.editEntity(
            { "labels": labels, "descriptions": descriptions },
            summary=f"Create item for Steam application `{steam_id}`"
        )

        super().__init__(item, steam_page)

        self.add_claims("P31", [steam_page.get_instance_item()], "instance of")
        self.add_claims_with_qualifiers("P1733", "P400", [(steam_id, steam_page.get_platform_items())], "Steam ID", get_source=None)
        if base_property and base_game:
            self.add_claims(base_property, [base_game], "base game")

        if not arguments.watch:
            item.watch(unwatch=True)

def cache_pages():
    """
    Download every steam page listed in `to_cache.txt` (Steam ID, number only, one per line),
    and save each of them them locally at "steam_cache/{steam_id}" file. They lately would be used
    at get_html() function.

    I personally used it to bypass regional restrictions: download steam pages via vpn, turn off
    the vpn, launch the wikidata bot.
    """
    with open("to_cache.txt", encoding="utf-8") as listfile:
        for line in listfile:
            steam_id = line.strip()
            try:
                SteamPage(steam_id, bypass_cache=True).cache()
            except RuntimeError as error:
                print(f"{steam_id}: {error}")

def remove_duplicates(id_list):
    """Remove Steam IDs that already set in some Wikidata items."""
    ok_items = []
    sparql = SparqlQuery()
    for idx in range(0, len(id_list), 100):
        codes = " ".join([f"\"{steam_id}\"" for steam_id in id_list[idx:idx+100]])
        ok_items += sparql.select(f"""
            SELECT ?code WHERE {{
              VALUES ?code {{ {codes} }} .
              FILTER NOT EXISTS {{
                ?item wdt:P1733 ?code
              }}
            }}
        """)

    # we can just return [el["code"] for el in ok_items], but we want to keep
    # original order and notify about every duplicate
    ok_items = { el["code"] for el in ok_items }

    result = []
    for steam_id in id_list:
        if steam_id in ok_items:
            result.append(steam_id)
        else:
            print(f"{steam_id}: Duplicates existing item, skipped")
    return result

def main(input_filename):
    """Filter duplicates, sort identifiers and process them."""

    # Remove duplicates and sort IDs
    q_list = []
    s_list = []
    with open(input_filename, encoding="utf-8") as listfile:
        for line in listfile:
            line = line.strip()
            if line.startswith("Q"):
                if line not in q_list:
                    q_list.append(line)
            else:
                if line not in s_list:
                    s_list.append(line)
    s_list = remove_duplicates(s_list)

    # Process existing items
    for item_id in q_list:
        try:
            ExistingItemProcessor(item_id).process()
        except RuntimeError as error:
            print(f"{item_id}: {error}")

    # Create new items
    for steam_id in s_list:
        try:
            NewItemProcessor(steam_id).process()
        except RuntimeError as error:
            print(f"{steam_id}: {error}")

def parse_item_page_arg(arg_value):
    """Parse pywikibot.ItemPage for ArgumentParser."""
    if not re.match(r"^Q\d+$", arg_value):
        raise argparse.ArgumentTypeError
    return pywikibot.ItemPage(repo, arg_value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract various video game data from Steam based on Steam application ID.")
    parser.add_argument("input", help="a path to file with list of IDs of items to process (Qnnn) or Steam IDs to be included in newly created items (just number); mixed input is supported")
    parser.add_argument("-publisher", "-p", type=parse_item_page_arg, nargs="+", action="store", dest="publishers", help="wikidata element(s) to state in P123 (optional)")
    parser.add_argument("-genres", "-g", type=parse_item_page_arg, nargs="+", action="store", dest="genres", help="wikidata element(s) to state in P136 (optional)")
    parser.add_argument("-developer", "-d", type=parse_item_page_arg, nargs="+", action="store", dest="developers", help="wikidata element(s) to state in P178 (optional)")
    parser.add_argument("-series", "-s", type=parse_item_page_arg, action="store", dest="series", help="wikidata element to state in P179 (optional)")
    parser.add_argument("-output", "-o", action="store", dest="output", help="a path to a file to fill with a list of IDs of the processed items, including newly created (optional)")
    parser.add_argument("-watch", "-w", action="store_true", help="if set, keep newly created items in the user's watchlist")

    arguments = parser.parse_args()
    if arguments.output:
        output = open(arguments.output, "a", encoding="utf-8")

    main(arguments.input)
