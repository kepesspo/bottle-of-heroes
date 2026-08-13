# v10.356 - A Finger It UJJOSSZEG lett: Csapat -> PAROS
#
# A regi Finger It csapatjatek volt: mindenki ujjat tesz az asztalra, egy ember
# szamol, es aki eltalalja a fennmarado ujjak szamat, az nyer. Az uj jatek a
# klasszikus MORRA paros valtozata: ketten EGYSZERRE mutattok 0–5 ujjat, es
# kozben bemondjatok, mit tippeltek a KOZOS OSSZEGRE. Aki eltalalta, nyer.
#
# ⚠️ AZ EGYIDEJUSEG A JATEK FELE. Ha az egyik elobb mondja be a tippjet, a masik
# trivialisan igazodik hozza — nincs blöff. Ezert 3-2-1 visszaszamlalas van, es
# a host UTANA jelzi, ki talalt. Ugyanaz a minta, mint a „Ne ugyanazt!"-nal
# (v10.342): a telefonos, rejtett beadas kesobb johet ra.
#
# A jatek `id`-ja MARAD `fingerit`: az azonositohoz jatek-statisztika
# (`game_stats/fingerit.playCount`) es a jatszottsagi sorrend tapad. Uj id-vel
# az eddigi szamlalo elveszne, es a jatek hatra kerulne a listaban.
#
# A regi `FingeritGame` (185 sor) KIKERUL: a `GameContent` mar az ujat mountolja,
# tehat elerhetetlen lenne — halott kod (v10.340 / v10.354 mintajara).
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. A regi komponens kivezetese ──────────────────────────────────────────
i = src.index('function FingeritGame({ gameIdx, players, onAdvance, onResult, drinkMult = 1 }) {')
j = src.index('function SohanemGame(', i)
assert j > i and (j - i) > 4000, 'a regi FingeritGame hatarai gyanusak: %d' % (j - i)
src = src[:i] + '''// ═══════════════ Ujjösszeg (Morra) — páros blöff ═══════════════
// Ketten EGYSZERRE mutattok 0–5 ujjat, es kozben bemondjatok, mit tippeltek a
// KOZOS OSSZEGRE (0–10). Aki eltalalta, nyer.
//
// ⚠️ AZ EGYIDEJUSEG A JATEK FELE: ha az egyik elobb mondja be a tippjet, a masik
// trivialisan igazodik hozza. Ezert visszaszamlalas van, es a host UTANA jelzi,
// ki talalt — ugyanaz a minta, mint a „Ne ugyanazt!"-nal (v10.342).
const UJJ_ROUNDS = 3;

function UjjosszegGame({ gameIdx, challenger, opponent, onAdvance, onResult, drinkMult = 1 }) {
  const [phase, setPhase] = React.useState('ready');   // 'ready' | 'count' | 'judge' | 'done'
  const [round, setRound] = React.useState(1);
  const [tick, setTick] = React.useState(3);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setRound(1); setTick(3); advancedRef.current = false;
  }, [gameIdx, challenger?.id]);

  // 3-2-1-MOST. A „MOST" pillanataban kell egyszerre mutatni es bemondani.
  React.useEffect(() => {
    if (phase !== 'count') return;
    if (tick <= 0) { const t = setTimeout(() => setPhase('judge'), 550); return () => clearTimeout(t); }
    const t = setTimeout(() => setTick(v => v - 1), 800);
    return () => clearTimeout(t);
  }, [phase, tick]);

  const finish = (winner, loser, drinks, note) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    setPhase('done');
    onResult && onResult({
      winners: winner ? [winner] : [], losers: loser ? [loser] : [],
      drinks, winNote: winner ? '+1 pont' : '', loseNote: note,
    });
    const dm = {}, pm = {};
    if (loser)  dm[loser.id]  = drinks;
    if (winner) pm[winner.id] = 1;
    onAdvance && onAdvance(dm, pm);
  };

  const hit = (who) => finish(who, who && who.id === challenger?.id ? opponent : challenger, 1,
                              `${who?.name || 'A játékos'} eltalálta az összeget!`);

  // Senki nem talalt: uj kor. Az UTOLSO kor utan mindketten isznak egyet —
  // enelkul a jatek vegtelen lehetne, es a tet elszallna.
  const nobody = () => {
    if (round < UJJ_ROUNDS) { setRound(r => r + 1); setTick(3); setPhase('count'); return; }
    if (advancedRef.current) return;
    advancedRef.current = true;
    setPhase('done');
    const both = [challenger, opponent].filter(Boolean);
    onResult && onResult({ winners: [], losers: both, drinks: 1,
                           loseNote: `Három kör, egy találat sem — mindketten isztok.` });
    const dm = {}; both.forEach(p => { dm[p.id] = 1; });
    onAdvance && onAdvance(dm, {});
  };

  const judgeBtn = (label, color, onClick) => (
    <button onClick={onClick} style={{ width:'100%', minHeight:56, borderRadius:16, border:'none',
      background:color, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16,
      cursor:'pointer', boxShadow:T.shadow }}>{label}</button>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', textAlign:'center', boxShadow:T.shadow, boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>
          {round}. / {UJJ_ROUNDS}. kör
        </div>
        <div style={{ fontFamily:T.font, fontSize:13.5, color:T.inkSoft, marginTop:6, lineHeight:1.5 }}>
          Egyszerre mutassatok <strong style={{ color:T.ink }}>0–5 ujjat</strong>, és közben
          mondjátok be, mennyi lesz a <strong style={{ color:T.ink }}>közös összeg</strong>.
        </div>
      </div>

      {phase === 'ready' || phase === 'count' ? (
        phase === 'ready' ? (
          <button onClick={() => { setTick(3); setPhase('count'); }} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Indítás</div>
          </button>
        ) : (
          <div style={{ width:170, height:170, borderRadius:'50%', background: tick > 0 ? T.mintSoft : T.coral, display:'grid', placeItems:'center', boxShadow:T.shadow }}>
            <span style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize: tick > 0 ? 76 : 40, color: tick > 0 ? T.ink : '#fff', lineHeight:1 }}>
              {tick > 0 ? tick : 'MOST!'}
            </span>
          </div>
        )
      ) : phase === 'judge' ? (
        <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:10 }}>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, textAlign:'center' }}>Ki találta el az összeget?</div>
          {judgeBtn(challenger?.name || 'Kihívó', T.mint, () => hit(challenger))}
          {judgeBtn(opponent?.name || 'Ellenfél', T.mint, () => hit(opponent))}
          {judgeBtn(round < UJJ_ROUNDS ? 'Senki — új kör' : 'Senki — vége', T.inkMute, nobody)}
        </div>
      ) : (
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink }}>Vége!</div>
      )}
    </div>
  );
}

''' + src[j:]

