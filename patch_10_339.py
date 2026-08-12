# v10.339 - 5 dolog: PAROS jatek licittel
#
# A jatekos maga valasztja meg, HANY szot vallal (3-8). Ha osszejon, o kap
# pontot es az ellenfele iszik; ha nem, forditva.
#
# ⚠️ AZ IDOABLAK: `bid * perWord`, ahol a `perWord` a nehezsegbol jon, es
# pontosan ugy van beallitva, hogy 5-os licitnel az ablak UGYANANNYI legyen,
# mint ma (9 / 7 / 5 / 4 mp). Vagyis alapertelmezett liciten a jatek pontosan
# az, ami eddig volt - csak a licit valtoztat rajta.
#
# Miert aranyos az ido, ha a licit igy nem "szoritja" a jatekost? Mert magasabb
# liciten nem az IDO fogy el, hanem az OTLET: nyolc szerszamot mondani akkor is
# nehez, ha van ra ido. A kockazat tehat tudas-alapu, nem tempo-alapu - es igy
# nem valik jatszhatatlanna extrem szinten sem.
#
# A `MIN_WINDOW` alsó korlat kell: extrem szinten 3-as licit 2,4 mp lenne, amibe
# meg bejelolni sem lehet.
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# --- 1. GAMES bejegyzes: Paros, uj leiras -----------------------------------
sub1(
"  { id:'otdolog', stake:[1,1],   roundTime:'fast',  name:'5 dolog',               difficulty:'könnyű',  category:'Egyéni',",
"  { id:'otdolog', stake:[1,1],   roundTime:'fast',  name:'5 dolog',               difficulty:'könnyű',  category:'Páros',",
'otdolog kategoria')

sub1(
"desc:'Az app kisorsol egy játékost aki játszani fog. Meg fog jelenni a képernyőn egy kategória. Ebben a kategóriában kell a játékosnak 5 mp alatt 5 odatartozó szót mondania. Amennyiben ez nem sikerül innia kell.' }",
"desc:'Páros játék. Megjelenik egy kategória, és a soros játékos LICITÁL: megmondja, hány odaillő szót vállal (3–8). Az idő a licithez igazodik. Ha összejön, ő kap pontot és az ellenfele iszik — ha nem, fordítva. Minél többet vállalsz, annál nagyobb a tét: nem az idő fogy el, hanem az ötlet.' }",
'otdolog leiras')

# --- 2. a jatek: licit + valtozo jelolo-szam + paros konyveles ---------------
sub1(
"""function OtdologGame({ gameIdx, challenger, onAdvance, onResult, difficulty }) {
  const cat = OTDOLOG_CATEGORIES[gameIdx % OTDOLOG_CATEGORIES.length];
  const [phase, setPhase] = React.useState('ready'); // 'ready' | 'running' | 'done'
  const DIFF_TIME = { 'easy': 9, 'mid': 7, 'hard': 5, 'extreme': 4 };
  const totalTime = DIFF_TIME[difficulty] || 9;
  const [timeLeft, setTimeLeft] = React.useState(totalTime);
  const [checked, setChecked] = React.useState([false,false,false,false,false]);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setTimeLeft(DIFF_TIME[difficulty] || 9); setChecked([false,false,false,false,false]); advancedRef.current = false;
  }, [gameIdx, difficulty]);""",
"""// ⚠️ Az idoablak = `licit * PER_WORD`. A `PER_WORD` szandekosan ugy van
// beallitva, hogy 5-os liciten pontosan a REGI ablak jojjon ki (9 / 7 / 5 / 4
// mp) — alapertelmezett liciten tehat a jatek valtozatlan.
// Miert aranyos az ido? Mert magasabb liciten nem az IDO fogy el, hanem az
// OTLET: nyolc szerszamot mondani akkor is nehez, ha van ra ido. A kockazat
// tudas-alapu, nem tempo-alapu, es igy extrem szinten sem valik jatszhatatlanna.
const OTDOLOG_PER_WORD = { easy: 1.8, mid: 1.4, hard: 1.0, extreme: 0.8 };
const OTDOLOG_MIN_BID = 3, OTDOLOG_MAX_BID = 8, OTDOLOG_DEF_BID = 5;
// Alsó korlat: extrem szinten a 3-as licit 2,4 mp lenne, amibe bejelolni sem
// lehet.
const OTDOLOG_MIN_WINDOW = 4;
function otdologWindow(bid, difficulty) {
  const per = OTDOLOG_PER_WORD[difficulty] || OTDOLOG_PER_WORD.easy;
  return Math.max(OTDOLOG_MIN_WINDOW, Math.round(bid * per * 10) / 10);
}

function OtdologGame({ gameIdx, challenger, opponent, onAdvance, onResult, difficulty }) {
  const cat = OTDOLOG_CATEGORIES[gameIdx % OTDOLOG_CATEGORIES.length];
  const [phase, setPhase] = React.useState('ready'); // 'ready' | 'running' | 'done'
  const [bid, setBid] = React.useState(OTDOLOG_DEF_BID);
  const totalTime = otdologWindow(bid, difficulty);
  const [timeLeft, setTimeLeft] = React.useState(totalTime);
  const [checked, setChecked] = React.useState(() => Array(OTDOLOG_DEF_BID).fill(false));
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready'); setBid(OTDOLOG_DEF_BID);
    setTimeLeft(otdologWindow(OTDOLOG_DEF_BID, difficulty));
    setChecked(Array(OTDOLOG_DEF_BID).fill(false)); advancedRef.current = false;
  }, [gameIdx, difficulty]);

  // A licit modositasa atmeretezi a jelolo-sort ES az orat — de csak indulas
  // elott (`ready`), kesobb mar futna az ora.
  const changeBid = (n) => {
    if (phase !== 'ready') return;
    const v = Math.max(OTDOLOG_MIN_BID, Math.min(OTDOLOG_MAX_BID, n));
    setBid(v); setChecked(Array(v).fill(false)); setTimeLeft(otdologWindow(v, difficulty));
  };""",
'otdolog fej')

