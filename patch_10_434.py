# v10.434 — Gender Reveal vetítő: 1–3 polaroid, 3/5/8 mp, krém-papír felület (mint a Babakvíz)
import re
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.433';", "const APP_VERSION = 'v10.434';")
rep("const REVEAL_SECS = [5, 8, 12, 20];", """const REVEAL_SECS = [3, 5, 8];
// A vetítőn egyszerre látszó polaroidok száma: a vetítő gépén választható (1–3).
const REVEAL_SLOT_OPTS = [1, 2, 3];
// A vetítő papír-színei — UGYANAZ a krém alap és pasztell foltok, mint a Babakvízé.
const REVEAL_PAPER = '#FFF7EE', REVEAL_INK = '#23202B';""")

# ── a hely-szám: a választott érték, a szélességre és a képek számára szorítva
rep("""// ── A polaroid-asztal (v10.433) ──────────────────────────────────────────────────
// Széles vásznon TÖBB polaroid látszik egyszerre, kis átfedéssel. A helyek száma a
// kijelző arányából és szélességéből jön (`revealBoardCount`); minden váltás a
// LEGRÉGEBBI helyre ejt új képet, és az kerül felülre. Kevés képnél nincs ismétlés:
// a már kint lévő kép csak előre jön, nem kerül ki másodszor.
function revealBoardCount(w, h) {
  const ar = w / Math.max(1, h);
  const byAr = ar >= 1.9 ? 5 : ar >= 1.45 ? 4 : ar >= 1.1 ? 3 : ar >= 0.8 ? 2 : 1;
  return Math.max(1, Math.min(byAr, Math.floor(w / 300)));
}""", """// ── A polaroid-asztal (v10.433, v10.434) ────────────────────────────────────────
// Széles vásznon TÖBB polaroid látszik egyszerre, kis átfedéssel. A számot a vetítő
// gépén választják (1–3, `boh_reveal_slots`), de egy lap legalább 260 px széles
// marad — álló telefonon ezért mindig 1 —, és több hely nincs, mint kép. Minden
// váltás a LEGRÉGEBBI helyre ejt új képet, és az kerül felülre. Kevés képnél nincs
// ismétlés: a már kint lévő kép csak előre jön, nem kerül ki másodszor.
function revealBoardCount(pref, w, nItems) {
  const want = REVEAL_SLOT_OPTS.includes(pref) ? pref : 3;
  return Math.max(1, Math.min(want, Math.floor(w / 260), nItems || 1));
}
// A krém „papír" pasztell foltjai — a Babakvíz és a képfolyam ugyanezt viseli.
// Leleplezés után a foltok a kiderült szín árnyalatait kapják.
function RevealPaperBlobs({ tones }) {
  const c = tones || ['#F7B6CB', '#FAD47E', '#A9D0F5', '#F7B6CB'];
  return (
    <React.Fragment>
      <div aria-hidden="true" style={{ position:'absolute', left:'-6vh', top:'-8vh', width:'min(26vh, 24vw)', height:'min(26vh, 24vw)', borderRadius:'50%', background:c[0], transition:'background 1.5s' }} />
      <div aria-hidden="true" style={{ position:'absolute', left:'min(10vh, 8vw)', top:'6vh', width:'min(11vh, 9vw)', height:'min(13vh, 11vw)', borderRadius:'50%', background:c[1], transition:'background 1.5s' }} />
      <div aria-hidden="true" style={{ position:'absolute', right:'-7vh', top:'-9vh', width:'min(28vh, 26vw)', height:'min(28vh, 26vw)', borderRadius:'50%', background:c[2], transition:'background 1.5s' }} />
      <div aria-hidden="true" style={{ position:'absolute', right:'min(14vh, 12vw)', top:'5vh', width:'min(10vh, 8vw)', height:'min(12vh, 10vw)', borderRadius:'50%', background:c[3], transition:'background 1.5s' }} />
    </React.Fragment>
  );
}""")

