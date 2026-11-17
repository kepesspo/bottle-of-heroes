# v10.436 — Gender Reveal: tippek a kép alatt (személy / pár) + számláló a vetítőn
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.435';", "const APP_VERSION = 'v10.436';")

# ── 1. adat + számolás
rep("function useRevealPhotos(all) {", """// ── Tippek (v10.436): az operátor a kép alá jelöli, ki mire tippelt ────────────────
// `revealPhotos/<id>.pair` (személy / pár) + `.votes` = ['boy'|'girl'|null, …] — páron
// KÉT tipp (a pár két tagja máshogy is tippelhet). A számláló a VETÍTŐN lévő képek
// (jóváhagyott, nem rejtett) tippjeit adja össze: ami nem látszik, az nem is számít.
// ⚠️ Személyre visszaváltva a második tipp a tömbben maradhat — ezért MINDEN olvasás a
// `revealVotesOf`-on megy, ami a `pair` szerint vágja.
const REVEAL_VOTE_SIDES = ['boy', 'girl'];
function revealVotesOf(p) {
  const v = Array.isArray(p && p.votes) ? p.votes : [];
  return v.slice(0, p && p.pair ? 2 : 1).filter(x => x === 'boy' || x === 'girl');
}
function revealVoteTally(items) {
  const t = { boy:0, girl:0 };
  (items || []).forEach(p => { if (!p || p.pending || p.hidden || p.kind === 'wish') return; revealVotesOf(p).forEach(v => { t[v]++; }); });
  return t;
}
function revealVoteWrite(p, pair, votes) {
  const db = revealDb(); if (!db || !p) return;
  const clean = [0, 1].slice(0, pair ? 2 : 1).map(i => (votes[i] === 'boy' || votes[i] === 'girl') ? votes[i] : null);
  db.collection('revealPhotos').doc(p.id).set({ pair: !!pair, votes: clean }, { merge:true }).catch(() => {});
}
function useRevealPhotos(all) {""")

# ── 2. a polaroidon is látszik, ki mire tippelt
rep("""  const fs = Math.max(14, Math.min(g.ih / (len > 90 ? 7.5 : len > 50 ? 6 : 4.6), g.iw / (len > 90 ? 13 : 10)));""",
"""  const fs = Math.max(14, Math.min(g.ih / (len > 90 ? 7.5 : len > 50 ? 6 : 4.6), g.iw / (len > 90 ? 13 : 10)));
  const vs = wish ? [] : revealVotesOf(item);""")
rep("""      {cap && <div style={{ position:'absolute', left:0, right:0, bottom:0, height: g.bottom, display:'flex', alignItems:'center', justifyContent:'center', padding:'0 8px', boxSizing:'border-box',""",
"""      {vs.length > 0 && <div data-reveal-cardvotes={vs.join(',')} aria-hidden="true" style={{ position:'absolute', right: g.pad, bottom:0, height: g.bottom, display:'flex', alignItems:'center', gap:2, fontSize: Math.max(13, g.bottom * 0.42), lineHeight:1 }}>{vs.map((v, i) => <span key={i}>{REVEAL_RESULTS[v].emoji}</span>)}</div>}
      {cap && <div style={{ position:'absolute', left:0, right:0, bottom:0, height: g.bottom, display:'flex', alignItems:'center', justifyContent:'center', padding: vs.length ? `0 ${Math.round(g.bottom * (vs.length > 1 ? 1.5 : 1))}px` : '0 8px', boxSizing:'border-box',""")

