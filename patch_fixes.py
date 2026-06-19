#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ──────────────────────────────────────────────────────────────
# 1. SORREND BUG FIX — turn követi az aktuális játékost
#    + ne töröljük a pendingCommit-ot átrendezéskor
# ──────────────────────────────────────────────────────────────
old = """                const shuffleOrder = () => {
                  const arr = [...players];
                  for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
                  setPlayers(arr); setPendingCommit(null);
                };
                const movePlayer = (from, to) => {
                  if (from===to) return;
                  const arr=[...players];
                  const [item]=arr.splice(from,1);
                  arr.splice(to,0,item);
                  setPlayers(arr); setPendingCommit(null);
                };"""
new = """                const reorder = (arr) => {
                  const curId = players[turn % players.length]?.id;
                  const newTurnIdx = arr.findIndex(p => p.id === curId);
                  setPlayers(arr);
                  if (newTurnIdx >= 0) setTurn(newTurnIdx);
                };
                const shuffleOrder = () => {
                  const arr = [...players];
                  for (let i=arr.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}
                  reorder(arr);
                };
                const movePlayer = (from, to) => {
                  if (from===to) return;
                  const arr=[...players];
                  const [item]=arr.splice(from,1);
                  arr.splice(to,0,item);
                  reorder(arr);
                };"""
assert old in html, "FAIL: sorrend movePlayer"
html = html.replace(old, new, 1)

# ──────────────────────────────────────────────────────────────
# 2. KÖR GYŰRŰ — round progress a maxRounds-hoz képest
#    végtelen módban piros szín + pulzálás
# ──────────────────────────────────────────────────────────────
old = """          const gamePct = (gameIdx % games.length) / Math.max(games.length, 1);
          const rOuter = 25, circOuter = +(2 * Math.PI * rOuter).toFixed(1);
          const dashOuter = +(circOuter * gamePct).toFixed(1);
          const rInner = 19, circInner = +(2 * Math.PI * rInner).toFixed(1);
          return (
            <div style={{ position:'relative', width:54, height:54, flexShrink:0 }}>
              <svg viewBox="0 0 54 54" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
                {/* Outer ring: game progress */}
                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={T.inkMute} strokeWidth="2.5" opacity="0.15" />
                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={T.mint} strokeWidth="2.5"
                  strokeDasharray={circOuter} strokeDashoffset={circOuter - dashOuter}
                  strokeLinecap="round" style={{ transition:'stroke-dashoffset 0.5s ease' }} />
                {/* Inner ring: static background */}
                <circle cx="27" cy="27" r={rInner} fill="none" stroke={T.inkMute} strokeWidth="2" opacity="0.12" />
              </svg>"""
new = """          const maxRounds = gameMeta?.maxRounds || null;
          const isInfinite = !maxRounds;
          const roundPct = maxRounds ? Math.min(1, (round - 1) / maxRounds) : 0;
          const rOuter = 25, circOuter = +(2 * Math.PI * rOuter).toFixed(1);
          const dashOuter = +(circOuter * roundPct).toFixed(1);
          const rInner = 19, circInner = +(2 * Math.PI * rInner).toFixed(1);
          const ringColor = isInfinite ? T.coral : (roundPct > 0.75 ? T.coral : roundPct > 0.5 ? T.yellow : T.mint);
          return (
            <div style={{ position:'relative', width:54, height:54, flexShrink:0 }}>
              <svg viewBox="0 0 54 54" style={{ position:'absolute', inset:0, width:'100%', height:'100%', transform:'rotate(-90deg)' }}>
                {/* Outer ring: round progress vs maxRounds */}
                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={T.inkMute} strokeWidth="2.5" opacity="0.15" />
                <circle cx="27" cy="27" r={rOuter} fill="none" stroke={ringColor} strokeWidth="2.5"
                  strokeDasharray={isInfinite ? `${circOuter * 0.15} ${circOuter * 0.85}` : circOuter}
                  strokeDashoffset={isInfinite ? 0 : circOuter - dashOuter}
                  strokeLinecap="round"
                  style={{ transition:'stroke-dashoffset 0.5s ease', animation: isInfinite ? 'spin 3s linear infinite' : 'none' }} />
                {/* Inner ring: static background */}
                <circle cx="27" cy="27" r={rInner} fill="none" stroke={T.inkMute} strokeWidth="2" opacity="0.12" />
              </svg>"""
assert old in html, "FAIL: ring code"
html = html.replace(old, new, 1)

# Add spin keyframe to CSS if not already there
spin_kf = "@keyframes spin { from{transform:rotate(-90deg)} to{transform:rotate(270deg)} }"
if "spin" not in html or "@keyframes spin" not in html:
    old_kf = "@keyframes bounceSelect"
    assert old_kf in html, "FAIL: keyframe anchor"
    html = html.replace(old_kf, spin_kf + "\n@keyframes bounceSelect", 1)

