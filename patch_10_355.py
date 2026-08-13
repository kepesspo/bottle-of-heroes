# v10.355 - NEW jelolo (kartya + szuro) + az elso uj paros jatek: CHICKEN
#
# ── A NEW JELOLO ────────────────────────────────────────────────────────────
# A jelolo a `GAMES[]` bejegyzesen az `isNew:true` mezo — ugyanaz a minta, mint
# a `dnr:true` (v10.314). Ket helyre hat, es mindketto magatol koveti:
#   • a kartyan a „★ NEW" szalag,
#   • a Szures „Új játékok" sora.
#
# ⚠️ A SZIN FIX (`NEW_PINK`), nem temafuggo — ugyanaz a szabaly, mint a DNR
# parosnal: az „ez uj" jelentes minden temaban ugyanaz. A DNR szalaggal EGY
# helyre kerul (a kartya aljara), ezert a ketto kizarja egymast: ha egy jatek
# valaha mindketto lenne, a DNR nyer (az a marka, a NEW csak idobeli).
#
# ── CHICKEN ─────────────────────────────────────────────────────────────────
# Felvaltva nyomtok; minden nyomas +1 kortyot rak a kalapba. Van egy REJTETT
# robbanas-pont: aki azt a nyomast teszi, issza az EGESZ kalapot. Aki elobb
# passzol, a kalap FELET issza — a pontot mindket esetben a masik kapja.
#
# ⚠️ A robbanas-pont a kor ELEJEN eldol (`boomRef`), nem nyomasonkent sorsolunk.
# Nyomasonkenti sorsolassal a kockazat NEM nőne a kalappal, es a passzolas
# dontese ertelmet vesztene — pont az veszne el, amitol ez „push your luck".
#
# ⚠️ A szamok NYERSEN mennek ki mindket csatornan: az `onResult` `drinks`-et es
# az `onAdvance` terkepet a PlayScreen szorozza `diffDrinks * wcMult`-tal.
# Ha itt is szoroznank, duplan menne fel (v10.299 Loverseny-lecke).
import io

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
orig = src

def sub1(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new)

# ── 1. NEW szin + a jelolo egy forrasa ──────────────────────────────────────
sub1(
"""function isDnrGame(g) { return !!g && (g.id === 'busz' || !!g.dnr); }""",
"""function isDnrGame(g) { return !!g && (g.id === 'busz' || !!g.dnr); }

// Az „uj jatek" jelolo. ⚠️ FIX szin, nem temafuggo: az „ez uj" ugyanazt jelenti
// minden temaban — ugyanaz a szabaly, mint a DNR parosnal.
const NEW_PINK = '#FF4D6D';
// EGY forras arrol, melyik jatek uj. A jelolo a `GAMES[]` bejegyzesen az
// `isNew:true` mezo; ket felulet olvassa (kartya-szalag + Szures sora).
function isNewGame(g) { return !!g && !!g.isNew; }""",
'NEW konstans + isNewGame')

# ── 2. A szuro NEW sora ─────────────────────────────────────────────────────
sub1(
"""  { k:'Önálló',  l:'Önálló',       tone:'#E0A32E', ic:(c)=>Icon.user(c) },
];""",
"""  { k:'Önálló',  l:'Önálló',       tone:'#E0A32E', ic:(c)=>Icon.user(c) },
  { k:'NEW',     l:'Új játékok',   tone:NEW_PINK,  ic:(c)=><svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M12 2.6l2.5 5.6 6.1.7-4.5 4.1 1.2 6-5.3-3-5.3 3 1.2-6L3.4 8.9l6.1-.7z" stroke={c} strokeWidth="2" strokeLinejoin="round"/></svg> },
];""",
'FILTER_CATS NEW sor')

sub1(
"""    const catFilters = activeFilters.filter(f => ['Egyéni','Páros','Csapat','Önálló'].includes(f));""",
"""    const catFilters = activeFilters.filter(f => ['Egyéni','Páros','Csapat','Önálló','NEW'].includes(f));""",
'catFilters lista')

sub1(
"""      f === 'Önálló' ? SOLO_IDS.has(g.id) :""",
"""      f === 'NEW'    ? isNewGame(g) :
      f === 'Önálló' ? SOLO_IDS.has(g.id) :""",
'gameMatchesFilter NEW ag')

