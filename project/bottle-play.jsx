// bottle-play.jsx — In-game screen + end-game/leaderboard

const { useState: useStateP, useEffect: useEffectP, useRef: useRefP } = React;

// Mini scenarios — each game has a short prompt for the active turn.
const SCENARIOS = {
  busz:      { prompt: 'Talál ki a következő lapot — piros vagy fekete?', cta: ['Piros', 'Fekete'] },
  memoria:   { prompt: 'Fordíts meg két lapot. Talált párt?', cta: ['Nem találtam', 'Pár!'] },
  erem:      { prompt: 'Érem dobás', cta: ['Nem sikerült', 'Sikerült!'] },
  ticktak:   { prompt: 'A csengő szólt — nálad maradt?', cta: ['Tovább adtam', 'Nálam maradt'] },
  kezcsere:  { prompt: 'Kéz csere — sikerült követni?', cta: ['Elrontottam', 'Megcsináltam'] },
  anagramma: { prompt: 'NÖSÉRH → fejtsd meg!', cta: ['Feladom', 'Megvan!'] },
  ringfire:  { prompt: 'Húzz egy lapot. Megúsztad?', cta: ['Iszom', 'Megúsztam'] },
  rulett:    { prompt: 'Válassz egy poharat — vajon ez a kemény?', cta: ['Kemény!', 'Sima'] },
  kisebb:    { prompt: 'A következő szám kisebb vagy nagyobb 7-nél?', cta: ['Kisebb', 'Nagyobb'] },
  kerdes:    { prompt: 'Soha nem ittam még tequilát.', cta: ['Igen', 'Soha'] },
  irany:     { prompt: 'Reagáltál időben az irányváltásra?', cta: ['Nem', 'Igen'] },
  szabaly:   { prompt: 'Új szabály: nincs név használat. Betartottad?', cta: ['Megszegtem', 'Betartottam'] },
};