# ── 3. számláló-komponens + tippválasztó (modul-szintűek — v10.335)
rep("function RevealQrCard({ url, big }) {", """// A szavazás állása a vetítő alján: két szám, köztük az arány-sáv. A leleplezés után a
// nyertes oldal kiemelve („🎯"), a másik halványítva.
function RevealVoteMeter({ tally, revealed }) {
  const tot = tally.boy + tally.girl, pb = tot ? tally.boy / tot : 0.5;
  const side = s => {
    const R = REVEAL_RESULTS[s], win = revealed === s, lose = !!revealed && revealed !== s;
    return (
      <div data-reveal-votes-side={s} data-win={win ? '1' : '0'} style={{ display:'flex', flexDirection: s === 'boy' ? 'row' : 'row-reverse', alignItems:'center', gap:'0.6vw', opacity: lose ? 0.45 : 1, flexShrink:0 }}>
        <span aria-hidden="true" style={{ fontSize:'clamp(18px, 3.2vh, 40px)', lineHeight:1 }}>{R.emoji}</span>
        <span style={{ display:'flex', flexDirection:'column', alignItems: s === 'boy' ? 'flex-start' : 'flex-end', lineHeight:1 }}>
          <span data-reveal-votes-n style={{ fontFamily:T.font, fontWeight:900, fontSize:'clamp(20px, 4vh, 52px)', color:R.ink, fontVariantNumeric:'tabular-nums' }}>{tally[s]}</span>
          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(10px, 1.5vh, 18px)', color:REVEAL_INK, opacity:0.7, letterSpacing:'0.06em', textTransform:'uppercase', whiteSpace:'nowrap', marginTop:'0.3vh' }}>{win ? '🎯 ' : ''}{R.name}</span>
        </span>
      </div>
    );
  };
  return (
    <div data-reveal-votes data-boy={tally.boy} data-girl={tally.girl} style={{ position:'absolute', left:'50%', bottom:'3vh', transform:'translateX(-50%)', zIndex:46,
      width:'min(520px, 36vw)', minWidth:280, boxSizing:'border-box', padding:'1.2vh 1.4vw', borderRadius:20, background:'#fff', border:'2px solid #EFE2D2', boxShadow:'0 1vh 2.6vh rgba(60,40,20,0.14)' }}>
      <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:'clamp(10px, 1.5vh, 18px)', letterSpacing:'0.2em', color:'#2F63A8', marginBottom:'0.8vh' }}>TIPPEK · {tot}</div>
      <div style={{ display:'flex', alignItems:'center', gap:'1vw' }}>
        {side('boy')}
        <div style={{ flex:1, minWidth:40, height:'clamp(10px, 1.6vh, 20px)', borderRadius:999, overflow:'hidden', display:'flex', background:'#EFE2D2' }}>
          <div data-reveal-votes-bar style={{ width: (pb * 100).toFixed(1) + '%', background:REVEAL_RESULTS.boy.c1, transition:'width .6s' }} />
          <div style={{ flex:1, background:REVEAL_RESULTS.girl.c1 }} />
        </div>
        {side('girl')}
      </div>
    </div>
  );
}
// Az operátor a kép ALÁ jelöli: személy vagy pár, és mire tippelt(ek). Ugyanarra
// koppintva a tipp törlődik. Páron két sor: a pár két tagja máshogy is tippelhet.
function RevealVotePicker({ item }) {
  const pair = !!item.pair;
  const votes = Array.isArray(item.votes) ? item.votes : [];
  const cur = [votes[0] || null, votes[1] || null];
  const set = (i, v) => { const nv = cur.slice(); nv[i] = nv[i] === v ? null : v; revealVoteWrite(item, pair, nv); };
  const seg = on => ({ flex:1, padding:'5px 0', borderRadius:8, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:11.5,
    background: on ? T.surface : 'transparent', color: on ? T.ink : T.inkSoft, boxShadow: on ? '0 1px 3px rgba(0,0,0,0.12)' : 'none' });
  const vb = (on, s) => ({ flex:1, minWidth:0, padding:'7px 2px', borderRadius:10, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:12,
    border: on ? `1.5px solid ${REVEAL_RESULTS[s].c1}` : `1.5px solid ${T.border}`, background: on ? REVEAL_RESULTS[s].c1 : 'transparent', color: on ? '#fff' : T.ink,
    whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis' });
  const row = i => (
    <div key={i} style={{ display:'flex', alignItems:'center', gap:5 }}>
      {pair && <span style={{ width:14, flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:11, color:T.inkSoft }}>{i + 1}.</span>}
      {REVEAL_VOTE_SIDES.map(s => (
        <button key={s} data-reveal-vote={s} data-vote-idx={i} aria-pressed={cur[i] === s} onClick={() => set(i, s)} style={vb(cur[i] === s, s)}>{REVEAL_RESULTS[s].emoji} {REVEAL_RESULTS[s].name}</button>
      ))}
    </div>
  );
  return (
    <div data-reveal-votepick={item.id} data-pair={pair ? '1' : '0'} style={{ padding:8, display:'flex', flexDirection:'column', gap:6 }}>
      <div style={{ display:'flex', gap:3, padding:3, borderRadius:10, background:T.bg }}>
        <button data-reveal-votekind="single" aria-pressed={!pair} onClick={() => { if (pair) revealVoteWrite(item, false, cur); }} style={seg(!pair)}>👤 Személy</button>
        <button data-reveal-votekind="pair" aria-pressed={pair} onClick={() => { if (!pair) revealVoteWrite(item, true, cur); }} style={seg(pair)}>👥 Pár</button>
      </div>
      {row(0)}{pair && row(1)}
    </div>
  );
}
function RevealQrCard({ url, big }) {""")