# ── 3. A kartya-szalag ──────────────────────────────────────────────────────
sub1(
"""      {/* DNR exclusive badge */}
      {!g.comingSoon && (g.id === 'busz' || g.dnr) && (""",
"""      {/* ⚠️ ÚJ jelolo — UGYANOTT all, ahol a DNR szalag (a kartya aljan), ezert
          a ketto kizarja egymast. Ha egy jatek valaha mindketto lenne, a DNR
          nyer: az marka-jelzes, a NEW csak idobeli. */}
      {!g.comingSoon && !isDnrGame(g) && isNewGame(g) && (
        <div style={{
          position:'absolute', bottom:-5, left:'50%',
          transform:'translateX(-50%) rotate(-3deg)',
          padding:'1px 8px 2px',
          background:NEW_PINK, color:'#fff',
          border:'1.25px solid #fff', borderRadius:999,
          fontFamily:T.font, fontWeight:900, fontSize:7.5,
          letterSpacing:'0.15em', boxShadow:'0 1.5px 4px rgba(255,77,109,0.45)',
          zIndex:3, whiteSpace:'nowrap', pointerEvents:'none',
        }}>★ NEW</div>
      )}

      {/* DNR exclusive badge */}
      {!g.comingSoon && isDnrGame(g) && (""",
'NEW szalag a kartyan')

# ── 4. Az assetek ───────────────────────────────────────────────────────────
sub1(
"""  'neugyanazt_icon.png': 'assets/neugyanazt_icon.png',""",
"""  'neugyanazt_icon.png': 'assets/neugyanazt_icon.png',
  // Az uj paros jatekok — az ikon a `make_new_icons.py`-bol, a banner PEDIG
  // AZ IKONBOL (`make_banners.py`), tehat a ketto nem tud elcsuszni egymastol.
  'chicken_icon.png': 'assets/chicken_icon.png',
  'chicken_banner.png': 'assets/chicken_banner.png',""",
'IMGS chicken')

# ── 5. A jatek bejegyzese ───────────────────────────────────────────────────
sub1(
"""  { id:'csakegyszó',""",
"""  { id:'chicken', stake:[1,7], roundTime:'fast', name:'Chicken',            difficulty:'közepes', category:'Páros',  emoji:'💣', isNew:true, img:IMGS['chicken_icon.png'], banner:IMGS['chicken_banner.png'], color:'#E0544B', desc:'Páros bátorság-próba. Felváltva nyomjátok a gombot — minden nyomás egy kortyot rak a kalapba. Van egy rejtett robbanás-pont: aki azt a nyomást teszi, megissza az EGÉSZ kalapot, és a másik kap pontot. Bármikor passzolhatsz: akkor csak a kalap felét iszod, de a pont a másiké. Minél tovább mész, annál nagyobb a tét.' },
  { id:'csakegyszó',""",
'GAMES chicken')

# ── 6. A jatek MAGA konyvel -> ures cta ─────────────────────────────────────
sub1(
"""  otdolog:   { prompt:""",
"""  // `cta: []` — a jatek maga konyvel (robbanas/passz), tehat a kezi
  // „Vesztettem / Nyertem!" par egy masodik, ellentmondo utat nyitna (v10.350).
  chicken:   { prompt:'Felváltva nyomjátok — de vigyázz, mikor robban!', cta:[] },
  otdolog:   { prompt:""",
'SCENARIOS chicken')

