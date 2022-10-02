python steam_parser.py input.txt %* -o temp.txt
python seek_lutris_id.py temp.txt
python seek_mailru_id.py temp.txt
python seek_rawg_id.py temp.txt
python seek_hltb_id.py temp.txt
python seek_riotpixels_id.py temp.txt
del temp.txt