# ── 2. Bekotes ──────────────────────────────────────────────────────────────
sub1(
"""  if (gameId === 'fingerit') return <FingeritGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} drinkMult={drinkMult} />;""",
"""  if (gameId === 'fingerit') return <UjjosszegGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} drinkMult={drinkMult} />;""",
'GameContent ujjosszeg')

# ── 3. Assetek ──────────────────────────────────────────────────────────────
sub1(
"""  'chicken_banner.png': 'assets/chicken_banner.png',""",
"""  'chicken_banner.png': 'assets/chicken_banner.png',
  'igennem_icon.png': 'assets/igennem_icon.png',
  'igennem_banner.png': 'assets/igennem_banner.png',
  'ultimatum_icon.png': 'assets/ultimatum_icon.png',
  'ultimatum_banner.png': 'assets/ultimatum_banner.png',
  'mennyi_icon.png': 'assets/mennyi_icon.png',
  'mennyi_banner.png': 'assets/mennyi_banner.png',""",
'IMGS tobbi asset')

# ── 4. A GAMES bejegyzes atirasa ────────────────────────────────────────────
old_entry_start = src.index("  { id:'fingerit',")
old_entry_end = src.index("\n", old_entry_start)
src = (src[:old_entry_start]
       + "  { id:'fingerit', stake:[1,1],  roundTime:'fast',  name:'Ujjösszeg',            difficulty:'közepes', category:'Páros', emoji:'✋', isNew:true, symbol:IMGS['fingerit_symbol.png'], img:IMGS['fingerit_icon.png'], banner:IMGS['fingerit_banner.png'], color:'#06B6D4', desc:'Klasszikus kocsmajáték párban (Morra). Egyszerre mutattok 0–5 ujjat, és KÖZBEN bemondjátok, mennyi lesz a két kéz közös összege. Aki eltalálta, pontot kap és a másik iszik. Ha egyik sem talál, jöhet a következő kör — három kör után mindketten isztok egyet.' },"
       + src[old_entry_end:])

# ── 5. A jatek maga konyvel ─────────────────────────────────────────────────
sub1(
"""  chicken:   { prompt:'Felváltva nyomjátok — de vigyázz, mikor robban!', cta:[] },""",
"""  chicken:   { prompt:'Felváltva nyomjátok — de vigyázz, mikor robban!', cta:[] },
  fingerit:  { prompt:'Egyszerre mutassatok ujjakat — és mondjátok be az összeget!', cta:[] },""",
'SCENARIOS ujjosszeg')

# ⚠️ A SCENARIOS-ban MAR VOLT egy `fingerit` bejegyzes („Finger it — ki
# tévesztett?"), es a kesobbi kulcs nyer a JS objektum-literalban — az uj
# felirat ezert nem latszott volna. A regit ki kell venni, nem ujat hozzaadni.
sub1("""  fingerit:  { prompt:'Finger it — ki tévesztett?', cta:[] },\n""", "", 'regi fingerit prompt')

sub1("const APP_VERSION = 'v10.355';", "const APP_VERSION = 'v10.356';", 'verzio')

assert 'FingeritGame' not in src, 'maradt FingeritGame hivatkozas'
assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_356 alkalmazva')