// ───────────────────────────────────────────────────────────
// SCREEN: PLAY — turn-by-turn with success/fail
// ───────────────────────────────────────────────────────────
function PlayScreen({ t, r, players, setPlayers, selectedGames, go }) {
  const isB = t.id === 'B';
  const [round, setRound] = useStateP(1);
  const [turn, setTurn] = useStateP(0);   // index into players
  const [gameIdx, setGameIdx] = useStateP(0); // index into selectedGames cycle
  const [drinkPulse, setDrinkPulse] = useStateP(false);
  const [scorePulse, setScorePulse] = useStateP(false);
  const [feedback, setFeedback] = useStateP(null); // 'win' | 'lose'
  const [transitioning, setTransitioning] = useStateP(false);
  const [showInfo, setShowInfo] = useStateP(false);

  const games = selectedGames.length ? selectedGames : GAMES.slice(0, 6).map(g => g.id);
  const currentGameId = games[gameIdx % games.length];
  const currentGame = GAMES.find(g => g.id === currentGameId);
  const currentPlayer = players[turn];
  const scenario = SCENARIOS[currentGameId] || SCENARIOS.erem;

  const advance = (success) => {
    if (transitioning) return;
    setTransitioning(true);
    setFeedback(success ? 'win' : 'lose');
    if (success) {
      setPlayers(players.map((p, i) => i === turn ? { ...p, points: p.points + 1 } : p));
      setScorePulse(true); setTimeout(() => setScorePulse(false), 600);
    } else {
      setPlayers(players.map((p, i) => i === turn ? { ...p, drinks: p.drinks + 1 } : p));
      setDrinkPulse(true); setTimeout(() => setDrinkPulse(false), 600);
    }
    setTimeout(() => {
      setFeedback(null);
      const nextTurn = (turn + 1) % players.length;
      setTurn(nextTurn);
      setGameIdx(gameIdx + 1);
      // Round counter advances each time a new game starts (every turn).
      setRound(round + 1);
      setTransitioning(false);
    }, 700);
  };

  const totalDrinks = players.reduce((s, p) => s + p.drinks, 0);
  const totalRounds = 8; // round target to enable "end game"

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: t.bg, position: 'relative', overflow: 'hidden' }}>
      {/* drink counter pill — top right */}
      <div style={{ position: 'absolute', top: 16, right: 16, zIndex: 5 }}>
        <CounterPill t={t} r={r} value={totalDrinks} pulse={drinkPulse} icon="beer" />
      </div>
      {/* end game button — top left */}
      <button onClick={() => go('end')} style={{
        position: 'absolute', top: 16, left: 16, zIndex: 5,
        width: 44, height: 44, borderRadius: '50%',
        background: t.surface, border: isB ? '2px solid #0E0E18' : 'none',
        boxShadow: isB ? '2px 2px 0 #0E0E18' : t.shadow,
        cursor: 'pointer', display: 'grid', placeItems: 'center', padding: 0,
      }}>{Icon.trophy(t.ink)}</button>

      {/* main play area */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '80px 24px 20px', gap: 18 }}>
        {/* game illustration card */}
        <div key={gameIdx} style={{
          width: 160, height: 160, borderRadius: R(r, 28),
          background: `${currentGame.color}22`,
          border: isB ? '2.5px solid #0E0E18' : 'none',
          boxShadow: isB ? '5px 5px 0 #0E0E18' : `0 14px 36px ${currentGame.color}40`,
          display: 'grid', placeItems: 'center', padding: 18,
          animation: feedback === 'win' ? 'shakeWin .5s' : feedback === 'lose' ? 'shakeLose .5s' : 'popIn .4s cubic-bezier(.2,.9,.3,1.4)',
        }}>
          <GameImg g={currentGame} size="full"/>
        </div>

        <div style={{
          fontFamily: t.fontDisplay, fontWeight: t.weightDisplay,
          fontSize: isB ? 36 : 28, color: t.ink, textAlign: 'center',
          textTransform: 'uppercase', letterSpacing: t.letterDisplay, lineHeight: 1,
          maxWidth: 260,
        }}>{currentGame.name}</div>

        <div style={{
          fontFamily: t.font, fontSize: 14, fontWeight: 600, color: t.inkSoft,
          textAlign: 'center', maxWidth: 280, lineHeight: 1.4,
        }}>{scenario.prompt}</div>

        {/* points strip — show all players + their points */}
        <div style={{
          display: 'flex', gap: 8, padding: '10px 14px',
          background: 'rgba(255,255,255,0.45)',
          borderRadius: R(r, 14),
          border: isB ? '2px solid #0E0E18' : 'none',
          marginTop: 6,
        }}>
          {players.map((p, i) => (
            <div key={p.id} style={{
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
              padding: '2px 6px',
              opacity: i === turn ? 1 : 0.55,
              transform: i === turn ? 'scale(1.05)' : 'scale(1)',
              transition: 'all .2s',
            }}>
              <div style={{ width: 8, height: 8, borderRadius: '50%', background: p.color }} />
              <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 13, color: t.ink, fontVariantNumeric: 'tabular-nums' }}>{p.points}</div>
            </div>
          ))}
        </div>
      </div>

      {/* action buttons */}
      <div style={{ padding: '0 24px 16px', display: 'flex', gap: 12 }}>
        <button onClick={() => advance(false)} disabled={transitioning} style={{
          flex: 1, minHeight: 60, border: isB ? '2px solid #0E0E18' : 'none',
          background: t.coral, color: '#fff',
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 17,
          borderRadius: R(r, 16), cursor: 'pointer',
          boxShadow: isB ? '4px 4px 0 #0E0E18' : t.shadow,
        }}>{scenario.cta[0]}</button>
        <button onClick={() => advance(true)} disabled={transitioning} style={{
          flex: 1, minHeight: 60, border: isB ? '2px solid #0E0E18' : 'none',
          background: t.mint, color: '#fff',
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 17,
          borderRadius: R(r, 16), cursor: 'pointer',
          boxShadow: isB ? '4px 4px 0 #0E0E18' : t.shadow,
        }}>{scenario.cta[1]}</button>
      </div>

      {/* footer player nav */}
      <div style={{
        background: t.surface,
        borderTopLeftRadius: R(r, 24), borderTopRightRadius: R(r, 24),
        border: isB ? '2px solid #0E0E18' : 'none', borderBottom: 'none',
        boxShadow: isB ? '0 -4px 0 #0E0E18' : '0 -4px 18px rgba(20,30,50,0.05)',
        padding: '14px 18px 22px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
      }}>
        {/* round indicator */}
        <div style={{
          width: 54, height: 54, borderRadius: '50%',
          border: `2px solid ${t.inkMute}40`,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        }}>
          <div style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: t.inkSoft, letterSpacing: '0.05em' }}>KÖR</div>
          <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 18, color: t.ink, lineHeight: 1, fontVariantNumeric: 'tabular-nums' }}>{round}</div>
        </div>

        {/* current player */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
          <div key={currentPlayer.id} style={{
            width: 56, height: 56, borderRadius: '50%', background: currentPlayer.color,
            border: isB ? '2.5px solid #0E0E18' : 'none',
            display: 'grid', placeItems: 'center',
            fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: '#fff',
            boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : 'none',
            animation: 'popIn .35s cubic-bezier(.2,.9,.3,1.4)',
            transition: 'box-shadow .3s',
          }}>{currentPlayer.name.charAt(0).toUpperCase() || '?'}</div>
          <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 14, color: t.ink }}>{currentPlayer.name}</div>
        </div>

        {/* help — opens current game's info modal */}
        <button onClick={() => setShowInfo(true)} aria-label="Játék leírása" style={{
          width: 54, height: 54, borderRadius: '50%',
          border: `2px solid ${t.inkMute}40`, background: 'transparent',
          cursor: 'pointer', display: 'grid', placeItems: 'center', color: t.inkSoft, padding: 0,
        }}>{Icon.info(t.inkSoft)}</button>
      </div>

      {showInfo && (
        <GameInfoModal t={t} r={r} game={currentGame} onClose={() => setShowInfo(false)} />
      )}
    </div>
  );
}

