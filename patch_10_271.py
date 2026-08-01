#!/usr/bin/env python3
# v10.271 — EGY buntetes-fuggveny, es a korty-szam vegre atmegy a bannerbe
#
# A HIBA, AMIT JELEZTEL
#   Buntetes utan a result banner nem irta ki a korty-szamot. Az ok: az
#   `applyPenalty` `drinks` mezo NELKUL hivta az `onResult`-ot, tehat a
#   bannerben `drinks = 0` lett, es a v10.263 ota ervenyes szabaly
#   (`showMetric = kind === 'win' || drinks > 0`) elnyomta a szam-oszlopot.
#   A kiosztott mennyiseg csak a `loseNote` szovegeben jelent meg
#   ("Sere 2🍺, Luca 1🍺").
#
# A KET MEGVALOSITAS
#   Ugyanaz a funkcio — buntetes-korty kiosztasa jatekon kivul — ket helyen,
#   ketfele viselkedessel:
#     * MENU -> 🎲 Buntetes  (`applyPenalty`): fejenkent tetszoleges szam,
#       bannert nyitott, de korty-szam nelkul;
#     * Wildcard -> "Szabalyszego?" (`punishWildcard`): fix 1 korty, es
#       EGYALTALAN nem nyitott bannert, csak egy Toastot mutatott.
#   Ket kulon players-frissites, ket kulon szoba-szinkron, ket kulon hang.
#
# A JAVITAS: egyetlen `givePenalty(map, opts)`
#   Mindket ut ezt hivja. Egy helyen frissul a players tomb, egy helyen megy a
#   szoba-szinkron, egy helyen szol a hang (az `onResult`-ban, ahol amugy is).
#
# KET FONTOS RESZLET, AMI NELKUL A JAVITAS ROSSZ SZAMOT IRNA KI
#   1. A buntetes ABSZOLUT. A jatekos konkret kortyszamot valasztott, es
#      PONTOSAN annyi ment a players tombbe. Az `onResult` viszont minden
#      korty-szamot beszoroz (`d * diffDrinks * wcMult`) — extrem nehezsegen
#      egy 2 kortyos buntetesbol 10 lenne a bannerben, mikozben 2 ment a
#      jatekosra. Ezert kap az `onResult` egy `penalty` jelzot, ami kihagyja
#      a szorzast.
#   2. A "forditott kor" wildcard megcsereli a nyerteseket es a veszteseket.
#      Egy buntetesnel ez azt jelentene, hogy a szabalyszego a bannerben
#      NYERTESKENT jelenik meg. A `penalty` jelzo ezt a cseret is kihagyja —
#      a buntetes buntetes marad.
#
# MIT IR KI A BANNER
#   Ha mindenki UGYANANNYIT kapott (a tipikus eset: wildcard = 1 korty, vagy
#   a lapon mindenkinek ugyanannyi), van egyetlen igaz szam -> kiirjuk.
#   Ha fejenkent MAS, nincs olyan egy szam, ami igaz lenne (sem az osszeg, sem
#   barmelyik ertek), ezert marad a nevenkenti felsorolas — ugyanugy, mint a
#   Sohanem/Fingerit eseteben.
#
# A wcToast ezzel folosleges: a banner tobbet mutat (avatar, nev, korty-szam),
# mint a "X iszik 1-et!" sav. Kiszedjuk, hogy ne legyen ket ertesites egyszerre.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─────────────────────────────────────────────────────────────────────────────
# 1. onResult: a `penalty` jelzo kihagyja a szorzast ES a forditott-kor cseret
# ─────────────────────────────────────────────────────────────────────────────
sub("""    // Fordított kör: nyertes ↔ vesztes csere a bannerben (a nyertes iszik, a vesztes pontoz)
    if (wcEffect === 'reverse' && ((res.winners||[]).length || (res.losers||[]).length)) {""",
    """    // Fordított kör: nyertes ↔ vesztes csere a bannerben (a nyertes iszik, a vesztes pontoz).
    // BUNTETESRE NEM VONATKOZIK: ott a szabalyszego nyertesnek latszana. Lasd patch_10_271.py
    if (wcEffect === 'reverse' && !res.penalty && ((res.winners||[]).length || (res.losers||[]).length)) {""",
    'reverse kihagyas')

sub("""    const d = r.drinks ?? 0;
    const scaled = d > 0 ? d * diffDrinks * wcMult : 0;""",
    """    const d = r.drinks ?? 0;
    // A buntetes ABSZOLUT: pontosan ennyi korty ment a players tombbe, tehat
    // nem szabad ujra beszorozni a nehezseggel — kulonben a banner mast irna
    // ki, mint amennyit a jatekos tenylegesen kapott.
    const scaled = r.penalty ? d : (d > 0 ? d * diffDrinks * wcMult : 0);""",
    'penalty skalazas')