# polaroid a krém alapon: halványabb árnyék + finom perem
rep("""background:'#FFFDF8', padding:`${g.pad}px ${g.pad}px ${g.bottom}px`, borderRadius:6,
        boxShadow: isCur ? '0 2.6vh 7vh rgba(0,0,0,0.6)' : '0 1.6vh 4vh rgba(0,0,0,0.45)',""",
"""background:'#FFFFFF', border:'1px solid #EFE2D2', padding:`${g.pad}px ${g.pad}px ${g.bottom}px`, borderRadius:6,
        boxShadow: isCur ? '0 2.6vh 6vh rgba(60,40,20,0.28)' : '0 1.4vh 3.4vh rgba(60,40,20,0.18)',""")
rep("color:'#1B1830', fontFamily:T.font, fontWeight:900,\n      fontSize:'max(14px, 2.2vh)', letterSpacing:'0.1em', boxShadow:'0 6px 24px rgba(0,0,0,0.35)'",
    "color:REVEAL_INK, fontFamily:T.font, fontWeight:900,\n      fontSize:'max(14px, 2.2vh)', letterSpacing:'0.1em', boxShadow:'0 6px 24px rgba(60,40,20,0.2)'")

# visszaszámlálás is a papíron (a videó fekete, a robbanás a kiderült szín marad)
rep("background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : '#07060C', transition:'background .5s' }}>",
    "background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : REVEAL_PAPER, transition:'background .5s' }}>\n      {stage === 'count' && <RevealPaperBlobs />}")
rep("letterSpacing:'0.3em', color:'rgba(255,255,255,0.7)', textAlign:'center' }}>{show.test ? 'PRÓBA-LELEPLEZÉS' : 'FIÚ VAGY LÁNY?'}</div>",
    "letterSpacing:'0.3em', color:'#2F63A8', textAlign:'center' }}>{show.test ? 'PRÓBA-LELEPLEZÉS' : 'FIÚ VAGY LÁNY?'}</div>")

# kvíz: a közös foltokat használja
old_blobs = s[s.index("  const blobs = (\n    <React.Fragment>\n      <div aria-hidden=\"true\" style={{ position:'absolute', left:'-6vh'"):]
old_blobs = old_blobs[:old_blobs.index("  );\n") + 5]
assert old_blobs.count('aria-hidden') == 4
rep(old_blobs, "  const blobs = <RevealPaperBlobs />;\n")
rep("const ink = '#23202B';\n  const bg = { position:'absolute', inset:0, zIndex:30, overflow:'hidden', background:'#FFF7EE' };",
    "const ink = REVEAL_INK;\n  const bg = { position:'absolute', inset:0, zIndex:30, overflow:'hidden', background:REVEAL_PAPER };")

# vetítő: választott hely-szám
rep("""  const [secs, setSecs] = React.useState(() => { const n = +revealStore('boh_reveal_secs'); return REVEAL_SECS.includes(n) ? n : 8; });""",
"""  const [secs, setSecs] = React.useState(() => { const n = +revealStore('boh_reveal_secs'); return REVEAL_SECS.includes(n) ? n : 5; });
  const [slotPref, setSlotPref] = React.useState(() => { const n = +revealStore('boh_reveal_slots'); return REVEAL_SLOT_OPTS.includes(n) ? n : 3; });""")
rep("const nSlots = Math.max(1, Math.min(revealBoardCount(vp.w, vp.h), photos.length || 1));",
    "const nSlots = revealBoardCount(slotPref, vp.w, photos.length);")

# vetítő: krém felület, sötét tinta
rep("""  const chip = (on) => ({ flexShrink:0, whiteSpace:'nowrap', padding: narrow ? '6px 10px' : '7px 12px', borderRadius:999, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize: narrow ? 12 : 13,
    background: on ? '#fff' : 'rgba(255,255,255,0.14)', color: on ? '#1B1830' : '#fff' });
  const grad = RR
    ? `radial-gradient(70% 80% at 20% 20%, ${RR.c1}66, transparent 70%), radial-gradient(70% 80% at 80% 80%, ${RR.c2}55, transparent 70%), ${REVEAL_NIGHT}`
    : `radial-gradient(60% 70% at 15% 20%, ${REVEAL_PINK}33, transparent 70%), radial-gradient(60% 70% at 85% 80%, ${REVEAL_BLUE}33, transparent 70%), ${REVEAL_NIGHT}`;""",
"""  // ⚠️ A felület a Babakvíz krém papírja (v10.434): sötét tinta, fehér/pasztell chipek.
  const chip = (on) => ({ flexShrink:0, whiteSpace:'nowrap', padding: narrow ? '6px 10px' : '7px 12px', borderRadius:999, cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize: narrow ? 12 : 13,
    border: on ? `1.5px solid ${REVEAL_INK}` : '1.5px solid #EFE2D2', background: on ? REVEAL_INK : '#fff', color: on ? '#fff' : REVEAL_INK });
  const tones = RR ? [RR.c2, '#FAD47E', RR.c1 + '88', RR.c2] : null;""")
