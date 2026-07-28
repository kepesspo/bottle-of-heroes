# v10.175 (b) — a hat beallito lap
#
# Kozos vaz: a lapok szerkezete eddig is ismetlodott (SheetOverlay + cimke +
# pirulasor). Egy segedkomponens, hogy hat uj lap ne hat uj masolat legyen.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

SHEETS = '''
// ── Kozos vaz a jatek-beallito lapokhoz ─────────────────────────────
// A meglevo lapok (Busz, Beer Pong, ...) mind ugyanezt a szerkezetet irtak le
// kezzel. Az uj hat mar ebbol dolgozik, hogy ne szulessen hat ujabb masolat.
function CfgSheet({ title, subtitle, onClose, children }) {
  return (
    <SheetOverlay onClose={onClose} title={title} footer={
      <button onClick={onClose} style={{ width:'100%', padding:'15px', borderRadius:16, background:T.mint,
        border:'none', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Kész</button>
    }>
      <div style={{ padding:'0 18px 18px' }}>
        {subtitle && <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkSoft, padding:'10px 0 6px', lineHeight:1.5 }}>{subtitle}</div>}
        {children}
      </div>
    </SheetOverlay>
  );
}
// Egy sor: cimke + magyarazat + pirulasor. A `value` az aktualis ertek.
function CfgRow({ label, hint, options, value, onPick, wide }) {
  return (
    <div style={{ padding:'13px 0', borderTop:`1px solid ${T.surfaceMuted}` }}>
      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink }}>{label}</div>
      {hint && <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:1, lineHeight:1.5 }}>{hint}</div>}
      <div style={{ display:'flex', background:T.surfaceMuted, padding:4, borderRadius:12, gap:3, marginTop:8 }}>
        {options.map(o => {
          const sel = value === o.v;
          return (
            <button key={String(o.v)} onClick={() => onPick(o.v)} style={{
              flex:1, minWidth:0, padding: wide ? '8px 2px' : '8px 4px', borderRadius:9, border:'none', cursor:'pointer',
              fontFamily:T.font, fontWeight:800, fontSize: wide ? 12 : 13, transition:'all .15s',
              background: sel ? T.mint : 'transparent', color: sel ? '#fff' : T.inkSoft,
            }}>{o.l}</button>
          );
        })}
      </div>
    </div>
  );
}

function MemoriaConfigSheet({ config, setConfig, onClose }) {
  const pairs = config.pairs || 8;
  return (
    <CfgSheet title="Memória beállítások" onClose={onClose}
      subtitle="Emoji-párokat kell megtalálni. Minél több a pár, annál hosszabb és nehezebb a kör.">
      <CfgRow label="Párok száma" hint="Kevesebb pár = rövidebb, könnyebb kör"
        options={[4,6,8,10,12].map(n => ({ v:n, l:String(n) }))}
        value={pairs} onPick={v => setConfig(c => ({ ...c, pairs: v }))} />
    </CfgSheet>
  );
}

function RitmusConfigSheet({ config, setConfig, onClose }) {
  return (
    <CfgSheet title="Ritmus beállítások" onClose={onClose}
      subtitle="Koppints a felvillanó emojikra — a koponyát viszont hagyd ki.">
      <CfgRow label="Hossz" hint="Mennyi ideig tart egy kör"
        options={[{v:20,l:'20 mp'},{v:30,l:'30 mp'},{v:45,l:'45 mp'},{v:60,l:'60 mp'}]}
        value={config.duration || 30} onPick={v => setConfig(c => ({ ...c, duration: v }))} />
      <CfgRow label="Rács mérete" hint="Több mező = nehezebb eltalálni"
        options={[{v:9,l:'9'},{v:12,l:'12'},{v:16,l:'16'}]}
        value={config.grid || 12} onPick={v => setConfig(c => ({ ...c, grid: v }))} />
      <CfgRow wide label="Csapdák" hint="Milyen gyakran jelenjen meg a koponya"
        options={[{v:0,l:'Nincs'},{v:0.1,l:'Kevés'},{v:0.2,l:'Normál'},{v:0.35,l:'Sok'}]}
        value={config.trapChance ?? 0.2} onPick={v => setConfig(c => ({ ...c, trapChance: v }))} />
    </CfgSheet>
  );
}

function UtvesztoConfigSheet({ config, setConfig, onClose }) {
  return (
    <CfgSheet title="Útvesztő beállítások" onClose={onClose}
      subtitle="Egyik saroktól a másikig kell eljutni, a csapdákat kerülgetve.">
      <CfgRow label="Pálya mérete" hint="Nagyobb pálya = hosszabb út, több csapda"
        options={[{v:4,l:'4×4'},{v:5,l:'5×5'},{v:6,l:'6×6'},{v:7,l:'7×7'}]}
        value={config.grid || 5} onPick={v => setConfig(c => ({ ...c, grid: v }))} />
    </CfgSheet>
  );
}

function MeduzaConfigSheet({ config, setConfig, onClose }) {
  return (
    <CfgSheet title="Medúza beállítások" onClose={onClose}
      subtitle="Mindenki lenéz, majd felnéz valakire. Akik egymásra néznek, isznak.">
      <CfgRow label="Körök száma" hint="Ennyi menet után zárul a játék"
        options={[3,5,7,10].map(n => ({ v:n, l:String(n) }))}
        value={config.rounds || 5} onPick={v => setConfig(c => ({ ...c, rounds: v }))} />
    </CfgSheet>
  );
}

function CardBattleConfigSheet({ config, setConfig, onClose }) {
  return (
    <CfgSheet title="Kártyacsata beállítások" onClose={onClose}
      subtitle="Két játékos lapokat oszt szét — a magasabb érték nyeri a párharcot.">
      <CfgRow label="Körök száma" hint="Ennyi lapot oszt ki mindkét játékos"
        options={[3,4,5,6,7].map(n => ({ v:n, l:String(n) }))}
        value={config.rounds || 5} onPick={v => setConfig(c => ({ ...c, rounds: v }))} />
    </CfgSheet>
  );
}

// A Kviz mar eddig is olvasta a gameMeta?.quizConfig?.cats-ot — csak felulet
// nem volt hozza. Ures/hianyzo lista = mind a negy temakor.
const QUIZ_CATS = [
  { k:'altalanos', l:'Általános 🧠' },
  { k:'sport',     l:'Sport ⚽' },
  { k:'zene',      l:'Zene 🎵' },
  { k:'film',      l:'Film & TV 🎬' },
];
function QuizConfigSheet({ config, setConfig, onClose }) {
  const all = QUIZ_CATS.map(c => c.k);
  const cats = (config.cats && config.cats.length) ? config.cats : all;
  const toggle = (k) => setConfig(c => {
    const cur = (c.cats && c.cats.length) ? c.cats : all;
    const next = cur.includes(k) ? cur.filter(x => x !== k) : [...cur, k];
    // Az utolso temakort nem lehet kikapcsolni — kerdes nelkul nincs jatek.
    return { ...c, cats: next.length ? next : cur };
  });
  return (
    <CfgSheet title="Kvíz beállítások" onClose={onClose}
      subtitle="Melyik témakörökből jöjjenek a kérdések. Legalább egy kell.">
      <div style={{ display:'flex', flexDirection:'column', gap:8, paddingTop:10 }}>
        {QUIZ_CATS.map(c => {
          const on = cats.includes(c.k);
          const last = on && cats.length === 1;
          return (
            <button key={c.k} onClick={() => toggle(c.k)} disabled={last} style={{
              display:'flex', alignItems:'center', gap:10, width:'100%', textAlign:'left',
              padding:'13px 14px', borderRadius:14, cursor: last ? 'default' : 'pointer',
              border: on ? `2px solid ${T.mint}` : `2px solid ${T.inkMute}22`,
              background: on ? `${T.mint}14` : T.surface, opacity: last ? 0.65 : 1,
              fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink,
            }}>
              <span style={{ flex:1 }}>{c.l}</span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: on ? T.mintDeep : T.inkMute }}>
                {on ? '✓' : ''}
              </span>
            </button>
          );
        })}
      </div>
    </CfgSheet>
  );
}

'''

