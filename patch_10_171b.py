# v10.171 (b) — egyedul futo jateknal a sajat beallitasa kerul elore
#
# Busznal / Beer Pongnal a jatek sajat beallitasa az egyetlen erdemi dolog a
# kepernyon — ne a nehezseg alatt legyen. Tobb jateknal marad a v10.168-ban
# kert sorrend (osszegzo -> nehezseg -> jatekok -> modok -> egyeb).
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# a jatek-sorok blokkja valtozoba
a = s.index('        {/* Fejléc nélkül: a játék-sorok magukért beszélnek. */}')
b = s.index('          )}\n        </div>\n', a) + len('          )}\n        </div>\n')
block = s[a:b]
assert 'configurable.map' in block
s = s[:a] + '        {!soloGame && gamesBlock}\n' + s[b:]

# a nehezseg-doboz ELE a solo valtozat
old_diff = """        <div style={{ ...cardStyle, marginTop:12, padding:'14px 16px' }}>
          <GameSettingsContent meta={gameMeta} setMeta={setGameMeta}
            group={soloGame ? ['difficulty'] : ['difficulty', 'order', 'maxRounds']} />
        </div>"""
assert s.count(old_diff) == 1
s = s.replace(old_diff, """        {soloGame && gamesBlock}
""" + old_diff)

# a blokk definicioja a return ele
inner = block.replace('        {/* Fejléc nélkül: a játék-sorok magukért beszélnek. */}\n', '')
inner = '\n'.join(('  ' + l) if l.strip() else l for l in inner.split('\n'))
marker = "  return (\n    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>\n      <AppBar title=\"Játékmenet\""
assert s.count(marker) == 1
s = s.replace(marker, """  // A kivalasztott jatekok sajat beallitasai. Egyedul futo jateknal ez az
  // egyetlen erdemi dolog a kepernyon, ezert oda a nehezseg ELE kerul.
  const gamesBlock = (
""" + inner.rstrip() + """
  );

""" + marker)

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK')