sub1(
"""  const handleResult = (correct) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    const dm = {};
    const pm = {};
    if (!correct && challenger) dm[challenger.id] = 1;
    if (correct && challenger) pm[challenger.id] = 1;""",
"""  // PAROS konyveles: aki nyer, pontot kap, a masik iszik. A licitet elvallalo
  // jatekos a kihivo — ha teljesiti, o a nyertes.
  const handleResult = (correct) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    const dm = {};
    const pm = {};
    const winner = correct ? challenger : opponent;
    const loser  = correct ? opponent   : challenger;
    if (winner) pm[winner.id] = 1;
    if (loser)  dm[loser.id]  = 1;""",
'otdolog konyveles')

# ⚠️ Ez az `onResult`-blokk BETUHIVEN ugyanigy all a Tabu Szo jatekban is,
# ezert a MAR ATIRT konyveles-sorokkal egyutt cserelunk — az csak itt van meg.
sub1(
"""    if (loser)  dm[loser.id]  = 1;
    // Eloszor a BANNER, utana az advance — ez a sorrend minden mas jatekban.
    // Forditva a `gameIdx` valtasa (`useEffect([gameIdx])` → setGameResult(null))
    // kitorolhette a bannert, mielott egyaltalan megjelent volna.
    onResult && onResult({ correct, playerName: challenger ? challenger.name : null, drinks: correct ? 0 : 1,
      winners: correct && challenger ? [challenger] : [], losers: !correct && challenger ? [challenger] : [] });""",
"""    if (loser)  dm[loser.id]  = 1;
    // Eloszor a BANNER, utana az advance — ez a sorrend minden mas jatekban.
    onResult && onResult({
      winners: winner ? [winner] : [], losers: loser ? [loser] : [], drinks: 1,
      winNote: correct ? `Megvolt mind a ${bid}!` : `${challenger?.name || 'A kihívó'} nem tudta a ${bid}-t`,
    });""",
'otdolog banner')

sub1(
"""  // Auto-win when all 5 checked
  React.useEffect(() => {
    if (phase === 'running' && checkedCount === 5) { setPhase('done'); handleResult(true); }
  }, [checkedCount, phase]);""",
"""  // Auto-win, ha a LICIT annyi jelolo megvan (nem fix ot)
  React.useEffect(() => {
    if (phase === 'running' && checkedCount >= bid) { setPhase('done'); handleResult(true); }
  }, [checkedCount, phase, bid]);""",
'otdolog auto-win')

