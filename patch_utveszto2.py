# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# 1. GRID 7 -> 5
OLD1 = "function UtvesztoGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter }) {\n  const GRID = 7;"
NEW1 = "function UtvesztoGame({ gameIdx, challenger, players, onAdvance, onResult, onSetHideFooter }) {\n  const GRID = 5;"
assert OLD1 in src, '1 not found'
src = src.replace(OLD1, NEW1, 1)

# 2. placeOrRemove: block adjacent to start
OLD2 = "  // Setup: place trap\n  const placeOrRemove = (board, setBoard, idx) => {\n    if (idx === START_IDX || idx === END_IDX) return;"
NEW2 = "  // Setup: place trap — START és közvetlen szomszédai védett zóna\n  const startNeighbors = [1, GRID]; // jobb + le START-tól (idx 0)\n  const placeOrRemove = (board, setBoard, idx) => {\n    if (idx === START_IDX || idx === END_IDX || startNeighbors.includes(idx)) return;"
assert OLD2 in src, '2 not found'
src = src.replace(OLD2, NEW2, 1)

# 3. Add useEffect for auto-transition after reveal2 animation
OLD3 = "  React.useEffect(() => { return () => { if (animRef.current) clearInterval(animRef.current); }; }, []);"
NEW3 = """  React.useEffect(() => { return () => { if (animRef.current) clearInterval(animRef.current); }; }, []);

  // Auto-transition to done after reveal2 animation finishes
  React.useEffect(() => {
    if (phase !== 'reveal2') return;
    if (!result2?.seq) return;
    if (animStep < result2.seq.length) return;
    const t = setTimeout(() => {
      const r1 = result1 || {steps:999, korty:0};
      const r2_ = result2 || {steps:999, korty:0};
      const winnerIsP1 = r1.steps <= r2_.steps;
      const loserKorty = winnerIsP1 ? (r2_.korty + 2) : (r1.korty + 2);
      const loserId = winnerIsP1 ? p2?.id : p1?.id;
      if (onAdvance && loserId) onAdvance({[loserId]: loserKorty});
      const winnerName = winnerIsP1 ? (p1?.name||'P1') : (p2?.name||'P2');
      const loserName = winnerIsP1 ? (p2?.name||'P2') : (p1?.name||'P1');
      if (onResult) onResult({ correct: winnerIsP1, playerName: winnerName, drinks: loserKorty, subtitle: `${loserName} iszik ${loserKorty} kortyot!` });
      setPhase('done');
    }, 1200);
    return () => clearTimeout(t);
  }, [phase, animStep, result1, result2]);"""
assert OLD3 in src, '3 not found'
src = src.replace(OLD3, NEW3, 1)

# 4. Setup 1: show selected trap description hint
OLD4 = "        {selTrap && <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.5)',textAlign:'center',marginTop:4}}>"
# Check if already patched
if OLD4 not in src:
    # Find and patch setup1 trap palette
    S1_OLD = "        <button onClick={()=>{setSelTrap(null);setPhase('setup2');}} disabled={placed===0} style={{"
    S1_NEW = "        {selTrap && <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.5)',textAlign:'center',marginTop:4}}>\n          {TRAP_TYPES.find(t=>t.id===selTrap)?.emoji} {TRAP_TYPES.find(t=>t.id===selTrap)?.desc} — koppints a pályára!\n        </div>}\n        <button onClick={()=>{setSelTrap(null);setPhase('setup2');}} disabled={placed===0} style={{"
    assert S1_OLD in src, 'setup1 btn not found'
    src = src.replace(S1_OLD, S1_NEW, 1)

    S2_OLD = "        <button onClick={()=>{setSelTrap(null);setPhase('path1');}} disabled={placed===0} style={{"
    S2_NEW = "        {selTrap && <div style={{fontFamily:T.font,fontSize:11,color:'rgba(255,255,255,0.5)',textAlign:'center',marginTop:4}}>\n          {TRAP_TYPES.find(t=>t.id===selTrap)?.emoji} {TRAP_TYPES.find(t=>t.id===selTrap)?.desc} — koppints a pályára!\n        </div>}\n        <button onClick={()=>{setSelTrap(null);setPhase('path1');}} disabled={placed===0} style={{"
    assert S2_OLD in src, 'setup2 btn not found'
    src = src.replace(S2_OLD, S2_NEW, 1)

# 5. Remove "Eredmény!" button from reveal2
OLD5 = "        {animDoneHere && (\n          <button onClick={goToResult} style={{\n            marginTop:10,padding:'13px',borderRadius:14,border:'none',background:YELLOW,color:'#1a0a3e',\n            fontFamily:T.font,fontWeight:900,fontSize:15,cursor:'pointer',\n          }}>🏆 Eredmény!</button>\n        )}"
NEW5 = "        {animDoneHere && (\n          <div style={{fontFamily:T.font,fontSize:12,color:'rgba(255,255,255,0.4)',textAlign:'center',marginTop:8}}>\n            Az eredmény kiszámítása...\n          </div>\n        )}"
assert OLD5 in src, '5 not found'
src = src.replace(OLD5, NEW5, 1)

# 6. Version bump
assert 'v9.434' in src, 'version not found'
src = src.replace('v9.434', 'v9.435', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
