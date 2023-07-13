python steam_parser.py input.txt %* -o temp.txt

python seek_igdb_id.py temp.txt
python seek_rawg_id.py temp.txt
python seek_lutris_id_fast.py temp.txt

python seek_adventuregamers_id.py temp.txt
python seek_cooptimus_id.py temp.txt
python seek_hltb_id.py temp.txt
python seek_indiemag_id.py temp.txt
python seek_lutris_id.py temp.txt
python seek_mailru_id.py temp.txt
python seek_moddb_id.py temp.txt
python seek_pcgamingwiki_id.py temp.txt
python seek_riotpixels_id.py temp.txt
python seek_stopgame_id.py temp.txt
python seek_tuxdb_id.py temp.txt
python seek_uvl_id.py temp.txt

python seek_indiedb_id.py temp.txt
python qualify_uvl.py temp.txt

del temp.txt
