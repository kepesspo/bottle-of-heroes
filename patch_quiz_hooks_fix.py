# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# Move the auto-confirm useEffect out of the conditional distribute block
# and up to top-level of QuizGame, right after the gifts state declaration

OLD_EFFECT_IN_BLOCK = """    // auto-confirm when all drinks distributed
    React.useEffect(() => {
      if (phase !== 'distribute') return;
      if (remaining !== 0) return;
      const t = setTimeout(confirmGifts, 800);
      return () => clearTimeout(t);
    }, [remaining, phase]);"""
NEW_EFFECT_IN_BLOCK = "    // auto-confirm: moved to top-level useEffect"
assert OLD_EFFECT_IN_BLOCK in src, 'effect in block not found'
src = src.replace(OLD_EFFECT_IN_BLOCK, NEW_EFFECT_IN_BLOCK, 1)

# Also need to compute totalGifted/remaining at top level for the effect
# Add the top-level useEffect after the gifts state + gameIdx reset
OLD_TOPLEVEL = "  React.useEffect(() => { setStreak(0); setQIdx(0); setGiftPool(null); setGifts({}); setDistributeTarget(null); }, [gameIdx]);"
NEW_TOPLEVEL = """  React.useEffect(() => { setStreak(0); setQIdx(0); setGiftPool(null); setGifts({}); setDistributeTarget(null); }, [gameIdx]);

  // Auto-confirm distribute when all kortyok assigned (top-level — no conditional hooks)
  const _distributeTotal = Object.values(gifts).reduce((s,v)=>s+v,0);
  const _distributeRemaining = kortyok - _distributeTotal;
  React.useEffect(() => {
    if (phase !== 'distribute') return;
    if (_distributeRemaining !== 0) return;
    const drinkMap = {};
    Object.entries(gifts).forEach(([pid,n]) => { if(n>0) drinkMap[pid]=n; });
    const t = setTimeout(() => {
      if (onAdvance) onAdvance(drinkMap);
      setPhase('done');
    }, 800);
    return () => clearTimeout(t);
  }, [phase, _distributeRemaining]);"""
assert OLD_TOPLEVEL in src, 'top-level effect anchor not found'
src = src.replace(OLD_TOPLEVEL, NEW_TOPLEVEL, 1)

# version bump
assert 'v9.445' in src, 'version not found'
src = src.replace('v9.445', 'v9.446', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
