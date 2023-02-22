# Dependencies

## Pywikibot

All scripts are based on [Pywikibot framework](https://pywikibot.toolforge.org). You'll be required to install and configure it.

For quick start, install pywikibot via `pip install pywikibot`, then open the directory you've cloned this repository to and create `user-config.py` file with the following code:
```py
family = 'wikidata'
mylang = 'wikidata'
usernames['wikidata']['wikidata'] = 'YOUR_WIKIDATA_NICKNAME'
put_throttle = True
```
The script would ask you to type your password at the first lauch. For more sophisticated configuration, refer to [Pywikibot configuring manual](https://www.mediawiki.org/wiki/Manual:Pywikibot/user-config.py).

## Other dependencies

Some scripts might require additional dependencies or configuration:

- Scripts working with IGDB are based on [official Python wrapper for IGDB API](https://pypi.org/project/igdb-api-v4/). You will also need to register application at [Twitch Developer Portal](https://dev.twitch.tv/console/apps), get your API keys and place them at `keys/igdb-id.key` and `keys/igdb-secret.key` files.
- To use `seek_rawg_id.py`, you'll need to get [RAWG API key](https://rawg.io/apidocs) and place it at `keys/rawg.key`.
- `seek_hltb_id.py` is based on [howlongtobeatpy](https://pypi.org/project/howlongtobeatpy/).
