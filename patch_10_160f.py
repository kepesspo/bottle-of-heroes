# v10.160 (f) — a folyamat bekotese
#
# A Jatekok oldal indito gombja a kapcsolotol fuggoen vagy egybol a jatekot
# inditja (regi ut), vagy a Jatekmenet oldalra visz (uj ut). A szobat tovabbra
# is a go('play') hozza letre — az uj oldal csak koze ekelodik, a jatek
# inditasanak logikaja valtozatlan.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# ── 1) router ag ──
old = "        {screen==='games'    && <GamesScreen    go={go} selectedGames={selectedGames} setSelectedGames={setSelectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} />}"
assert s.count(old) == 1
s = s.replace(old, old + """
        {screen==='setup'    && <SetupScreen    go={go} players={players} selectedGames={selectedGames} gameMeta={gameMeta} setGameMeta={setGameMeta} />}""")

# ── 2) a Jatekok oldal indito gombja ──
old_btn = """        <PrimaryButton disabled={selectedGames.length < 1} onClick={() => go('play')}>
          <span>{t('startGame')} ({selectedGames.length})</span>"""
assert s.count(old_btn) == 1
s = s.replace(old_btn, """        <PrimaryButton disabled={selectedGames.length < 1} onClick={() => go(setupFlow ? 'setup' : 'play')}>
          <span>{setupFlow ? 'Tovább' : t('startGame')} ({selectedGames.length})</span>""")

# a GamesScreen olvassa a kapcsolot
hook = "  const [filterSheet, setFilterSheet] = useState(false);"
assert s.count(hook) == 1
s = s.replace(hook, hook + "\n  const setupFlow = useSetupFlow();")

# ── 3) a Jatekmenet-lap gombja a Jatekok oldalon csak a REGI uton kell:
#      az uj uton ugyanaz a tartalom kap sajat oldalt, ket helyen felesleges.
old_gear = """      <BottomBar extra={
        <button onClick={() => setSheet(true)} style={{"""
assert s.count(old_gear) == 1
s = s.replace(old_gear, """      <BottomBar extra={setupFlow ? null : (
        <button onClick={() => setSheet(true)} style={{""")
old_gear_end = """        }}>{Icon.settings(T.ink)}</button>
      }>"""
assert s.count(old_gear_end) == 1
s = s.replace(old_gear_end, """        }}>{Icon.settings(T.ink)}</button>
      )}>""")

s = s.replace("const APP_VERSION = 'v10.159';", "const APP_VERSION = 'v10.160';", 1)
assert "v10.160" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — folyamat bekotve')
