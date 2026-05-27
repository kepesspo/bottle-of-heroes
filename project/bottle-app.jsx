// bottle-app.jsx — the BottleApp component. Owns routing + shared state.
// Renders inside an IOSDevice frame.

const { useState: useStateA, useEffect: useEffectA } = React;

function BottleApp({ variant = 'A', radius = 1, tileStyle = 1, dimMode = 'fade', buszBadge = 'corner' }) {
  const t = variant === 'B' ? THEME_B : variant === 'C' ? THEME_C : THEME_A;
  const r = radius;
  const [screen, setScreen] = useStateA('home');
  const [prev, setPrev] = useStateA(null);
  const [mode, setMode] = useStateA('Online');
  const [players, setPlayers] = useStateA(INITIAL_PLAYERS);
  const [selectedGames, setSelectedGames] = useStateA(['busz', 'memoria', 'erem']);
  const [gameMeta, setGameMeta] = useStateA({ modes: ['points', 'bonus'], difficulty: 'easy' });

  const go = (next) => {
    setPrev(screen);
    setScreen(next);
  };
  const resetGame = () => {
    setPlayers(players.map(p => ({ ...p, drinks: 0, points: 0 })));
    setScreen('play');
  };

  // Map screen names → forward/back direction for slide animation.
  const order = ['home', 'players', 'games', 'play', 'end', 'observer'];
  const dir = order.indexOf(screen) >= order.indexOf(prev || 'home') ? 1 : -1;

  return (
    <div key={t.id} style={{
      width: '100%', height: '100%', position: 'relative',
      fontFamily: t.font, color: t.ink,
      WebkitFontSmoothing: 'antialiased',
      overflow: 'hidden',
    }}>
      {/* status bar zone padding so content doesn't underlap the island */}
      <div style={{ height: 58, flexShrink: 0 }} />
      <div key={screen} style={{
        position: 'absolute', top: 58, left: 0, right: 0, bottom: 0,
        display: 'flex', flexDirection: 'column',
        animation: `slide${dir > 0 ? 'In' : 'Back'} .35s cubic-bezier(.2,.85,.3,1.05)`,
      }}>
        {screen === 'home'     && <HomeScreen     t={t} r={r} go={go} mode={mode} setMode={setMode} />}
        {screen === 'players'  && <PlayersScreen  t={t} r={r} go={go} players={players} setPlayers={setPlayers} />}
        {screen === 'games'    && <GamesScreen    t={t} r={r} go={go} selectedGames={selectedGames} setSelectedGames={setSelectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} tileStyle={tileStyle} dimMode={dimMode} buszBadge={buszBadge} />}
        {screen === 'play'     && <PlayScreen     t={t} r={r} go={go} players={players} setPlayers={setPlayers} selectedGames={selectedGames} />}
        {screen === 'end'      && <EndScreen      t={t} r={r} go={go} players={players} resetGame={resetGame} />}
        {screen === 'observer' && <ObserverScreen t={t} r={r} go={go} />}
      </div>
    </div>
  );
}

window.BottleApp = BottleApp;
