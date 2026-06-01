# -*- coding: utf-8 -*-
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Scenarios: rulett cta [] ───────────────────────────────────────────────
assert "cta:['Kemény — iszom','Megúsztam!']" in html, "Step 1 not found"
html = html.replace(
    "cta:['Kemény — iszom','Megúsztam!']",
    "cta:[]",
    1
)

# ── 2. Scenarios: tapper cta [] ──────────────────────────────────────────────
assert "cta:['Én engedtem el','Ő engedte el']" in html, "Step 2 not found"
html = html.replace(
    "cta:['Én engedtem el','Ő engedte el']",
    "cta:[]",
    1
)

# ── 3. RulettGame: add onAdvance prop ─────────────────────────────────────────
html = html.replace(
    'function RulettGame({ gameIdx }) {',
    'function RulettGame({ gameIdx, onAdvance }) {',
    1
)

# ── 4. RulettGame: flip cards to 2 pia + 1 fire ──────────────────────────────
html = html.replace(
    "    const cards = ['fire','fire','pia'];",
    "    const cards = ['pia','pia','fire'];",
    1
)

# ── 5. RulettGame: update outcome chips (🔥2×tűz → 🍺2×pia, 🥃1×pia → 🔥1×tűz)
old5 = "          <span style={{ fontSize:16 }}>🔥</span>\n          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#D05040' }}>2× tűz</span>"
new5 = "          <span style={{ fontSize:16 }}>🍺</span>\n          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#50A882' }}>2× pia</span>"
assert old5 in html, "Step 5a not found"
html = html.replace(old5, new5, 1)

old5b = "          <span style={{ fontSize:16 }}>🥃</span>\n          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#50A882' }}>1× pia</span>"
new5b = "          <span style={{ fontSize:16 }}>🔥</span>\n          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:'#D05040' }}>1× tűz</span>"
assert old5b in html, "Step 5b not found"
html = html.replace(old5b, new5b, 1)

# ── 6. RulettGame: fan layout → horizontal row ───────────────────────────────
old6_fan_start = "      {/* Card fan */}\n      <div style={{ position:'relative', width:'100%', height:210 }}>"
new6_fan_start = "      {/* Horizontal card row */}\n      <div style={{ display:'flex', gap:14, justifyContent:'center' }}>"
assert old6_fan_start in html, "Step 6 fan start not found"
html = html.replace(old6_fan_start, new6_fan_start, 1)

# Replace the absolute positioning style with flex item style
old6_style = (
    "              style={{\n"
    "                position:'absolute', left:'50%', bottom:0,\n"
    "                marginLeft:-60, width:120, height:168,\n"
    "                transformOrigin:'bottom center',\n"
    "                transform:`rotate(${ANGLES[i]}deg)${isSelected ? ' scale(1.06) translateY(-6px)' : ''}`,\n"
    "                zIndex: isSelected ? 5 : i===1 ? 2 : 1,\n"
    "                cursor: picked===null ? 'pointer' : 'default',\n"
    "                transition:'transform .25s',\n"
    "                borderRadius:16,"
)
new6_style = (
    "              style={{\n"
    "                width:104, height:148,\n"
    "                cursor: picked===null ? 'pointer' : 'default',\n"
    "                transition:'transform .2s',\n"
    "                transform: isSelected ? 'scale(1.1) translateY(-8px)' : 'scale(1)',\n"
    "                borderRadius:16,"
)
assert old6_style in html, "Step 6 style not found"
html = html.replace(old6_style, new6_style, 1)

# Update fontSize inside card from 42→40 and 48→44
html = html.replace(
    "<div style={{ fontSize:42, animation:'burstPop .3s' }}>{res === 'pia' ? '🍺' : '🔥'}</div>",
    "<div style={{ fontSize:40, animation:'burstPop .3s' }}>{res === 'pia' ? '🍺' : '🔥'}</div>",
    1
)
html = html.replace(
    "                <span style={{ fontFamily:'Georgia,serif', fontWeight:900, fontSize:48, color:'rgba(255,255,255,0.5)' }}>?</span>",
    "                <span style={{ fontFamily:'Georgia,serif', fontWeight:900, fontSize:44, color:'rgba(255,255,255,0.5)' }}>?</span>",
    1
)

