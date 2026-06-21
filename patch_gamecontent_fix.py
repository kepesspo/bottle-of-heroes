# -*- coding: utf-8 -*-
with open('index.html','r',encoding='utf-8') as f: src=f.read()

OLD = """  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'idopárbaj') return <IdoparbajGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'csakegyszó') return <CsakEgySzoGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'uveg') return <UvegGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'ticktak') return <TicktakGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'erem') return <EremGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} roomCode={roomCode} />;
  if (gameId === 'anagramma') return <AnagrammaGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;
  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;
  if (gameId === 'kopapir') return <KoPapirGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;
  if (gameId === 'powerhour') return <PowerHourGame key={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'kategoria') return <KategoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'memoria') return <MemoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} difficulty={gameMeta?.difficulty} />;
  if (gameId === 'sohanem') return <SohanemGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;
  if (gameId === 'fingerit') return <FingeritGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'cardbattle') return <CardBattleGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;
  if (gameId === 'utveszto') return <UtvesztoGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} initialBpState={null} onSetHideFooter={onSetHideFooter} />;
  return null;"""

NEW = """  if (gameId === 'szolánc') return <SzolancGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'idopárbaj') return <IdoparbajGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'csakegyszó') return <CsakEgySzoGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'uveg') return <UvegGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'ticktak') return <TicktakGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'erem') return <EremGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'tapper') return <TapperGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} roomCode={roomCode} />;
  if (gameId === 'anagramma') return <AnagrammaGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;
  if (gameId === 'ringfire') return <RingFireGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;
  if (gameId === 'kopapir') return <KoPapirGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'collect') return <CollectBoomGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;
  if (gameId === 'powerhour') return <PowerHourGame key={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'kategoria') return <KategoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'memoria') return <MemoriaGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'kezcsere') return <KezCsereGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'otdolog') return <OtdologGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} difficulty={gameMeta?.difficulty} />;
  if (gameId === 'sohanem') return <SohanemGame key={gameIdx} gameIdx={gameIdx} onAdvance={onAdvance} />;
  if (gameId === 'fingerit') return <FingeritGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} />;
  if (gameId === 'cardbattle') return <CardBattleGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'quiz') return <QuizGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} gameMeta={gameMeta} />;
  if (gameId === 'utveszto') return <UtvesztoGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} players={players||[]} onAdvance={onAdvance} onResult={onResult} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'beerpong') return <BeerPongGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} roomCode={roomCode} initialBpState={null} onSetHideFooter={onSetHideFooter} />;
  if (gameId === 'busz') return <BuszGame key={gameIdx} gameIdx={gameIdx} players={players||[]} roomCode={roomCode} gameMeta={gameMeta} onAdvance={onAdvance} onSetHideFooter={onSetHideFooter} onSetBuszSwitch={onSetBuszSwitch} />;
  if (gameId === 'imposztor') return <ImposztorGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'rulett') return <RulettGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'kisebb') return <KisebbGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} onLiveDrinkUpdate={onLiveDrinkUpdate} gameMeta={gameMeta} roomCode={roomCode} />;
  if (gameId === 'zene') return <ZeneGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} gameMeta={gameMeta} />;
  if (gameId === 'loverseny') return <LóversenyGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onUnready={onUnready} onResult={onResult} />;
  if (gameId === 'szerencse') return <SzerencsekerékGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'kivagyok') return <KivagyokGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'mindenki') return <MindenkiGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'igazhamis') return <IgazHamisGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'farkasos') return <FarkasosGame key={gameIdx} gameIdx={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'meduza') return <MeduzaGame key={gameIdx} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'ritmus') return <RitmusGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} players={players||[]} onAdvance={onAdvance} onResult={onResult} />;
  if (gameId === 'szamsor') return <SzamsorGame key={gameIdx} gameIdx={gameIdx} challenger={challenger} opponent={opponent} onAdvance={onAdvance} onResult={onResult} />;
  return null;"""

assert OLD in src, 'GameContent block not found'
src = src.replace(OLD, NEW, 1)

assert 'v9.433' in src, 'version not found'
src = src.replace('v9.433', 'v9.434', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print('OK')
