python steam_parser.py input.txt %* -o temp.txt
python lutris_seek_id.py temp.txt
python mailru_seek_id.py temp.txt
python rawg_seek_id.py 1 temp.txt
python hltb_seek_id.py temp.txt
python riotpixels_seek_id.py temp.txt
del temp.txt