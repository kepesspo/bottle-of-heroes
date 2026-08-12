# v10.341 - A wildcard-sav „Szabalyszego?" gombja MARAD, pontgyujtes nelkul is
#
# A v10.338-ban a MENU -> Buntetes gombbal EGYUTT ezt is elrejtettem, mert
# ugyanazt a `PenaltyModal`-t nyitja. A tulajdonos donteset koveti a javitas:
# a wildcard-savi belepo maradjon, mert kezreesobb, mint a menuben turkalni.
#
# A menubeli gomb TOVABBRA IS kimarad pontgyujtes nelkul — igy EGY belepo van,
# a kenyelmes.
#
# ⚠️ EBBOL KOVETKEZIK a banner-kapu finomitasa. A v10.338 pontgyujtes nelkul
# MINDEN eredmeny-bannert elnyelt. Ha a gomb marad, de a banner nem jon,
# a jatekos megnyomja, kioszt harom kortyot — es SEMMI visszajelzest nem kap.
# Ezert a kapu mostantol csak a JATEK-eredmenyeket nyeli el: a buntetes
# (`res.penalty`) atmegy, mert az tenylegesen megtortent es tenylegesen ir a
# jatekosokra. Egy jatek-kor viszont pontgyujtes nelkul nem konyvel semmit,
# tehat ott tovabbra sincs mit hirdetni.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1. a gomb visszaal ------------------------------------------------------
sub1(
"""            {/* Ugyanazt a `PenaltyModal`-t nyitja, mint a MENU -> Buntetes,
                tehat pontgyujtes nelkul ugyanugy kimarad. */}
            {trackScores && (
            <button onClick={() => setWcPunishOpen(true)}""",
"""            {/* Ez a belepo pontgyujtes nelkul IS kint marad: kezreesobb, mint a
                menuben turkalni. A menubeli „Buntetes" gomb ilyenkor kimarad,
                tehat EGY belepo van — a kenyelmes. */}
            <button onClick={() => setWcPunishOpen(true)}""",
'szabalyszego gomb vissza')

sub1(
"""              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>
            )}""",
"""              <BohIcon name="beer" size={13} />Szabályszegő?
            </button>""",
'szabalyszego gomb zaras')

# --- 2. a banner-kapu: a BUNTETES atmegy ------------------------------------
sub1(
"""    // Pontgyujtes nelkul nincs mit hirdetni: a `trackScores` hamis, tehat a
    // konyveles meg sem tortenik. A banner "+1 pont"-ot es korty-szamot igerne,
    // amibol semmi nem kerul fel. A kapu ITT van, es nem lentebb: igy a hang, a
    // konfetti es a nezoknek kuldott `gameEvent` is elmarad.
    if (!trackScores) { setGameResult(null); return; }""",
"""    // Pontgyujtes nelkul a JATEK-korok nem konyvelnek semmit, tehat nincs mit
    // hirdetni: a banner "+1 pont"-ot es korty-szamot igerne, amibol semmi nem
    // kerul fel. A kapu ITT van, es nem lentebb: igy a hang, a konfetti es a
    // nezoknek kuldott `gameEvent` is elmarad.
    //
    // ⚠️ A BUNTETES KIVETEL. Az `givePenalty` a `trackScores`-tol fuggetlenul
    // ir a jatekosokra, es a wildcard-savi „Szabalyszego?" belepo pontgyujtes
    // nelkul is kint van. Banner nelkul a jatekos kiosztana harom kortyot, es
    // semmi visszajelzest nem kapna rola.
    if (!trackScores && !res.penalty) { setGameResult(null); return; }""",
'banner kapu finomitas')

sub1("const APP_VERSION = 'v10.340';", "const APP_VERSION = 'v10.341';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_341 alkalmazva')
