# v10.168 — a Jatekmenet oldal szekcio-sorrendje
#
# Kert sorrend:
#   1. osszegzo (jatekos / jatek / perc)
#   2. nehezsegi szint doboz (nehezseg + jateksorrend + max korok)
#   3. jatekok (a kivalasztott jatekok sajat beallitasai)
#   4. modok
#   5. egyeb
#
# A jatek-sorok blokkja EGYBEN mozdul a nehezsegi doboz moge; a harom
# beallitas-doboz kozul a "difficulty" csoport elore, a "modes" es "other"
# moge kerul.
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# a jatek-sorok blokkja (a kommenttol a lezaro </div>-ig)
a = s.index('        {/* Fejléc nélkül: a játék-sorok magukért beszélnek. */}')
b = s.index('          )}\n        </div>\n', a) + len('          )}\n        </div>\n')
games_block = s[a:b]
assert 'configurable.map' in games_block and games_block.count('<button key={g.id}') == 1, 'gyanus vagas'
s = s[:a] + s[b:]

# a beallitas-dobozok: a nehezsegi csoport elore, a tobbi utana
old = """        {/* A "Játékmenet" felirat itt nem kell — a fejlécben már ott van. */}
        {[['modes'], ['difficulty', 'order', 'maxRounds'], ['other']].map((grp, i) => (
          <div key={i} style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
            <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={grp} />
          </div>
        ))}
"""
assert s.count(old) == 1
BOX = """        {/* A "Játékmenet" felirat itt nem kell — a fejlécben már ott van. */}
        <div style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
          <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={['difficulty', 'order', 'maxRounds']} />
        </div>

"""
TAIL = """
        {[['modes'], ['other']].map((grp, i) => (
          <div key={i} style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
            <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} group={grp} />
          </div>
        ))}
"""
s = s.replace(old, BOX + games_block + TAIL)

s = s.replace("const APP_VERSION = 'v10.167';", "const APP_VERSION = 'v10.168';", 1)
assert "v10.168" in s and s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
