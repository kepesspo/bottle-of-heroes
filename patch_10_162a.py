# v10.162 (a) — a hangos musorvezeto kivezetese
#
# "soha nem hasznaltuk es szerintem nem is mukodik". Megy a kapcsolo es a jatek
# kozbeni ot bemondas is — kulonben halott kod maradna.
#
# A window.bohSpeak segedfuggveny MARAD: nem csak a musorvezeto hasznalja,
# hanem a Poharkoszonto is (a jatek menujebol inditva, kapcsolotol fuggetlenul).
# Az elso valtozat torolni akarta, es azzal nemava tette volna a poharkoszontot.
import io

P = 'app.src.html'
lines = io.open(P, encoding='utf-8').read().split('\n')

one, blk = [], None
for i, ln in enumerate(lines):
    if 'ttsHost' not in ln: continue
    st = ln.strip()
    if 'meta.ttsHost' in ln and 'gameMeta' not in ln: continue   # a kapcsolo sajat sorai
    if st.startswith('if (') and st.endswith('{'):
        assert blk is None, 'egynel tobb blokk'
        blk = i
    elif st.startswith('if (') and 'bohSpeak' in st:
        one.append(i)
assert len(one) == 4, f'egysoros bemondas: {len(one)} (4 kellene)'
assert blk is not None

indent = len(lines[blk]) - len(lines[blk].lstrip())
end = None
for j in range(blk + 1, blk + 40):
    if lines[j].strip() == '}' and (len(lines[j]) - len(lines[j].lstrip())) == indent:
        end = j; break
assert end is not None, 'nem talalom a blokk zarasat'
assert 'bohSpeak' in '\n'.join(lines[blk:end]), 'gyanus blokk'

drop = set(one) | set(range(blk, end + 1))
s = '\n'.join(ln for i, ln in enumerate(lines) if i not in drop)

i = s.find('      <ToggleRow\n        icon="party"\n        label="Hangos műsorvezető"')
assert i > 0, 'nincs meg a kapcsolo'
j = s.index('/>', s.index('infoText=', i)) + len('/>') + 1
assert s[i:j].count('<ToggleRow') == 1, 'a vagas tulnyulik'
s = s[:i] + s[j:]

assert 'ttsHost' not in s, 'maradt ttsHost'
assert s.count('bohSpeak') == 3, f'bohSpeak: {s.count("bohSpeak")} (definicio 1 + a poharkoszonto sora 2)'
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — musorvezeto kivezetve; a bohSpeak marad a poharkoszontonek')