function CounterPill({ t, r, value, pulse, icon }) {
  const isB = t.id === 'B';
  return (
    <div style={{
      minWidth: 54, height: 54, padding: '0 10px',
      borderRadius: R(r, 999), background: t.surface,
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ? '3px 3px 0 #0E0E18' : t.shadow,
      display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
      gap: 2, transform: pulse ? 'scale(1.15)' : 'scale(1)',
      transition: 'transform .3s cubic-bezier(.2,.9,.3,1.4)',
    }}>
      <div style={{ color: t.ink, lineHeight: 0 }}>{Icon.beer(t.ink)}</div>
      <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 14, color: t.ink, fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>{value}</div>
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// SCREEN: END — leaderboard
// ───────────────────────────────────────────────────────────
function EndScreen({ t, r, players, go, resetGame }) {
  const isB = t.id === 'B';
  const sorted = [...players].sort((a, b) => (b.points - a.points) || (a.drinks - b.drinks));
  const winner = sorted[0];
  const maxScore = Math.max(1, ...players.map(p => p.points));
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: t.bg }}>
      <AppBar t={t} r={r} title="Vége!" onBack={() => go('play')} />
      <div style={{ flex: 1, padding: '20px 22px 24px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 16 }}>
        {/* winner hero */}
        <div style={{
          background: t.surface, borderRadius: R(r, 22),
          border: isB ? '2.5px solid #0E0E18' : 'none',
          boxShadow: isB ? '5px 5px 0 #0E0E18' : t.shadowLift,
          padding: '22px 18px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10,
          position: 'relative', overflow: 'hidden',
        }}>
          {isB && (
            <div style={{ position: 'absolute', top: 8, left: 8, background: t.yellow, padding: '2px 8px', border: '2px solid #0E0E18', fontFamily: t.font, fontWeight: 700, fontSize: 10, transform: 'rotate(-4deg)' }}>NYERTES</div>
          )}
          <div style={{ color: t.yellow, filter: 'drop-shadow(0 2px 0 rgba(0,0,0,0.15))' }}>{Icon.trophy(t.yellow)}</div>
          <div style={{
            width: 92, height: 92, borderRadius: '50%', background: winner.color,
            border: isB ? '3px solid #0E0E18' : 'none',
            display: 'grid', placeItems: 'center',
            fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 36, color: '#fff',
          }}>{winner.name.charAt(0).toUpperCase() || '?'}</div>
          <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 30, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay, lineHeight: 1 }}>{winner.name}</div>
          <div style={{ display: 'flex', gap: 14 }}>
            <Stat t={t} r={r} value={winner.points} label="pont" tone={t.mint}/>
            <Stat t={t} r={r} value={winner.drinks} label="korty" tone={t.coral}/>
          </div>
        </div>

        {/* leaderboard rows */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {sorted.map((p, i) => (
            <LeaderRow key={p.id} t={t} r={r} p={p} rank={i + 1} maxScore={maxScore} />
          ))}
        </div>
      </div>

      <BottomBar t={t} r={r}>
        <div style={{ display: 'flex', gap: 10 }}>
          <button onClick={resetGame} style={{
            flex: 1, minHeight: 56, border: isB ? '2px solid #0E0E18' : `2px solid ${t.ink}`,
            background: 'transparent', color: t.ink,
            fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 16,
            borderRadius: R(r, 14), cursor: 'pointer',
          }}>Új meccs</button>
          <button onClick={() => go('home')} style={{
            flex: 1, minHeight: 56, border: isB ? '2px solid #0E0E18' : 'none',
            background: t.mint, color: '#fff',
            fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 16,
            borderRadius: R(r, 14), cursor: 'pointer',
            boxShadow: isB ? '4px 4px 0 #0E0E18' : t.shadow,
          }}>Főmenü</button>
        </div>
      </BottomBar>
    </div>
  );
}

function Stat({ t, r, value, label, tone }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'baseline', gap: 6,
      padding: '6px 14px', borderRadius: R(r, 999),
      background: tone + '22', border: t.id === 'B' ? '2px solid #0E0E18' : 'none',
    }}>
      <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: tone, fontVariantNumeric: 'tabular-nums', lineHeight: 1 }}>{value}</div>
      <div style={{ fontFamily: t.font, fontSize: 12, fontWeight: 700, color: t.inkSoft, letterSpacing: '0.04em', textTransform: 'uppercase' }}>{label}</div>
    </div>
  );
}

function LeaderRow({ t, r, p, rank, maxScore }) {
  const isB = t.id === 'B';
  const pct = (p.points / maxScore) * 100;
  return (
    <div style={{
      background: t.surface, borderRadius: R(r, 14),
      border: isB ? '2px solid #0E0E18' : 'none',
      boxShadow: isB ? '3px 3px 0 #0E0E18' : t.shadow,
      padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 12,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{
        position: 'absolute', left: 0, top: 0, bottom: 0,
        width: `${pct}%`, background: `${p.color}1A`, transition: 'width .5s',
      }}/>
      <div style={{ position: 'relative', fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 20, color: t.inkSoft, minWidth: 22 }}>{rank}</div>
      <div style={{ position: 'relative', width: 36, height: 36, borderRadius: '50%', background: p.color, border: isB ? '2px solid #0E0E18' : 'none', display: 'grid', placeItems: 'center', color: '#fff', fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 15 }}>
        {p.name.charAt(0).toUpperCase() || '?'}
      </div>
      <div style={{ position: 'relative', flex: 1, fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 15, color: t.ink }}>{p.name}</div>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 4, color: t.coral }}>
        {Icon.beer(t.coral)}
        <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 15, fontVariantNumeric: 'tabular-nums', color: t.ink }}>{p.drinks}</div>
      </div>
      <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 4 }}>
        {Icon.star(t.yellow)}
        <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 15, fontVariantNumeric: 'tabular-nums', color: t.ink }}>{p.points}</div>
      </div>
    </div>
  );
}