rep("""fontSize:'clamp(15px, 2.6vh, 32px)', color:'rgba(255,255,255,0.7)' }}>{loaded ? 'Hamarosan""",
    """fontSize:'clamp(15px, 2.6vh, 32px)', color:'#2F63A8' }}>{loaded ? 'Hamarosan""")
rep("""style={{ position:'fixed', inset:0, zIndex:6000, overflow:'hidden', cursor: ui ? 'default' : 'none', background:grad, transition:'background 1.5s' }}>""",
    """style={{ position:'fixed', inset:0, zIndex:6000, overflow:'hidden', cursor: ui ? 'default' : 'none', background:REVEAL_PAPER }}>""")
rep("""`}</style>
      {stage()}""", """`}</style>
      <RevealPaperBlobs tones={tones} />
      {stage()}""")
rep("""background:'rgba(15,12,24,0.72)', border:`2px solid ${REVEAL_PINK}88`, boxShadow:'0 8px 30px rgba(0,0,0,0.35)', backdropFilter:'blur(6px)', WebkitBackdropFilter:'blur(6px)' }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(11px, 1.7vh, 20px)', letterSpacing:'0.18em', color:'rgba(255,255,255,0.75)' }}>""",
"""background:'#fff', border:'2px solid #EFE2D2', boxShadow:'0 1vh 2.6vh rgba(60,40,20,0.12)' }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:'clamp(11px, 1.7vh, 20px)', letterSpacing:'0.18em', color:'#2F63A8' }}>""")
rep("style={{ ...chip(false), background:'rgba(35,32,43,0.75)' }}>‹ Előző</button>", "style={chip(false)}>‹ Előző</button>")
rep("style={{ ...chip(true), background:'#23202B', color:'#fff' }}>{revealQuizNextLabel(qstate)}</button>", "style={chip(true)}>{revealQuizNextLabel(qstate)}</button>")
rep("style={{ ...chip(false), background:'rgba(35,32,43,0.45)' }}>✕ Kilépés</button>", "style={chip(false)}>✕ Kilépés</button>")
rep("background:'linear-gradient(rgba(0,0,0,0.6), transparent)', opacity: ui ? 1 : 0",
    "background:`linear-gradient(${REVEAL_PAPER}F2 55%, ${REVEAL_PAPER}00)`, opacity: ui ? 1 : 0")
rep("""        {REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => { setSecs(n); revealStore('boh_reveal_secs', String(n)); }} style={chip(secs === n)}>{n} mp</button>)}""",
"""        {REVEAL_SECS.map(n => <button key={n} data-reveal-secs={n} onClick={() => { setSecs(n); revealStore('boh_reveal_secs', String(n)); }} style={chip(secs === n)}>{n} mp</button>)}
        <span aria-hidden="true" style={{ flexShrink:0, width:1.5, alignSelf:'stretch', margin:'4px 2px', background:'#EFE2D2' }} />
        {REVEAL_SLOT_OPTS.map(n => <button key={n} data-reveal-slotsbtn={n} aria-label={n + ' polaroid egyszerre'} title={n + ' polaroid egyszerre'} onClick={() => { setSlotPref(n); revealStore('boh_reveal_slots', String(n)); }} style={chip(slotPref === n)}>🖼 {n}</button>)}""")
rep("""fontWeight:800, fontSize:13, color:'rgba(255,255,255,0.8)' }}>{photos.filter(p => p.src).length} kép</span>""",
    """fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>{photos.filter(p => p.src).length} kép</span>""")
