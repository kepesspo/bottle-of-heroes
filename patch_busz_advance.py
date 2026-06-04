with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# 1. Add onAdvance to BuszGame signature
old = "function BuszGame({ players, roomCode, mode, gameIdx, gameMeta }) {"
new = "function BuszGame({ players, roomCode, mode, gameIdx, gameMeta, onAdvance }) {"
assert old in html, "sig not found"
html = html.replace(old, new, 1)

# 2. Add useEffect after the existing useEffects to fire onAdvance when phase=done
old = "  const persist = async (newState) => {"
new = """  useEffect(() => {
    if (buszState?.phase === 'done') {
      onAdvance && onAdvance({});
    }
  }, [buszState?.phase]);

  const persist = async (newState) => {"""
assert old in html, "persist not found"
html = html.replace(old, new, 1)

# 3. Pass onAdvance from PlayScreen
old = "  if (gameId === 'busz') return <BuszGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={gameId==='busz'&&typeof roomCode!=='undefined'?roomCode:undefined} mode={mode} gameMeta={gameMeta} />;"
new = "  if (gameId === 'busz') return <BuszGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={gameId==='busz'&&typeof roomCode!=='undefined'?roomCode:undefined} mode={mode} gameMeta={gameMeta} onAdvance={onAdvance} />;"
assert old in html, "PlayScreen busz line not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
