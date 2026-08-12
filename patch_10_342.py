# v10.342 - UJ JATEK: „Ne ugyanazt!" (paros, 3 kor)
#
# Ket jatekos KOZOSEN jatszik: kapnak egy temat, es harom korben ugy kell szot
# mondaniuk, hogy NE ugyanazt mondjak. Ha mind a harom kor kulonbozo -> mindketten
# pontot kapnak. Ha nem, annyi kortyot isznak, ahanyszor egyezett.
#
# ⚠️ A JATEK A TEMAK SZELESSEGEN ALL VAGY BUKIK. „Allatok"-nal ket ember
# gyakorlatilag SOHA nem mond ugyanazt: mindig pont jarna, nincs tet. Ezert
# minden tema SZUK — 3-8 kezenfekvo valasz. Ilyenkor a jatek arrol szol, hogy
# szandekosan a kevesbe kezenfekvot mondod, mert a masik is a kezenfekvore
# gondol. Uj tema felvetelenel EZ a szabaly, nem a „legyen erdekes".
#
# ⚠️ AZ EGYIDEJUSEG kikenyszeritese a jatek masik fele. Ha az egyik hangosan
# kimondja elobb, a masik trivialisan kikeruli — nincs jatek. Ezert 3-2-1
# visszaszamlalas van, es a host utana jelzi, hogy egyezett-e. Ez ugyanaz, ahogy
# a jatekot elo emberek jatsszak; telefonos, rejtett beadas kesobb johet ra.
#
# Az alkomponensek MODUL-SZINTUEK (lasd CLAUDE.md v10.335): a torzsben minden
# ujrarenderelesnel uj tipust kapnanak, es a React ujramountolna oket.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1. a 40 SZUK tema + a jatek komponens ----------------------------------
GAME = r'''
// ═══════════════ NE UGYANAZT! ═══════════════
// ⚠️ A TEMAK SZANDEKOSAN SZUKEK: 3-8 kezenfekvo valasz. Tag temanal („Allatok")
// ket ember gyakorlatilag soha nem mond ugyanazt, tehat mindig pont jarna, es
// nem lenne tet. Szuk halmaznal viszont a jatek arrol szol, hogy szandekosan a
// kevesbe kezenfekvot mondod — mert a masik is a kezenfekvore gondol.
// UJ TEMA FELVETELENEL EZ A SZABALY, nem az, hogy „legyen erdekes".
const NEUGYANAZT_THEMES = [
  'Piros gyümölcs', 'Magyar folyó', 'Fekete-fehér állat', 'Téli sport',
  'Reggeli ital', 'Kenyérre kenhető', 'Csíkos állat', 'Magyar tó',
  'Karácsonyi étel', 'Sivatagi állat', 'Fúvós hangszer', 'Bolygó',
  'Kártyajáték', 'Testrész az arcon', 'Zöld zöldség', 'Óceán',
  'Kontinens', 'Évszak', 'Világtáj', 'Húros hangszer',
  'Tejtermék', 'Pizzafeltét', 'Magyar hegység', 'Röpképtelen madár',
  'Fém', 'Rágcsáló', 'Sakkfigura', 'Úszásnem',
  'Csípős fűszer', 'Nagymacska', 'Hüllő', 'Sarkvidéki állat',
  'Olajos mag', 'Buborékos ital', 'Sajtféle', 'Vízi sport',
  'Magyar népmese-szereplő', 'Konyhai fűszernövény', 'Éjszakai állat', 'Savanyúság',
];

const NEUGYANAZT_ROUNDS = 3;

// A kor-jelolok: hany kor volt eddig, es melyik ment el. Modul-szintu.
function NeUgyanaztDots({ results, current }) {
  return (
    <div style={{ display:'flex', gap:8, justifyContent:'center' }}>
      {Array.from({ length: NEUGYANAZT_ROUNDS }).map((_, i) => {
        const r = results[i];
        const done = r !== undefined;
        return (
          <div key={i} style={{ width:44, height:8, borderRadius:99,
            background: !done ? T.inkMute + '33' : (r ? T.coral : T.mint),
            border: !done && i === current ? `2px solid ${T.inkMute}66` : 'none',
            boxSizing:'border-box', transition:'background .2s' }} />
        );
      })}
    </div>
  );
}

function NeUgyanaztThemeCard({ theme, hidden }) {
  return (
    <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'18px 22px 20px', textAlign:'center', boxShadow:T.shadow, boxSizing:'border-box' }}>
      <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, letterSpacing:'0.1em', textTransform:'uppercase', marginBottom:8 }}>Téma</div>
      {hidden ? (
        <div style={{ height:34, borderRadius:8, background:'repeating-linear-gradient(-45deg,#e0e4f0,#e0e4f0 4px,#d0d4e4 4px,#d0d4e4 8px)' }} />
      ) : (
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, color:T.ink, lineHeight:1.15, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>{theme}</div>
      )}
    </div>
  );
}

function NeUgyanaztGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {
  // phase: 'intro' | 'count' | 'judge' | 'done'
  const [phase, setPhase] = React.useState('intro');
  const [round, setRound] = React.useState(0);
  const [results, setResults] = React.useState([]);   // true = UGYANAZT mondtak
  const [tick, setTick] = React.useState(3);
  const advRef = React.useRef(false);

  // Harom KULONBOZO tema egy meccsre — a `gameIdx` lepteti a keszletet, igy
  // egy hosszabb estén sem jon vissza ugyanaz a harmas.
  const themes = React.useMemo(() => {
    const n = NEUGYANAZT_THEMES.length;
    return Array.from({ length: NEUGYANAZT_ROUNDS }, (_, i) =>
      NEUGYANAZT_THEMES[(gameIdx * NEUGYANAZT_ROUNDS + i) % n]);
  }, [gameIdx]);

  React.useEffect(() => {
    setPhase('intro'); setRound(0); setResults([]); setTick(3); advRef.current = false;
  }, [gameIdx]);

  // A 3-2-1 visszaszamlalas. EZ a jatek fele: enelkul az egyik jatekos elobb
  // szolal meg, a masik pedig trivialisan kikeruli a szavat.
  React.useEffect(() => {
    if (phase !== 'count') return;
    if (tick <= 0) { setPhase('judge'); return; }
    const t = setTimeout(() => setTick(v => v - 1), 900);
    return () => clearTimeout(t);
  }, [phase, tick]);

  const finish = (all) => {
    if (advRef.current) return;
    advRef.current = true;
    const same = all.filter(Boolean).length;
    const both = [challenger, opponent].filter(Boolean);
    const dm = {}, pm = {};
    if (same === 0) both.forEach(p => { pm[p.id] = 1; });
    else both.forEach(p => { dm[p.id] = same; });
    // Eloszor a BANNER, utana az advance (lasd CLAUDE.md v10.318).
    onResult && onResult(same === 0
      ? { winners: both, losers: [], drinks: 0, winNote: 'Egyszer sem egyeztetek!' }
      : { winners: [], losers: both, drinks: same,
          loseNote: same === NEUGYANAZT_ROUNDS ? 'Mind a háromszor ugyanazt…' : `${same}× ugyanazt mondtátok` });
    onAdvance && onAdvance(dm, pm);
  };

  const judge = (wasSame) => {
    const all = [...results, wasSame];
    setResults(all);
    if (all.length >= NEUGYANAZT_ROUNDS) { setPhase('done'); finish(all); return; }
    setRound(all.length); setTick(3); setPhase('count');
  };

  const sameCount = results.filter(Boolean).length;

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:14, width:'100%' }}>

      <NeUgyanaztDots results={results} current={round} />

      <NeUgyanaztThemeCard theme={themes[round]} hidden={phase === 'intro'} />

      {phase === 'intro' && (
        <React.Fragment>
          <div style={{ width:'100%', background:T.surface, borderRadius:18, padding:'14px 16px', boxShadow:T.shadow, boxSizing:'border-box' }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, textAlign:'center', marginBottom:6 }}>
              {challenger?.name || 'Ti'} és {opponent?.name || 'a párod'} együtt játszotok
            </div>
            <div style={{ fontFamily:T.font, fontSize:13.5, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>
              Három körben mondtok egy-egy szót a témára — <strong style={{ color:T.ink }}>egyszerre</strong>.
              A cél, hogy NE ugyanazt mondjátok.<br/>
              Ha egyszer sem egyeztek: <strong style={{ color:T.ink }}>mindketten pont</strong>.
              Ahányszor egyeztek, <strong style={{ color:T.ink }}>annyit isztok</strong>.
            </div>
          </div>
          <button onClick={() => { setTick(3); setPhase('count'); }}
            style={{ width:'100%', padding:'18px 0', background:T.mint, color:'#fff', border:'none', borderRadius:20, fontFamily:T.font, fontWeight:900, fontSize:20, cursor:'pointer', boxShadow:T.shadowLift }}>
            Kezdjük
          </button>
        </React.Fragment>
      )}

      {phase === 'count' && (
        <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:8, padding:'10px 0' }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize: tick > 0 ? 96 : 54, color: tick > 0 ? T.ink : T.mint, lineHeight:1, animation:'popIn .25s cubic-bezier(.2,.9,.3,1.3)' }}
            key={tick}>
            {tick > 0 ? tick : 'MOST!'}
          </div>
          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft }}>
            {tick > 0 ? 'Készüljetek…' : 'Mondjátok ki egyszerre!'}
          </div>
        </div>
      )}

      {phase === 'judge' && (
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:700, color:T.inkSoft, textAlign:'center' }}>
            {round + 1}. kör — ugyanazt mondtátok?
          </div>
          <div style={{ display:'flex', gap:10, width:'100%' }}>
            <button onClick={() => judge(false)}
              style={{ flex:1, minHeight:96, background:T.mint, color:'#fff', border:'none', borderRadius:20, fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:T.shadow, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
              <BohIcon name="check" size={26} /><span>Mást mondtunk</span>
            </button>
            <button onClick={() => judge(true)}
              style={{ flex:1, minHeight:96, background:T.coral, color:'#fff', border:'none', borderRadius:20, fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer', boxShadow:T.shadow, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6 }}>
              <BohIcon name="cross" size={26} /><span>Ugyanazt</span>
            </button>
          </div>
        </React.Fragment>
      )}

      {phase === 'done' && (
        <div style={{ width:'100%', background: sameCount === 0 ? `${T.mint}18` : `${T.coral}18`, borderRadius:20, padding:'20px 18px', textAlign:'center', border:`2px solid ${sameCount === 0 ? T.mint : T.coral}` }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, lineHeight:1.2 }}>
            {sameCount === 0 ? '🎉 Egyszer sem egyeztetek!' : `${sameCount}× ugyanazt mondtátok`}
          </div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, marginTop:6 }}>
            {sameCount === 0 ? 'Mindketten pontot kaptok.' : `Mindketten isztok ${sameCount} kortyot.`}
          </div>
        </div>
      )}

    </div>
  );
}

'''
sub1("// ─── CSAK EGY SZÓ ────────────────────────────────────────────────────────────",
     GAME + "// ─── CSAK EGY SZÓ ────────────────────────────────────────────────────────────",
     'NeUgyanaztGame beszurasa')

