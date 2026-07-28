# v10.162 (b) — a jatekmenet-beallitasok csoportokra bonthatoak
#
# Eddig egyetlen lapos lista volt, ezert nem lehetett kulon dobozokba tenni.
# Mostantol a `group` proppal kerheto belole egy-egy szelet. A regi folyamat
# lapja tovabbra is prop nelkul hivja, tehat egyben, valtozatlanul jelenik meg.
import io, re

P = 'app.src.html'
src = io.open(P, encoding='utf-8').read()
lines = src.split('\n')

start = next(i for i, l in enumerate(lines) if l.startswith('function GameSettingsContent'))
ret = next(i for i in range(start, start + 80) if lines[i] == '  return (')
opener = ret + 1
assert "padding:'0 18px 18px'" in lines[opener], lines[opener]
close = next(i for i in range(opener + 1, opener + 200)
             if lines[i] == '    </div>' and lines[i + 1] == '  );')

body = lines[opener + 1:close]
heads = [i for i, l in enumerate(body) if "letterSpacing:'0.13em'" in l]
assert len(heads) == 5, f'{len(heads)} szekciofejlec (5 kellene)'

KEYS = ['modes', 'difficulty', 'order', 'maxRounds', 'other']
chunks = []
for n, h in enumerate(heads):
    stop = heads[n + 1] if n + 1 < len(heads) else len(body)
    chunk = body[h:stop]
    # a fejlec felso margoja fuggjon attol, hogy a csoport elso eleme-e
    chunk[0] = re.sub(r"margin:'\d+px 0 (\d+)px'", r"margin: first ? '0 0 \1px' : '20px 0 \1px'", chunk[0])
    assert 'first ?' in chunk[0], chunk[0][:120]
    chunks.append(chunk)

out = ['  const SECTIONS = {']
for key, chunk in zip(KEYS, chunks):
    out.append('    %s: (first) => (<React.Fragment>' % key)
    out.extend('  ' + l for l in chunk)
    out.append('    </React.Fragment>),')
out.append('  };')
out.append("  const keys = (group && group.length ? group : %s).filter(k => SECTIONS[k]);" % KEYS)
out.append('  return (')
out.append("    <div style={{ padding: group ? 0 : '0 18px 18px', display:'flex', flexDirection:'column' }} onClick={() => setOpenInfo(null)}>")
out.append('      {keys.map((k, i) => <React.Fragment key={k}>{SECTIONS[k](i === 0)}</React.Fragment>)}')
out.append('    </div>')
out.append('  );')

lines[ret:close + 2] = out
s = '\n'.join(lines)
s = s.replace('function GameSettingsContent({ meta, setMeta, onDone, go }) {',
              'function GameSettingsContent({ meta, setMeta, onDone, go, group }) {', 1)
assert 'group }' in s
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — %d szekcio kulon kerheto: %s' % (len(KEYS), ', '.join(KEYS)))