# a "Felfed & Indit" gomb ELE bekerul a licit-valaszto
sub1(
"""      {phase === 'ready' ? (
        <button onClick={() => { setTimeLeft(totalTime); setPhase('running'); }} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>{totalTime}mp · Felfed & Indít</div>
        </button>
      ) : (""",
"""      {phase === 'ready' ? (
        <React.Fragment>
          {/* LICIT — a jatek lenyege. A kategoria meg REJTVE van (a satirozott
              sav fent), tehat a licit vak dontes: a kategoriat ismerve mar nem
              lenne tet. */}
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box' }}>
            <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em', textAlign:'center' }}>
              {challenger?.name || 'A kihívó'} licitál
            </div>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', marginTop:4, marginBottom:12 }}>
              Hány szót vállalsz?
            </div>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:16 }}>
              <button onClick={() => changeBid(bid - 1)} disabled={bid <= OTDOLOG_MIN_BID}
                aria-label="Eggyel kevesebb"
                style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.coralSoft, cursor: bid > OTDOLOG_MIN_BID ? 'pointer' : 'default', opacity: bid > OTDOLOG_MIN_BID ? 1 : 0.4, display:'grid', placeItems:'center' }}>
                <BohIcon name="minus" size={22} />
              </button>
              <div style={{ minWidth:76, textAlign:'center' }}>
                <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:46, color:T.ink, lineHeight:1 }}>{bid}</div>
                <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.1em' }}>szó</div>
              </div>
              <button onClick={() => changeBid(bid + 1)} disabled={bid >= OTDOLOG_MAX_BID}
                aria-label="Eggyel több"
                style={{ width:48, height:48, borderRadius:'50%', border:'none', background:T.mintSoft, cursor: bid < OTDOLOG_MAX_BID ? 'pointer' : 'default', opacity: bid < OTDOLOG_MAX_BID ? 1 : 0.4, display:'grid', placeItems:'center' }}>
                <BohIcon name="plus" size={22} />
              </button>
            </div>
            {opponent && (
              <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, textAlign:'center', marginTop:12, lineHeight:1.45 }}>
                Ha összejön, <strong style={{ color:T.ink }}>{opponent.name}</strong> iszik —<br/>ha nem, ő kap pontot és te iszol.
              </div>
            )}
          </div>
          <button onClick={() => { setTimeLeft(totalTime); setPhase('running'); }} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>{totalTime}mp · Felfed & Indít</div>
          </button>
        </React.Fragment>
      ) : (""",
'licit valaszto')

# a jelolo-sor: nyolc elemnel a fix 64 px magassag es a 22 px szam kicsordul
sub1(
"""              style={{ flex:1, minWidth:0, height:64, borderRadius:16, cursor: phase==='done' ? 'default' : 'pointer', background:c?T.mint:T.surface, opacity: phase==='done' && !c ? 0.45 : 1, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ display:'grid', placeItems:'center' }}>{Icon.check('#fff')}</span>
                 : <span style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color:T.ink }}>{i+1}</span>}""",
"""              style={{ flex:1, minWidth:0, height: bid > 6 ? 52 : 64, borderRadius: bid > 6 ? 13 : 16, cursor: phase==='done' ? 'default' : 'pointer', background:c?T.mint:T.surface, opacity: phase==='done' && !c ? 0.45 : 1, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ display:'grid', placeItems:'center' }}>{Icon.check('#fff')}</span>
                 : <span style={{ fontFamily:T.font, fontWeight:800, fontSize: bid > 6 ? 17 : 22, color:T.ink }}>{i+1}</span>}""",
'jelolo meret')

# a jelolo-sor kozei nyolc elemnel
sub1(
"""        <div style={{ display:'flex', gap:10, width:'100%' }}>
          {checked.map((c, i) => (""",
"""        <div style={{ display:'flex', gap: bid > 6 ? 6 : 10, width:'100%' }}>
          {checked.map((c, i) => (""",
'jelolo koz')

# az also mondat: fix "5" helyett a licit
sub1(
"""            {checkedCount===5 ? '🎉 Mind megvan!' : checkedCount>0 ? `${checkedCount} / 5 ${t('otdologGo')}` : phase==='done' ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}""",
"""            {checkedCount>=bid ? '🎉 Mind megvan!' : checkedCount>0 ? `${checkedCount} / ${bid} ${t('otdologGo')}` : phase==='done' ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}""",
'also mondat')

# --- 3. a dispatch: az ellenfel is lemegy -----------------------------------
sub1(
"  if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} difficulty={gameMeta?.difficulty} />;",
"  if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} difficulty={gameMeta?.difficulty} />;",
'otdolog dispatch')

sub1("const APP_VERSION = 'v10.338';", "const APP_VERSION = 'v10.339';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_339 alkalmazva')
