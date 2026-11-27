# v10.475 — DNR Bingó „Ki vagy?": az adminban állítható, ki léphet be —
# Profil + vendég (alap) · Csak vendég · Csak profil. `bingoConfig.bingoWho`, azonnal ment (merge).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.474';", "const APP_VERSION = 'v10.475';")

# ── modul-szintű segéd: egy forrás a módhoz ──
rep("""function AdminBingo({ app })""",
"""// v10.475: ki léphet be a Bingóba — 'both' (alap, hiányzó mező is) · 'guest' · 'profile'
const BINGO_WHO_MODES = [
  { id:'both',    label:'Profil + vendég' },
  { id:'guest',   label:'Csak vendég' },
  { id:'profile', label:'Csak profil' },
];
function bingoWhoOf(cfg) {
  const v = cfg && cfg.bingoWho;
  return (v === 'guest' || v === 'profile') ? v : 'both';
}
// Egy elmentett „who" érvényes-e a mostani módban (a vendég-azonosító `g_`-vel kezdődik)
function bingoWhoAllowed(whoMode, id) {
  if (!id) return false;
  const guest = String(id).indexOf('g_') === 0;
  return whoMode === 'both' || (whoMode === 'guest' ? guest : !guest);
}
function AdminBingo({ app })""")

# ── AdminBingo: állapot, betöltés, payload, kapcsoló ──
rep("""  const [askSet, setAskSet] = React.useState(null);   // váltás / új kör megerősítése""",
    """  const [askSet, setAskSet] = React.useState(null);   // váltás / új kör megerősítése
  const [whoMode, setWhoMode] = React.useState('both'); // v10.475: ki léphet be
  const [whoMsg, setWhoMsg] = React.useState('');""")
rep("""      setRound((c && c.bingoRound) || '');""",
    """      setRound((c && c.bingoRound) || '');
      setWhoMode(bingoWhoOf(c));""")
rep("""bingoSetId: setId, bingoSets: nextSets, bingoRound: round, tippTitle:""",
    """bingoSetId: setId, bingoSets: nextSets, bingoRound: round, bingoWho: whoMode, tippTitle:""")
rep("""          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}""",
"""          {/* v10.475: ki léphet be — AZONNAL ment (merge), mint a láthatóság */}
          <div data-bingo-whobox style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Ki léphet be? (Ki vagy?)')}
            <div style={{ display:'flex', gap:6, background:T.bg, borderRadius:12, padding:4 }}>
              {BINGO_WHO_MODES.map(m => {
                const on = m.id === whoMode;
                return <button key={m.id} type="button" data-bingo-who={m.id} aria-pressed={on} onClick={() => {
                  if (on) return;
                  const prev = whoMode; setWhoMode(m.id); setWhoMsg('mentés…');
                  if (typeof firebase === 'undefined') { setWhoMsg(''); return; }
                  firebase.firestore().collection('config').doc('bingoConfig').set({ bingoWho: m.id }, { merge: true })
                    .then(() => setWhoMsg('mentve'))
                    .catch(e => { setWhoMode(prev); setWhoMsg('nem sikerült menteni' + (e && e.code ? ` (${e.code})` : '')); });
                }} style={{ flex:1, minWidth:0, height:38, borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis',
                  background: on ? T.surface : 'transparent', color: on ? T.ink : T.inkSoft, boxShadow: on ? T.shadow : 'none' }}>{m.label}</button>;
              })}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkSoft, marginTop:7, lineHeight:1.4 }}>
              {whoMode === 'guest' ? 'Mindenki névvel (vagy „Vendég N"-ként) lép be — a profilok nem látszanak.'
                : whoMode === 'profile' ? 'Csak a mentett profilok választhatók — vendégként nem lehet belépni.'
                : 'Lenyitható profil-lista és vendég-belépés is.'}{whoMsg ? ` · ${whoMsg}` : ''}
            </div>
          </div>
          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}""")

# ── BingoScreen: a választó a módhoz igazodik ──
rep("""  const showPicker = !who || (mode === 'torta' && tortaTeams.length > 0 && profiles.length > 0 && !tortaTeamOf(who));""",
"""  // v10.475: a Bingóban az admin dönti el, ki léphet be. Egy elmentett, de a mostani módban
  // nem engedett „who" (pl. vendég „Csak profil" mellett) visszakerül a választóra.
  const whoMode = bingoWhoOf(cfg);
  const showPicker = !who || (mode === 'torta' && tortaTeams.length > 0 && profiles.length > 0 && !tortaTeamOf(who))
    || (mode === 'bingo' && !bingoWhoAllowed(whoMode, who));""")
rep("""            {mode === 'bingo' ? (
              <div data-who-split""",
    """            {mode === 'bingo' && whoMode !== 'profile' ? (
              <div data-who-split""")
rep("""                {/* v10.472: 1. lenyitható — a profilok */}
                <div style={{ border:`1.5px solid ${T.border}`, borderRadius:16, overflow:'hidden' }}>""",
    """                {/* v10.472: 1. lenyitható — a profilok (v10.475: „Csak vendég" módban nincs) */}
                {whoMode !== 'guest' && <div style={{ border:`1.5px solid ${T.border}`, borderRadius:16, overflow:'hidden' }}>""")
rep("""                  ) : <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute, padding:'0 14px 14px' }}>Nincs profil — lépj be vendégként.</div>)}
                </div>""",
    """                  ) : <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute, padding:'0 14px 14px' }}>Nincs profil — lépj be vendégként.</div>)}
                </div>}""")
rep("""                      <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>Nincs profilod? Írd be a neved — vagy hagyd üresen.</span>""",
    """                      <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>{whoMode === 'guest' ? 'Írd be a neved — vagy hagyd üresen.' : 'Nincs profilod? Írd be a neved — vagy hagyd üresen.'}</span>""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
