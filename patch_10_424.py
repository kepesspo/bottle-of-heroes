# v10.424 — az egységes app-ikonok ÚJ fájlnévre: dnr_<app>_icon.png → dnr_<app>_app.png
# Ok: a v10.423 ugyanazon a néven írta felül a képeket, és a készülékek a régit
# mutatták a gyorsítótárból (SW cache-first + böngésző HTTP-cache).
import re, os, subprocess
APPS = 'events|box|pub|tipp|torta|bingo|liga'
pat = re.compile(r"dnr_(%s)_icon\.png" % APPS)
files = ['app.src.html'] + sorted(f for f in os.listdir('.') if f.startswith('manifest') and f.endswith('.json')) \
        + ['tests/pwa_apps_test.js', 'tests/torta_home_test.js']
total = 0
for f in files:
    s = open(f, encoding='utf8').read()
    s2, n = pat.subn(r"dnr_\1_app.png", s)
    assert n > 0 or f == 'manifest.json', f
    total += n
    open(f, 'w', encoding='utf8').write(s2)
assert total == 29 + 21 + 4, total
for a in APPS.split('|'):
    subprocess.check_call(['git', 'mv', 'assets/dnr_%s_icon.png' % a, 'assets/dnr_%s_app.png' % a])
g = open('make_unified_icons.py', encoding='utf8').read()
g2 = g.replace("for base, suffix in ((WHITE, 'icon'),", "for base, suffix in ((WHITE, 'app'),") \
      .replace("if suffix == 'icon':", "if suffix == 'app':") \
      .replace("#   dnr_<app>_icon.png  — 1024", "#   dnr_<app>_app.png   — 1024")
assert g2.count("'app'") == 2 and g2 != g
open('make_unified_icons.py', 'w', encoding='utf8').write(g2)
s = open('app.src.html', encoding='utf8').read()
assert s.count("const APP_VERSION = 'v10.423';") == 1
open('app.src.html', 'w', encoding='utf8').write(s.replace("const APP_VERSION = 'v10.423';", "const APP_VERSION = 'v10.424';"))
print('ok', total)
