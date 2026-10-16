# v10.427 — Imposztor „Más szó" mód: a csapat egy szót kap, az imposztor egy MÁSIK
# (lehetőleg azonos kategóriájú) szót — és nem tudja, hogy ő a kakukktojás.
f = 'app.src.html'; s = open(f, encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:90])
    s = s.replace(old, new)

# 1) a kakukktojás-szó választója (modul-szint, a tipp-szótár után)
rep("\nconst IMPOSZTOR_SZAVAK_SHUFFLED = (() => {", """
// „Más szó" mód (v10.427): a kakukktojás szava. Lehetőleg UGYANABBÓL a kategóriából
// (IMPOSZTOR_TIPPEK) jön — Banán mellé egy másik gyümölcs —, különben az első tipp
// után lebukna. Ha a kategóriában nincs más szó, a bankból húz.
function imposztorOddWord(word, rnd) {
  const r = rnd || Math.random;
  const cat = IMPOSZTOR_TIPPEK[word];
  const same = IMPOSZTOR_SZAVAK.filter(w => w !== word && cat && IMPOSZTOR_TIPPEK[w] === cat);
  const pool = same.length ? same : IMPOSZTOR_SZAVAK.filter(w => w !== word);
  return pool[Math.floor(r() * pool.length)];
}

const IMPOSZTOR_SZAVAK_SHUFFLED = (() => {""")

# 2) a játék
rep("  const hintOn = !!(gameMeta && gameMeta.imposztorConfig && gameMeta.imposztorConfig.hint);",
    "  const undercover = !!(gameMeta && gameMeta.imposztorConfig && gameMeta.imposztorConfig.mode === 'undercover');\n"
    "  // A segítség csak a klasszikus módban él — „Más szó\" módban az imposztor maga is kap egy szót.\n"
    "  const hintOn = !undercover && !!(gameMeta && gameMeta.imposztorConfig && gameMeta.imposztorConfig.hint);")
rep("  const [voteReady, setVoteReady] = useState(false);\n  const resultFiredRef = useRef(false);",
    "  const [voteReady, setVoteReady] = useState(false);\n  const [oddWord, setOddWord] = useState(null);   // „Más szó\" mód: az imposztor szava\n  const resultFiredRef = useRef(false);")
rep("    setWordIdx(gameIdx % IMPOSZTOR_SZAVAK_SHUFFLED.length);\n",
    "    setWordIdx(gameIdx % IMPOSZTOR_SZAVAK_SHUFFLED.length);\n"
    "    setOddWord(imposztorOddWord(IMPOSZTOR_SZAVAK_SHUFFLED[gameIdx % IMPOSZTOR_SZAVAK_SHUFFLED.length]));\n")
rep("roles[p.id] = { imp, word: imp ? null : word, hint: imp ? impHint : null }; });",
    "roles[p.id] = { imp, word: imp ? (undercover ? oddWord : null) : word, hint: imp ? impHint : null }; });")
rep("  }, [online, gameIdx, impostorIndices.join(','), impHint]);",
    "  }, [online, gameIdx, impostorIndices.join(','), impHint, undercover, oddWord]);")
# offline felfedés: „Más szó" módban az imposztor is a TITKOS SZÓ lapot kapja, a saját szavával
rep("""            {holding ? (
              isImpostor ? (""", """            {holding ? (
              (isImpostor && !undercover) ? (""")
rep("""                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:36, color:'#fff', letterSpacing:'0.02em' }}>{word}</div>""",
    """                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:36, color:'#fff', letterSpacing:'0.02em' }}>{isImpostor ? oddWord : word}</div>""")
# host koordinátor szövege
rep("{isReveal ? 'Aki tudja a szót, mondjon rá tippet — csak az imposztor nem ismeri.' : 'Mindenki válasszon egy nevet a telefonján.'}",
    "{isReveal ? (undercover ? 'Mindenki kapott egy szót — de egyikőtöké más. Mondjatok rá tippet!' : 'Aki tudja a szót, mondjon rá tippet — csak az imposztor nem ismeri.') : 'Mindenki válasszon egy nevet a telefonján.'}")
# eredmény: a két szó
rep("""          <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.45)', marginTop:4 }}>Szó: <strong style={{ color:'rgba(255,255,255,0.85)' }}>{word}</strong></div>""",
    """          <div data-imp-words style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.45)', marginTop:4 }}>Szó: <strong style={{ color:'rgba(255,255,255,0.85)' }}>{word}</strong>{undercover && oddWord && <React.Fragment> · az imposztoré: <strong style={{ color:T.coral }}>{oddWord}</strong></React.Fragment>}</div>""")

# 3) a telefon: ha a szerep szót visz, azt mutatja (a „Más szó" imposztor sem tudja, hogy ő az)
rep("""          {hold ? (
            myRole.imp ? (""", """          {hold ? (
            (myRole.imp && !myRole.word) ? (""")

# 4) beállító lap
rep("""      <CfgRow label="Imposztor-segítség" hint="Az imposztor megkapja a szó kategóriáját (pl. Banán → Gyümölcs), így könnyebb blöffölni"
        options={[{ v:false, l:'Ki' }, { v:true, l:'Be' }]}
        value={!!config.hint} onPick={v => setConfig(c => ({ ...c, hint: v }))} />""",
"""      <CfgRow label="Játékmód" hint={config.mode === 'undercover'
          ? 'Mindenki kap egy szót, de az imposztoré MÁS (hasonló) — és ő sem tudja, hogy ő az'
          : 'Az imposztor nem kap szót, tudja, hogy ő az — blöffölnie kell'}
        options={[{ v:'classic', l:'Klasszikus' }, { v:'undercover', l:'Más szó' }]}
        value={config.mode === 'undercover' ? 'undercover' : 'classic'} onPick={v => setConfig(c => ({ ...c, mode: v }))} />
      {config.mode !== 'undercover' && (
        <CfgRow label="Imposztor-segítség" hint="Az imposztor megkapja a szó kategóriáját (pl. Banán → Gyümölcs), így könnyebb blöffölni"
          options={[{ v:false, l:'Ki' }, { v:true, l:'Be' }]}
          value={!!config.hint} onPick={v => setConfig(c => ({ ...c, hint: v }))} />
      )}""")
rep("const APP_VERSION = 'v10.426';", "const APP_VERSION = 'v10.427';")
open(f, 'w', encoding='utf8').write(s)
print('ok')
