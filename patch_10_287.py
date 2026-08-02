#!/usr/bin/env python3
# v10.287 — Szólánc: 10 kategória helyett 23
#
# Tiz kategorianal egy hosszabb buliban gyakran ismetlodott ugyanaz: a
# `listIdx` mountonkent veletlen, tehat mar ~4-5 Szolanc-kor utan borulekony,
# hogy visszajojjon egy mar latott lista. Huszonharommal ez erezhetoen ritkul.
#
# MINDEN UJ LISTA PONTOSAN 20 SZAVAS — ez nem eszteitka, hanem kovetelmeny:
# a `chainPool` `SZ_MAX_LEN` (=12) szot visz el, es a maradek a csalie. 20-nal
# ez 12 + 8, tehat a `decoysFor` nyolc kozul forog. Ha egy lista rovidebb lenne,
# a `Math.max(2, a.length - 3)` vagas ugyan megvedene a jatekot az osszeomlastol,
# de a lanc rovidebben erne veget, es a 12-es jackpot elerhetetlen lenne benne.
#
# A SZOHOSSZRA IS FIGYELNI KELLETT. A racs ketoszlopos: (402 − 32 − 10)/2 = 180 px
# egy chip, minusz 16 px belso margo → 164 px szoveghely 15 px-es felkover
# Nunitoval, ami durvan 20 karakter. A leghosszabb uj szo az "Amerika Kapitány"
# (16), tehat mindegyik befer egy sorba.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

UJ = """    { cat:'Testrészek 🖐️',  words:['fej','kéz','láb','orr','fül','szem','száj','váll','térd','könyök','hát','nyak','ujj','boka','csukló','homlok','áll','comb','sarok','tenyér'] },
    { cat:'Színek 🎨',       words:['piros','kék','zöld','sárga','fehér','fekete','barna','lila','rózsaszín','narancssárga','szürke','bordó','türkiz','arany','ezüst','bézs','olívzöld','mályva','korall','indigó'] },
    { cat:'Ruhadarabok 👕',  words:['póló','nadrág','zokni','cipő','kabát','sapka','sál','kesztyű','ing','szoknya','ruha','pulóver','öv','mellény','farmer','papucs','csizma','sort','kalap','nyakkendő'] },
    { cat:'Foglalkozások 👷', words:['orvos','tanár','pék','rendőr','tűzoltó','pilóta','szakács','fodrász','ügyvéd','mérnök','ápoló','asztalos','postás','könyvelő','újságíró','sofőr','kertész','fogorvos','pincér','villanyszerelő'] },
    { cat:'Bútorok 🪑',      words:['asztal','szék','ágy','szekrény','polc','kanapé','fotel','komód','tükör','lámpa','szőnyeg','függöny','íróasztal','könyvespolc','puff','zsámoly','pad','ágyneműtartó','dohányzóasztal','éjjeliszekrény'] },
    { cat:'Konyhai eszközök 🍴', words:['kés','villa','kanál','tányér','pohár','bögre','fazék','serpenyő','vágódeszka','reszelő','habverő','merőkanál','szűrő','tálca','nyújtófa','tepsi','keverőtál','kotyogó','mikró','konzervnyitó'] },
    { cat:'Országok 🗺️',     words:['Magyarország','Németország','Franciaország','Olaszország','Spanyolország','Ausztria','Horvátország','Szlovákia','Lengyelország','Görögország','Portugália','Hollandia','Belgium','Svédország','Norvégia','Dánia','Írország','Csehország','Szerbia','Románia'] },
    { cat:'Tantárgyak 📚',   words:['matek','magyar','töri','kémia','fizika','biológia','rajz','ének','földrajz','angol','német','irodalom','nyelvtan','filozófia','etika','technika','latin','francia','testnevelés','informatika'] },
    { cat:'Növények 🌿',     words:['rózsa','tulipán','kaktusz','pálma','fenyő','tölgy','nyír','juhar','levendula','bazsalikom','menta','rozmaring','orchidea','napraforgó','ibolya','jácint','borostyán','páfrány','muskátli','nárcisz'] },
    { cat:'Szuperhősök 🦸',  words:['Pókember','Batman','Superman','Vasember','Hulk','Thor','Deadpool','Rozsomák','Aquaman','Flash','Loki','Thanos','Robin','Sólyomszem','Zöld Lámpás','Fekete Özvegy','Fekete Párduc','Doctor Strange','Wonder Woman','Amerika Kapitány'] },
    { cat:'Márkák 🏷️',       words:['Nike','Adidas','Apple','Samsung','Pepsi','Google','Amazon','Sony','Puma','Reebok','IKEA','Zara','Lego','Nintendo','Netflix','Spotify','Microsoft','Gucci','Rolex','Coca-Cola'] },
    { cat:'Édességek 🍬',    words:['csoki','cukorka','fagyi','torta','keksz','gumicukor','nyalóka','muffin','croissant','marcipán','karamell','méz','tejberizs','puding','ostya','brownie','sajttorta','csokigolyó','mézeskalács','habcsók'] },
    { cat:'Időjárás ☀️',     words:['eső','hó','nap','szél','felhő','köd','vihar','villám','jégeső','szivárvány','fagy','hőség','pára','zápor','dér','harmat','monszun','hurrikán','tornádó','olvadás'] },
"""

sub("""    { cat:'Filmek 🎬',     words:['Titanic','Avatar','Inception','Matrix','Gladiátor','Interstellar','Joker','Avengers','Parasite','Tenet','Dune','Oppenheimer','Barbie','Top Gun','Ratatouille','Rocky','Alien','Shrek','Terminátor','Vasember'] },
  ];""",
    """    { cat:'Filmek 🎬',     words:['Titanic','Avatar','Inception','Matrix','Gladiátor','Interstellar','Joker','Avengers','Parasite','Tenet','Dune','Oppenheimer','Barbie','Top Gun','Ratatouille','Rocky','Alien','Shrek','Terminátor','Csillagok háborúja'] },
""" + UJ + """  ];""",
    'uj kategoriak')

sub("const APP_VERSION = 'v10.286';", "const APP_VERSION = 'v10.287';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 23 kategória')