# Fix result text color (pia=bad, fire=good) and add Következő button
old6_result = (
    "      {/* Result text */}\n"
    "      {result && (\n"
    "        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color: result==='pia' ? '#50A882' : '#D05040', animation:'popIn .3s', textAlign:'center' }}>\n"
    "          {result === 'pia' ? '🍺 Pia! Megúsztad!' : '🔥 Tűz! Iszol!'}\n"
    "        </div>\n"
    "      )}"
)
new6_result = (
    "      {/* Result text */}\n"
    "      {result && (\n"
    "        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:16, color: result==='pia' ? '#D05040' : '#50A882', animation:'popIn .3s', textAlign:'center' }}>\n"
    "          {result === 'pia' ? '🍺 Pia! Iszol!' : '🔥 Tűz! Megúsztad!'}\n"
    "        </div>\n"
    "      )}\n"
    "\n"
    "      {/* Next game button */}\n"
    "      {result && (\n"
    "        <button onClick={() => onAdvance && onAdvance({})} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>\n"
    "          Következő játék →\n"
    "        </button>\n"
    "      )}"
)
assert old6_result in html, "Step 6 result not found"
html = html.replace(old6_result, new6_result, 1)

# ── 7. Remove ANGLES constant ────────────────────────────────────────────────
html = html.replace("\n  const ANGLES = [-22, 0, 22];\n", "\n", 1)

# ── 8. GameContent: pass onAdvance to RulettGame ─────────────────────────────
html = html.replace(
    "  if (gameId === 'rulett') return <RulettGame key={gameIdx} gameIdx={gameIdx} />;",
    "  if (gameId === 'rulett') return <RulettGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;",
    1
)

# ── 9. TapperGame: add onAdvance prop ─────────────────────────────────────────
html = html.replace(
    'function TapperGame({ gameIdx, challenger, opponent }) {',
    'function TapperGame({ gameIdx, challenger, opponent, onAdvance }) {',
    1
)

# ── 10. TapperGame: square bigger buttons ────────────────────────────────────
old10 = "            width:104, height:104, borderRadius:'50%',"
new10 = "            width:130, height:130, borderRadius:18,"
assert old10 in html, "Step 10 not found"
html = html.replace(old10, new10, 1)

# ── 11. TapperGame: bigger timer bubble ──────────────────────────────────────
html = html.replace(
    "      <div style={{ width:56, height:56, borderRadius:'50%', background:T.surface, boxShadow:T.shadow, display:'flex', alignItems:'center', justifyContent:'center' }}>",
    "      <div style={{ width:80, height:80, borderRadius:'50%', background:T.surface, boxShadow:T.shadow, display:'flex', alignItems:'center', justifyContent:'center' }}>",
    1
)
html = html.replace(
    "          ? <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:22, color:timerColor, lineHeight:1 }}>{Math.ceil(countdown)}</span>",
    "          ? <span style={{ fontFamily:'monospace', fontWeight:900, fontSize:30, color:timerColor, lineHeight:1 }}>{Math.ceil(countdown)}</span>",
    1
)

# ── 12. TapperGame: add Következő button after result ────────────────────────
old12_end = (
    "      )}\n"
    "    </div>\n"
    "  );\n"
    "}\n"
    "\n"
    "function AnagrammaGame({ gameIdx, onAdvance }) {"
)
new12_end = (
    "      )}\n"
    "\n"
    "      {phase === 'done' && result !== null && (\n"
    "        <button onClick={() => {\n"
    "          const dm = {};\n"
    "          if (result === 1) dm[p2.id] = 1;\n"
    "          else if (result === 2) dm[p1.id] = 1;\n"
    "          else if (result === 'both-lose') { dm[p1.id] = 1; dm[p2.id] = 1; }\n"
    "          if(onAdvance) onAdvance(dm);\n"
    "        }} style={{ width:'100%', padding:'14px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:16, border:'none', cursor:'pointer', boxShadow:T.shadow }}>\n"
    "          Következő játék →\n"
    "        </button>\n"
    "      )}\n"
    "    </div>\n"
    "  );\n"
    "}\n"
    "\n"
    "function AnagrammaGame({ gameIdx, onAdvance }) {"
)
# Count how many TapperGame closing divs exist (there might be the "no opponent" early return too)
# We need to match the one that belongs to the main return
assert old12_end in html, "Step 12 not found"
html = html.replace(old12_end, new12_end, 1)

# ── 13. GameContent: pass onAdvance to TapperGame ────────────────────────────
html = html.replace(
    "  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} />;",
    "  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} />;",
    1
)

# ── 14. ImposztorGame: add timer states ───────────────────────────────────────
old14 = (
    "  const [votes, setVotes] = useState({});\n"
    "  const [voteStep, setVoteStep] = useState(0);"
)
new14 = (
    "  const [votes, setVotes] = useState({});\n"
    "  const [voteStep, setVoteStep] = useState(0);\n"
    "  const [timerTotal, setTimerTotal] = useState(0);\n"
    "  const [timerEnd, setTimerEnd] = useState(0);\n"
    "  const [timerLeft, setTimerLeft] = useState(0);"
)
assert old14 in html, "Step 14 not found"
html = html.replace(old14, new14, 1)