# ── 7. A komponens ──────────────────────────────────────────────────────────
sub1(
"""function OtdologGame({ gameIdx, challenger, opponent, onAdvance, onResult, difficulty }) {""",
"""// ═══════════════ Chicken — kockázat-lépcső ═══════════════
// ⚠️ A robbanas-pont a kor ELEJEN dol el (`boomRef`). Nyomasonkent sorsolva a
// kockazat nem nőne a kalappal, es a passzolas dontese ertelmet vesztene — pont
// az veszne el, amitol ez „push your luck".
const CHICKEN_MIN_BOOM = 3, CHICKEN_MAX_BOOM = 7;

function ChickenGame({ gameIdx, challenger, opponent, onAdvance, onResult, drinkMult = 1 }) {
  const [phase, setPhase] = React.useState('ready');   // 'ready' | 'run' | 'done'
  const [pot, setPot] = React.useState(0);
  const [step, setStep] = React.useState(0);           // hanyadik nyomas kovetkezik
  const boomRef = React.useRef(0);
  const advancedRef = React.useRef(false);

  const fresh = React.useCallback(() => {
    boomRef.current = CHICKEN_MIN_BOOM + Math.floor(Math.random() * (CHICKEN_MAX_BOOM - CHICKEN_MIN_BOOM + 1));
    setPhase('ready'); setPot(0); setStep(0); advancedRef.current = false;
  }, []);
  React.useEffect(() => { fresh(); }, [gameIdx, challenger?.id]);

  // Aki eppen sorra kerul. A kihivo kezd, aztan felvaltva.
  const who   = step % 2 === 0 ? challenger : opponent;
  const other = step % 2 === 0 ? opponent   : challenger;

  // ⚠️ NYERS szamok mennek ki: a PlayScreen szoroz (`diffDrinks * wcMult`) —
  // az `onResult` `drinks`-et es az `onAdvance` terkepet is. Itt szorozva
  // duplan menne fel (v10.299 Loverseny-lecke).
  const finish = (loser, winner, drinks, note) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    setPhase('done');
    onResult && onResult({
      winners: winner ? [winner] : [], losers: loser ? [loser] : [],
      drinks, winNote: '+1 pont', loseNote: note,
    });
    const dm = {}, pm = {};
    if (loser)  dm[loser.id]  = drinks;
    if (winner) pm[winner.id] = 1;
    onAdvance && onAdvance(dm, pm);
  };

  const press = () => {
    if (phase !== 'run') return;
    const n = pot + 1;
    if (n >= boomRef.current) {
      setPot(n);
      finish(who, other, n, `${who?.name || 'A játékos'} robbantott — issza az egész kalapot!`);
    } else {
      setPot(n); setStep(s => s + 1);
    }
  };

  const chicken = () => {
    if (phase !== 'run' || pot <= 0) return;
    const half = Math.max(1, Math.ceil(pot / 2));
    finish(who, other, half, `${who?.name || 'A játékos'} passzolt — a kalap felét issza.`);
  };

  const potShown = pot * drinkMult;

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      {/* A KALAP — ez a tet, es ez nő minden nyomassal */}
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px 18px', textAlign:'center', boxShadow:T.shadow, boxSizing:'border-box' }}>
        <div style={{ fontFamily:T.font, fontSize:11.5, fontWeight:800, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>A kalapban</div>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, marginTop:4 }}>
          <span style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:52, color: pot > 0 ? T.coral : T.inkMute, lineHeight:1 }}>{potShown}</span>
          <BohIcon name="beer" size={26} />
        </div>
      </div>

      {phase === 'ready' ? (
        <React.Fragment>
          <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'16px 18px', boxShadow:T.shadow, boxSizing:'border-box', fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center', lineHeight:1.5 }}>
            Felváltva nyomtok. Minden nyomás <strong style={{ color:T.ink }}>+1 korty</strong> a kalapba —
            de valahol robban. Aki akkor nyom, <strong style={{ color:T.ink }}>issza az egészet</strong>;
            aki előbb passzol, csak a felét, de a pont a másiké.
          </div>
          <button onClick={() => setPhase('run')} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Kezdés</div>
          </button>
        </React.Fragment>
      ) : phase === 'run' ? (
        <React.Fragment>
          {/* KI JON — a footer pirulaja a PAROST mutatja, nem a sorosat */}
          <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:9 }}>
            <PlayerAvatar player={who} size={30} />
            <span style={{ fontFamily:T.font, fontSize:15, color:T.inkSoft }}>
              <strong style={{ color:T.ink }}>{who?.name}</strong> jön
            </span>
          </div>
          <button onClick={press} style={{ width:184, height:184, borderRadius:'50%', background:T.coral, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2, boxShadow:`0 8px 26px ${T.coral}55` }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:30, color:'#fff', lineHeight:1.1 }}>NYOMOM</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>+1 korty a kalapba</div>
          </button>
          {/* Passzolni csak MAR NOVO kalapbol lehet: nulla kalappal a „passz"
              ingyen pont lenne a masiknak, dontés nélkül. */}
          {pot > 0 && (
            <button onClick={chicken} style={{ background:'transparent', border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:14.5, color:T.inkSoft, padding:'6px 12px' }}>
              Passzolok — {Math.max(1, Math.ceil(pot / 2)) * drinkMult} 🍺 és a pont a másiké
            </button>
          )}
        </React.Fragment>
      ) : (
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:16, color:T.ink, textAlign:'center' }}>💥 Vége!</div>
      )}
    </div>
  );
}

function OtdologGame({ gameIdx, challenger, opponent, onAdvance, onResult, difficulty }) {""",
'ChickenGame komponens')

# ── 8. Bekotes a GameContent-be ─────────────────────────────────────────────
sub1(
"""  if (gameId === 'otdolog') return <OtdologGame""",
"""  if (gameId === 'chicken') return <ChickenGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} drinkMult={drinkMult} />;
  if (gameId === 'otdolog') return <OtdologGame""",
'GameContent chicken')

sub1("const APP_VERSION = 'v10.354';", "const APP_VERSION = 'v10.355';", 'verzio')

assert src != orig
io.open(P, 'w', encoding='utf-8').write(src)
print('OK - patch_10_355 alkalmazva')
