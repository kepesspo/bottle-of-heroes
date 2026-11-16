# v10.432: Gender Reveal — leleplezés, vendégfeltöltés jóváhagyással, jókívánság-fal,
# Babaquiz, album (ZIP + galéria-link). A teljes Gender Reveal blokkot cseréli.
import sys
p = 'app.src.html'
s = open(p, encoding='utf-8').read()
a = s.index('// ── Gender Reveal: élő képvetítő kivetítőre (v10.430)')
b = s.index('// ── Pub: saját keverés űrlap (új / szerkesztés)')
block = open(sys.argv[1] if len(sys.argv) > 1 else 'patch_10_432_reveal.jsx', encoding='utf-8').read()
s = s[:a] + block + s[b:]
assert s.count("const APP_VERSION = 'v10.431';") == 1
s = s.replace("const APP_VERSION = 'v10.431';", "const APP_VERSION = 'v10.432';")
open(p, 'w', encoding='utf-8').write(s)
print('ok')
