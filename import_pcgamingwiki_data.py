import re
import requests
import pywikibot
from common.import_basis import DataImporterBot

"""
Add genre (P136) and some other data based on PCGamingWiki ID (P6337).
"""

class PCGamingWikiPage():
    def __init__(self, slug):
        params = {
            'action': 'query',
            'prop': 'revisions',
            'titles': slug,
            'rvslots': '*',
            'rvprop': 'content',
            'format': 'json',
            'formatversion': 2,
        }
        response = requests.get('https://www.pcgamingwiki.com/w/api.php', params=params)
        try:
            page = response.json()['query']['pages'][0]

            self.slug = slug
            self.pageid = page['pageid']
            self.content = page['revisions'][0]['slots']['main']['content']
        except Exception:
            raise RuntimeError(f"couldn't get `{slug}` content")

    @staticmethod
    def from_steam_appid(appid):
        params = { 'appid': appid }
        response = requests.get('https://www.pcgamingwiki.com/api/appid.php', params=params)
        html = response.text
        if "No such AppID" in html:
            raise RuntimeError(f'no PCGamingWiki entries are linked to Steam application ID `{appid}`')

        match = re.match(r'https?://www\.pcgamingwiki\.com/wiki/(\S+)$', response.url)
        if not match:
            raise RuntimeError(f'unknown link format `{response.url}` (linked to Steam application ID `{appid}`)')

        return PCGamingWikiPage(match.group(1))

    def get_slug(self):
        return self.slug

    def get_page_id(self):
        return self.pageid

    def get_engines(self):
        return re.findall(r'\{\{\s*[Ii]nfobox game/row/engine\s*\|(\s*[^\}\|]+?\s*)(?:\|[^\}]+)?\}\}', self.content)

    def get_game_modes(self):
        result = []
        match = re.search(r'\{\{\s*[Ii]nfobox game/row/taxonomy/modes\s*\|(\s*[^\}\|]+?\s*)\}\}', self.content)
        if match:
            for entry in match.group(1).split(','):
                entry = entry.strip()
                if entry:
                    result.append(entry)
        return result

    def get_genres(self):
        result = []
        match = re.search(r'\{\{\s*[Ii]nfobox game/row/taxonomy/genres\s*\|(\s*[^\}\|]+?\s*)\}\}', self.content)
        if match:
            for entry in match.group(1).split(','):
                entry = entry.strip()
                if entry:
                    result.append(entry)
        return result

class PCGamingWikiBot(DataImporterBot):
    def __init__(self):
        super().__init__(
            prop='P6337',
            query_constraints=['?item wdt:P31/wdt:P279* wd:Q7889 .'],
        )

        def get_item(x): return pywikibot.ItemPage(self.repo, x)
        self.modes_map = {
            'singleplayer': get_item('Q208850'),
            'single-player': get_item('Q208850'),
            'multiplayer': get_item('Q6895044'),
        }
        self.genres_map = {
            # 'exploration': None, # not a genre?
            # 'open world': get_item('Q867123'), # not a genre?
            # 'quick time events': get_item('Q1392636'), # not a genre?

            '4x': get_item('Q603555'),
            'action': get_item('Q270948'),
            'adventure': get_item('Q23916'),
            'arcade': get_item('Q15613992'),
            'arpg': get_item('Q1422746'),
            'artillery': get_item('Q122207'),
            'battle royale': get_item('Q30607131'),
            'board': get_item('Q19272838'),
            'brawler': get_item('Q401831'),
            'building': get_item('Q588289'),
            'business': get_item('Q1198141'),
            'card/tile': get_item('Q29471320'),
            'ccg': get_item('Q48997688'),
            'chess': get_item('Q71679871'),
            'clicker': get_item('Q126394863'),
            'dating': get_item('Q1339223'),
            'driving': get_item('Q116680021'),
            'educational': get_item('Q1140363'),
            'endless runner': get_item('Q57775833'),
            'falling block': get_item('Q10308060'),
            'farming': get_item('Q111149309'),
            'fighting': get_item('Q846224'),
            'fps': get_item('Q185029'),
            'gambling/casino': get_item('Q60617897'),
            'hack and slash': get_item('Q1163960'),
            'hidden object': get_item('Q25377002'),
            'hunting': get_item('Q71474253'),
            'idle': get_item('Q18351283'),
            'immersive sim': get_item('Q30680823'),
            'interactive book': get_item('Q1143118'),
            'jrpg': get_item('Q5923834'),
            'life sim': get_item('Q1199309'),
            'mental training': get_item('Q17232662'),
            'metroidvania': get_item('Q19643088'),
            'mini-games': get_item('Q126598654'),
            'mmo': get_item('Q862490'),
            'mmorpg': get_item('Q175173'),
            'music/rhythm': get_item('Q2632782'), # = Q584105?
                  'rhythm': get_item('Q2632782'),
            'paddle': get_item('Q2941225'),
            'party game': get_item('Q7888616'),
            'pinball': get_item('Q3177954'),
            'platform': get_item('Q828322'),
            'puzzle': get_item('Q54767'),
            'racing': get_item('Q860750'),
            'rail shooter': get_item('Q2127647'),
            'roguelike': get_item('Q1143132'),
            'rolling ball': get_item('Q121769643'),
            'rpg': get_item('Q744038'),
            'rts': get_item('Q208189'),
            'sandbox': get_item('Q25397095'),
            'shooter': get_item('Q4282636'),
            'simulation': get_item('Q1610017'),
            'sports': get_item('Q868217'),
            'stealth': get_item('Q858523'),
            'strategy': get_item('Q1150710'),
            'survival': get_item('Q21030988'),
            'survival horror': get_item('Q333967'),
            'tactical rpg': get_item('Q1529437'),
            'tactical shooter': get_item('Q1260861'),
            'tbs': get_item('Q2176159'),
            'text adventure': get_item('Q126393551'),
            'tile matching': get_item('Q7802107'),
            'time management': get_item('Q18822231'),
            'tower defense': get_item('Q1137896'),
            'tps': get_item('Q380266'),
            'tricks': get_item('Q126652372'),
            'trivia/quiz': get_item('Q60617948'),
            'vehicle combat': get_item('Q2070892'),
            'vehicle simulator': get_item('Q578868'),
            'visual novel': get_item('Q689445'),
            'wargame': get_item('Q2454898'),
            'word': get_item('Q15220419'),
        }

    def parse_entry(self, entry_id):
        result = {}
        page = PCGamingWikiPage(entry_id)

        def apply_mapping(prop, mapping, array, label):
            new_array = [mapping.get(item.lower()) for item in array]
            if None in new_array:
                for i, value in enumerate(new_array):
                    if value is None:
                        print(f'{entry_id}: {label} `{array[i]}` not in mapping')
            elif new_array:
                result[prop] = new_array

        apply_mapping('P404', self.modes_map, page.get_game_modes(), 'game mode')
        apply_mapping('P136', self.genres_map, page.get_genres(), 'genre')
        return result

if __name__ == '__main__':
    PCGamingWikiBot().run()
