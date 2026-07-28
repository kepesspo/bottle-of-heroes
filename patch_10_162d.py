# v10.162 (d) — a v10.160-ban feleslegesen hozzaadott fogaskerek visszavonasa
#
# A v10.160-ban azt allapitottam meg, hogy a jatek-beallitasok csak hosszu
# nyomasra nyilnak es semmi nem jelzi oket. EZ TEVEDES VOLT: mind a harom
# csempen ott van mar egy lila CERUZA-gomb ugyanerre, `onLongPress &&`
# feltetellel. Tul szuk ablakban kerestem (a NetflixTile elso 60 sora), a
# ceruza pedig lejjebb van.
#
# Igy a ConfigDot egy MASODIK, ugyanoda kerulo gomb lett — a kepen a ket kor
# egymasra is csuszott. A fogaskerek megy, marad az eredeti ceruza.
#
# Ami a v10.160-bol ERVENYES marad: a beallithato jatekok listaja harom kulon
# ternaryban volt, es a kedvencek-sorban csak negy szerepelt a hetbol. Vagyis
# a ceruza harom jateknal (kisebb, collect, ovfj) tenyleg hianyzott — azt a
# GAME_CONFIG_DEFS javitotta, es az megmarad.
import io, re

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# a ConfigDot komponens
i = s.find('// A kartyan ulo fogaskerek.')
assert i > 0, 'nincs meg a ConfigDot komment'
j = s.find('\n}\n', s.find('function ConfigDot(', i)) + len('\n}\n')
assert j > i
s = s[:i] + s[j:].lstrip('\n')

# a harom hasznalat
n = len(re.findall(r'^\s*<ConfigDot [^>]*/>\n', s, re.M))
assert n == 3, f'ConfigDot hasznalat: {n} (3 kellene)'
s = re.sub(r'^\s*<ConfigDot [^>]*/>\n', '', s, flags=re.M)
assert 'ConfigDot' not in s

# a MAR MEGLEVO ceruza-gombok kapjanak aria-label-t: eddig semmi nem azonositotta
# oket, ezert tudott egy masodik gomb eszrevetlenul melle kerulni
n2 = s.count("<button onClick={e => { e.stopPropagation(); onLongPress(); }} style={{")
assert n2 == 3, f'ceruza-gomb: {n2} (3 kellene)'
s = s.replace("<button onClick={e => { e.stopPropagation(); onLongPress(); }} style={{",
              "<button aria-label=\"Beállítások\" onClick={e => { e.stopPropagation(); onLongPress(); }} style={{")

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — fogaskerek visszavonva, az eredeti ceruza kapott aria-label-t')