// ───────────────────────────────────────────────────────────
// SCREEN: OBSERVER — enter room code → connecting → watching
// ───────────────────────────────────────────────────────────
function ObserverScreen({ t, r, go }) {
  const isB = t.id === 'B';
  const CODE_LEN = 6;
  const [code, setCode] = useStateP('');
  const [status, setStatus] = useStateP('enter'); // enter | connecting | watching | error

  const push = (d) => {
    if (status !== 'enter') return;
    if (code.length < CODE_LEN) setCode((code + d).slice(0, CODE_LEN));
  };
  const back = () => setCode(code.slice(0, -1));

  const submit = () => {
    if (code.length < CODE_LEN) return;
    setStatus('connecting');
    setTimeout(() => {
      // mock: any non-trivial code connects; "000000" fails.
      if (code === '000000') setStatus('error');
      else setStatus('watching');
    }, 1200);
  };

  const reset = () => { setCode(''); setStatus('enter'); };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', background: t.bg }}>
      <AppBar t={t} r={r} title="Megfigyelő" onBack={() => go('home')} />

      {status === 'enter' && (
        <ObserverEnter t={t} r={r}
          code={code} codeLen={CODE_LEN}
          onDigit={push} onBack={back} onSubmit={submit}
          onPaste={(v) => setCode(v.replace(/\D/g, '').slice(0, CODE_LEN))}
        />
      )}
      {status === 'connecting' && (
        <ObserverStatus t={t} r={r}
          icon="📡" title="Csatlakozás…"
          sub={`Szoba: ${code}`}
          spinning
        />
      )}
      {status === 'watching' && (
        <ObserverWatching t={t} r={r} code={code} onLeave={reset} />
      )}
      {status === 'error' && (
        <ObserverStatus t={t} r={r}
          icon="🚫" title="Nincs ilyen szoba"
          sub={`A ${code} kód nem érvényes, vagy a szoba bezárult.`}
          actionLabel="Próbáld újra"
          onAction={reset}
        />
      )}
    </div>
  );
}

function ObserverEnter({ t, r, code, codeLen, onDigit, onBack, onSubmit, onPaste }) {
  const isB = t.id === 'B';
  const ready = code.length === codeLen;
  // Keyboard input + paste support (handy on desktop preview).
  useEffectP(() => {
    const onKey = (e) => {
      if (/^[0-9]$/.test(e.key)) onDigit(e.key);
      else if (e.key === 'Backspace') onBack();
      else if (e.key === 'Enter') onSubmit();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  });

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '12px 22px 22px' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 22, paddingTop: 8 }}>
        <div style={{ fontSize: 52, lineHeight: 1, filter: 'drop-shadow(0 4px 10px rgba(20,30,50,0.15))' }}>👀</div>
        <div style={{ textAlign: 'center', maxWidth: 280 }}>
          <div style={{
            fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22,
            color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay,
          }}>Szoba kód</div>
          <div style={{ marginTop: 6, fontFamily: t.font, fontSize: 13, fontWeight: 600, color: t.inkSoft, lineHeight: 1.4 }}>
            Add meg a barátaid szobájának kódját, hogy nézd a játékot.
          </div>
        </div>

        {/* code boxes */}
        <div style={{ display: 'flex', gap: 8 }} onPaste={(e) => { onPaste(e.clipboardData.getData('text')); e.preventDefault(); }}>
          {Array.from({ length: codeLen }).map((_, i) => {
            const filled = i < code.length;
            const active = i === code.length;
            return (
              <div key={i} style={{
                width: 38, height: 52,
                background: filled ? t.surface : 'rgba(255,255,255,0.5)',
                borderRadius: R(r, 12),
                border: isB ? '2px solid #0E0E18'
                  : active ? `2px solid ${t.mint}`
                  : `2px solid ${filled ? 'transparent' : 'rgba(20,30,50,0.08)'}`,
                boxShadow: filled ? t.shadow : 'none',
                display: 'grid', placeItems: 'center',
                fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 24,
                color: t.ink, fontVariantNumeric: 'tabular-nums',
                transition: 'all .15s',
                transform: filled ? 'scale(1)' : (active ? 'scale(1.04)' : 'scale(1)'),
              }}>
                {filled ? code[i] : (active ? <span style={{ width: 2, height: 22, background: t.mint, opacity: 0.7, animation: 'caretBlink 1s infinite' }} /> : '')}
              </div>
            );
          })}
        </div>

        <div style={{ fontFamily: t.font, fontSize: 12, color: t.inkSoft, fontWeight: 600, opacity: 0.7 }}>
          Tipp: a házigazda osztja meg a szoba kódját
        </div>
      </div>

      {/* number pad */}
      <NumberPad t={t} r={r} onDigit={onDigit} onBack={onBack} />

      <PrimaryButton t={t} r={r} disabled={!ready} onClick={onSubmit} style={{ marginTop: 14 }}>
        Csatlakozás
      </PrimaryButton>
    </div>
  );
}

function NumberPad({ t, r, onDigit, onBack }) {
  const isB = t.id === 'B';
  const keys = ['1','2','3','4','5','6','7','8','9','','0','⌫'];
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 8, marginTop: 8 }}>
      {keys.map((k, i) => {
        if (!k) return <div key={i} />;
        const isBack = k === '⌫';
        return (
          <button key={i}
            onClick={() => isBack ? onBack() : onDigit(k)}
            style={{
              height: 52, border: 'none',
              background: isBack ? 'transparent' : t.surface,
              borderRadius: R(r, 14),
              boxShadow: isBack ? 'none' : t.shadow,
              fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22,
              color: t.ink, cursor: 'pointer',
              transition: 'transform .08s',
            }}
            onMouseDown={e => e.currentTarget.style.transform = 'scale(0.95)'}
            onMouseUp={e => e.currentTarget.style.transform = ''}
            onMouseLeave={e => e.currentTarget.style.transform = ''}
          >{k}</button>
        );
      })}
    </div>
  );
}