# ─────────────────────────────────────────────────────────────────────────────
# 2. Egyetlen kozos givePenalty — a ket regi ut helyett
# ─────────────────────────────────────────────────────────────────────────────
sub("""  const applyPenalty = (assigned) => {
    setPenaltyOpen(false);
    const map = assigned || {};
    const total = Object.values(map).reduce((s, v) => s + v, 0);
    if (!total) return;
    const upd = playersRef.current.map(p => (map[p.id] || 0) > 0 ? { ...p, drinks: (p.drinks || 0) + map[p.id] } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    // Fejenkent mas az osszeg, ezert nincs egyetlen kozos "drinks" szam —
    // a loseNote sorolja fel nevenkent, ugyanugy mint pl. a Sohanem/Fingerit.
    const drinkers = upd.filter(p => (map[p.id] || 0) > 0);
    onResult({ losers: drinkers, loseNote: drinkers.map(p => `${p.name} ${map[p.id]}🍺`).join(', ') });
  };""",
    """  // ── EGY buntetes-fuggveny, ket belepovel (v10.271) ──
  // Korabban a MENÜ->Buntetes es a Wildcard->"Szabalyszego?" ket kulon
  // implementacio volt: mas players-frissites, mas szinkron, mas hang, es az
  // egyik bannert nyitott korty-szam nelkul, a masik csak Toastot mutatott.
  // `map`  : { playerId: korty }  — MINDIG abszolut szam
  // `opts` : { note } — a banner alatti rovid jegyzet
  const givePenalty = (map, opts) => {
    const m = map || {};
    const total = Object.values(m).reduce((s, v) => s + v, 0);
    if (!total) return;
    const upd = playersRef.current.map(p => (m[p.id] || 0) > 0 ? { ...p, drinks: (p.drinks || 0) + m[p.id] } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    const drinkers = upd.filter(p => (m[p.id] || 0) > 0);
    // Ha mindenki UGYANANNYIT kapott, van egyetlen igaz szam -> a banner
    // kiirja. Ha fejenkent mas, nincs olyan EGY szam, ami igaz lenne (sem az
    // osszeg, sem barmelyik ertek), ezert marad a nevenkenti felsorolas.
    const amounts = drinkers.map(p => m[p.id]);
    const uniform = amounts.length > 0 && amounts.every(v => v === amounts[0]);
    onResult({
      losers: drinkers,
      drinks: uniform ? amounts[0] : 0,
      penalty: true,   // abszolut szam: se nehezseg-szorzo, se forditott-kor csere
      loseNote: uniform ? (opts && opts.note ? opts.note : '')
                        : drinkers.map(p => `${p.name} ${m[p.id]}🍺`).join(', '),
    });
  };

  const applyPenalty = (assigned) => {
    setPenaltyOpen(false);
    givePenalty(assigned, { note: 'Büntetés' });
  };""",
    'givePenalty')

# ─────────────────────────────────────────────────────────────────────────────
# 3. punishWildcard: ugyanaz az ut, csak fix 1 korty
# ─────────────────────────────────────────────────────────────────────────────
sub("""  const punishWildcard = (pid) => {
    const upd = playersRef.current.map(p => p.id === pid ? { ...p, drinks: (p.drinks || 0) + 1 } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    const pl = upd.find(p => p.id === pid);
    setWcPunishOpen(false);
    setWcToast({ name: pl ? pl.name : '?' });
    setTimeout(() => setWcToast(null), 2000);
    try { if (typeof window.bohSound === 'function') window.bohSound('lose'); } catch(e) {}
  };""",
    """  // A szabalyszeges is buntetes — ugyanazt az utat jarja, csak fix 1 kortyot
  // oszt. A regi kulon Toast helyett ugyanugy a result banner jon, ami tobbet
  // mutat: avatar, nev, korty-szam. Lasd patch_10_271.py
  const punishWildcard = (pid) => {
    setWcPunishOpen(false);
    givePenalty({ [pid]: 1 }, { note: 'Szabályszegés' });
  };""",
    'punishWildcard')

# ─────────────────────────────────────────────────────────────────────────────
# 4. A wcToast folosleges — a banner tobbet mutat nala
# ─────────────────────────────────────────────────────────────────────────────
sub("""  const [wcToast, setWcToast] = useState(null); // {name}
""", "", 'wcToast state')

sub("""      {wcToast && (
        <Toast>{wcToast.name} iszik 1-et! <BohIcon name="beer" size={16} /></Toast>
      )}
""", "", 'wcToast render')

sub("const APP_VERSION = 'v10.270';", "const APP_VERSION = 'v10.271';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — egy givePenalty, a korty-szam atmegy a bannerbe')
