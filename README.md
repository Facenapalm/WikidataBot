# Dependencies

## Pywikibot

All scripts are written in Python 3 and based on [Pywikibot framework](https://pywikibot.toolforge.org). You'll be required to install and configure it.

For quick start, install pywikibot via `pip install pywikibot`, then open the directory you've cloned this repository to and create `user-config.py` file with the following code:
```py
family = 'wikidata'
mylang = 'wikidata'
usernames['wikidata']['wikidata'] = 'YOUR_WIKIDATA_NICKNAME'
put_throttle = True
```
The script would ask you to type your password at the first launch. For more sophisticated configuration, refer to [Pywikibot configuring manual](https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py).

## Other Dependencies

Some scripts might require additional dependencies or configuration:

- Scripts working with IGDB are based on [official Python wrapper for IGDB API](https://pypi.org/project/igdb-api-v4/). You will also need to register application at [Twitch Developer Portal](https://dev.twitch.tv/console/apps), get your API keys and place them at `keys/igdb-id.key` and `keys/igdb-secret.key` files.
- To use `seek_rawg_id.py`, you'll need to get [RAWG API key](https://rawg.io/apidocs) and place it at `keys/rawg.key`.
- `seek_hltb_id.py` is based on [howlongtobeatpy](https://pypi.org/project/howlongtobeatpy/).

# Scripts
All `*.py` scripts in root directory are separate bots built for specific task. To get more information about particular bot, launch it with `-h` key, for instance:
```
python steam_parser.py -h
```
`common` directory contains auxiliary modules that are not designed to be launched separately.

## Steam Parser
The `steam_parser.py` script is creating new items ([sample](https://www.wikidata.org/w/index.php?oldid=1605017234)) and filling in existing ones ([sample](https://www.wikidata.org/w/index.php?diff=1605678995&oldid=1575252496)) based on Steam application ID (P1733).

This script requires input file passed as the first positional argument. Input file should contain IDs of items to process (Qnnn) or Steam application IDs to be included in newly created items (just number), one per line. Mixed input is supported. Example input file:
```
220
440
Q4115189
```

The script does not set developer, publisher, series and genres. However, if you're processing the series of similar games, you can pass them as named arguments. For instance, `-developer Q193559` would set Valve (Q193559) as a developer for each processed or created item. Launch the script with `-h` key to get the list of available arguments.

`-o [filename]` key would create a file and fill it with a list of processed or created item IDs. You can later use it in other bots, e. g. [ID Seekers](#id-seekers).

## ID Seekers

The `seek_xxx_id.py` scripts are connecting Wikidata items with given database based on matching external identifiers. For instance, `seek_stopgame_id.py` would connect Wikidata item with StopGame.ru entry if both of these are linked with the same Steam application.

Generally the algorithm of these scripts is the following (see [common/seek_basis.py](https://github.com/Facenapalm/WikidataBot/blob/main/common/seek_basis.py)):
1. Make a search request to a database using item label or alias as a query.
2. Parse each found entry to get external links it contains.
3. If there's a match between entry's external link and item's external ID, link this entry to the item.

Usage:
```
python seek_xxx_id.py %input_source% %base_property%
```
- If `%input_source%` equals `all`, the script would make a SPARQL request and process all the items that contain `%base_property%` and do not contain desired database link. Otherwise it treated as a path to file with list of item IDs to process (Qnnn, one per line).
- `%base_property%` is the property ID (Pnnn) that would be used as an matching property.
- Use `-h` key to get information about specific script, including the list of supported base properties.

Most of the scripts are supporting Steam application ID (P1733) as the base property. That in combination with [steam_parser.py](#steam-parser) allows user to create well filled items with minimal effort. [steam.bat](https://github.com/Facenapalm/WikidataBot/blob/main/steam.bat) is an example batch file that creates items for Steam application IDs listed in `input.txt` file.

## Other Scripts
- `qualify_xxx.py` is a set of bots that are adding required qualifiers (usually platform, P400) to certain external ID.
- `igdb_check_slugs.py` processes changed and deprecates withdrawn IGDB slugs (P5794) based on IGDB numeric ID (P9043) qualifier.
- `ogdb_extract_country.py` adds country of origin (P495) based on OGDB ID (P7564).
- `esportsearnings_extract_discipline.py` adds sports discipline competed in (P2416) based on Esports Earnings player ID (P10803).

# Licensing
All scripts are licensed under the terms of [MIT license](https://opensource.org/license/mit/). You're free to use, modify and distribute the scripts any way you want.
