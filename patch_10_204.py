#!/usr/bin/env python3
# v10.204 — Koccintó ki, Büntetés = korty-kiosztó
#
# 1) A Koccintó kikerül. Egy generált köszöntőt olvasott fel, sosem hasznaltuk.
#
# 2) A Büntetés eddig egy VELETLEN buntetes-szoveget dobott fel ("igyál bal
#    kézzel" stb.), amit senki nem tudott hova tenni: nem lehetett megmondani,
#    KI rontott, es semmi nyoma nem maradt. Mostantol a gomb egy korty-kiosztot
#    nyit — kivalasztod, ki mennyit iszik, es az bekerul az alsó allasba, tehat
#    a parti vegen a statisztikaba is.
#
#    Ez a wildcardhoz kell igazan: ott a jatekon KIVUL ront valaki (bal kezzel
#    ivott, kimondta a tiltott szot), es eddig ezt sehol nem lehetett rogziteni.
#
# A veletlen buntetes-lista (Admin > Büntetés) igy hasznalat nelkul marad —
# nem torlom, mert lehet, hogy mas celra kell, de mar semmi nem olvassa.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ─── 1) A ket menugomb helyere EGY gomb ───
sub("""                {/* Koccintó — köszöntő generátor + TTS felolvasás */}
                <button onClick={() => { setShowMenu(false); fireToast(); }} style={{ width:'100%', height:50, border:'none', borderRadius:16, background:`linear-gradient(135deg, ${T.yellow}, ${T.coral})`, color:'#1A2A4A', fontFamily:T.font, fontWeight:900, fontSize:14.5, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:`0 4px 14px ${T.coral}44` }}>
                  <span style={{ fontSize:18, lineHeight:1 }}>🥂</span><span>Koccintó — mondj egy köszöntőt!</span>
                </button>

                {/* Büntetés — random büntetés a nem teljesített feladatokhoz, admin szerkeszthető lista */}
                <button onClick={() => { setShowMenu(false); firePunishment(); }} style={{ width:'100%', height:50, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14.5, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                  <span style={{ fontSize:18, lineHeight:1 }}>🎲</span><span>Büntetés — ki nem teljesített?</span>
                </button>""",
    """                {/* Büntetés — korty kiosztása játékon kívül (wildcard-szegés,
                    fogadás, bármi). Az itt kiosztott korty ugyanoda kerül, mint
                    a játékban szerzett, tehát a parti végén a statisztikába is. */}
                <button onClick={() => { setShowMenu(false); setPenaltyOpen(true); }} style={{ width:'100%', height:50, border:'none', borderRadius:16, background:`linear-gradient(135deg, #7C5CC4, #A78BFA)`, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14.5, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8, boxShadow:'0 4px 14px rgba(124,92,196,0.44)' }}>
                  <BohIcon name="beer" size={18} /><span>Büntetés — ki igyon?</span>
                </button>""",
    'menugombok')

# ─── 2) allapot + kiosztas ───
sub("""  const [punishment, setPunishment] = useState(null); // {emoji, text}
  const firePunishment = () => {
    const pool = PUNISHMENTS.length ? PUNISHMENTS : PUNISHMENTS_DEFAULT;
    const pick = pool[Math.floor(Math.random() * pool.length)];
    setPunishment(pick);
  };""",
    """  // Büntetés: korty kiosztása kézzel, játékon kívül. A korty a players
  // tömbbe kerül, onnan a parti végén magától a statisztikába megy — nem
  // logolunk külön, mert az duplán számolna.
  const [penaltyOpen, setPenaltyOpen] = useState(false);
  const applyPenalty = (assigned) => {
    setPenaltyOpen(false);
    const map = assigned || {};
    const total = Object.values(map).reduce((s, v) => s + v, 0);
    if (!total) return;
    const upd = playersRef.current.map(p => (map[p.id] || 0) > 0 ? { ...p, drinks: (p.drinks || 0) + map[p.id] } : p);
    setPlayers(upd);
    if (roomCode && typeof syncRoom === 'function') syncRoom(roomCode, { players: upd, turn, gameIdx, round });
    const names = upd.filter(p => (map[p.id] || 0) > 0).map(p => `${p.name} ${map[p.id]}`).join(' · ');
    setWcToast({ name: names, penalty: true });
    setTimeout(() => setWcToast(null), 2600);
    try { if (typeof window.bohSound === 'function') window.bohSound('lose'); } catch (e) {}
  };""",
    'allapot')

# ─── 3) a modalok cserejе ───
sub("""      {toastText && (
        <ActionModal onClose={() => setToastText(null)} kicker="Koccintó 🥂" onSecondary={fireToast} onPrimary={() => setToastText(null)} primaryLabel="Egészségünkre!">
          {toastText}
        </ActionModal>
      )}
      {punishment && (
        <ActionModal onClose={() => setPunishment(null)} icon={<div style={{ fontSize:52, lineHeight:1 }}>{punishment.emoji}</div>} kicker="Büntetés 🎲" kickerColor="#7C5CC4" onSecondary={firePunishment} onPrimary={() => setPunishment(null)} primaryLabel="Rendben!" primaryColor="#7C5CC4">
          {punishment.text}
        </ActionModal>
      )}""",
    """      {penaltyOpen && (
        <SheetOverlay onClose={() => setPenaltyOpen(false)} title="Büntetés — ki igyon?">
          <div style={{ padding:'0 16px 20px', display:'flex', flexDirection:'column', gap:12 }}>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5 }}>
              Játékon kívüli korty — wildcard megszegése, fogadás, bármi.
              A kiosztott korty a játékban szerzettel együtt számít.
            </div>
            <DrinkDistributor players={players || []} onFinish={applyPenalty} />
          </div>
        </SheetOverlay>
      )}""",
    'modalok')

sub("const APP_VERSION = 'v10.203';", "const APP_VERSION = 'v10.204';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — Koccinto kivezetve, Buntetes = korty-kioszto')
