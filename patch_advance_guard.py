# -*- coding: utf-8 -*-
# Fix dupla onAdvance hívások → Firebase crash
with open('index.html','r',encoding='utf-8') as f: src=f.read()

# ── 1. SzerencsekerékGame: advancedRef guard + remove dead proceed() ────────
OLD_SZERENCSE = """function SzerencsekerékGame({ gameIdx, players, onAdvance, onResult }) {
  const [phase, setPhase] = React.useState('ready'); // ready | spinning | result
  const [currentIdx, setCurrentIdx] = React.useState(0);
  const [winner, setWinner] = React.useState(null);

  React.useEffect(() => {
    setPhase('ready');
    setCurrentIdx(gameIdx % Math.max(players.length,1));
    setWinner(null);
  }, [gameIdx]);

  // Reset to ready after result so user can spin again
  React.useEffect(() => {
    if (phase === 'result') {
      const t = setTimeout(() => setPhase('ready'), 2200);
      return () => clearTimeout(t);
    }
  }, [phase]);

  const spin = () => {
    if (phase !== 'ready' || players.length === 0) return;
    setPhase('spinning');
    const n = players.length;
    const winnerIdx = Math.floor(Math.random() * n);
    const stepsToWinner = ((winnerIdx - currentIdx + n) % n) || n;
    const totalSteps = n * 4 + stepsToWinner;
    let step = 0;
    let cur = currentIdx;

    const next = () => {
      step++;
      cur = (cur + 1) % n;
      setCurrentIdx(cur);
      if (step < totalSteps) {
        const progress = step / totalSteps;
        const delay = 55 + Math.pow(progress, 2.2) * 560;
        setTimeout(next, delay);
      } else {
        setWinner(players[winnerIdx]);
        setPhase('result');
        // Auto-show drink result via onResult after short delay
        setTimeout(() => {
          const w = players[winnerIdx];
          if (w) {
            onResult && onResult({ correct: false, playerName: w.name, drinks: 1, subtitle: w.name + ' iszik egyet!' });
            const dm = { [w.id]: 1 };
            onAdvance && onAdvance(dm);
          }
        }, 600);
      }
    };
    setTimeout(next, 55);
  };

  const proceed = () => {
    if (!winner) return;
    onResult && onResult({ correct: false, playerName: winner.name, drinks: 1, subtitle: winner.name + ' iszik egyet!' });
    const dm = { [winner.id]: 1 };
    onAdvance && onAdvance(dm);
  };"""

NEW_SZERENCSE = """function SzerencsekerékGame({ gameIdx, players, onAdvance, onResult }) {
  const [phase, setPhase] = React.useState('ready'); // ready | spinning | result
  const [currentIdx, setCurrentIdx] = React.useState(0);
  const [winner, setWinner] = React.useState(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('ready');
    setCurrentIdx(gameIdx % Math.max(players.length,1));
    setWinner(null);
    advancedRef.current = false;
  }, [gameIdx]);

  // Reset to ready after result so user can spin again (visual only)
  React.useEffect(() => {
    if (phase === 'result') {
      const t = setTimeout(() => setPhase('ready'), 2200);
      return () => clearTimeout(t);
    }
  }, [phase]);

  const spin = () => {
    if (phase !== 'ready' || players.length === 0) return;
    setPhase('spinning');
    const n = players.length;
    const winnerIdx = Math.floor(Math.random() * n);
    const stepsToWinner = ((winnerIdx - currentIdx + n) % n) || n;
    const totalSteps = n * 4 + stepsToWinner;
    let step = 0;
    let cur = currentIdx;

    const next = () => {
      step++;
      cur = (cur + 1) % n;
      setCurrentIdx(cur);
      if (step < totalSteps) {
        const progress = step / totalSteps;
        const delay = 55 + Math.pow(progress, 2.2) * 560;
        setTimeout(next, delay);
      } else {
        const w = players[winnerIdx];
        setWinner(w);
        setPhase('result');
        // Fire onAdvance only once per game turn
        if (!advancedRef.current) {
          advancedRef.current = true;
          setTimeout(() => {
            if (w) {
              onResult && onResult({ correct: false, playerName: w.name, drinks: 1, subtitle: w.name + ' iszik egyet!' });
              onAdvance && onAdvance({ [w.id]: 1 });
            }
          }, 600);
        }
      }
    };
    setTimeout(next, 55);
  };"""

assert OLD_SZERENCSE in src, 'SzerencsekerékGame not found'
src = src.replace(OLD_SZERENCSE, NEW_SZERENCSE, 1)

# ── 2. TapperGame: advancedRef guard on useEffect([p1Time, p2Time]) ─────────
OLD_TAPPER_STATE = """  const phaseRef = React.useRef('idle');
  const p1HoldRef = React.useRef(false);
  const p2HoldRef = React.useRef(false);
  const p1TimeRef = React.useRef(null);
  const p2TimeRef = React.useRef(null);
  const startRef = React.useRef(null);
  const ivRef = React.useRef(null);

  React.useEffect(() => {
    setPhase('idle'); setP1Hold(false); setP2Hold(false);
    setCountdown(5.0); setP1Time(null); setP2Time(null);
    phaseRef.current = 'idle';
    p1HoldRef.current = false; p2HoldRef.current = false;
    p1TimeRef.current = null; p2TimeRef.current = null;
    clearInterval(ivRef.current);"""

NEW_TAPPER_STATE = """  const phaseRef = React.useRef('idle');
  const p1HoldRef = React.useRef(false);
  const p2HoldRef = React.useRef(false);
  const p1TimeRef = React.useRef(null);
  const p2TimeRef = React.useRef(null);
  const startRef = React.useRef(null);
  const ivRef = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPhase('idle'); setP1Hold(false); setP2Hold(false);
    setCountdown(5.0); setP1Time(null); setP2Time(null);
    phaseRef.current = 'idle';
    p1HoldRef.current = false; p2HoldRef.current = false;
    p1TimeRef.current = null; p2TimeRef.current = null;
    advancedRef.current = false;
    clearInterval(ivRef.current);"""

assert OLD_TAPPER_STATE in src, 'TapperGame state not found'
src = src.replace(OLD_TAPPER_STATE, NEW_TAPPER_STATE, 1)

OLD_TAPPER_EFFECT = """    onResult && onResult({ correct: r !== 'both-lose' && r !== 'draw', playerName: winner?.name, drinks: r === 'both-lose' ? 1 : loser ? 1 : 0, subtitle });
    onAdvance && onAdvance(dm, pm);
  }, [p1Time, p2Time]);"""

NEW_TAPPER_EFFECT = """    if (!advancedRef.current) {
      advancedRef.current = true;
      onResult && onResult({ correct: r !== 'both-lose' && r !== 'draw', playerName: winner?.name, drinks: r === 'both-lose' ? 1 : loser ? 1 : 0, subtitle });
      onAdvance && onAdvance(dm, pm);
    }
  }, [p1Time, p2Time]);"""

assert OLD_TAPPER_EFFECT in src, 'TapperGame effect not found'
src = src.replace(OLD_TAPPER_EFFECT, NEW_TAPPER_EFFECT, 1)

# ── 3. EremGame: one remaining #1B2340 in SVG path ──────────────────────────
src = src.replace(
    'stroke="#1B2340" strokeWidth="3.5" strokeLinecap="round"/>',
    'stroke={T.ink} strokeWidth="3.5" strokeLinecap="round"/>',
    3
)

# ── 4. version bump ──────────────────────────────────────────────────────────
assert 'v9.452' in src, 'version not found'
src = src.replace('v9.452', 'v9.453', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