open(p, 'w', encoding='utf-8').write(s)
print('ok')

# ── HIBA (képernyőkép): a polaroid a Babakvíz FÖLÖTT. A lap z-indexe minden váltással
# nő (zRef), a fal pedig nem zárta le a saját rétegét → ~30 váltás után átlépte a kvíz
# 30-as rétegét. A fal mostantól saját rétegben (zIndex:1 + isolation), és kvíz alatt
# nem is rajzolódik.
s = open(p, encoding='utf-8').read()
def rep2(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)
rep2("<div data-reveal-board data-slots={nSlots} style={{ position:'absolute', inset:0 }}>",
     "<div data-reveal-board data-slots={nSlots} style={{ position:'absolute', inset:0, zIndex:1, isolation:'isolate' }}>")
rep2("""`}</style>
      <RevealPaperBlobs tones={tones} />
      {stage()}""", """`}</style>
      <RevealPaperBlobs tones={tones} />
      {!qstate && stage()}""")
open(p, 'w', encoding='utf-8').write(s)
print('ok2')

# ── Szerepek: Vetítő · Operátor · Szülők — a Babakvíz lapozója a Szülőkhöz került
s = open(p, encoding='utf-8').read()
rep2("// Jelszó → szerep (Vetítő / Operátor / Leleplező).", "// Jelszó → szerep (Vetítő / Operátor / Szülők).")
rep2("""          <RevealQuizControl />
          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginTop:4 }}>""",
"""          <div style={{ display:'flex', alignItems:'baseline', justifyContent:'space-between', marginTop:4 }}>""")
rep2("// ── Leleplező (a szülő): külön kóddal, NEM az operátor ───────────────────────────",
"""// ── Szülők: külön kóddal, NEM az operátor (v10.434: „Leleplező" → „Szülők") ─────────
// A szülők engedélyezik/indítják a leleplezést ÉS ők lapozzák a Babakvízt — az
// operátornál (aki a képeket kezeli) nincs kvíz-vezérlő.""")
rep2('<AppBar title="Leleplezés" onBack={onBack} />', '<AppBar title="Szülők" onBack={onBack} />')
rep2(">🎉 Leleplező kód</div>", ">👶 Szülői kód</div>")
rep2("Ez nem a közös jelszó — a leleplezést csak a szülő engedélyezheti, ezzel a kóddal.",
     "Ez nem a közös jelszó — a leleplezést és a Babakvízt a szülők kezelik, ezzel a kóddal.")
rep2("""            {msg && <div data-reveal-firemsg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mint }}>{msg}</div>}
          </div>
        )}""", """            {msg && <div data-reveal-firemsg style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mint }}>{msg}</div>}
          </div>
        )}
        {secret.loaded && sec.code && ok && <div data-reveal-parentquiz style={{ width:'100%', maxWidth:440 }}><RevealQuizControl /></div>}""")
rep2("{ id:'operator', emoji:'📷', name:'Operátor', sub:'Feltöltés, a vendégek képeinek jóváhagyása, a Babakvíz lapozása.' },",
     "{ id:'operator', emoji:'📷', name:'Operátor', sub:'Feltöltés és a vendégek képeinek, üzeneteinek jóváhagyása.' },")
rep2("{ id:'trigger', emoji:'🎉', name:'Leleplező', sub:'Külön kóddal — ő indítja a nagy pillanatot. Az eredményt ő sem látja.' },",
     "{ id:'trigger', emoji:'👶', name:'Szülők', sub:'Külön kóddal — a nagy leleplezés és a Babakvíz. Az eredményt ők sem látják.' },")
rep2("A leleplezést a „Leleplező\" szerep indítja a saját kódjával", "A leleplezést a „Szülők\" szerep indítja a saját kódjával")
rep2("{label('Leleplező kód (nem a közös jelszó)')}", "{label('Szülői kód (nem a közös jelszó)')}")
rep2("de csak ha a szülő (Leleplező szerep, a saját kódjával)", "de csak ha a szülő (Szülők szerep, a saját kódjával)")
open(p, 'w', encoding='utf-8').write(s)
print('ok3')
