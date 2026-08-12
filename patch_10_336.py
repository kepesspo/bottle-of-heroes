# v10.336 - Beer Pong: a DONTO kulon pohar-szammal es MINDIG egy meccs,
#           + a bajnoksag vege utan nem jon tobbe push
#
# 1) A DONTO
#    A "Visszavago" kapcsolo szovege szerint MINDEN meccs ket menetes - a
#    megerosito gomb viszont az SE-agban a DONTOT is automatikusan ket menetre
#    bontotta. Mostantol a donto MINDIG egy meccs, es sajat pohar-szama van
#    (`finalCups`, alapbol = `maxCups`).
#
#    A donto felismerese NEM az, hogy "egy meccs van a korben": 3 jatekosnal a
#    0. kor is egy meccs (a harmadik szabadkartyat kap), utana viszont meg jon
#    a donto. Ezert azt is nezzuk, epult-e mar kovetkezo kor.
#
# 2) A PUSH A BAJNOKSAG UTAN
#    A nezo-kepernyo az ELSO pillanatkepnel is ertesitett: a feltetel
#    `!prev?.bpNotif` volt, `prev` pedig a szoba React-allapota, ami mountolaskor
#    meg `null`. Igy a szobaban ULO, REGI `bpNotif` minden megnyitaskor ujra
#    elsult - a bajnoksag vege utan is, amikor mar nincs kovetkezo meccs.
#    Ugyanez allt a `roundEvent`, `gameEvent` es `bpTimerAlert` esemenyekre is.
#
#    A javitas: az elso pillanatkepnel csak MEGJEGYEZZUK az idobelyegeket, nem
#    ertesitunk. Radasul a bajnoksag lezarasakor a ket beerpong-esemeny torlodik
#    is a szobabol.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1a. beallitas: kulon pohar-szam a dontoben ------------------------------
sub1(
"  const maxCups      = config.maxCups ?? 10;",
"""  const maxCups      = config.maxCups ?? 10;
  // A donto sajat pohar-szama. Alapbol UGYANANNYI, mint a tobbi meccse, igy
  // aki nem nyul hozza, semmit nem vesz eszre.
  const finalCups    = config.finalCups ?? maxCups;""",
'finalCups olvasas')

sub1(
"    { key:'maxCups',       label:'Poharak száma',    val:maxCups,       min:4, max:16, step:2 },\n",
"""    { key:'maxCups',       label:'Poharak száma',    val:maxCups,       min:4, max:16, step:2 },
    { key:'finalCups',     label:'Poharak a döntőben', val:finalCups, min:4, max:16, step:2,
      sub:'A döntő mindig egy meccs — visszavágó nélkül' },
""",
'finalCups sor')

# A felirat-markup KET helyen all a fajlban, ezert a kornyezetevel egyutt csere.
sub1(
"""        {numCfg.map(s => (
          <div key={s.key} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0', borderTop:'none' }}>
            <span style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{s.label}</span>""",
"""        {numCfg.map(s => (
          <div key={s.key} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'13px 0', borderTop:'none' }}>
            <div style={{ minWidth:0, paddingRight:10 }}>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{s.label}</div>
              {s.sub && <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>{s.sub}</div>}
            </div>""",
'numCfg sor felirat')

# --- 1b. a jatek: a donto felismerese es a kulon pohar-szam ------------------
sub1(
"  const MAX_CUPS = bpCfg.maxCups ?? 10;",
"""  const MAX_CUPS = bpCfg.maxCups ?? 10;
  const FINAL_CUPS = bpCfg.finalCups ?? MAX_CUPS;""",
'FINAL_CUPS')

sub1(
"""  const isSEFinals = VISSZAVAGO && (
    TOURNAMENT === 'se' ||
    (TOURNAMENT.startsWith('grp_') && tsPhase === 'finals' && finalsType === 'se')
  );""",
"""  // FIGYELEM a nevre: az `isSEFinals` azt jelenti, hogy EGYENES KIESESES agban
  // vagyunk ES be van kapcsolva a visszavago (minden meccs ket menetes). NEM
  // azt, hogy eppen a dontot jatsszuk - az az `isSEFinalMatch` lent.
  const seBracket = (
    TOURNAMENT === 'se' ||
    (TOURNAMENT.startsWith('grp_') && tsPhase === 'finals' && finalsType === 'se')
  );
  const isSEFinals = VISSZAVAGO && seBracket;
  // A DONTO: az utolso kor egyetlen meccse. Az "egy meccs van a korben"
  // onmagaban KEVES - 3 jatekosnal a 0. kor is egy meccs (a harmadik
  // szabadkartyat kap), utana viszont meg jon a donto. Ezert azt is nezzuk,
  // epult-e mar kovetkezo kor.
  const isSEFinalMatch = seBracket && !champion
    && (seRounds[seCurRound] || []).length === 1
    && !(seRounds[seCurRound + 1] && seRounds[seCurRound + 1].length);
  // A dontonek sajat pohar-szama lehet.
  const curMaxCups = isSEFinalMatch ? FINAL_CUPS : MAX_CUPS;""",
'isSEFinalMatch')

