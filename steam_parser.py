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

import pywikibot
from pywikibot.data.sparql import SparqlQuery
import urllib.request
import time
import re
import random
import argparse
import os.path
from datetime import datetime

title_replacements = [
    (r"&quot;", "\""),
    (r"&reg;|®", ""),
    (r"&trade;|™", ""),
    (r"&amp;", "&"),
]

vg_descriptions_data = [
    # (lang_code, default_description, description_with_year)
    ("ast", "videoxuegu", "videoxuegu espublizáu en {}"),
    ("be", "камп’ютарная гульня", "камп’ютарная гульня {} году"),
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
    ("fi", "videopeli", "{} videopeli"),
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

dlc_descriptions_data = [
    ("en", "expansion pack", "{} expansion pack"),
    ("ru", "дополнение", "дополнение {} года"),
]

mod_descriptions_data = [
    ("en", "mod", "{} mod"),
    ("ru", "мод", "мод {} года"),
]

descriptions_data = {
    "game": vg_descriptions_data,
    "dlc": dlc_descriptions_data,
    "mod": mod_descriptions_data,
}

arguments = None
output = None

repo = pywikibot.Site()
get_item = lambda x: pywikibot.ItemPage(repo, x)

steam = get_item("Q337535")
digital_distribution = get_item("Q269415")

def find_item_for_id(steam_id):
    sparql = SparqlQuery()
    result = sparql.select("""
        SELECT ?item WHERE {{
          ?item wdt:P1733 \"{}\" .
        }}
    """.format(steam_id))
    if len(result) != 1:
        return None
    match = re.match(r"^https?://www\.wikidata\.org/entity/(Q\d+)$", result[0]["item"])
    if not match:
        return None
    return pywikibot.ItemPage(repo, match.group(1))



class SteamPage():
    """
    One parsed Steam store page related to a videogame, an expansion, a modification or
    a soundtrack.
    """

    instance_map = {
        "game": get_item("Q7889"),
        "dlc": get_item("Q209163"),
        "mod": get_item("Q865493"),
        "soundtrack": get_item("Q100749465"),
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
        "English": get_item("Q1860"),
        "French": get_item("Q150"),
        "Italian": get_item("Q652"),
        "German": get_item("Q188"),
        "Spanish - Spain": get_item("Q1321"),
        "Japanese": get_item("Q5287"),
        "Korean": get_item("Q9176"),
        "Polish": get_item("Q809"),
        "Portuguese - Brazil": get_item("Q750553"),
        "Russian": get_item("Q7737"),
        "Simplified Chinese": get_item("Q13414913"),
        "Spanish - Latin America": get_item("Q56649449"),
        "Thai": get_item("Q9217"),
        "Traditional Chinese": get_item("Q18130932"),
        "Arabic": get_item("Q13955"),
        "Bulgarian": get_item("Q7918"),
        "Hungarian": get_item("Q9067"),
        "Vietnamese": get_item("Q9199"),
        "Greek": get_item("Q9129"),
        "Danish": get_item("Q9035"),
        "Dutch": get_item("Q7411"),
        "Norwegian": get_item("Q9043"),
        "Portuguese": get_item("Q5146"),
        "Portuguese - Portugal": get_item("Q5146"),
        "Romanian": get_item("Q7913"),
        "Serbian": get_item("Q9299"),
        "Turkish": get_item("Q256"),
        "Ukrainian": get_item("Q8798"),
        "Finnish": get_item("Q1412"),
        "Czech": get_item("Q9056"),
        "Slovakian": get_item("Q9058"),
        "Swedish": get_item("Q9027"),
        "Hebrew": get_item("Q9288"),
        "Lithuanian": get_item("Q9083"),
    }

    languages_qualifiers = [
        get_item("Q47146"), # inteface
        get_item("Q22920017"), # full_audio
        get_item("Q204028"), # subtitles
    ]

    month_names = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    def __init__(self, steam_id, quiet=False, bypass_cache=False):
        match = re.match(r"https://store\.steampowered\.com/app/(\d+)/?", steam_id)
        if match:
            steam_id = match.group(1)
        else:
            steam_id = steam_id.strip()

        filename = "steam_cache/{}".format(steam_id)
        if os.path.isfile(filename) and not bypass_cache:
            html = open(filename, encoding="utf-8").read()
            retrieve_date = datetime.utcfromtimestamp(os.path.getmtime(filename))
            print("{}: used cached HTML".format(steam_id))
        else:
            attempts = 3
            headers = {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3",
                "Accept-Encoding": "none",
                "Accept-Language": "en-US,en;q=0.8",
                "Connection": "keep-alive",
                "Cookie": "wants_mature_content=1;birthtime=470682001;lastagecheckage=1-0-1985;Steam_Language=english"
            }
            url = "https://store.steampowered.com/app/{}/".format(steam_id)
            for attempt_no in range(attempts):
                try:
                    time.sleep(random.randint(1, 3))
                    request = urllib.request.Request(url, None, headers)
                    response = urllib.request.urlopen(request)
                    html = response.read().decode("utf-8")
                except Exception as error:
                    if attempt_no == (attempts - 1):
                        raise error
            match = re.search(r"<span class=\"error\">(.*?)</span>", html)
            if match:
                raise RuntimeError(match.group(1))
            if "<title>Welcome to Steam</title>" in html:
                raise RuntimeError("Redirected to the main page")
            retrieve_date = datetime.utcnow()

            print("{}: HTML downloaded".format(steam_id))

        self.steam_id = steam_id
        self.html = html
        self.retireve_date = pywikibot.WbTime(year=retrieve_date.year, month=retrieve_date.month, day=retrieve_date.day)

    def cache(self):
        """
        Save html code as steam_cache/{steam_id} file. Next time it would be requested,
        __init__ would read a file instead of making a request.
        """
        if not os.path.isdir("steam_cache"):
            os.mkdir("steam_cache")
        filename = "steam_cache/{}".format(self.steam_id)
        open(filename, "w", encoding="utf-8").write(self.html)

    def uncache(self):
        """Delete current Steam ID from cache."""
        filename = "steam_cache/{}".format(self.steam_id)
        if os.path.isfile(filename):
            os.remove(filename)

    def get_retireve_date(self):
        """Get the date of downloading the HTML (handy for pages taken from cache)."""
        return self.retireve_date

    def generate_source(self):
        """Create a Wikidata "stated in" source linking to this Steam page."""
        statedin = pywikibot.Claim(repo, "P248")
        statedin.setTarget(steam)
        steam_id = pywikibot.Claim(repo, "P1733")
        steam_id.setTarget(self.steam_id)
        retrieved = pywikibot.Claim(repo, "P813")
        retrieved.setTarget(self.retireve_date)
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
        else:
            raise RuntimeError("Can't retrieve game title")

    def get_dlc_base_game(self):
        """Get Steam ID of the base game for this DLC or expansion."""
        match = re.search(r"<h1>Downloadable Content</h1>\s*<p>[^<>]+<a href=\"https?://store\.steampowered\.com/app/(\d+)[\"/]", self.html)
        if match:
            return match.group(1)
        else:
            raise RuntimeError("Can't get DLC base game")

    def get_dlc_base_game_item(self):
        """Get base game for this DLC or expansion as pywikibot.ItemPage instance."""
        return find_item_for_id(self.get_dlc_base_game())

    def get_mod_base_game(self):
        """Get Steam ID of the base game for this modification."""
        match = re.search(r"<h1>Community-Made Mod</h1>\s*<p>[^<>]+<a href=\"https?://store\.steampowered\.com/app/(\d+)[\"/]", self.html)
        if match:
            return match.group(1)
        else:
            raise RuntimeError("Can't get modification base game")

    def get_mod_base_game_item(self):
        """Get base game for this modification as pywikibot.ItemPage instance."""
        return find_item_for_id(self.get_mod_base_game())

    def get_status(self):
        """Get status as a string: 'unreleased', 'early access' or 'released'."""
        if "game_area_comingsoon" in self.html:
            return "unreleased"
        if "early_access_header" in self.html:
            return "early access"
        return "released"

    def get_release_date(self):
        """Get release date as an pywikibot.WbTime instance. Throw an exception if the game isn't released yet."""
        status = self.get_status()
        if status != "released":
            raise RuntimeError("Can't retrieve release date of an {} game".format(status))
        match = re.search(r"<div class=\"date\">(\d+) ([A-Z][a-z]{2}), (\d+)</div>", self.html)
        if match is None:
            raise RuntimeError("Release date parsing error")
        return pywikibot.WbTime(year=int(match.group(3)), month=self.month_names[match.group(2)], day=int(match.group(1)))

    def get_release_year(self):
        """Get release year, or None if the game isn't released yet."""
        try:
            return self.get_release_date().year
        except Exception:
            return None

    def get_developers(self):
        """Get developers as a list of strings, for instance, ['Valve']."""
        match = re.search(r"id=\"developers_list\">([\s\S]+?)</div>", self.html)
        if match:
            return [developer.strip() for developer in re.findall(r"<a[^>]+>(.*?)</a>", match.group(1))]
        else:
            return []

    def get_publishers(self):
        """Get publishers as a list of strings, for instance, ['Valve']."""
        match = re.search(r"Publisher:</div>\s*<div[^>]+>([\s\S]+?)</div>", self.html)
        if match:
            return [publisher.strip() for publisher in re.findall(r"<a[^>]+>(.*?)</a>", match.group(1))]
        else:
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
        for language, info in re.findall(r"class=\"ellipsis\">\s*(.*?)\s*</td>\s*(.*?)\s*</tr>", self.html, flags=re.DOTALL):
            if "Not supported" in info:
                continue
            checks = re.findall(r"<td class=\"checkcol\">\s*(<span>&#10004;</span>)?\s*</td>\s*", info)
            if len(checks) != 3:
                raise ValueError("Can't parse language tables")
            qualifiers = [qualifier for qualifier, check in zip(self.languages_qualifiers, checks) if check]
            try:
                result.append((self.languages_map[language], qualifiers))
            except KeyError as error:
                raise RuntimeError("Unknown language `{}`".format(error.args[0]))
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
        match = re.search(r"<a href=\"https://www\.metacritic\.com/(game/pc/[\-a-z0-9!+_()]+)(?:\?[^\"]+)\" target=\"_blank\">Read Critic Reviews</a>", self.html)
        if match:
            return match.group(1)
        else:
            return None


class ItemProcessor():
    """Processor for one (ItemPage, SteamPage) pair."""

    def __init__(self, item_page, steam_page):
        self.item = item_page
        self.steam = steam_page

    def generate_inferred_from_source(self):
        """Create a Wikidata "inferred_from" source linking to Steam item."""
        source = pywikibot.Claim(repo, "P3452")
        source.setTarget(steam)
        return [source]

    def find_claim(self, prop, value):
        """Return requested prop=value claim as pywikibot.Claim."""
        if prop not in self.item.claims:
            return None
        for claim in self.item.claims[prop]:
            if claim.getTarget() == value:
                return claim
        return None

    def add_steam_qualifier(self, prop, values, typename="claim"):
        """For each value, add prop=value qualifier to the Steam ID claim."""
        steam_id = self.steam.get_id()
        claim = self.find_claim("P1733", steam_id)
        if prop in claim.qualifiers:
            return
        for value in values:
            qualifier = pywikibot.Claim(repo, prop)
            qualifier.setTarget(value)
            claim.addQualifier(qualifier, summary="Add {} qualifier to Steam ID `{}`".format(typename, steam_id))
            print("{}: Added {} qualifier".format(steam_id, typename))

    def add_claims(self, prop, values, typename="claim", get_source="default"):
        """If requested property is not set, add prop=value claim for each given value."""
        if prop in self.item.claims:
            return
        if get_source == "default":
            get_source = self.steam.generate_source
        for value in values:
            claim = pywikibot.Claim(repo, prop)
            claim.setTarget(value)
            if get_source:
                claim.addSources(get_source())
            self.item.addClaim(claim, summary="Add {} based on Steam page".format(typename))
            print("{}: Added {}".format(self.steam.get_id(), typename))

    def add_claims_with_update(self, prop, values, typename="claim", get_source="default", add_sources=False):
        """
        Add prop=value claim for each given value. Unlike add_claims(), this method would not ignore
        set properties, if it has new values to add.
        If add_sources is True, also add sources to uncited set values.
        """
        if get_source == "default":
            get_source = self.steam.generate_source
        for value in values:
            claim = self.find_claim(prop, value)
            if claim:
                # claim is already set, let's add a source if it's neccessary
                if add_sources and len(claim.getSources()) == 0:
                    claim.addSources(get_source(), summary="Add source")
                    print("{}: Added a source for {}".format(self.steam.get_id(), typename))
            else:
                # there's no such claim, let's create it
                claim = pywikibot.Claim(repo, prop)
                claim.setTarget(value)
                if get_source:
                    claim.addSources(get_source())
                self.item.addClaim(claim, summary="Add {} based on Steam page".format(typename))
                print("{}: Added {}".format(self.steam.get_id(), typename))

    def add_claims_with_qualifiers(self, prop, qualifier_prop, values, typename="claim", get_source="default"):
        """
        Add given values with given qualifiers.
        `values` is a list of the following tuple: (property_value, [list_of_qualifier_values]).
        """
        if get_source == "default":
            get_source = self.steam.generate_source
        if prop in self.item.claims:
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
            self.item.addClaim(claim, summary="Add {} based on Steam page".format(typename))
            print("{}: Added {}".format(self.steam.get_id(), typename))

    def process(self):
        """Import missing information from Steam to Wikidata."""
        try:
            date = self.steam.get_release_date()
        except Exception as error:
            date = None
            print("{}: {}".format(self.steam.get_id(), error))
        platforms = self.steam.get_platform_items()
        gamemodes = self.steam.get_gamemode_items()
        languages = self.steam.get_language_items()
        metacritic = self.steam.get_metacritic_id()

        self.add_steam_qualifier("P400", platforms, "platform")
        self.add_claims_with_update("P437", [digital_distribution], "distribution format", get_source=self.generate_inferred_from_source)
        self.add_claims_with_update("P750", [steam], "distributor")
        if arguments.publishers:
            self.add_claims("P123", arguments.publishers, "publisher")
        if arguments.developers:
            self.add_claims("P178", arguments.developers, "developer")
        if arguments.series:
            self.add_claims("P179", [arguments.series], "series")
        if arguments.genres:
            self.add_claims("P136", arguments.genres, "series")
        if date is not None:
            self.add_claims("P577", [date], "release date")
        self.add_claims_with_update("P400", platforms, "platform", add_sources=True)
        self.add_claims_with_update("P404", gamemodes, "game mode", add_sources=True)
        self.add_claims_with_qualifiers("P407", "P518", languages, "language")
        if metacritic:
            data = (metacritic, [self.steam.platform_map["pc"]])
            self.add_claims_with_qualifiers("P1712", "P400", [data], "Metacritic ID")

        print("{}: Item {} processed".format(self.steam.get_id(), self.item.title()))
        if output:
            output.write("{}\n".format(self.item.title()))

class ExistingItemProcessor(ItemProcessor):
    """
    ItemProcessor for existing Wikidata item. Item must have Steam application ID (P1733) set,
    this class would use it to get SteamPage.
    """

    def __init__(self, item_id):
        item = pywikibot.ItemPage(repo, item_id)

        # Check P31
        if "P31" not in item.claims:
            raise RuntimeError("Instance of is not set")
        supported_instances = {
            "Q7889", # video game
            "Q209163", # video game expansion pack
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
            "Q64170203", # video game project
            "Q90181054", # video game episode
            "Q111223304", # video game reboot
        }
        instance_is_correct = False
        for claim in item.claims["P31"]:
            if claim.getTarget().getID() in supported_instances:
                instance_is_correct = True
                break
        if not instance_is_correct:
            raise RuntimeError("Item is not an instance of video game, DLC or expansion pack")

        # check P1733
        if "P1733" not in item.claims:
            raise RuntimeError("Steam application ID not found")
        if len(item.claims["P1733"]) > 1:
            raise RuntimeError("Several Steam application IDs found")
        steam_claim = item.claims["P1733"][0]
        steam_id = steam_claim.getTarget()

        super().__init__(item, SteamPage(steam_id))

class NewItemProcessor(ItemProcessor):
    """
    ItemProcessor for newly created item (NewItemProcessor would create it automatically).
    """

    def __init__(self, steam_id):
        steam = SteamPage(steam_id)
        title = steam.get_title()
        year = steam.get_release_year()
        instance = steam.get_instance()
        if instance not in descriptions_data:
            raise RuntimeError("{} items are not supported".format(instance))

        base_property = None
        base_game = None
        if instance == "dlc":
            base_property = "P8646"
            base_game = steam.get_dlc_base_game_item()
        elif instance == "mod":
            base_property = "P7075"
            base_game = steam.get_mod_base_game_item()

        labels = { data[0] : title for data in descriptions_data[instance] }
        if year:
            descriptions = { data[0]: data[2].format(year) for data in descriptions_data[instance] if data[2] }
        else:
            descriptions = { data[0]: data[1] for data in descriptions_data[instance] if data[1] }

        item = pywikibot.ItemPage(repo)
        item.editEntity(
            { "labels": labels, "descriptions": descriptions },
            summary="Create item for Steam application `{}`".format(steam_id)
        )
        super().__init__(item, steam)

        self.add_claims("P31", [steam.get_instance_item()], "instance of")
        self.add_claims_with_qualifiers("P1733", "P400", [(steam_id, steam.get_platform_items())], "Steam ID", get_source=None)
        if base_property and base_game:
            self.add_claims(base_property, [base_game], "base game")

        item.watch(unwatch=True)

def cache_pages():
    """
    Download every steam page listed in `to_cache.txt` (Steam ID, number only, one per line),
    and save each of them them locally at "steam_cache/{steam_id}" file. They lately would be used
    at get_html() function.

    I personally used it to bypass regional restrictions: download steam pages via vpn, turn off
    the vpn, launch the wikidata bot.
    """
    for line in open("to_cache.txt"):
        steam_id = line.strip()
        try:
            SteamPagem(steam_id, bypass_cache=True).cache()
        except Exception as error:
            print("{}: {}".format(steam_id, error))

def remove_duplicates(id_list):
    """Remove Steam IDs that already set in some Wikidata items."""
    sparql = SparqlQuery()
    # TODO: split id_list to 1000 element chunks or whatever ?
    ok_items = sparql.select("""
        SELECT ?code WHERE {{
          VALUES ?code {{ {} }} .
          FILTER NOT EXISTS {{
            ?item wdt:P1733 ?code
          }}
        }}
    """.format(" ".join(["\"{}\"".format(steam_id) for steam_id in id_list])))
    # we can just return [el["code"] for el in ok_items], but we want to keep
    # original order and notify about every duplicate
    ok_items = { el["code"] for el in ok_items }

    result = []
    for steam_id in id_list:
        if steam_id in ok_items:
            result.append(steam_id)
        else:
            print("{}: duplicates existing item, skipped".format(steam_id))
    return result

def main(input_filename):
    # Remove duplicates and sort IDs
    q_list = []
    s_list = []
    for line in open(input_filename, encoding="utf-8"):
        line = line.strip();
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
        except Exception as error:
            print("{}: {}".format(item_id, error))

    # Create new items
    for steam_id in s_list:
        try:
            NewItemProcessor(steam_id).process()
        except Exception as error:
            print("{}: {}".format(steam_id, error))

def parse_item_page_arg(arg_value):
    if not re.match(r"^Q\d+$", arg_value):
        raise argparse.ArgumentTypeError
    return pywikibot.ItemPage(repo, arg_value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract various video game data from Steam based on Steam application ID.")
    parser.add_argument("input", help="A path to file with list of IDs of items to process (Qnnn) or or Steam IDs to be included in newly created items (just number). Mixed input is supported.")
    parser.add_argument("-publisher", "-p", type=parse_item_page_arg, nargs="+", action="store", dest="publishers", help="Wikidata element(s) to state in P123 (optional)")
    parser.add_argument("-genres", "-g", type=parse_item_page_arg, nargs="+", action="store", dest="genres", help="Wikidata element(s) to state in P136 (optional)")
    parser.add_argument("-developer", "-d", type=parse_item_page_arg, nargs="+", action="store", dest="developers", help="Wikidata element(s) to state in P178 (optional)")
    parser.add_argument("-series", "-s", type=parse_item_page_arg, action="store", dest="series", help="Wikidata element to state in P179 (optional)")
    parser.add_argument("-output", "-o", action="store", dest="output", help="A path to a file to fill with a list of IDs of the processed items, including newly created (optional)")

    arguments = parser.parse_args()
    if arguments.output:
        output = open(arguments.output, "w", encoding="utf-8")

    main(arguments.input)
