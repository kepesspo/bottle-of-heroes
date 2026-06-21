# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# Move animStep state and effects to top-level, out of the conditional reveal block
# Also remove old done phase useEffect comment placeholder

OLD_TOP = """  const [S, setS] = React.useState(fresh);
  const dragRef = React.useRef(null);
  const [ghost, setGhost] = React.useState(null);
  const [dropHover, setDropHover] = React.useState(null);
  React.useEffect(() => { setS(fresh()); }, [gameIdx]);"""

NEW_TOP = """  const [S, setS] = React.useState(fresh);
  const dragRef = React.useRef(null);
  const [ghost, setGhost] = React.useState(null);
  const [dropHover, setDropHover] = React.useState(null);
  const [animStep, setAnimStep] = React.useState(0);
  const animTimer = React.useRef(null);
  React.useEffect(() => { setS(fresh()); setAnimStep(0); }, [gameIdx]);"""

assert OLD_TOP in src, 'TOP not found'
src = src.replace(OLD_TOP, NEW_TOP, 1)

# Remove the old onAdvance comment placeholder
OLD_COMMENT = "  // onAdvance/onResult is now fired inside the reveal phase animation useEffect"
NEW_COMMENT = ""
assert OLD_COMMENT in src, 'comment not found'
src = src.replace(OLD_COMMENT, NEW_COMMENT, 1)

# Replace the reveal phase block — remove the local useState/useRef/useEffect hooks, use top-level ones
OLD_REVEAL = """  // ── REVEAL (animated, merged result) ────────────────────────────────────
  if (S.phase === 'reveal') {
    const {rounds, p1W, p2W} = results;
    const NR_total = rounds.length;

    // animStep: how many rows are revealed so far
    const [animStep, setAnimStep] = React.useState(0);
    const animTimer = React.useRef(null);

    React.useEffect(() => {
      setAnimStep(0);
    }, [S.phase]);

    React.useEffect(() => {
      if (animStep >= NR_total) return;
      animTimer.current = setTimeout(() => setAnimStep(s => s+1), 800);
      return () => clearTimeout(animTimer.current);
    }, [animStep, NR_total]);

    // Fire result after last row revealed + short pause
    React.useEffect(() => {
      if (animStep < NR_total) return;
      const t = setTimeout(() => {
        const p1id = challenger?.id;
        const p2id = opponent?.id;
        const diff = Math.abs(p1W - p2W);
        if (p1W > p2W) {
          if (onAdvance) onAdvance({[p2id]: diff}, {[p1id]: 1});
          if (onResult) onResult({ correct: true, playerName: p1Name, drinks: 0, subtitle: p1Name + ' nyerte a meccset!' });
        } else if (p2W > p1W) {
          if (onAdvance) onAdvance({[p1id]: diff}, {[p2id]: 1});
          if (onResult) onResult({ correct: false, playerName: p2Name, drinks: 0, subtitle: p2Name + ' nyerte a meccset!' });
        } else {
          if (onAdvance) onAdvance({[p1id]: 1, [p2id]: 1}, {});
          if (onResult) onResult({ correct: false, playerName: null, drinks: 1, subtitle: 'Döntetlen — mindenki iszik!' });
        }
        setS(s=>({...s,phase:'done'}));
      }, 1600);
      return () => clearTimeout(t);
    }, [animStep, NR_total]);

    const allDone = animStep >= NR_total;"""

NEW_REVEAL = """  // ── Reveal animation effects (top-level, must not be inside conditional) ─
  const _revealResults = S.phase === 'reveal' ? results : null;
  const _revealNR = NR;
  React.useEffect(() => {
    if (S.phase !== 'reveal') return;
    if (animStep >= _revealNR) return;
    animTimer.current = setTimeout(() => setAnimStep(s => s+1), 800);
    return () => clearTimeout(animTimer.current);
  }, [S.phase, animStep]);

  React.useEffect(() => {
    if (S.phase !== 'reveal') return;
    if (animStep < _revealNR) return;
    const {p1W, p2W} = results;
    const t = setTimeout(() => {
      const p1id = challenger?.id;
      const p2id = opponent?.id;
      const diff = Math.abs(p1W - p2W);
      if (p1W > p2W) {
        if (onAdvance) onAdvance({[p2id]: diff}, {[p1id]: 1});
        if (onResult) onResult({ correct: true, playerName: p1Name, drinks: 0, subtitle: p1Name + ' nyerte a meccset!' });
      } else if (p2W > p1W) {
        if (onAdvance) onAdvance({[p1id]: diff}, {[p2id]: 1});
        if (onResult) onResult({ correct: false, playerName: p2Name, drinks: 0, subtitle: p2Name + ' nyerte a meccset!' });
      } else {
        if (onAdvance) onAdvance({[p1id]: 1, [p2id]: 1}, {});
        if (onResult) onResult({ correct: false, playerName: null, drinks: 1, subtitle: 'Döntetlen — mindenki iszik!' });
      }
      setS(s=>({...s,phase:'done'}));
    }, 1600);
    return () => clearTimeout(t);
  }, [S.phase, animStep]);

  // ── REVEAL (animated, merged result) ────────────────────────────────────
  if (S.phase === 'reveal') {
    const {rounds, p1W, p2W} = results;
    const NR_total = NR;
    const allDone = animStep >= NR_total;"""

assert OLD_REVEAL in src, 'REVEAL block not found'
src = src.replace(OLD_REVEAL, NEW_REVEAL, 1)

# version bump
assert 'v9.441' in src, 'version not found'
src = src.replace('v9.441', 'v9.442', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
