python steam_parser.py input.txt %* -o temp_steam.txt

python seek_rawg_id.py temp_steam.txt

python seek_igdb_id.py temp_steam.txt -o temp_igdb.txt
python seek_lutris_id_fast.py temp_igdb.txt
del temp_igdb.txt

python seek_pcgamingwiki_id.py temp_steam.txt -o temp_pgw.txt
python import_pcgamingwiki_data.py temp_pgw.txt
del temp_pgw.txt

python seek_moddb_id.py temp_steam.txt -o temp_moddb.txt
python seek_indiedb_id.py temp_moddb.txt
del temp_moddb.txt

python seek_uvl_id.py temp_steam.txt -o temp_uvl.txt
python qualify_uvl.py temp_uvl.txt
del temp_uvl.txt

python seek_adventuregamers_id.py temp_steam.txt
python seek_cooptimus_id.py temp_steam.txt
python seek_hltb_id.py temp_steam.txt
python seek_indiemag_id.py temp_steam.txt
python seek_lutris_id.py temp_steam.txt
python seek_mobygames_id.py temp_steam.txt
python seek_playground_id.py temp_steam.txt
python seek_riotpixels_id.py temp_steam.txt
python seek_steamgriddb_id.py temp_steam.txt
python seek_stopgame_id.py temp_steam.txt
python seek_tuxdb_id.py temp_steam.txt
python seek_vgtimes_id.py temp_steam.txt
python seek_vkplay_id.py temp_steam.txt

del temp_steam.txt
