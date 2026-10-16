# v10.425 — DNR Games fejléc: a Beállítások (fogaskerék) helyett „Kiegészítők" gomb.
# Első kiegészítő: Betűsorsoló. A TESZT DB-s safe-area diagnosztika a Kiegészítők lap aljára költözik.
import re
f = 'app.src.html'; s = open(f, encoding='utf8').read()
def rep(old, new, cnt=1):
    global s
    assert s.count(old) == cnt, (s.count(old), old[:80])
    s = s.replace(old, new)

# 1) HomeScreen: splash/hang állapot ki, showSettings → showTools
rep("""  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const [sndOn, setSndOn] = React.useState(() => { try { return localStorage.getItem('boh_snd') !== '0'; } catch(e) { return true; } });
  const toggleSnd = () => { const n = !sndOn; setSndOn(n); try { localStorage.setItem('boh_snd', n ? '1' : '0'); } catch(e) {} if (n && typeof window.bohSound === 'function') window.bohSound('zsulli'); };
  const toggleSplash = () => {
    const next = !splashOn;
    setSplashOn(next);
    try { localStorage.setItem('boh_splash', next ? '1' : '0'); } catch(e) {}
  };
""", "")
rep("  const [showSettings, setShowSettings] = React.useState(false);\n",
    "  const [showTools, setShowTools] = React.useState(false);   // v10.425: a Beállítások helyén a Kiegészítők\n")

# 2) a fogaskerék gomb → Kiegészítők gomb
i0 = s.index("          {/* v10.410: a hosszú nyomásos admin-belépő a DNR KÖZPONT fejlécébe költözött")
i1 = s.index("          <div style={{ width:1, background:T.inkMute+'25', margin:'12px 0' }} />", i0)
s = s[:i0] + """          {/* v10.425: a Beállítások (Splash, Hangeffektek) megszűnt — helyette a játék-KIEGÉSZÍTŐK
              (GameToolsSheet, első: Betűsorsoló). */}
          <button data-home-tools onClick={() => setShowTools(true)} aria-label="Kiegészítők"
            style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer', WebkitTapHighlightColor:'transparent', userSelect:'none' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><rect x="3.5" y="3.5" width="17" height="17" rx="4.5"/><circle cx="8.5" cy="8.5" r="1.3" fill={T.ink} stroke="none"/><circle cx="15.5" cy="8.5" r="1.3" fill={T.ink} stroke="none"/><circle cx="12" cy="12" r="1.3" fill={T.ink} stroke="none"/><circle cx="8.5" cy="15.5" r="1.3" fill={T.ink} stroke="none"/><circle cx="15.5" cy="15.5" r="1.3" fill={T.ink} stroke="none"/></svg>
          </button>
""" + s[i1:]

# 3) a Beállítások lap → Kiegészítők lap; a diagnosztika átköltözik
j0 = s.index("        {showSettings && (\n          <SheetOverlay onClose={() => setShowSettings(false)} title={t('settings')}>")
j1 = s.index("        <div className=\"home-actions\">", j0)
block = s[j0:j1]
d0 = block.index("              {(() => {\n                try { if (!(typeof window.isTestDb")
d1 = block.index("              })()}\n", d0) + len("              })()}\n")
diag = block[d0:d1]
s = s[:j0] + "        {showTools && <GameToolsSheet onClose={() => setShowTools(false)} />}\n" + s[j1:]