# ── 4. vetítő: a számláló (kvíz és leleplezés alatt nem)
rep("  const RR = revealed ? REVEAL_RESULTS[revealed] : null;",
    "  const RR = revealed ? REVEAL_RESULTS[revealed] : null;\n  const tally = revealVoteTally(photos);")
rep("""      {qstate && !show && <RevealQuizStage qstate={qstate} narrow={narrow} />}""",
"""      {tally.boy + tally.girl > 0 && !qstate && !show && <RevealVoteMeter tally={tally} revealed={revealed} />}
      {qstate && !show && <RevealQuizStage qstate={qstate} narrow={narrow} />}""")

# ── 5. távirányító: az állás egy sorban
rep("""          <div data-reveal-remote-count style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, marginTop:8 }}>{photos.filter(x => x.src || x.kind === 'wish').length} tétel a vetítőn</div>""",
"""          <div data-reveal-remote-count style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.ink, marginTop:8 }}>{photos.filter(x => x.src || x.kind === 'wish').length} tétel a vetítőn</div>
          {(() => { const t = revealVoteTally(photos); return t.boy + t.girl > 0 && <div data-reveal-remote-tally style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, marginTop:6 }}>Tippek: {REVEAL_RESULTS.boy.emoji} {t.boy} · {REVEAL_RESULTS.girl.emoji} {t.girl}</div>; })()}""")

# ── 6. operátor: a tippválasztó a kép ALATT, és az állás a lista fölött
rep("""  const latest = approved.slice().reverse();""", """  const latest = approved.slice().reverse();
  const tally = revealVoteTally(items);""")
rep("""            <div data-reveal-opcount style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft }}>""",
"""            <div data-reveal-opcount style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkSoft, textAlign:'right' }}>{tally.boy + tally.girl > 0 && <span data-reveal-optally style={{ fontWeight:900, color:T.ink, marginRight:8 }}>Tippek: {REVEAL_RESULTS.boy.emoji} {tally.boy} · {REVEAL_RESULTS.girl.emoji} {tally.girl}</span>}""")
old_tile = """          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(150px, 1fr))', gap:10 }}>
            {latest.map(p => (
              <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} style={{ position:'relative', borderRadius:14, overflow:'hidden', background:T.surface, boxShadow:T.shadow, aspectRatio:'1 / 1' }}>"""