# ── 15. ImposztorGame: reset timer + add countdown effect ─────────────────────
old15 = "    setPhase('reveal'); setRevealStep(0); setHolding(false); setVotes({}); setVoteStep(0);\n  }, [gameIdx]);"
new15 = (
    "    setPhase('reveal'); setRevealStep(0); setHolding(false); setVotes({}); setVoteStep(0);\n"
    "    setTimerTotal(0); setTimerEnd(0); setTimerLeft(0);\n"
    "  }, [gameIdx]);\n"
    "\n"
    "  useEffect(() => {\n"
    "    if (!timerEnd) return;\n"
    "    const iv = setInterval(() => {\n"
    "      const left = Math.max(0, Math.ceil((timerEnd - Date.now()) / 1000));\n"
    "      setTimerLeft(left);\n"
    "      if (left <= 0) clearInterval(iv);\n"
    "    }, 200);\n"
    "    return () => clearInterval(iv);\n"
    "  }, [timerEnd]);"
)
assert old15 in html, "Step 15 not found"
html = html.replace(old15, new15, 1)

# ── 16. ImposztorGame: bigger reveal card area ────────────────────────────────
old16 = "          <div style={{ width:94, height:94, borderRadius:18, border:'2px dashed rgba(255,255,255,0.28)', background:'rgba(255,255,255,0.05)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6, padding:8 }}>"
new16 = "          <div style={{ width:'100%', minHeight:150, borderRadius:18, border:'2px dashed rgba(255,255,255,0.28)', background:'rgba(255,255,255,0.05)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8, padding:20 }}>"
assert old16 in html, "Step 16 not found"
html = html.replace(old16, new16, 1)

# Make spy/word bigger inside the reveal area
html = html.replace(
    "                  <div style={{ fontSize:26 }}>🕵️</div>\n                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:'#EF4444', letterSpacing:'0.05em' }}>IMPOSZTOR</div>",
    "                  <div style={{ fontSize:48 }}>🕵️</div>\n                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color:'#EF4444', letterSpacing:'0.05em' }}>IMPOSZTOR</div>",
    1
)
html = html.replace(
    "                  <div style={{ fontFamily:T.font, fontSize:10, color:'rgba(255,255,255,0.45)', letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:2 }}>Titkos szó</div>\n                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:'#fff' }}>{word}</div>",
    "                  <div style={{ fontFamily:T.font, fontSize:12, color:'rgba(255,255,255,0.45)', letterSpacing:'0.08em', textTransform:'uppercase', marginBottom:8 }}>Titkos szó</div>\n                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:36, color:'#fff', letterSpacing:'0.02em' }}>{word}</div>",
    1
)
html = html.replace(
    '              <svg width="34" height="34" viewBox="0 0 34 34" fill="none">',
    '              <svg width="52" height="52" viewBox="0 0 34 34" fill="none">',
    1
)

