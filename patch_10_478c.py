# v10.478 (3. rész) — BINGÓ = +1 korty: a „Fenékig!" helyett, és be is számít a kortyösszegbe.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("""function bingoLinesOf(sz) {""", """// v10.478: minden összejött sor (BINGÓ) +1 korty — a kortyösszegbe is beszámít
const BINGO_LINE_SIPS = 1;
function bingoLinesOf(sz) {""")
rep("""  const sipsOf = (pid, set) => { const cd = bingoCardFor(pid, ITEMS.length); let t = 0; set.forEach(c => { if (c !== grid.free && c < grid.s * grid.s) { const it = ITEMS[bingoItemIdx(grid, cd, c)]; if (it) t += bingoK(it); } }); return t; };""",
    """  const sipsOf = (pid, set) => { const cd = bingoCardFor(pid, ITEMS.length); let t = 0; set.forEach(c => { if (c !== grid.free && c < grid.s * grid.s) { const it = ITEMS[bingoItemIdx(grid, cd, c)]; if (it) t += bingoK(it); } }); return t + bingosOf(set) * BINGO_LINE_SIPS; };""")
rep("""{celebrate === 'full' ? 'Minden mező kipipálva — összegyűjtötted az egészet!' : celebrate + '. sorod jött össze — ezt meg kell ünnepelni!'} 🍻</div>
            <button onClick={() => setCelebrate(null)} style={{ marginTop:6, width:'100%', padding:'13px 0', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Fenékig! 🍻</button>""",
    """{celebrate === 'full' ? 'Minden mező kipipálva — összegyűjtötted az egészet! 🍻' : celebrate + '. sorod jött össze — ez +' + BINGO_LINE_SIPS + ' korty!'}</div>
            <button data-bingo-celebrate-ok onClick={() => setCelebrate(null)} style={{ marginTop:6, width:'100%', padding:'13px 0', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>{celebrate === 'full' ? 'Fenékig! 🍻' : '+' + BINGO_LINE_SIPS + ' korty 🍺'}</button>""")
rep("""Teljes sor, oszlop vagy átló = BINGÓ — a teli kártya a csúcs!""", """Teljes sor, oszlop vagy átló = BINGÓ, +1 korty — a teli kártya a csúcs!""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