function ObserverStatus({ t, r, icon, title, sub, spinning, actionLabel, onAction }) {
  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: 28, gap: 14, textAlign: 'center' }}>
      <div style={{
        fontSize: 64, lineHeight: 1,
        animation: spinning ? 'pulse 1.6s ease-in-out infinite' : 'popIn .35s',
      }}>{icon}</div>
      <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay }}>{title}</div>
      <div style={{ fontFamily: t.font, fontSize: 13, color: t.inkSoft, fontWeight: 600, lineHeight: 1.4, maxWidth: 260 }}>{sub}</div>
      {spinning && (
        <div style={{ display: 'flex', gap: 6, marginTop: 6 }}>
          {[0,1,2].map(i => (
            <span key={i} style={{
              width: 8, height: 8, borderRadius: '50%', background: t.mint,
              animation: `dotBounce 1.2s ${i*0.15}s infinite ease-in-out`,
            }}/>
          ))}
        </div>
      )}
      {actionLabel && (
        <button onClick={onAction} style={{
          marginTop: 12, padding: '12px 24px',
          background: t.mint, color: '#fff', border: 'none',
          borderRadius: R(r, 14), boxShadow: t.shadow,
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 15,
          cursor: 'pointer',
        }}>{actionLabel}</button>
      )}
    </div>
  );
}

