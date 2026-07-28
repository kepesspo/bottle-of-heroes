# v10.178 — a negy hianyzo jatek-banner
#
# Negy jateknak nem volt bannere: erem, tabu, reakcio, szamsor. A fejlecben
# ezert a tartalek jelent meg (ikon + szoveg), mig a masik 41 jatek banner-kepet
# kapott — ranezesre ugy tunt, mintha rossz kep jonne fel.
#
# A kepek a meglevok stilusaban keszultek (make_banners.py): 800x120, atlatszo
# hatter, Nunito 900 sotetkek #1F3048, #EF8A6D arnyek 6 px-el, balra a jatek
# sajat ikonja. A betutipus a projekt sajat woff2-jebol jon, tehat pontosan az,
# amit az app is hasznal.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── IMGS bejegyzesek ──
anchor = "  'reakcio_icon.png': 'assets/reakcio_icon.png',"
assert s.count(anchor) == 1
s = s.replace(anchor, "\n".join(
    "  '%s_banner.png': 'assets/%s_banner.png'," % (g, g)
    for g in ['erem', 'tabu', 'reakcio', 'szamsor']) + "\n" + anchor)

# ── a jatek-definiciokba a banner mezo, az img melle ──
for gid in ['erem', 'tabu', 'reakcio', 'szamsor']:
    i = s.index("{ id:'%s'," % gid)
    j = s.index("\n", i)
    line = s[i:j]
    assert 'banner:' not in line, gid
    key = "img:IMGS['%s_icon.png']," % gid
    assert line.count(key) == 1, (gid, line[:120])
    s = s[:i] + line.replace(key, key + " banner:IMGS['%s_banner.png']," % gid) + s[j:]

s = s.replace("const APP_VERSION = 'v10.177';", "const APP_VERSION = 'v10.178';", 1)
assert "v10.178" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — 4 banner bekotve')
