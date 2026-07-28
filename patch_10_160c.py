# v10.160 (c) — admin kapcsolo a jatekindito folyamathoz
#
# A felhasznalo feltetele: az uj Jatekmenet oldal adminbol kapcsolhato legyen,
# hogy buli kozben is vissza lehessen allni a regi folyamatra verziozas nelkul.
# Ugyanaz a minta, mint a dnrAppsEnabled: config/homeConfig, onSnapshot, elo.
#
# A kliens oldali olvasas localStorage-be is menti az utolso ismert allast, mert
# a kapcsolot offline is tudni kell — kulonben halozat nelkul mindig a regi
# folyamat jonne, fuggetlenul attol, mit allitott be az admin.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) megoszott hook, a GAME_CONFIG_IDS melle ──
anchor = "// Melyik jateknak van sajat beallito lapja."
assert s.count(anchor) == 1
s = s.replace(anchor, """// A jatekindito folyamat: regi (Jatekosok -> Jatekok -> Jatek) vagy uj
// (… -> Jatekmenet -> Jatek). Adminbol kapcsolhato, elo. Az utolso ismert
// allast localStorage-ben tartjuk, kulonben halozat nelkul mindig a regi
// folyamat jonne, fuggetlenul a beallitastol.
const SETUP_FLOW_KEY = 'boh_setup_flow';
function useSetupFlow() {
  const [on, setOn] = React.useState(() => {
    try { return localStorage.getItem(SETUP_FLOW_KEY) === '1'; } catch (e) { return false; }
  });
  React.useEffect(() => {
    if (typeof firebase === 'undefined') return;
    let un;
    try {
      un = firebase.firestore().collection('config').doc('homeConfig').onSnapshot(d => {
        const v = (d && d.exists && d.data() && d.data().setupFlowEnabled) === true;
        setOn(v);
        try { localStorage.setItem(SETUP_FLOW_KEY, v ? '1' : '0'); } catch (e) {}
      }, () => {});
    } catch (e) {}
    return () => { try { un && un(); } catch (e) {} };
  }, []);
  return on;
}

""" + anchor)

# ── 2) admin kapcsolo a Fooldal kartyaba, a szezonzaro ele ──
old = """      <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />

      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Szezonzáró ablak</div>"""
assert s.count(old) == 1
s = s.replace(old, """      <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />

      <div style={{ display:'flex', alignItems:'center', gap:12 }}>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Játékmenet oldal</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>
            Bekapcsolva a játékok kiválasztása után jön egy Játékmenet oldal, ahol a nehézség, a módok
            és a kiválasztott játékok saját beállításai egy helyen vannak. Kikapcsolva a Játékok
            oldalról indul a parti, mint eddig.
          </div>
        </div>
        <Toggle on={setupFlow} onChange={() => write({ setupFlowEnabled: !setupFlow })} />
      </div>
      <div style={{ marginTop:10, fontFamily:T.font, fontSize:11.5, fontWeight:700, color: setupFlow ? T.mintDeep : T.inkMute }}>
        {setupFlow
          ? 'Játékosok → Játékok → Játékmenet → Játék'
          : 'Játékosok → Játékok → Játék'}
      </div>

      <div style={{ height:1, background:`${T.inkMute}22`, margin:'14px 0' }} />

      <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Szezonzáró ablak</div>""")

# a kartya sajat cfg-jebol olvassa, hogy azonnal frissuljon a kapcsolas utan
old2 = "  const closeMode = (cfg && cfg.seasonCloseMode) || 'always';"
assert s.count(old2) == 1
s = s.replace(old2, old2 + "\n  const setupFlow = !!(cfg && cfg.setupFlowEnabled);")

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — hook + admin kapcsolo')
