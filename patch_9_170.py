#!/usr/bin/env python3
"""patch_9_170.py — Tabu → Csapat egyéni (mindkettő kap/iszik); Mist téma eltávolítása"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.169';" in content
content = content.replace("const APP_VERSION = 'v9.169';", "const APP_VERSION = 'v9.170';")

# ── 1. Tabu: back to Csapat ──
OLD_TABU_DEF = "{ id:'tabu',     roundTime:'fast', name:'Tabu Szó',         difficulty:'nehéz',   category:'Páros',  emoji:'🚫', img:IMGS['tabu_icon.png'], symbol:IMGS['tabu_symbol.png'], color:'#EF4444', desc:'Páros párharc: mindkét játékos magyaráz egy szót, a másik talál. Aki sikeresen elmagyarázta +1 pont, aki nem — iszik.' }"
NEW_TABU_DEF = "{ id:'tabu',     roundTime:'fast', name:'Tabu Szó',         difficulty:'nehéz',   category:'Csapat', emoji:'🚫', img:IMGS['tabu_icon.png'], symbol:IMGS['tabu_symbol.png'], color:'#EF4444', desc:'Az app kisorsol egy játékost akinek el kell magyaráznia egy szót 3 tiltott szó nélkül. Ha a csapat kitalálja mindenki +1 pont, ha nem — mindenki iszik.' }"
assert OLD_TABU_DEF in content, "Tabu game def not found"
content = content.replace(OLD_TABU_DEF, NEW_TABU_DEF, 1)

# ── 2. Restore tabu to Csapat "Ki rontott?" exclusion ──
OLD_CSAPAT_EXCL = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && ("
NEW_CSAPAT_EXCL = "currentGameId !== 'powerhour' && currentGameId !== 'ovfj' && currentGameId !== 'tabu' && ("
assert OLD_CSAPAT_EXCL in content, "Csapat exclusion not found"
content = content.replace(OLD_CSAPAT_EXCL, NEW_CSAPAT_EXCL, 1)

# ── 3. Remove opponent prop from TabuGame render call ──
OLD_TABU_RENDER = "if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;"
NEW_TABU_RENDER = "if (gameId === 'tabu')     return <TabuGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;"
assert OLD_TABU_RENDER in content, "TabuGame render not found"
content = content.replace(OLD_TABU_RENDER, NEW_TABU_RENDER, 1)

# ── 4. Remove tabu from Páros CTA exclusion ──
OLD_PAROS_EXCL = "currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && currentGameId !== 'tabu' && ("
NEW_PAROS_EXCL = "currentGameId !== 'szamsor' && currentGameId !== 'reakcio' && currentGameId !== 'ritmus' && ("
assert OLD_PAROS_EXCL in content, "Páros CTA exclusion not found"
content = content.replace(OLD_PAROS_EXCL, NEW_PAROS_EXCL, 1)

# ── 5. Replace TabuGame with simple single-player Csapat version ──
# Find start of TabuGame component
OLD_TABU_COMPONENT_START = "// ── Tabu Szó (Páros duel) ──────────────────────────────────────────────────────\nfunction TabuGame({ gameIdx, challenger, opponent, onAdvance, onResult }) {"
assert OLD_TABU_COMPONENT_START in content, "TabuGame component start not found"

# Find the end by locating the next component comment after TabuGame
COMPONENT_END_MARKER = "\n// ── Gyors Matek ────────────────────────────────────────────────────────────────"
idx_start = content.index(OLD_TABU_COMPONENT_START)
idx_end = content.index(COMPONENT_END_MARKER, idx_start)

OLD_TABU_FULL = content[idx_start:idx_end]

NEW_TABU_COMPONENT = """// ── Tabu Szó ───────────────────────────────────────────────────────────────────
function TabuGame({ gameIdx, challenger, onAdvance, onResult }) {
  const q = TABU_SHUFFLED[gameIdx % TABU_SHUFFLED.length];
  const [phase, setPhase] = useState('ready');
  const [timeLeft, setTimeLeft] = useState(30);
  const ivRef = useRef(null);
  const advancedRef = useRef(false);

  useEffect(() => () => clearInterval(ivRef.current), []);

  const start = () => {
    setPhase('playing');
    const end = Date.now() + 30000;
    clearInterval(ivRef.current);
    ivRef.current = setInterval(() => {
      const rem = Math.max(0, (end - Date.now()) / 1000);
      setTimeLeft(Math.ceil(rem));
      if (rem <= 0) { clearInterval(ivRef.current); setPhase('done'); }
    }, 100);
  };

  const handleResult = (won) => {
    if (advancedRef.current) return;
    advancedRef.current = true;
    clearInterval(ivRef.current);
    if (won) {
      onResult && onResult({ correct: true, playerName: challenger?.name||'', drinks:0, subtitle: 'Mindenki kitalálta — mindenki +1 pont!' });
      onAdvance && onAdvance({}, {});  // everyone gets +1 via result banner
    } else {
      onResult && onResult({ correct: false, playerName: challenger?.name||'', drinks:1, subtitle: 'Nem sikerült — mindenki iszik 1-et!' });
      onAdvance && onAdvance({}, {});
    }
  };

  if (phase === 'ready') return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div style={{ fontSize:52 }}>🚫</div>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>{challenger?.name} magyaráz!</div>
      <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, textAlign:'center' }}>30 mp alatt el kell magyarázni a szót a 3 tiltott szó nélkül. Ha kitalálják — mindenki kap pontot, ha nem — mindenki iszik.</div>
      <button onClick={start} style={{ width:'100%', padding:'16px 0', background:T.mint, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:17, cursor:'pointer' }}>Megmutat!</button>
    </div>
  );

  return (
    <div style={{ display:'flex', flexDirection:'column', gap:12 }}>
      <div style={{ textAlign:'center', fontFamily:T.font, fontWeight:900, fontSize:28, color: timeLeft <= 5 ? T.coral : T.mint }}>
        {phase === 'done' ? '⏰' : timeLeft + 's'}
      </div>
      <div style={{ background:'#1B2340', borderRadius:20, padding:'20px', textAlign:'center' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', marginBottom:12 }}>{q.word}</div>
        <div style={{ fontFamily:T.font, fontSize:11, color:'#94A3B8', textTransform:'uppercase', letterSpacing:'0.08em', marginBottom:8 }}>🚫 Tiltott szavak</div>
        <div style={{ display:'flex', gap:8, justifyContent:'center', flexWrap:'wrap' }}>
          {q.taboo.map((t, i) => <div key={i} style={{ padding:'5px 14px', background:T.coral+'33', borderRadius:999, fontFamily:T.font, fontWeight:700, fontSize:14, color:T.coral, border:`1.5px solid ${T.coral}44` }}>{t}</div>)}
        </div>
      </div>
      <div style={{ display:'flex', gap:10 }}>
        <button onClick={() => handleResult(true)} style={{ flex:1, padding:'14px 0', background:T.mint, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✓ Kitalálták</button>
        <button onClick={() => handleResult(false)} style={{ flex:1, padding:'14px 0', background:T.coral, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>✗ Nem / Szabálysértés</button>
      </div>
    </div>
  );
}"""

content = content[:idx_start] + NEW_TABU_COMPONENT + content[idx_end:]

# ── 6. Remove mist from splash themes ──
OLD_SPLASH_MIST = "\n    mist: { bg:'#B8C8D8', deep:'#8FA8BC', ring:'rgba(60,100,150,0.3)',  glow:'rgba(70,110,160,0.65)' },"
assert OLD_SPLASH_MIST in content, "splash mist not found"
content = content.replace(OLD_SPLASH_MIST, "", 1)

# ── 7. Remove mist from THEMES object ──
OLD_MIST_THEME = """  mist: {
    bg: '#B8C8D8',
    bgSoft: '#C8D6E4',
    bgDeep: '#8FA8BC',
    surface: 'rgba(255,255,255,0.72)',
    surfaceMuted: 'rgba(255,255,255,0.45)',
    ink: '#1C2B38',
    inkSoft: '#3D5268',
    inkMute: '#7A96AA',
    mint: '#3DA888',
    mintSoft: '#C8EAE0',
    mintDeep: '#2D9070',
    coral: '#D96060',
    coralSoft: '#F2D8D8',
    purple: '#6A80C8',
    yellow: '#D4A830',
    blue: '#4A80CC',
    pink: '#C870A8',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(20,40,60,0.06), 0 6px 20px rgba(20,40,60,0.10)',
    shadowLift: '0 4px 0 rgba(20,40,60,0.08), 0 12px 32px rgba(20,40,60,0.14)',
    bgShapes: true,
  },
  sky: {"""
NEW_WITHOUT_MIST = """  sky: {"""
assert OLD_MIST_THEME in content, "mist THEMES block not found"
content = content.replace(OLD_MIST_THEME, NEW_WITHOUT_MIST, 1)

# ── 8. Remove mist from settings theme selector ──
OLD_THEME_BTNS = "[['warm','☀️',t('themeWarm')],['sky','🌤️',t('themeSky')],['dark','🌙',t('themeDark')],['mist','🌊','Mist']]"
NEW_THEME_BTNS = "[['warm','☀️',t('themeWarm')],['sky','🌤️',t('themeSky')],['dark','🌙',t('themeDark')]]"
assert OLD_THEME_BTNS in content, "theme btns not found"
content = content.replace(OLD_THEME_BTNS, NEW_THEME_BTNS, 1)

# ── 9. Remove MistBackground component and bgShapes usage ──
OLD_MIST_BG_COMPONENT = """// ─── APP ROUTER ───────────────────────────────────────────────
function MistBackground() {
  return React.createElement('div', {
    style: {
      position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none',
      background: 'linear-gradient(145deg, #C8D8E8 0%, #A8BED0 35%, #90AABE 60%, #B0C4D4 100%)',
      overflow: 'hidden',
    }
  },
    React.createElement('svg', {
      style: { position:'absolute', inset:0, width:'100%', height:'100%' },
      viewBox: '0 0 390 844', preserveAspectRatio: 'xMidYMid slice',
      xmlns: 'http://www.w3.org/2000/svg',
    },
      React.createElement('defs', null,
        React.createElement('filter', { id:'mist-blur' },
          React.createElement('feGaussianBlur', { stdDeviation: '28' })
        )
      ),
      // Large curved blob top-right
      React.createElement('ellipse', { cx:'340', cy:'80', rx:'220', ry:'160', fill:'rgba(255,255,255,0.18)', filter:'url(#mist-blur)' }),
      // Elegant S-curve shape (paper fold)
      React.createElement('path', {
        d: 'M -40 200 C 80 100, 200 320, 160 480 C 120 640, 320 700, 420 620',
        fill: 'none', stroke: 'rgba(255,255,255,0.55)', strokeWidth: '1.5',
      }),
      React.createElement('path', {
        d: 'M -20 220 C 100 120, 220 340, 180 500 C 140 660, 340 720, 440 640',
        fill: 'none', stroke: 'rgba(255,255,255,0.25)', strokeWidth: '0.8',
      }),
      // Second fold
      React.createElement('path', {
        d: 'M 200 -20 C 360 60, 280 260, 180 360 C 80 460, 200 640, 420 760',
        fill: 'none', stroke: 'rgba(255,255,255,0.40)', strokeWidth: '1.2',
      }),
      // Soft bottom blob
      React.createElement('ellipse', { cx:'80', cy:'780', rx:'200', ry:'140', fill:'rgba(255,255,255,0.12)', filter:'url(#mist-blur)' }),
      // Subtle surface sheen top
      React.createElement('path', {
        d: 'M 0 0 C 120 40, 280 10, 390 60 L 390 0 Z',
        fill: 'rgba(255,255,255,0.14)',
      }),
    )
  );
}

function BottleApp() {"""
NEW_WITHOUT_MIST_BG = """// ─── APP ROUTER ───────────────────────────────────────────────
function BottleApp() {"""
assert OLD_MIST_BG_COMPONENT in content, "MistBackground component not found"
content = content.replace(OLD_MIST_BG_COMPONENT, NEW_WITHOUT_MIST_BG, 1)

# ── 10. Restore simple background in app root ──
OLD_APP_ROOT = "background: T.bgShapes ? 'transparent' : T.bg }} data-theme={appTheme}>\n      {T.bgShapes && <MistBackground />}"
NEW_APP_ROOT = "background:T.bg }} data-theme={appTheme}>"
assert OLD_APP_ROOT in content, "app root bgShapes not found"
content = content.replace(OLD_APP_ROOT, NEW_APP_ROOT, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.170 ready")