# 4) modul-szintű komponensek a HomeScreen elé
diag2 = '\n'.join(l[8:] if l.startswith('        ') else l for l in diag.split('\n'))
tools = r"""// ─── JÁTÉK-KIEGÉSZÍTŐK (v10.425) ─────────────────────────────
// A DNR Games fejlécében a régi Beállítások helyén. Önálló segédeszközök, amik
// NEM játékok (nincs pont, nincs korty) — egy asztal mellett jól jönnek.
// Új kiegészítő: egy sor a GAME_TOOLS-ba + egy ág a GameToolsSheet-ben.
const GAME_TOOLS = [
  { id:'letter', name:'Betűsorsoló', emoji:'🔤', sub:'Véletlen betű Ország-Városhoz és szójátékokhoz' },
];
// A betűkészletek. Az „Alap" UGYANAZ, mint az Ország-Város húzása (OVFJ_LETTERS) —
// függvényként, mert az a konstans lejjebb van deklarálva (betöltéskor TDZ lenne).
const LETTER_SETS = [
  { id:'basic', label:'Alap',       sub:'Q, W, X, Y nélkül', letters: () => OVFJ_LETTERS },
  { id:'full',  label:'Teljes A–Z', sub:'mind a 26 betű',    letters: () => 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('') },
];
const LETTER_SPIN_TICKS = 14;   // a pörgés lépései; a köz egyre nő (lassuló tárcsa)

function LetterDrawTool() {
  const lsGet = (k, d) => { try { const v = localStorage.getItem(k); return v == null ? d : v; } catch (e) { return d; } };
  const lsSet = (k, v) => { try { localStorage.setItem(k, v); } catch (e) {} };
  const [setId, setSetId] = React.useState(() => LETTER_SETS.some(x => x.id === lsGet('boh_letter_set', '')) ? lsGet('boh_letter_set', 'basic') : 'basic');
  const [noRepeat, setNoRepeat] = React.useState(() => lsGet('boh_letter_norep', '1') !== '0');
  const [used, setUsed] = React.useState([]);     // ebben a munkamenetben kihúzott betűk, sorrendben
  const [face, setFace] = React.useState(null);   // ami épp a lapon áll (pörgés közben is)
  const [spinning, setSpinning] = React.useState(false);
  const timers = React.useRef([]);
  React.useEffect(() => () => timers.current.forEach(clearTimeout), []);

  const letters = (LETTER_SETS.find(x => x.id === setId) || LETTER_SETS[0]).letters();
  const pool = noRepeat ? letters.filter(l => !used.includes(l)) : letters;
  const exhausted = noRepeat && pool.length === 0;

  const draw = () => {
    if (spinning || exhausted) return;
    const final = pool[Math.floor(Math.random() * pool.length)];
    setSpinning(true);
    let t = 0;
    for (let i = 0; i < LETTER_SPIN_TICKS; i++) {
      t += 40 + i * 9;
      const last = i === LETTER_SPIN_TICKS - 1;
      // a pörgés közben se mutassa kétszer egymás után ugyanazt (v10.418 tanulsága)
      timers.current.push(setTimeout(() => {
        if (last) {
          setFace(final); setSpinning(false);
          setUsed(u => [...u, final]);
          try { navigator.vibrate && navigator.vibrate(25); } catch (e) {}
        } else {
          setFace(prev => { const c = letters.filter(l => l !== prev && l !== final); return c[Math.floor(Math.random() * c.length)] || final; });
        }
      }, t));
    }
  };
  const reset = () => { if (spinning) return; setUsed([]); setFace(null); };
  const pickSet = (id) => { if (spinning || id === setId) return; setSetId(id); lsSet('boh_letter_set', id); setUsed([]); setFace(null); };
  const toggleNoRepeat = () => { const n = !noRepeat; setNoRepeat(n); lsSet('boh_letter_norep', n ? '1' : '0'); };

  return (
    <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:16 }}>
      <div data-letter-face aria-live="polite"
        style={{ width:176, height:176, borderRadius:36, display:'flex', alignItems:'center', justifyContent:'center',
                 background: face ? T.mint : T.bgSoft, boxShadow: face ? `0 6px 0 ${T.mintDeep || T.mint}99, 0 16px 34px ${T.mint}55` : 'none',
                 border: face ? 'none' : `2.5px dashed ${T.inkMute}55`, transition:'background .2s',
                 fontFamily:T.font, fontWeight:900, fontSize: face ? 112 : 72, lineHeight:1,
                 color: face ? '#fff' : T.inkMute, transform: spinning ? 'scale(0.96)' : 'scale(1)' }}>
        {face || '?'}
      </div>
      <div style={{ width:'100%' }}>
        <PrimaryButton onClick={exhausted ? reset : draw} disabled={spinning}>
          <span data-letter-draw>{exhausted ? 'Minden betű elfogyott — újrakezdés' : spinning ? 'Sorsolás…' : face ? 'Új betű' : 'Sorsolás'}</span>
        </PrimaryButton>
      </div>

      <div style={{ width:'100%', display:'flex', gap:8 }}>
        {LETTER_SETS.map(x => {
          const on = x.id === setId;
          return (
            <button key={x.id} data-letter-set={x.id} aria-pressed={on} onClick={() => pickSet(x.id)}
              style={{ flex:1, padding:'10px 8px', borderRadius:14, cursor:'pointer', textAlign:'center',
                       border: on ? `2px solid ${T.mint}` : `1.5px solid ${T.inkMute}30`, background: on ? T.mintSoft : T.surface,
                       WebkitTapHighlightColor:'transparent' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color: on ? T.mint : T.ink }}>{x.label}</div>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkSoft, marginTop:2 }}>{x.sub}</div>
            </button>
          );
        })}
      </div>
      <div style={{ width:'100%', display:'flex', alignItems:'center', justifyContent:'space-between', gap:12 }}>
        <div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Ne ismételjen</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>Egy betű csak egyszer jön, amíg újra nem kezded</div>
        </div>
        <span data-letter-norepeat={noRepeat ? '1' : '0'}><Toggle on={noRepeat} onChange={toggleNoRepeat} /></span>
      </div>

      <div style={{ width:'100%', borderTop:`1px solid ${T.inkMute}22`, paddingTop:12 }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:8 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, letterSpacing:'0.08em', color:T.inkSoft, textTransform:'uppercase' }}>
            Kihúzott betűk{noRepeat ? ` · ${used.length}/${letters.length}` : ''}
          </div>
          {used.length > 0 && (
            <button data-letter-reset onClick={reset} disabled={spinning}
              style={{ border:'none', background:'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.coral, padding:'2px 4px' }}>
              Újrakezdés
            </button>
          )}
        </div>
        {used.length === 0
          ? <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute }}>Még nincs kihúzott betű.</div>
          : <div style={{ display:'flex', flexWrap:'wrap', gap:6 }}>
              {used.map((l, i) => (
                <span key={i} data-letter-used
                  style={{ minWidth:30, height:30, padding:'0 6px', borderRadius:9, display:'inline-flex', alignItems:'center', justifyContent:'center',
                           background: i === used.length - 1 ? T.mint : T.bgSoft, color: i === used.length - 1 ? '#fff' : T.ink,
                           fontFamily:T.font, fontWeight:900, fontSize:14 }}>{l}</span>
              ))}
            </div>}
      </div>
    </div>
  );
}

function GameToolsSheet({ onClose }) {
  const [toolId, setToolId] = React.useState(null);
  const tool = GAME_TOOLS.find(x => x.id === toolId);
  return (
    <SheetOverlay onClose={onClose} title={tool ? tool.name : 'Kiegészítők'}>
      <div data-game-tools={toolId || 'list'} style={{ padding:'0 20px 28px' }}>
        {tool ? (
          <React.Fragment>
            <button data-tool-back onClick={() => setToolId(null)}
              style={{ display:'inline-flex', alignItems:'center', gap:4, border:'none', background:'transparent', cursor:'pointer', padding:'2px 0', marginBottom:12, fontFamily:T.font, fontWeight:800, fontSize:13, color:T.inkSoft }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke={T.inkSoft} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M15 18l-6-6 6-6"/></svg>
              Kiegészítők
            </button>
            {tool.id === 'letter' && <LetterDrawTool />}
          </React.Fragment>
        ) : (
          <React.Fragment>
            <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginBottom:14 }}>Segédeszközök a játékokhoz — pont és korty nélkül.</div>
            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {GAME_TOOLS.map(x => (
                <button key={x.id} data-tool-open={x.id} onClick={() => setToolId(x.id)}
                  style={{ display:'flex', alignItems:'center', gap:14, width:'100%', padding:'12px 14px', borderRadius:18, border:`1.5px solid ${T.inkMute}22`,
                           background:T.surface, boxShadow:T.shadow, cursor:'pointer', textAlign:'left', WebkitTapHighlightColor:'transparent' }}>
                  <span style={{ width:46, height:46, borderRadius:14, background:T.mintSoft, display:'flex', alignItems:'center', justifyContent:'center', fontSize:24, flexShrink:0 }}>{x.emoji}</span>
                  <span style={{ flex:1, minWidth:0 }}>
                    <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{x.name}</span>
                    <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>{x.sub}</span>
                  </span>
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.inkMute} strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9 18l6-6-6-6"/></svg>
                </button>
              ))}
            </div>
            {/* Safe-area / státuszsáv diagnosztika — csak TESZT DB módban (v10.425 előtt a
                Beállítások alján). Visszatérő hibaosztály, leírás: docs/safe-area.md */}
""" + diag2 + r"""          </React.Fragment>
        )}
      </div>
    </SheetOverlay>
  );
}

"""
rep("function HomeScreen({ go, onStartGame,", tools + "function HomeScreen({ go, onStartGame,")
assert 'showSettings' not in s[s.index('function HomeScreen'):s.index('function PlayersScreen')]
rep("const APP_VERSION = 'v10.424';", "const APP_VERSION = 'v10.425';")
open(f, 'w', encoding='utf8').write(s)
print('ok')