# ── 17. ImposztorGame: describe phase with timer ──────────────────────────────
old17 = (
    "  if (phase === 'describe') {\n"
    "    return (\n"
    "      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:12, alignItems:'center' }}>\n"
    "        <div style={{ background:T.surface, borderRadius:14, padding:'12px 16px', width:'100%', boxShadow:T.shadow, textAlign:'center' }}>\n"
    "          <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:6 }}>Mit kell tenni</div>\n"
    "          <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, lineHeight:1.5 }}>Mindenki mondjon <strong>egy tippet</strong> a titkos szóra (anélkül hogy kimondaná). Az Imposztor blöfföljön!</div>\n"
    "        </div>\n"
    "        <div style={{ display:'flex', flexWrap:'wrap', gap:6, justifyContent:'center' }}>\n"
    "          {players.map(p => (\n"
    "            <div key={p.id} style={{ display:'flex', alignItems:'center', gap:5, padding:'4px 10px', borderRadius:10, background:T.surfaceMuted }}>\n"
    "              <div style={{ width:18, height:18, borderRadius:'50%', background:p.color }} />\n"
    "              <div style={{ fontFamily:T.font, fontSize:12, fontWeight:600, color:T.ink }}>{p.name}</div>\n"
    "            </div>\n"
    "          ))}\n"
    "        </div>\n"
    "        <button onClick={() => setPhase('vote')} style={{ padding:'10px 26px', background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, borderRadius:14, cursor:'pointer' }}>\n"
    "          Mindenki mondott → Szavazás\n"
    "        </button>\n"
    "      </div>\n"
    "    );\n"
    "  }"
)
new17 = (
    "  if (phase === 'describe') {\n"
    "    const timerDone = timerTotal > 0 && timerLeft <= 0;\n"
    "    const timerRunning = timerTotal > 0 && timerLeft > 0;\n"
    "    return (\n"
    "      <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:14, alignItems:'center' }}>\n"
    "        <div style={{ background:T.surface, borderRadius:14, padding:'12px 16px', width:'100%', boxShadow:T.shadow, textAlign:'center' }}>\n"
    "          <div style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:6 }}>Mit kell tenni</div>\n"
    "          <div style={{ fontFamily:T.font, fontSize:14, color:T.ink, lineHeight:1.5 }}>Mindenki mondjon <strong>egy tippet</strong> a titkos szóra (anélkül hogy kimondaná). Az Imposztor blöfföljön!</div>\n"
    "        </div>\n"
    "        {timerTotal === 0 && (\n"
    "          <div style={{ display:'flex', gap:10 }}>\n"
    "            {[1,2,3].map(m => (\n"
    "              <button key={m} onClick={() => { const end=Date.now()+m*60000; setTimerTotal(m*60); setTimerEnd(end); setTimerLeft(m*60); }}\n"
    "                style={{ padding:'12px 22px', background:T.surface, border:`2px solid ${T.mint}`, color:T.mint, fontFamily:T.font, fontWeight:700, fontSize:17, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>\n"
    "                {m} perc\n"
    "              </button>\n"
    "            ))}\n"
    "          </div>\n"
    "        )}\n"
    "        {timerRunning && (\n"
    "          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>\n"
    "            <div style={{ fontFamily:'monospace', fontWeight:900, fontSize:60, color:timerLeft<=10 ? T.coral : T.mint, lineHeight:1 }}>\n"
    "              {Math.floor(timerLeft/60)}:{String(timerLeft%60).padStart(2,'0')}\n"
    "            </div>\n"
    "            <button onClick={() => setPhase('vote')}\n"
    "              style={{ padding:'8px 22px', background:'rgba(255,255,255,0.6)', border:`2px solid rgba(0,0,0,0.1)`, color:T.inkSoft, fontFamily:T.font, fontWeight:600, fontSize:14, borderRadius:14, cursor:'pointer' }}>\n"
    "              Mindenki mondott → Szavazás\n"
    "            </button>\n"
    "          </div>\n"
    "        )}\n"
    "        {timerDone && (\n"
    "          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10 }}>\n"
    "            <div style={{ fontSize:36 }}>⏱️</div>\n"
    "            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:17, color:T.mint }}>Idő lejárt!</div>\n"
    "            <button onClick={() => setPhase('vote')}\n"
    "              style={{ padding:'13px 32px', background:T.mint, border:'none', color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>\n"
    "              Szavazás →\n"
    "            </button>\n"
    "          </div>\n"
    "        )}\n"
    "      </div>\n"
    "    );\n"
    "  }"
)
assert old17 in html, "Step 17 not found"
html = html.replace(old17, new17, 1)

# ── 18. AnagrammaGame: bigger word-building slots ────────────────────────────
html = html.replace(
    "              width:38, height:44, borderRadius:8,",
    "              width:48, height:56, borderRadius:8,",
    1
)
html = html.replace(
    "              fontFamily:'Georgia,serif', fontWeight:800, fontSize:20, color:'#1B2340',",
    "              fontFamily:'Georgia,serif', fontWeight:800, fontSize:24, color:'#1B2340',",
    1
)

# ── 19. AnagrammaGame: bigger hidden tiles ────────────────────────────────────
html = html.replace(
    "            <div key={i} style={{ width:58, height:64, borderRadius:10, background:'#1B2340', boxShadow:'0 4px 0 rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center' }}>",
    "            <div key={i} style={{ width:70, height:78, borderRadius:10, background:'#1B2340', boxShadow:'0 4px 0 rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center' }}>",
    1
)
html = html.replace(
    "              <span style={{ fontSize:26, color:'rgba(255,255,255,0.25)' }}>?</span>",
    "              <span style={{ fontSize:32, color:'rgba(255,255,255,0.25)' }}>?</span>",
    1
)