function ObserverWatching({ t, r, code, onLeave }) {
  const isB = t.id === 'B';
  // Mocked live room state. Scores grow over time so it feels live.
  const seed = [
    { ...INITIAL_PLAYERS[0], points: 4, drinks: 2 },
    { ...INITIAL_PLAYERS[1], points: 2, drinks: 5 },
    { ...INITIAL_PLAYERS[2], points: 3, drinks: 1 },
    { ...INITIAL_PLAYERS[3], points: 5, drinks: 3 },
  ];
  const [mockPlayers, setMockPlayers] = useStateP(seed);
  const [tick, setTick] = useStateP(0);
  const [pulseId, setPulseId] = useStateP(null);
  // Permission: 'read' | 'pending' | 'granted'
  const [access, setAccess] = useStateP('read');
  // GM features
  const [sheet, setSheet] = useStateP(null);   // 'drink' | 'emoji' | null
  const [burst, setBurst] = useStateP(null);   // transient feedback {icon, title, sub, tone}
  const [history, setHistory] = useStateP([]); // [{kind, label, undo: ()=>void}, ...]
  const [bonus, setBonus] = useStateP(false);
  const [emojiFly, setEmojiFly] = useStateP(null); // currently-floating emoji char

  useEffectP(() => {
    const id = setInterval(() => {
      setTick(x => x + 1);
      setMockPlayers(prev => {
        const i = Math.floor(Math.random() * prev.length);
        const win = Math.random() > 0.45;
        const next = prev.map((p, idx) => idx === i
          ? { ...p, points: p.points + (win ? 1 : 0), drinks: p.drinks + (win ? 0 : 1) }
          : p);
        setPulseId(prev[i].id + ':' + (win ? 'p' : 'd'));
        setTimeout(() => setPulseId(null), 700);
        setHistory(h => [{ kind: 'auto', label: `${prev[i].name} ${win ? '+1 pont' : '+1 korty'}`, undo: () => {
          setMockPlayers(curr => curr.map((p, idx) => idx === i ? { ...p, points: prev[i].points, drinks: prev[i].drinks } : p));
        }}, ...h].slice(0, 8));
        return next;
      });
    }, 2600);
    return () => clearInterval(id);
  }, []);

  const activeIdx = tick % mockPlayers.length;
  const currentGame = GAMES[tick % GAMES.length];
  const round = 1 + Math.floor(tick / mockPlayers.length);
  const sorted = [...mockPlayers].sort((a, b) => (b.points - a.points) || (a.drinks - b.drinks));
  const maxScore = Math.max(1, ...mockPlayers.map(p => p.points));
  const totalDrinks = mockPlayers.reduce((s, p) => s + p.drinks, 0);

  // ── intervention actions ────────────────────────────────
  const fireBurst = (b) => {
    setBurst(b);
    setTimeout(() => setBurst(null), 1400);
  };
  const giveDrinks = (player, amount) => {
    const before = player.drinks;
    setMockPlayers(prev => prev.map(p => p.id === player.id ? { ...p, drinks: p.drinks + amount } : p));
    setHistory(h => [{
      kind: 'drink', label: `${player.name} +${amount} korty`, undo: () =>
        setMockPlayers(prev => prev.map(p => p.id === player.id ? { ...p, drinks: before } : p)),
    }, ...h].slice(0, 8));
    fireBurst({ icon: '🍺', title: `Idd meg, ${player.name}!`, sub: `+${amount} korty osztva`, tone: t.coral });
  };
  const groupDrink = () => {
    const snapshot = mockPlayers.map(p => p.drinks);
    setMockPlayers(prev => prev.map(p => ({ ...p, drinks: p.drinks + 1 })));
    setHistory(h => [{
      kind: 'group', label: 'Csoportos ivás (+1 mindenki)', undo: () =>
        setMockPlayers(prev => prev.map((p, i) => ({ ...p, drinks: snapshot[i] }))),
    }, ...h].slice(0, 8));
    fireBurst({ icon: '🍻', title: 'Csoportos ivás!', sub: 'Mindenki egyet iszik', tone: t.yellow });
  };
  const triggerBonus = () => {
    setBonus(true);
    setHistory(h => [{ kind: 'bonus', label: 'Bonus képernyő', undo: () => setBonus(false) }, ...h].slice(0, 8));
    fireBurst({ icon: '🎁', title: 'Bonus indul!', sub: 'Mini-játék a szobába küldve', tone: t.mint });
    setTimeout(() => setBonus(false), 3200);
  };
  const sendEmoji = (e) => {
    setEmojiFly({ char: e, id: Date.now() });
    setTimeout(() => setEmojiFly(null), 2200);
    setHistory(h => [{ kind: 'emoji', label: `${e} elküldve`, undo: () => {} }, ...h].slice(0, 8));
    fireBurst({ icon: e, title: `${e} elküldve`, sub: 'A szoba látja', tone: t.purple });
  };
  const undoLast = () => {
    if (!history.length) return;
    const last = history[0];
    last.undo();
    setHistory(history.slice(1));
    fireBurst({ icon: '↩️', title: 'Visszavonva', sub: last.label, tone: t.inkSoft });
  };

  // ── permission flow (mock) ──────────────────────────────
  const requestAccess = () => {
    setAccess('pending');
    setTimeout(() => setAccess('granted'), 1800);
  };

  return (
    <div style={{ flex: 1, display: 'flex', flexDirection: 'column', position: 'relative', overflow: 'hidden' }}>
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', padding: '12px 18px 12px', gap: 12, overflowY: 'auto' }}>
        {/* live banner */}
        <div style={{
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          padding: '10px 14px', borderRadius: R(r, 14),
          background: t.surface, boxShadow: t.shadow,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 9, height: 9, borderRadius: '50%', background: '#E03A3A', animation: 'pulse 1.4s infinite' }}/>
            <span style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 12, color: t.ink, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Élő · Szoba {code}</span>
          </div>
          <button onClick={onLeave} style={{
            padding: '4px 10px', border: 'none', background: t.coralSoft, color: t.coral,
            borderRadius: R(r, 999), fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 11,
            cursor: 'pointer', textTransform: 'uppercase', letterSpacing: '0.06em',
          }}>Kilépés</button>
        </div>

        {/* current game + meta */}
        <div style={{
          background: t.surface, borderRadius: R(r, 18),
          boxShadow: t.shadow, padding: '14px 14px',
          display: 'flex', alignItems: 'center', gap: 12,
        }}>
          <div key={tick} style={{
            width: 64, height: 64, borderRadius: R(r, 14),
            background: bonus ? `${t.purple}30` : `${currentGame.color}26`,
            display: 'grid', placeItems: 'center', padding: 8,
            flexShrink: 0, animation: 'popIn .35s cubic-bezier(.2,.9,.3,1.4)',
          }}>{bonus ? <span style={{ fontSize: 30 }}>🎁</span> : <GameImg g={currentGame} size="full"/>}</div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: t.inkSoft, letterSpacing: '0.1em', textTransform: 'uppercase' }}>{bonus ? 'Bonus képernyő' : 'Most játszik'}</div>
            <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 18, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay, marginTop: 2 }}>{bonus ? 'BÓNUSZ!' : currentGame.name}</div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 4 }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: mockPlayers[activeIdx].color }}/>
              <span style={{ fontFamily: t.font, fontSize: 12, fontWeight: 700, color: t.inkSoft }}>{mockPlayers[activeIdx].name} köre</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4 }}>
            <ObserverStat t={t} icon={Icon.dice(t.inkSoft)} value={round} label="kör"/>
            <ObserverStat t={t} icon={Icon.beer(t.coral)} value={totalDrinks} label="korty"/>
          </div>
        </div>

        {/* leaderboard */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '4px 4px 2px' }}>
            <div style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: t.inkSoft, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Élő eredmények</div>
            <div style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: t.inkMute, letterSpacing: '0.06em' }}>pont · korty</div>
          </div>
          {sorted.map((p, i) => {
            const isActive = p.id === mockPlayers[activeIdx].id;
            const isLeader = i === 0;
            const pct = (p.points / maxScore) * 100;
            const ppulse = pulseId === (p.id + ':p');
            const dpulse = pulseId === (p.id + ':d');
            return (
              <div key={p.id} style={{
                position: 'relative', overflow: 'hidden',
                background: t.surface, borderRadius: R(r, 12),
                boxShadow: t.shadow, padding: '10px 12px',
                display: 'flex', alignItems: 'center', gap: 10,
                transition: 'all .35s',
                outline: isActive ? `2px solid ${p.color}` : '2px solid transparent',
                transform: isActive ? 'translateX(2px)' : 'translateX(0)',
              }}>
                <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${pct}%`, background: `${p.color}14`, transition: 'width .6s cubic-bezier(.2,.9,.3,1)' }}/>
                <div style={{ position: 'relative', width: 18, fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 14, color: isLeader ? t.yellow : t.inkSoft, textAlign: 'center' }}>{isLeader ? '★' : i + 1}</div>
                <div style={{ position: 'relative', width: 32, height: 32, borderRadius: '50%', background: p.color, display: 'grid', placeItems: 'center', color: '#fff', fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 13 }}>{p.name.charAt(0)}</div>
                <div style={{ position: 'relative', flex: 1, minWidth: 0 }}>
                  <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 14, color: t.ink, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{p.name}</div>
                  {isActive && (
                    <div style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: p.color, letterSpacing: '0.06em', textTransform: 'uppercase', marginTop: 1 }}>Most ő játszik</div>
                  )}
                </div>
                <div style={{ position: 'relative', display: 'flex', alignItems: 'center', gap: 12 }}>
                  <ScoreChip t={t} icon={Icon.star(t.yellow)} value={p.points} pulse={ppulse} tone={t.yellow}/>
                  <ScoreChip t={t} icon={Icon.beer(t.coral)} value={p.drinks} pulse={dpulse} tone={t.coral}/>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* GM panel — bottom dock */}
      <GMPanel t={t} r={r} access={access}
        onRequest={requestAccess}
        onDrink={() => setSheet('drink')}
        onGroup={groupDrink}
        onBonus={triggerBonus}
        onEmoji={() => setSheet('emoji')}
        onUndo={undoLast}
        canUndo={history.length > 0}
      />

      {/* sheets */}
      {sheet === 'drink' && (
        <SheetOverlay t={t} r={r} onClose={() => setSheet(null)}>
          <DrinkSheet t={t} r={r} players={mockPlayers}
            onPick={(p, n) => { giveDrinks(p, n); setSheet(null); }}
          />
        </SheetOverlay>
      )}
      {sheet === 'emoji' && (
        <SheetOverlay t={t} r={r} onClose={() => setSheet(null)}>
          <EmojiSheet t={t} r={r} onPick={(e) => { sendEmoji(e); setSheet(null); }}/>
        </SheetOverlay>
      )}

      {/* feedback burst */}
      {burst && <ActionBurst t={t} r={r} burst={burst} />}
      {emojiFly && <EmojiFly char={emojiFly.char} key={emojiFly.id} />}
    </div>
  );
}

// ─── GM Console — bottom dock with 5 action buttons ──────────
function GMPanel({ t, r, access, onRequest, onDrink, onGroup, onBonus, onEmoji, onUndo, canUndo }) {
  const isB = t.id === 'B';

  const Action = ({ emoji, label, onClick, dim, badge }) => (
    <button onClick={dim ? undefined : onClick} disabled={dim} style={{
      flex: 1, minWidth: 0, padding: '8px 4px',
      background: t.surface, border: 'none',
      borderRadius: R(r, 14), boxShadow: t.shadow,
      cursor: dim ? 'default' : 'pointer', opacity: dim ? 0.4 : 1,
      display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
      transition: 'transform .1s',
      position: 'relative',
    }}
      onMouseDown={e => !dim && (e.currentTarget.style.transform = 'scale(0.94)')}
      onMouseUp={e => e.currentTarget.style.transform = ''}
      onMouseLeave={e => e.currentTarget.style.transform = ''}
    >
      <div style={{ fontSize: 24, lineHeight: 1 }}>{emoji}</div>
      <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 10, color: t.ink, letterSpacing: '0.03em', textAlign: 'center', lineHeight: 1.15 }}>{label}</div>
      {badge && (
        <div style={{
          position: 'absolute', top: 4, right: 4,
          minWidth: 16, height: 16, padding: '0 4px', borderRadius: 8,
          background: t.coral, color: '#fff',
          fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 9,
          display: 'grid', placeItems: 'center',
        }}>{badge}</div>
      )}
    </button>
  );

  return (
    <div style={{
      background: t.surface,
      borderTopLeftRadius: R(r, 24), borderTopRightRadius: R(r, 24),
      boxShadow: '0 -4px 18px rgba(20,30,50,0.06)',
      padding: '10px 14px 18px',
      flexShrink: 0,
    }}>
      {/* header strip */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '0 4px 6px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: 4,
            padding: '2px 8px', borderRadius: R(r, 999),
            background: access === 'granted' ? t.mintSoft : t.surfaceMuted,
            color: access === 'granted' ? t.mintDeep : t.inkSoft,
            fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 9,
            letterSpacing: '0.1em', textTransform: 'uppercase',
          }}>
            <span style={{ width: 5, height: 5, borderRadius: '50%', background: access === 'granted' ? t.mint : t.inkMute }}/>
            GM Console
          </span>
          <span style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: t.inkSoft, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
            {access === 'read' && '· csak nézés'}
            {access === 'pending' && '· engedély kérve…'}
            {access === 'granted' && '· vezérlés aktív'}
          </span>
        </div>
      </div>

      {access === 'read' && (
        <button onClick={onRequest} style={{
          width: '100%', minHeight: 50, border: `2px dashed ${t.mint}`,
          background: t.mintSoft, color: t.mintDeep,
          borderRadius: R(r, 14),
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 14,
          letterSpacing: t.letterDisplay, cursor: 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        }}>
          🔑 Vezérlés kérése a házigazdától
        </button>
      )}

      {access === 'pending' && (
        <div style={{
          width: '100%', minHeight: 50,
          background: t.surfaceMuted, color: t.inkSoft,
          borderRadius: R(r, 14),
          fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 13,
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        }}>
          {[0,1,2].map(i => <span key={i} style={{ width: 7, height: 7, borderRadius: '50%', background: t.inkSoft, animation: `dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>) }
          <span style={{ marginLeft: 4 }}>Várakozás a házigazda engedélyére</span>
        </div>
      )}

      {access === 'granted' && (
        <div style={{ display: 'flex', gap: 6 }}>
          <Action emoji="🍺" label="Korty" onClick={onDrink} />
          <Action emoji="🍻" label="Csoport" onClick={onGroup} />
          <Action emoji="🎁" label="Bonus" onClick={onBonus} />
          <Action emoji="💬" label="Emoji" onClick={onEmoji} />
          <Action emoji="↩️" label="Vissza" onClick={onUndo} dim={!canUndo} />
        </div>
      )}
    </div>
  );
}

