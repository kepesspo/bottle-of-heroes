with open('index.html','r') as f: src=f.read()

OLD = "  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;\n  return null;"
NEW = "  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;\n  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} initialBpState={null} onSetHideFooter={onSetHideFooter} />;\n  return null;"

assert OLD in src, 'not found'
src = src.replace(OLD, NEW, 1)
with open('index.html','w') as f: f.write(src)
print('OK')