# ── 20. AnagrammaGame: bigger clickable letter tiles ─────────────────────────
old20 = (
    "              <div key={i} onClick={() => handleTap(i)} style={{\n"
    "                width:58, height:64, borderRadius:10,\n"
    "                background: used ? '#C8CCD8' : wrongFlash ? '#F47060' : TILE_COLORS[i % TILE_COLORS.length],\n"
    "                boxShadow: used ? 'none' : `0 4px 0 rgba(0,0,0,0.18)`,\n"
    "                display:'flex', alignItems:'center', justifyContent:'center',\n"
    "                fontFamily:'Georgia,serif', fontWeight:900, fontSize:30, color:'#fff',"
)
new20 = (
    "              <div key={i} onClick={() => handleTap(i)} style={{\n"
    "                width:70, height:78, borderRadius:10,\n"
    "                background: used ? '#C8CCD8' : wrongFlash ? '#F47060' : TILE_COLORS[i % TILE_COLORS.length],\n"
    "                boxShadow: used ? 'none' : `0 4px 0 rgba(0,0,0,0.18)`,\n"
    "                display:'flex', alignItems:'center', justifyContent:'center',\n"
    "                fontFamily:'Georgia,serif', fontWeight:900, fontSize:36, color:'#fff',"
)
assert old20 in html, "Step 20 not found"
html = html.replace(old20, new20, 1)

# ── 21. KisebbGame: Ace always correct ───────────────────────────────────────
old21 = "    const ok = same ? null : (guess==='K' && nv<cv) || (guess==='N' && nv>cv);"
new21 = "    const ok = same ? null : nextCard.value === 'A' ? true : (guess==='K' && nv<cv) || (guess==='N' && nv>cv);"
assert old21 in html, "Step 21 not found"
html = html.replace(old21, new21, 1)

# ── 22. KisebbGame: remove active player chips at bottom ─────────────────────
old22 = (
    "      {/* Active player chips */}\n"
    "      <div style={{ display:'flex', gap:6, flexWrap:'wrap', justifyContent:'center' }}>\n"
    "        {activePids.map(pid=>{\n"
    "          const p=players.find(x=>x.id===pid);\n"
    "          const isActive = pid===currentPid;\n"
    "          return (\n"
    "            <div key={pid} style={{ display:'flex', alignItems:'center', gap:6, padding:'5px 12px', borderRadius:999, background: isActive ? 'rgba(255,255,255,0.75)' : 'rgba(255,255,255,0.4)', border:`1.5px solid ${isActive ? p?.color||T.mint : 'transparent'}`, boxShadow: isActive ? '0 1px 6px rgba(0,0,0,0.1)' : 'none' }}>\n"
    "              <div style={{ width:14, height:14, borderRadius:'50%', background:p?.color, flexShrink:0 }}/>\n"
    "              <div style={{ fontFamily:T.font, fontSize:12, fontWeight: isActive ? 700 : 500, color: isActive ? T.ink : T.inkSoft }}>{p?.name||'?'}</div>\n"
    "            </div>\n"
    "          );\n"
    "        })}\n"
    "      </div>\n"
    "    </div>\n"
    "  );\n"
    "}"
)
new22 = "    </div>\n  );\n}"
assert old22 in html, "Step 22 not found"
html = html.replace(old22, new22, 1)

# ── 23. Info button: smaller (36x36, higher with top:8) ──────────────────────
html = html.replace(
    "style={{ position:'absolute', right:16, width:46, height:46, borderRadius:'50%', background:T.surface, border:'none', boxShadow:'0 3px 14px rgba(0,0,0,0.13)', cursor:'pointer', display:'grid', placeItems:'center', padding:0, flexShrink:0 }}",
    "style={{ position:'absolute', right:16, top:8, width:36, height:36, borderRadius:'50%', background:T.surface, border:'none', boxShadow:'0 3px 14px rgba(0,0,0,0.13)', cursor:'pointer', display:'grid', placeItems:'center', padding:0, flexShrink:0 }}",
    1
)
html = html.replace(
    "style={{ width:46, height:46, borderRadius:'50%', background:T.surface, border:'none', boxShadow:'0 3px 14px rgba(0,0,0,0.13)', cursor:'pointer', display:'grid', placeItems:'center', padding:0, flexShrink:0 }}",
    "style={{ width:36, height:36, borderRadius:'50%', background:T.surface, border:'none', boxShadow:'0 3px 14px rgba(0,0,0,0.13)', cursor:'pointer', display:'grid', placeItems:'center', padding:0, flexShrink:0 }}",
    1
)

# ── 24. Version bump ─────────────────────────────────────────────────────────
assert 'Verzió 5.29 · DNR · 2026.06.01 05:00' in html, "Version not found"
html = html.replace(
    'Verzió 5.29 · DNR · 2026.06.01 05:00',
    'Verzió 5.30 · DNR · 2026.06.01 06:00',
    1
)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done — v5.30")