# --- 2. GAMES bejegyzes ------------------------------------------------------
# A `symbol` mezot a kod SEHOL nem olvassa (mind a 45 bejegyzesen halott adat),
# az `img`-nek pedig emoji-tartaleka van — ezert csak `banner` + `emoji` kell.
sub1(
"  { id:'csakegyszó', stake:[1,1], name:'Csak Egy Szó',",
"""  { id:'neugyanazt', stake:[0,3], roundTime:'fast', name:'Ne ugyanazt!',       difficulty:'könnyű',  category:'Páros',  emoji:'🙊', banner:IMGS['neugyanazt_banner.png'], color:'#7C5CC4', desc:'Páros játék: ketten KÖZÖSEN játszotok. Kaptok egy szűk témát, és három körben egyszerre mondtok rá egy-egy szót — úgy, hogy NE ugyanazt. Ha egyszer sem egyeztek, mindketten pontot kaptok; ahányszor egyeztek, annyi kortyot isztok. A trükk: a másik is a kézenfekvő szóra gondol.' },
  { id:'csakegyszó', stake:[1,1], name:'Csak Egy Szó',""",
'GAMES bejegyzes')

# --- 3. az asset-terkep ------------------------------------------------------
sub1("  'otdolog_banner.png': 'assets/otdolog_banner.png',",
     "  'otdolog_banner.png': 'assets/otdolog_banner.png',\n  'neugyanazt_banner.png': 'assets/neugyanazt_banner.png',",
     'IMGS bejegyzes')

# --- 4. a dispatch -----------------------------------------------------------
sub1("  if (gameId === 'csakegyszó') return <CsakEgySzoGame",
     "  if (gameId === 'neugyanazt') return <NeUgyanaztGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;\n  if (gameId === 'csakegyszó') return <CsakEgySzoGame",
     'dispatch')

sub1("const APP_VERSION = 'v10.341';", "const APP_VERSION = 'v10.342';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_342 alkalmazva')