new_tile = """          <div style={{ display:'grid', gridTemplateColumns:'repeat(auto-fill, minmax(170px, 1fr))', gap:10, alignItems:'start' }}>
            {latest.map(p => (
              <div key={p.id} data-reveal-thumb={p.id} data-hidden={p.hidden ? '1' : '0'} style={{ borderRadius:14, overflow:'hidden', background:T.surface, boxShadow:T.shadow }}>
              <div style={{ position:'relative', aspectRatio:'1 / 1' }}>"""
rep(old_tile, new_tile)
# a négyzet lezárása után jön a tippválasztó (csak képnél — az üzenet nem szavaz)
i = s.index(new_tile)
j = s.index("""                </div>
              </div>
            ))}
          </div>""", i)
s = s[:j] + """                </div>
              </div>
              {p.kind !== 'wish' && <RevealVotePicker item={p} />}
              </div>
            ))}
          </div>""" + s[j + len("""                </div>
              </div>
            ))}
          </div>"""):]
open(p, 'w', encoding='utf-8').write(s)
print('ok')

# ── a számláló alatt nincs kép: amíg látszik, a polaroidok feljebb húzódnak
s = open(p, encoding='utf-8').read()
rep("""  const tally = revealVoteTally(photos);""",
"""  const tally = revealVoteTally(photos);
  // ⚠️ A számláló a vászon alját foglalja: amíg látszik, a fal a fennmaradó 86%-on áll,
  // különben a középső lap felirata (és a rajta lévő tipp) a számláló alá kerülne.
  const meterOn = tally.boy + tally.girl > 0 && !qstate && !show;
  const boardH = meterOn ? vp.h * REVEAL_METER_ROOM : vp.h;""")
rep("""      {tally.boy + tally.girl > 0 && !qstate && !show && <RevealVoteMeter tally={tally} revealed={revealed} />}""",
"""      {meterOn && <RevealVoteMeter tally={tally} revealed={revealed} />}""")
rep("return <RevealBoardCard key={s.key} item={it} g={revealCardGeom(i, nSlots, vp.w, vp.h, it, s.key)}",
    "return <RevealBoardCard key={s.key} item={it} g={revealCardGeom(i, nSlots, vp.w, boardH, it, s.key)}")
rep("const REVEAL_VOTE_SIDES = ['boy', 'girl'];", "const REVEAL_VOTE_SIDES = ['boy', 'girl'];\nconst REVEAL_METER_ROOM = 0.86;   // a vászon ennyi része marad a falnak, ha látszik a számláló")
# a pontosított megjegyzés: a mentés a pár→személy váltásnál vág, az olvasás is
rep("""// ⚠️ Személyre visszaváltva a második tipp a tömbben maradhat — ezért MINDEN olvasás a
// `revealVotesOf`-on megy, ami a `pair` szerint vágja.""",
"""// ⚠️ MINDEN olvasás a `revealVotesOf`-on megy, ami a `pair` szerint vág: egy személynek
// jelölt dokumentumban (régi adat, kézi írás) bennmaradt második tipp így sem számít.""")
# párnál keskenyebb gombok — telefonon két oszlopban a „Kislány" különben levágódna
rep("""  const vb = (on, s) => ({ flex:1, minWidth:0, padding:'7px 2px', borderRadius:10, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:12,""",
    """  const vb = (on, s) => ({ flex:1, minWidth:0, padding: pair ? '7px 0' : '7px 2px', borderRadius:10, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize: pair ? 11 : 12,""")
rep("""      {pair && <span style={{ width:14, flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:11, color:T.inkSoft }}>{i + 1}.</span>}""",
    """      {pair && <span style={{ width:9, flexShrink:0, fontFamily:T.font, fontWeight:900, fontSize:11, color:T.inkSoft }}>{i + 1}</span>}""")
rep("""    <div key={i} style={{ display:'flex', alignItems:'center', gap:5 }}>""", """    <div key={i} style={{ display:'flex', alignItems:'center', gap: pair ? 4 : 5 }}>""")
open(p, 'w', encoding='utf-8').write(s)
print('ok2')
