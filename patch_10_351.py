# v10.351 - A „Ne ugyanazt!" sajat ikont kap: a BANNER rajzat
#
# A jatek eddig ikon (`img`) nelkul volt felveve, tehat a kartyan es a
# jatekvalasztoban az EMOJI-tartalek (🙊) latszott — mas rajz, mint a banner
# ket buborekja. Innentol a ket felulet ugyanazt a kepet viszi.
#
# ⚠️ Az ikon nem a bannerbol van KIVAGVA: ott a rajz mindossze 127x93 px, egy
# 512-es ikonna nagyitva elmosodna. A `make_neugyanazt_icon.py` UJRARAJZOLJA
# ugyanazokkal a mert aranyokkal es szinekkel (#1A2A4A / #F08060), ikon-
# felbontason — igy a ket rajz nem tud elcsuszni egymastol.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

sub1("""  'neugyanazt_banner.png': 'assets/neugyanazt_banner.png',""",
     """  'neugyanazt_banner.png': 'assets/neugyanazt_banner.png',
  // A banner ket buborekja, ikon-felbontason ujrarajzolva
  // (`make_neugyanazt_icon.py`) — nem kivagas, mert a bannerben csak 127x93 px.
  'neugyanazt_icon.png': 'assets/neugyanazt_icon.png',""",
     'IMGS bejegyzes')

sub1("""category:'Páros',  emoji:'🙊', banner:IMGS['neugyanazt_banner.png'],""",
     """category:'Páros',  emoji:'🙊', img:IMGS['neugyanazt_icon.png'], banner:IMGS['neugyanazt_banner.png'],""",
     'GAMES img mezo')

sub1("const APP_VERSION = 'v10.350';", "const APP_VERSION = 'v10.351';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_351 alkalmazva')
