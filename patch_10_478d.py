# v10.478 (4. rész) — a BINGÓ-korty az adminban állítható: bingoConfig.bingoLineSips 0–3 (alap 1).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("""// v10.478: minden összejött sor (BINGÓ) +1 korty — a kortyösszegbe is beszámít
const BINGO_LINE_SIPS = 1;""",
"""// v10.478: minden összejött sor (BINGÓ) N korty — a kortyösszegbe is beszámít. Az adminban
// állítható (0–3), a hiányzó mező = 1. A 0 a régi viselkedés („Fenékig!", nem számít bele).
function bingoLineSipsOf(cfg) {
  const v = cfg && cfg.bingoLineSips;
  return (v === 0 || v === 1 || v === 2 || v === 3) ? v : 1;
}""")
# képernyő
rep("""  const sipsOf = (pid, set) =>""", """  const BINGO_LINE_SIPS = bingoLineSipsOf(cfg);   // v10.478 (a sipsOf ELŐTT — TDZ)
  const sipsOf = (pid, set) =>""")
rep("""{celebrate === 'full' ? 'Minden mező kipipálva — összegyűjtötted az egészet! 🍻' : celebrate + '. sorod jött össze — ez +' + BINGO_LINE_SIPS + ' korty!'}</div>""",
    """{celebrate === 'full' ? 'Minden mező kipipálva — összegyűjtötted az egészet! 🍻' : BINGO_LINE_SIPS ? celebrate + '. sorod jött össze — ez +' + BINGO_LINE_SIPS + ' korty!' : celebrate + '. sorod jött össze — ezt meg kell ünnepelni! 🍻'}</div>""")
rep("""{celebrate === 'full' ? 'Fenékig! 🍻' : '+' + BINGO_LINE_SIPS + ' korty 🍺'}</button>""",
    """{celebrate === 'full' || !BINGO_LINE_SIPS ? 'Fenékig! 🍻' : '+' + BINGO_LINE_SIPS + ' korty 🍺'}</button>""")
rep("""Teljes sor, oszlop vagy átló = BINGÓ, +1 korty — a teli kártya a csúcs!""",
    """Teljes sor, oszlop vagy átló = BINGÓ{BINGO_LINE_SIPS ? ', +' + BINGO_LINE_SIPS + ' korty' : ''} — a teli kártya a csúcs!""")
# admin
rep("""  const [roundN, setRoundN] = React.useState(0);""", """  const [roundN, setRoundN] = React.useState(0);
  const [lineSips, setLineSips] = React.useState(1);   // v10.478: BINGÓ-korty
  const [lineMsg, setLineMsg] = React.useState('');""")
rep("""      setCardStyle(bingoStyleOf(c));""", """      setCardStyle(bingoStyleOf(c));
      setLineSips(bingoLineSipsOf(c));""")
rep("""bingoCardStyle: cardStyle, tippTitle:""", """bingoCardStyle: cardStyle, bingoLineSips: lineSips, tippTitle:""")
rep("""          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}""",
"""          {/* v10.478: BINGÓ-korty — AZONNAL ment (merge) */}
          <div data-bingo-linebox style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Korty egy BINGÓ-ért (teljes sor / oszlop / átló)')}
            <div style={{ display:'flex', gap:6, background:T.bg, borderRadius:12, padding:4 }}>
              {[0, 1, 2, 3].map(v => {
                const on = v === lineSips;
                return <button key={v} type="button" data-bingo-linesips={v} aria-pressed={on} onClick={() => {
                  if (on) return;
                  const prev = lineSips; setLineSips(v); setLineMsg('mentés…');
                  if (typeof firebase === 'undefined') { setLineMsg(''); return; }
                  firebase.firestore().collection('config').doc('bingoConfig').set({ bingoLineSips: v }, { merge: true })
                    .then(() => setLineMsg('mentve'))
                    .catch(e => { setLineSips(prev); setLineMsg('nem sikerült menteni' + (e && e.code ? ` (${e.code})` : '')); });
                }} style={{ flex:1, minWidth:0, height:38, borderRadius:9, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, whiteSpace:'nowrap',
                  background: on ? T.surface : 'transparent', color: on ? T.ink : T.inkSoft, boxShadow: on ? T.shadow : 'none' }}>{v === 0 ? 'Nincs' : '+' + v}</button>;
              })}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkSoft, marginTop:7, lineHeight:1.4 }}>
              {lineSips ? `Minden összejött sor +${lineSips} korty, és beszámít a kortyösszegbe.` : 'A BINGÓ csak ünneplés („Fenékig!"), a kortyösszegbe nem számít.'}{lineMsg ? ` · ${lineMsg}` : ''}
            </div>
          </div>
          {/* v10.473: szettek — egy koppintás, és mindenki az új szett tiszta kártyáját kapja */}""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
