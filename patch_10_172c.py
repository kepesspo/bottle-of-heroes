# v10.172 (c) — a wildcard szovegek athangolasa
#
# Harom szoveg szo szerint "ezen a koron"-t mond. A wildcard mar eddig sem egy
# korre szolt (a kovetkezoig ervenyben maradt), percalapon pedig ez vegkepp
# felrevezeto: a szabaly egy IDOSZAKRA szol, amig le nem valtja a kovetkezo.
#
# A "kor" NEVEK maradnak (Fordított kör, Dupla kör...): azok a lap nevei, nem
# allitasok az idotartamrol.
#
# FONTOS: a wildcardok adminbol szerkesztheto lista (config/wildcards). Ez itt
# csak az ALAPERTELMEZEST irja at — akinek mentett sajat listaja van, annak az
# Adminban a "visszaallitas" gombbal jon at, vagy kezzel.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

FIX = [
    ("text:'Bal kézzel kell inni ezen a körön!'",
     "text:'Bal kézzel kell inni, amíg ez a lap érvényben van!'"),
    ("text:'Csak szavak nélkül lehet kommunikálni ezen a körön!'",
     "text:'Csak szavak nélkül lehet kommunikálni, amíg ez a lap érvényben van!'"),
    ("text:'Hangos kör — mindent hangosan kell mondani ezen a körön!'",
     "text:'Hangos kör — mindent hangosan kell mondani, amíg ez a lap érvényben van!'"),
]
for old, new in FIX:
    assert s.count(old) == 1, old[:50]
    s = s.replace(old, new)

assert 'ezen a körön' not in s, 'maradt "ezen a körön"'
s = s.replace("const APP_VERSION = 'v10.171';", "const APP_VERSION = 'v10.172';", 1)
assert "v10.172" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — 3 szoveg athangolva')