// ─── Drink picker sheet ──────────────────────────────────────
function DrinkSheet({ t, r, players, onPick }) {
  const [picked, setPicked] = useStateP(null);
  const [amount, setAmount] = useStateP(1);
  return (
    <div style={{ padding: '4px 22px 22px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay }}>Korty osztás</div>
        <div style={{ fontFamily: t.font, fontSize: 12, fontWeight: 600, color: t.inkSoft, marginTop: 4 }}>Válassz játékost és kortyszámot</div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 8 }}>
        {players.map(p => {
          const on = picked && picked.id === p.id;
          return (
            <button key={p.id} onClick={() => setPicked(p)} style={{
              padding: '10px 4px 8px', border: 'none', cursor: 'pointer',
              background: on ? `${p.color}22` : t.surfaceMuted,
              borderRadius: R(r, 14),
              outline: on ? `2px solid ${p.color}` : '2px solid transparent',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4,
            }}>
              <div style={{ width: 40, height: 40, borderRadius: '50%', background: p.color, display: 'grid', placeItems: 'center', color: '#fff', fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 16 }}>{p.name.charAt(0)}</div>
              <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightTitle, fontSize: 11, color: t.ink, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '100%' }}>{p.name}</div>
            </button>
          );
        })}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10 }}>
        {[1, 2, 3].map(n => {
          const on = amount === n;
          return (
            <button key={n} onClick={() => setAmount(n)} style={{
              flex: 1, minHeight: 60, border: 'none', cursor: 'pointer',
              background: on ? t.coral : t.coralSoft,
              color: on ? '#fff' : t.coral,
              borderRadius: R(r, 14),
              fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 20,
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 2,
            }}>
              <div style={{ fontSize: 22, lineHeight: 1 }}>🍺{n > 1 ? '🍺' : ''}{n > 2 ? '🍺' : ''}</div>
              <div style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', opacity: 0.9 }}>{n} korty</div>
            </button>
          );
        })}
      </div>
      <PrimaryButton t={t} r={r} disabled={!picked} onClick={() => onPick(picked, amount)}>
        {picked ? `Idd meg, ${picked.name}! (${amount})` : 'Válassz játékost'}
      </PrimaryButton>
    </div>
  );
}