marker = "// Ezek a jatekok egyedul futnak:"
assert s.count(marker) == 1
s = s.replace(marker, SHEETS.lstrip('\n') + marker)

# ── nyilvantartasba veve: innentol a ceruza-gomb es a Jatekmenet oldal is latja ──
old = """  zene:      { metaKey:'zeneConfig',      Comp: ZeneConfigSheet },
  blackjack: { metaKey:'blackjackConfig', Comp: BlackjackConfigSheet },
};"""
assert s.count(old) == 1
s = s.replace(old, """  zene:      { metaKey:'zeneConfig',      Comp: ZeneConfigSheet },
  blackjack: { metaKey:'blackjackConfig', Comp: BlackjackConfigSheet },
  memoria:    { metaKey:'memoriaConfig',    Comp: MemoriaConfigSheet },
  ritmus:     { metaKey:'ritmusConfig',     Comp: RitmusConfigSheet },
  utveszto:   { metaKey:'utvesztoConfig',   Comp: UtvesztoConfigSheet },
  meduza:     { metaKey:'meduzaConfig',     Comp: MeduzaConfigSheet },
  cardbattle: { metaKey:'cardbattleConfig', Comp: CardBattleConfigSheet },
  quiz:       { metaKey:'quizConfig',       Comp: QuizConfigSheet },
};""")

s = s.replace("const APP_VERSION = 'v10.174';", "const APP_VERSION = 'v10.175';", 1)
assert "v10.175" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — 6 lap + nyilvantartas')
