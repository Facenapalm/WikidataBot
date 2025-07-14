# Copyright (c) 2025 Facenapalm
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
    ("pt", "videojogo", "videojogo de {}"),
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