// ─── Emoji picker sheet ──────────────────────────────────────
function EmojiSheet({ t, r, onPick }) {
  const emojis = ['🔥','😂','👏','👎','🍻','💀','🤣','🤝','💩','🎯'];
  return (
    <div style={{ padding: '4px 22px 22px', display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 22, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay }}>Reakció</div>
        <div style={{ fontFamily: t.font, fontSize: 12, fontWeight: 600, color: t.inkSoft, marginTop: 4 }}>A választott emoji végigrepül a szobán</div>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 10 }}>
        {emojis.map(e => (
          <button key={e} onClick={() => onPick(e)} style={{
            aspectRatio: '1/1', border: 'none', cursor: 'pointer',
            background: t.surfaceMuted, borderRadius: R(r, 16),
            display: 'grid', placeItems: 'center', fontSize: 34,
            transition: 'transform .15s, background .15s',
          }}
            onMouseEnter={e2 => { e2.currentTarget.style.transform = 'scale(1.08)'; e2.currentTarget.style.background = t.surface; }}
            onMouseLeave={e2 => { e2.currentTarget.style.transform = ''; e2.currentTarget.style.background = t.surfaceMuted; }}
          >{e}</button>
        ))}
      </div>
    </div>
  );
}

// ─── Action burst — centered toast that pops + fades ─────────
function ActionBurst({ t, r, burst }) {
  return (
    <div style={{
      position: 'absolute', inset: 0, zIndex: 100,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      pointerEvents: 'none', padding: 24,
    }}>
      <div style={{
        background: t.surface,
        borderRadius: R(r, 22),
        padding: '20px 26px',
        boxShadow: '0 24px 60px rgba(20,30,50,0.25), 0 0 0 4px rgba(255,255,255,0.5)',
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 6,
        minWidth: 200, maxWidth: 280, textAlign: 'center',
        animation: 'burstPop .35s cubic-bezier(.2,.9,.3,1.5), burstFade .4s 1s forwards',
        borderTop: `4px solid ${burst.tone}`,
      }}>
        <div style={{ fontSize: 48, lineHeight: 1, animation: 'wobble .6s' }}>{burst.icon}</div>
        <div style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 18, color: t.ink, textTransform: 'uppercase', letterSpacing: t.letterDisplay, lineHeight: 1.1 }}>{burst.title}</div>
        <div style={{ fontFamily: t.font, fontSize: 12, fontWeight: 600, color: t.inkSoft }}>{burst.sub}</div>
      </div>
    </div>
  );
}

// ─── Floating emoji that flies up the screen ────────────────
function EmojiFly({ char }) {
  return (
    <div style={{
      position: 'absolute', inset: 0, zIndex: 90, pointerEvents: 'none',
      overflow: 'hidden',
    }}>
      {[0, 1, 2, 3, 4].map(i => (
        <div key={i} style={{
          position: 'absolute',
          left: `${15 + i * 18}%`, bottom: 0,
          fontSize: 36, opacity: 0,
          animation: `emojiRise 2.2s ${i * 0.15}s ease-out forwards`,
        }}>{char}</div>
      ))}
    </div>
  );
}

function ObserverStat({ t, icon, value, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
      <span style={{ display: 'inline-flex' }}>{icon}</span>
      <span style={{ fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 14, color: t.ink, fontVariantNumeric: 'tabular-nums' }}>{value}</span>
      <span style={{ fontFamily: t.font, fontSize: 10, fontWeight: 700, color: t.inkSoft, letterSpacing: '0.06em', textTransform: 'uppercase' }}>{label}</span>
    </div>
  );
}

function ScoreChip({ t, icon, value, pulse, tone }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 4, minWidth: 32, justifyContent: 'flex-end',
      transform: pulse ? 'scale(1.25)' : 'scale(1)',
      transition: 'transform .4s cubic-bezier(.2,.9,.3,1.4)',
    }}>
      <span style={{ display: 'inline-flex' }}>{icon}</span>
      <span style={{
        fontFamily: t.fontDisplay, fontWeight: t.weightDisplay, fontSize: 15,
        color: pulse ? tone : t.ink, fontVariantNumeric: 'tabular-nums',
        transition: 'color .3s',
      }}>{value}</span>
    </div>
  );
}

Object.assign(window, { PlayScreen, EndScreen, ObserverScreen });
