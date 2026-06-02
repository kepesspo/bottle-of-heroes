# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. BottomBar: lekerekített felső sarkok ────────────────────────────────
old1 = (
    "    <div className=\"bottombar-shell\" style={{\n"
    "      ...positioning,\n"
    "      background: T.surface,\n"
    "      boxShadow:'0 -2px 0 rgba(20,30,50,0.04), 0 -14px 32px rgba(20,30,50,0.12)',\n"
    "    }}>"
)
new1 = (
    "    <div className=\"bottombar-shell\" style={{\n"
    "      ...positioning,\n"
    "      background: T.surface,\n"
    "      boxShadow:'0 -2px 0 rgba(20,30,50,0.04), 0 -14px 32px rgba(20,30,50,0.12)',\n"
    "      borderTopLeftRadius:24, borderTopRightRadius:24,\n"
    "    }}>"
)
assert old1 in html, "Fix 1 not found"
html = html.replace(old1, new1, 1)

# ── 2. Adattömbök + Game komponensek (beszúrás ZeneGame elé) ───────────────
INSERT_BEFORE = "function ZeneGame({ gameIdx }) {"
DATA_AND_GAMES = r"""const OTDOLOG_CATEGORIES = [
  'Filmcímek','Állatfajták','Zenekarok','Fővárosok','Sportok',
  'Gyümölcsök','Zöldségek','Magyar városok','Autómárkák','Ételek',
  'Italok','Foglalkozások','Tánctípusok','Szerszámok','Bútorok',
  'Ruhafélék','Virágok','Madárfajták','Hegyek','Folyók',
  'Filmszínészek','Énekesek','Sportolók','Márkák','Konyhai eszközök',
  'Technológiai cégek','Magyar sütemények','Tengergyümölcsök','Hüvelyesek','Fűszerek',
];

const SOHANEM_CARDS = [
  {t:'csókolóztam vadidegennel',l:'vad'},
  {t:'aludtam szabad ég alatt',l:'alap'},
  {t:'ittam annyit hogy nem emlékeztem rá',l:'kozepes'},
  {t:'hazudtam a kórháznál',l:'kozepes'},
  {t:'valakit felhívtam éjjel kettő után',l:'alap'},
  {t:'buliban elveszítettem a pénztárcámat',l:'alap'},
  {t:'valakivel flörtöltem akiről nem sokat tudtam',l:'kozepes'},
  {t:'felmásztam egy épületre amit nem kellett volna',l:'kozepes'},
  {t:'egy hétnél tovább nem zuhanyoztam',l:'kozepes'},
  {t:'valakivel csaltam',l:'vad'},
  {t:'strandon öltöztem le teljesen',l:'vad'},
  {t:'megcsináltam egy 30+ km-es túrát',l:'alap'},
  {t:'hamis nevet mondtam a kávézóban',l:'alap'},
  {t:'ittam alkoholt tizennégy éves korom előtt',l:'kozepes'},
  {t:'valakinek a nevét tévesztettem el randin',l:'alap'},
  {t:'kiugrottam egy mozgó járóból',l:'kozepes'},
  {t:'elveszítettem a kulcsomat és betörtem a saját lakásomba',l:'alap'},
  {t:'egy filmben sírtam amit senki sem gondolt volna',l:'alap'},
  {t:'valakivel csókoltam akit nem kellett volna',l:'vad'},
  {t:'hazudtam a főnökömnek hogy beteg vagyok',l:'alap'},
  {t:'beugrottam egy hideg folyóba ruhában',l:'kozepes'},
  {t:'egy barátom ex-párjával randiztam',l:'vad'},
  {t:'megpróbáltam egész nap csak angolul beszélni',l:'alap'},
  {t:'hazudtam az életkorommal',l:'alap'},
  {t:'véletlenül elküldtem egy üzenetet a személynek akiről szólt',l:'kozepes'},
  {t:'megettem egy rovart',l:'kozepes'},
  {t:'valakivel a szüleim tudta nélkül találkoztam',l:'kozepes'},
  {t:'teljesen lekéstem egy repülőmről',l:'alap'},
  {t:'valakivel az utcán összekaptam',l:'vad'},
  {t:'próbáltam tűzriasztóval elmenekülni egy szituációból',l:'vad'},
  {t:'kétszer is megkaptam ugyanazt a büntetést',l:'alap'},
  {t:'valakinek hazudtam a végzettségemmel',l:'kozepes'},
  {t:'tengerben éjjel úsztam',l:'alap'},
  {t:'randevút mondtam le utolsó pillanatban üzenettel',l:'alap'},
  {t:'önkéntesen voltam valahol külföldön',l:'alap'},
  {t:'beleszerettem egy filmkarakterbe',l:'alap'},
  {t:'énekeltünk karaoke-n és elvittem az egész közönséget',l:'kozepes'},
  {t:'egyszerre két emberrel randiztam',l:'vad'},
  {t:'valakin megnevettem nyilvánosan és nem kértem bocsánatot',l:'kozepes'},
  {t:'megevtem más ételét a hűtőből beleegyezés nélkül',l:'alap'},
];

function OtdologGame({ gameIdx, challenger, onAdvance }) {
  const cat = OTDOLOG_CATEGORIES[gameIdx % OTDOLOG_CATEGORIES.length];
  const [timeLeft, setTimeLeft] = React.useState(5);
  const [checked, setChecked] = React.useState([false,false,false,false,false]);
  const [running, setRunning] = React.useState(false);
  const [expired, setExpired] = React.useState(false);

  React.useEffect(() => {
    setTimeLeft(5); setChecked([false,false,false,false,false]); setRunning(false); setExpired(false);
  }, [gameIdx]);

  React.useEffect(() => {
    if (!running || expired) return;
    const iv = setInterval(() => {
      setTimeLeft(prev => {
        const next = +(prev - 0.05).toFixed(2);
        if (next <= 0) { setExpired(true); setRunning(false); return 0; }
        return next;
      });
    }, 50);
    return () => clearInterval(iv);
  }, [running, expired]);

  const checkedCount = checked.filter(Boolean).length;
  const pct = timeLeft / 5;
  const r = 72, circ = +(2 * Math.PI * r).toFixed(1);
  const timerColor = pct > 0.5 ? T.mint : pct > 0.2 ? T.yellow : T.coral;
  const doWin = () => onAdvance && onAdvance({});
  const doLose = () => onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {});

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16, width:'100%' }}>
      <div style={{ width:'100%', background:T.surface, borderRadius:20, padding:'20px 24px', textAlign:'center', boxShadow:T.shadow }}>
        <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:T.inkSoft, letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:6 }}>KATEGÓRIA</div>
        <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:26, color:T.ink, lineHeight:1.1 }}>{cat}</div>
      </div>

      {(!running && !expired) ? (
        <button onClick={() => setRunning(true)} style={{ width:148, height:148, borderRadius:'50%', background:T.mint, border:'none', cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:4, boxShadow:T.shadow }}>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:36, color:'#fff', lineHeight:1 }}>▶</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:'rgba(255,255,255,0.85)' }}>Indítás</div>
        </button>
      ) : (
        <div style={{ position:'relative', width:160, height:160 }}>
          <svg viewBox="0 0 160 160" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
            <circle cx="80" cy="80" r={r} fill="none" stroke={`${T.inkMute}30`} strokeWidth="11" />
            <circle cx="80" cy="80" r={r} fill="none" stroke={timerColor} strokeWidth="11"
              strokeDasharray={circ} strokeDashoffset={+(circ*(1-pct)).toFixed(1)} strokeLinecap="round"
              style={{ transition:'stroke .3s' }} />
          </svg>
          <div style={{ position:'absolute', inset:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:52, color:T.ink, lineHeight:1 }}>{expired ? '0' : Math.ceil(timeLeft)}</div>
            <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, letterSpacing:'0.07em' }}>MP</div>
          </div>
        </div>
      )}

      {(running || expired) && (
        <div style={{ display:'flex', gap:8 }}>
          {checked.map((c, i) => (
            <div key={i} onClick={() => { const n=[...checked]; n[i]=!n[i]; setChecked(n); }}
              style={{ width:50, height:50, borderRadius:14, cursor:'pointer', background:c?T.mint:T.surface, display:'grid', placeItems:'center', boxShadow:T.shadow, border:`2px solid ${c?T.mint:'transparent'}`, transition:'all .15s' }}>
              {c ? <span style={{ color:'#fff', fontSize:20 }}>✓</span>
                 : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:T.inkSoft }}>{i+1}</span>}
            </div>
          ))}
        </div>
      )}

      {(running || expired) && (
        <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft }}>
          {checkedCount===5 ? '\U0001f389 Mind megvan!' : checkedCount>0 ? `${checkedCount} / 5 megvan — hajrá!` : expired ? 'Idő lejárt!' : 'Jelöld be amit kimondottál!'}
        </div>
      )}

      {(running || expired) && (
        <div style={{ display:'flex', gap:10, width:'100%' }}>
          <button onClick={doLose} style={{ flex:1, padding:'14px', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>Nem sikerült</button>
          <button onClick={doWin} style={{ flex:1, padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>Megvan! \U0001f389</button>
        </div>
      )}
    </div>
  );
}

function SohanemGame({ gameIdx, challenger, onAdvance }) {
  const card = SOHANEM_CARDS[gameIdx % SOHANEM_CARDS.length];
  const cardNum = (gameIdx % SOHANEM_CARDS.length) + 1;
  const total = SOHANEM_CARDS.length;
  const levelMap = { alap:{label:'ALAP',color:T.mint,emoji:'\U0001f336'}, kozepes:{label:'KÖZEPES',color:T.yellow,emoji:'\U0001f525'}, vad:{label:'VAD',color:T.coral,emoji:'\U0001f525'} };
  const lv = levelMap[card.l] || levelMap.alap;
  const backColors = ['#5BA0DB','#E985B8','#F4C95A'];
  const doIgaz = () => onAdvance && onAdvance(challenger ? {[challenger.id]:1} : {});
  const doNem = () => onAdvance && onAdvance({});

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:12, width:'100%' }}>
      <div style={{ position:'relative', width:'100%', paddingTop:'115%' }}>
        <div style={{ position:'absolute', left:'3%', right:'3%', top:10, bottom:-10, background:backColors[gameIdx%backColors.length], borderRadius:22, transform:'rotate(-7deg)', transformOrigin:'center bottom' }} />
        <div style={{ position:'absolute', left:'2%', right:'2%', top:5, bottom:-5, background:backColors[(gameIdx+1)%backColors.length], borderRadius:22, transform:'rotate(5deg)', transformOrigin:'center bottom' }} />
        <div style={{ position:'absolute', inset:0, background:T.surface, borderRadius:22, boxShadow:'0 6px 32px rgba(0,0,0,0.13)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'space-between', padding:'24px 20px 20px' }}>
          <div style={{ display:'flex', alignItems:'center', gap:6, background:`${lv.color}20`, borderRadius:999, padding:'6px 14px' }}>
            <span style={{ fontSize:14 }}>{lv.emoji}</span>
            <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:lv.color, letterSpacing:'0.06em' }}>{lv.label}</span>
          </div>
          <div style={{ textAlign:'center', padding:'0 8px' }}>
            <div style={{ fontFamily:T.font, fontSize:15, fontWeight:500, color:T.inkSoft, marginBottom:10 }}>Én még soha nem…</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, lineHeight:1.3 }}>{card.t}.</div>
          </div>
          <div style={{ fontFamily:T.font, fontSize:14, fontWeight:600, color:T.inkSoft }}>
            <span style={{ fontWeight:800, color:T.ink }}>{String(cardNum).padStart(2,'0')}</span> / {total} kártya
          </div>
        </div>
      </div>

      <div style={{ display:'flex', justifyContent:'space-between', width:'100%', padding:'0 4px' }}>
        <div>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, marginBottom:4 }}>Fűszer</div>
          <div style={{ display:'flex', gap:3 }}>
            {['alap','alap','kozepes','kozepes','vad'].map((l,i) => {
              const lvls=['alap','kozepes','vad'];
              const lit = lvls.indexOf(l) <= lvls.indexOf(card.l);
              const bc = l==='vad'?T.coral:l==='kozepes'?T.yellow:T.mint;
              return <div key={i} style={{ width:22, height:7, borderRadius:4, background:lit?bc:`${T.inkMute}28` }} />;
            })}
          </div>
        </div>
        <div style={{ textAlign:'right' }}>
          <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkSoft, marginBottom:4 }}>Vad kör</div>
          <div style={{ display:'flex', gap:3, justifyContent:'flex-end' }}>
            {[0,1,2].map(i => <div key={i} style={{ width:22, height:7, borderRadius:4, background:card.l==='vad'&&i===0?T.coral:`${T.inkMute}28` }} />)}
          </div>
        </div>
      </div>

      <div style={{ display:'flex', gap:10, width:'100%' }}>
        <button onClick={doIgaz} style={{ flex:1, padding:'14px 10px', background:T.coral, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow, lineHeight:1.3 }}>Igaz rám —{'\n'}iszom</button>
        <button onClick={doNem} style={{ flex:1, padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>Nem igaz rám</button>
      </div>
    </div>
  );
}

"""
assert INSERT_BEFORE in html, "Insertion point not found"
html = html.replace(INSERT_BEFORE, DATA_AND_GAMES + INSERT_BEFORE, 1)

# ── 3. GameContent dispatch: add otdolog + sohanem ────────────────────────
old3 = "  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n  return null;"
new3 = (
    "  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;\n"
    "  if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} />;\n"
    "  if (gameId === 'sohanem') return <SohanemGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} />;\n"
    "  return null;"
)
assert old3 in html, "Fix 3 not found"
html = html.replace(old3, new3, 1)

# ── 4. Egyéni CTA: sohanem + otdolog kivétel ──────────────────────────────
old4 = "      {currentGame.category === 'Egyéni' && scenario.cta.length > 0 && ("
new4 = "      {currentGame.category === 'Egyéni' && scenario.cta.length > 0 && currentGameId !== 'otdolog' && currentGameId !== 'sohanem' && ("
assert old4 in html, "Fix 4 not found"
html = html.replace(old4, new4, 1)

# ── 5. Version bump ───────────────────────────────────────────────────────
assert 'Verzió 5.38 · DNR · 2026.06.01 11:30' in html, "Version not found"
html = html.replace(
    'Verzió 5.38 · DNR · 2026.06.01 11:30',
    'Verzió 5.39 · DNR · 2026.06.01 12:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.39")