# ──────────────────────────────────────────────────────────────
# 3. ONBOARDING — első indításnál 4 lépéses bemutató
# ──────────────────────────────────────────────────────────────
# Add onboarding component before BottleApp
anchor = "// ─── APP ROUTER ───────────────────────────────────────────────"
assert anchor in html, "FAIL: APP ROUTER anchor"

onboarding_component = '''function OnboardingOverlay({ onDone }) {
  const [step, setStep] = React.useState(0);
  const steps = [
    { emoji:'🎮', title:'Üdv a Bottle of Heroes-ban!', desc:'Magyar ivós társasjáték app. Válassz játékokat, add hozzá a barátokat, és kezdődjön a buli!' },
    { emoji:'👥', title:'Játékosok hozzáadása', desc:'Adj hozzá legalább 2 játékost. Profilokat is létrehozhatsz a statisztikák követéséhez.' },
    { emoji:'🎯', title:'Játékok kiválasztása', desc:'Válassz a 30+ játék közül. Szűrhetsz nehézség és kategória szerint. A sorrend te állítod be.' },
    { emoji:'⚙️', title:'Beállítások és játék!', desc:'Állítsd be a nehézséget, módokat és max köröket — aztán nyomd meg a Start gombot. Jó mulatást! 🍺' },
  ];
  const s = steps[step];
  const isLast = step === steps.length - 1;
  return (
    <div style={{ position:'fixed', inset:0, zIndex:9999, background:'rgba(14,14,24,0.75)', display:'flex', alignItems:'flex-end', justifyContent:'center', padding:'0 16px 40px', backdropFilter:'blur(6px)' }}>
      <div style={{ background:T.surface, borderRadius:24, padding:'28px 24px 24px', width:'100%', maxWidth:420, display:'flex', flexDirection:'column', gap:20, animation:'popIn .35s cubic-bezier(.2,.9,.3,1.3)', boxShadow:'0 24px 64px rgba(0,0,0,0.35)' }}>
        {/* Progress dots */}
        <div style={{ display:'flex', gap:6, justifyContent:'center' }}>
          {steps.map((_,i) => (
            <div key={i} style={{ width: i===step ? 20 : 6, height:6, borderRadius:3, background: i===step ? T.mint : T.surfaceMuted, transition:'all .25s' }} />
          ))}
        </div>
        {/* Content */}
        <div style={{ textAlign:'center' }}>
          <div style={{ fontSize:52, lineHeight:1, marginBottom:16 }}>{s.emoji}</div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink, marginBottom:10 }}>{s.title}</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft, lineHeight:1.65 }}>{s.desc}</div>
        </div>
        {/* Buttons */}
        <div style={{ display:'flex', gap:10 }}>
          {step > 0 && (
            <button onClick={() => setStep(s => s-1)} style={{ flex:1, padding:'13px 0', borderRadius:16, border:`1.5px solid ${T.inkMute}30`, background:T.surface, color:T.inkSoft, fontFamily:T.font, fontWeight:700, fontSize:14, cursor:'pointer' }}>Vissza</button>
          )}
          <button onClick={() => { if (isLast) { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} onDone(); } else setStep(s => s+1); }} style={{ flex:2, padding:'14px 0', borderRadius:16, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:16, cursor:'pointer', boxShadow:`0 4px 16px ${T.mint}44` }}>
            {isLast ? 'Kezdjük! 🚀' : 'Tovább →'}
          </button>
        </div>
        {!isLast && (
          <button onClick={() => { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} onDone(); }} style={{ background:'none', border:'none', fontFamily:T.font, fontSize:12, color:T.inkMute, cursor:'pointer', padding:'4px 0' }}>Kihagyás</button>
        )}
      </div>
    </div>
  );
}

'''
html = html.replace(anchor, onboarding_component + anchor, 1)

# Add onboarding state to BottleApp and render it
old_screen_state = "  const [screen, setScreen] = useState(() => _initRoom ? 'observer' : 'home');"
new_screen_state = """  const [screen, setScreen] = useState(() => _initRoom ? 'observer' : 'home');
  const [showOnboarding, setShowOnboarding] = React.useState(() => {
    try { return !localStorage.getItem('boh_onboarded') && !_initRoom; } catch(e) { return false; }
  });"""
assert old_screen_state in html, "FAIL: screen state"
html = html.replace(old_screen_state, new_screen_state, 1)

# Render onboarding overlay in BottleApp return — find the opening return div
old_app_return = "  const go = (next) => {"
new_app_return = """  const go = (next) => {"""
# Find the app's JSX return and add onboarding there
# Look for the outermost app div
old_render = "        {screen==='home'     && <HomeScreen"
new_render = """        {showOnboarding && <OnboardingOverlay onDone={() => setShowOnboarding(false)} />}
        {screen==='home'     && <HomeScreen"""
assert old_render in html, "FAIL: HomeScreen render"
html = html.replace(old_render, new_render, 1)

# ── version bump
old_v = "const APP_VERSION = 'v9.273';"
new_v = "const APP_VERSION = 'v9.274';"
assert old_v in html, "FAIL: version"
html = html.replace(old_v, new_v, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.274 — sorrend bugfix, körgyűrű round progress, onboarding")