sub1(
"            <CupCounter value={cups1} onChange={setCups1} color={currentMatch.p1.color} max={MAX_CUPS} winning={cups1 > cups2} />",
"            <CupCounter value={cups1} onChange={setCups1} color={currentMatch.p1.color} max={curMaxCups} winning={cups1 > cups2} />",
'CupCounter 1')
sub1(
"            <CupCounter value={cups2} onChange={setCups2} color={currentMatch.p2.color} max={MAX_CUPS} winning={cups2 > cups1} />",
"            <CupCounter value={cups2} onChange={setCups2} color={currentMatch.p2.color} max={curMaxCups} winning={cups2 > cups1} />",
'CupCounter 2')

# --- 1c. a donto NEM kap automatikus visszavagot -----------------------------
sub1(
"""    const visszaApplies = VISSZAVAGO && (isSEFinals || isRRMode);
    const isVissza = visszaApplies && visszavagoUsedRef.current.has(matchKey);
    const visszaLabel = isVissza ? '⚔️ VISSZAVÁGÓ' : (visszaApplies ? '1. MECCS' : null);""",
"""    // A DONTO kimarad a ket menetbol - ott egy meccs dont.
    const visszaApplies = VISSZAVAGO && ((isSEFinals && !isSEFinalMatch) || isRRMode);
    const isVissza = visszaApplies && visszavagoUsedRef.current.has(matchKey);
    const visszaLabel = isSEFinalMatch ? '\U0001F3C6 DÖNTŐ'
      : isVissza ? '⚔️ VISSZAVÁGÓ' : (visszaApplies ? '1. MECCS' : null);""",
'visszaApplies')

sub1(
"            if (isSEFinals && !visszavagoUsedRef.current.has(seKey)) {",
"""            // A donto MINDIG egy meccs: nem bontjuk ket menetre akkor sem, ha a
            // "Visszavago" be van kapcsolva.
            if (isSEFinals && !isSEFinalMatch && !visszavagoUsedRef.current.has(seKey)) {""",
'confirm visszavago kapu')

# --- 2. a nezo-kepernyo: az ELSO pillanatkep nem ertesit ---------------------
sub1(
"""  const [obsRoundPopup, setObsRoundPopup] = React.useState(null);
  const [obsGameEvent, setObsGameEvent] = React.useState(null);""",
"""  const [obsRoundPopup, setObsRoundPopup] = React.useState(null);
  const [obsGameEvent, setObsGameEvent] = React.useState(null);
  // Az ELSO pillanatkep esemenyei REGIEK: a szobaban ott ul az utolso
  // `bpNotif` / `gameEvent` / `roundEvent`, a `prev` viszont mountolaskor meg
  // `null`, tehat a "valtozott-e?" feltetel igaz lenne. Igy minden megnyitas
  // ujra elsutotte az utolso ertesitest - a bajnoksag VEGE utan is, amikor mar
  // nincs kovetkezo meccs. Az elso pillanatkepnel csak megjegyezzuk oket.
  const seenEvtRef = React.useRef(null);""",
'seenEvtRef')

sub1(
"""          // Round popup event
          if (data.roundEvent && (!prev?.roundEvent || data.roundEvent.ts !== prev.roundEvent.ts)) {""",
"""          // Az elso pillanatkepnel csak jegyzunk, nem ertesitunk (lasd seenEvtRef).
          const _evtTs = k => (data[k] && data[k].ts) || null;
          const _first = seenEvtRef.current === null;
          const _seen = _first ? {} : seenEvtRef.current;
          const _fresh = k => !_first && _evtTs(k) !== null && _evtTs(k) !== _seen[k];
          seenEvtRef.current = { roundEvent:_evtTs('roundEvent'), gameEvent:_evtTs('gameEvent'),
                                 bpNotif:_evtTs('bpNotif'), bpTimerAlert:_evtTs('bpTimerAlert') };
          // Round popup event
          if (_fresh('roundEvent')) {""",
'roundEvent kapu')

sub1(
"""          // Game result event
          if (data.gameEvent && (!prev?.gameEvent || data.gameEvent.ts !== prev.gameEvent.ts)) {""",
"""          // Game result event
          if (_fresh('gameEvent')) {""",
'gameEvent kapu')

sub1(
"""          // Beer pong match notification
          if (data.bpNotif && (!prev?.bpNotif || data.bpNotif.ts !== prev.bpNotif.ts)) {""",
"""          // Beer pong match notification
          if (_fresh('bpNotif')) {""",
'bpNotif kapu')

sub1(
"""          // Beer pong 1 perces riasztás
          if (data.bpTimerAlert && (!prev?.bpTimerAlert || data.bpTimerAlert.ts !== prev.bpTimerAlert.ts)) {""",
"""          // Beer pong 1 perces riasztás
          if (_fresh('bpTimerAlert')) {""",
'bpTimerAlert kapu')

# --- 3. a bajnoksag lezarasakor a ket esemeny torlodik a szobabol ------------
sub1(
"""      champion: champion ? { id: champion.id, name: champion.name, color: champion.color } : null,
      drinkMap,
    }});""",
"""      champion: champion ? { id: champion.id, name: champion.name, color: champion.color } : null,
      drinkMap,
    }});
    // A bajnoksag lezarult: a fuggoben maradt ertesitesek TORLODNEK a szobabol.
    // Nelkuluk a "Kovetkezo meccs!" ott maradna a dokumentumban.
    if (champion) syncRoom(roomCode, { bpNotif: null, bpTimerAlert: null });""",
'esemeny-torles a vegen')

sub1("const APP_VERSION = 'v10.335';", "const APP_VERSION = 'v10.336';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_336 alkalmazva')
