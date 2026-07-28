# v10.169 — info gomb a nehezsegi szint mellett, sorral kevesebb
#
# Az eddigi inline magyarazo sor mindig ott volt, es csak a KIVALASZTOTT szintrol
# mondott egy mondatot. Helyette info gomb a cimke mellett, ami egy lapon mutatja
# mind a negyet — nagyobb feluleten, osszehasonlithatoan. Az inline sor kikerul,
# igy egy sorral rovidebb az oldal.
#
# A tartalom a KODBOL jon, nem a regi szovegekbol. A regiek ugyanis csak
# idozitokrol beszeltek — pedig a nehezseg fo hatasa a KORTYSZORZO, es az minden
# jatekra ervenyes (diffDrinks: 1 / 2 / 3 / 5). Az idozito valojaban csak negy
# jatekot erint, a szohossz pedig egyet.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── a szintek tenyleges hatasa, egy helyen ──
anchor = "// Melyik jateknak van sajat beallito lapja."
assert s.count(anchor) == 1
s = s.replace(anchor, """// Mit csinal valojaban a nehezsegi szint. A szamok a kodbol jonnek:
//   kortyszorzo  — diffDrinks, MINDEN jatekra
//   idozitok     — Ötdolog / Mit választanál / Tabu / Gyors Matek
//   szohossz     — Anagramma
const DIFFICULTY_INFO = [
  { id:'easy',    label:'Könnyű',  mult:1, tone:'#4FC2A0',
    who:'Új társaságnak, vagy ha hosszú estére készültök.',
    time:'Ötdolog 9 mp · Mit választanál 15 mp · Tabu 50 mp · Gyors Matek 7 mp',
    word:'Anagramma: 4 betűs szavak' },
  { id:'mid',     label:'Közepes', mult:2, tone:'#5BA0DB',
    who:'Az alapértelmezett. A legtöbb bulira ez való.',
    time:'Ötdolog 7 mp · Mit választanál 10 mp · Tabu 40 mp · Gyors Matek 5 mp',
    word:'Anagramma: 4–5 betűs szavak' },
  { id:'hard',    label:'Nehéz',   mult:3, tone:'#F59E0B',
    who:'Gyakorlott csapatnak, ha gyorsabban akartok haladni.',
    time:'Ötdolog 5 mp · Mit választanál 8 mp · Tabu 30 mp · Gyors Matek 4 mp',
    word:'Anagramma: 5 betűs szavak' },
  { id:'extreme', label:'Extrém',  mult:5, tone:'#F2A0A0',
    who:'Rövid, kemény menethez. Vigyázzatok magatokra.',
    time:'Ötdolog 4 mp · Mit választanál 5 mp · Tabu 20 mp · Gyors Matek 3 mp',
    word:'Anagramma: 5–6 betűs szavak' },
];

// A szintek osszehasonlito lapja. Azert lap es nem egysoros buborek, mert igy
// egyszerre lathato mind a negy — a valasztashoz ez kell, nem a kivalasztott
// szint egy mondata.
function DifficultyInfoSheet({ current, onClose }) {
  return (
    <SheetOverlay onClose={onClose} title="Nehézségi szintek" footer={
      <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint,
        border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Értem</button>
    }>
      <div style={{ padding:'0 18px 18px' }}>
        <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, lineHeight:1.6, marginBottom:14 }}>
          A szint elsősorban azt szabja meg, <strong style={{ color:T.ink }}>hány kortyot ér egy vesztes kör</strong>.
          Néhány játékban az időt és a szavak hosszát is állítja.
        </div>
        {DIFFICULTY_INFO.map(d => (
          <div key={d.id} style={{ marginBottom:10, borderRadius:14, overflow:'hidden',
            background: d.id === current ? `${d.tone}18` : T.surfaceMuted,
            border: d.id === current ? `2px solid ${d.tone}` : '2px solid transparent' }}>
            <div style={{ display:'flex', alignItems:'center', gap:10, padding:'11px 13px 6px' }}>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, flex:1 }}>{d.label}</span>
              {d.id === current && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10,
                letterSpacing:'0.08em', textTransform:'uppercase', color:T.inkSoft }}>most ez</span>}
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', background:d.tone,
                borderRadius:999, padding:'3px 10px', flexShrink:0 }}>{d.mult}× korty</span>
            </div>
            <div style={{ padding:'0 13px 11px', fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.6 }}>
              {d.who}
              <div style={{ marginTop:5, fontSize:11.5, color:T.inkMute }}>⏱ {d.time}</div>
              <div style={{ fontSize:11.5, color:T.inkMute }}>🔤 {d.word}</div>
            </div>
          </div>
        ))}
      </div>
    </SheetOverlay>
  );
}

""" + anchor)

# ── info gomb a cimke melle, az inline sor helyett ──
old_head = """    difficulty: (first) => (<React.Fragment>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkSoft, margin: first ? '0 0 8px' : '20px 0 8px' }}>{t('difficulty')}</div>"""
assert s.count(old_head) == 1, 'nem talalom a nehezseg-fejlecet'
s = s.replace(old_head, """    difficulty: (first) => (<React.Fragment>
        <div style={{ display:'flex', alignItems:'center', gap:6, margin: first ? '0 0 8px' : '20px 0 8px' }}>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.13em', textTransform:'uppercase', color:T.inkSoft }}>{t('difficulty')}</span>
          <button aria-label="Nehézségi szintek" onClick={e => { e.stopPropagation(); setDiffSheet(true); }} style={{
            width:20, height:20, borderRadius:'50%', border:'none', padding:0, flexShrink:0,
            background:`${T.mint}22`, color:T.mintDeep, cursor:'pointer', display:'grid', placeItems:'center',
            fontFamily:T.font, fontWeight:900, fontSize:12, lineHeight:1 }}>i</button>
        </div>""")

# az inline magyarazo sor kikerul — ezt valtja ki a lap
old_note = """        {selDiff && (
          <div style={{ marginTop:8, padding:'8px 12px', background:`${T.mint}12`, borderRadius:10, borderLeft:`3px solid ${T.mint}`, fontFamily:T.font, fontSize:12, color:T.inkSoft, lineHeight:1.5 }}>
            <strong style={{ color:T.ink }}>{selDiff.label}:</strong> {selDiff.note}
          </div>
        )}
"""
assert s.count(old_note) == 1, 'nem talalom az inline magyarazot'
s = s.replace(old_note, '')

# allapot + a lap mountolasa
hook = "  const [openInfo, setOpenInfo] = React.useState(null);"
assert s.count(hook) == 1
s = s.replace(hook, hook + "\n  const [diffSheet, setDiffSheet] = React.useState(false);")

close = """      {keys.map((k, i) => <React.Fragment key={k}>{SECTIONS[k](i === 0)}</React.Fragment>)}
    </div>"""
assert s.count(close) == 1
s = s.replace(close, """      {keys.map((k, i) => <React.Fragment key={k}>{SECTIONS[k](i === 0)}</React.Fragment>)}
      {diffSheet && <DifficultyInfoSheet current={meta.difficulty || 'easy'} onClose={() => setDiffSheet(false)} />}
    </div>""")

s = s.replace("const APP_VERSION = 'v10.168';", "const APP_VERSION = 'v10.169';", 1)
assert "v10.169" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
