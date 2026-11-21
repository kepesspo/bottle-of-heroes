# v10.460 — Gender Reveal: új logó („A · Lufipár"), ÚJ fájlnéven (a régi névvel a gyorsítótár nem frissülne)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt):
    global s
    n = s.count(old); assert n == cnt, (n, old)
    s = s.replace(old, new)
rep("const APP_VERSION = 'v10.459';", "const APP_VERSION = 'v10.460';", 1)
rep("assets/dnr_reveal_app.png", "assets/dnr_reveal_logo_app.png", 5)
rep("assets/dnr_reveal_mark.png", "assets/dnr_reveal_logo_mark.png", 2)
open(P, 'w', encoding='utf-8').write(s)
m = 'manifest-reveal.json'
t = open(m, encoding='utf-8').read()
assert t.count('assets/dnr_reveal_app.png') == 3
open(m, 'w', encoding='utf-8').write(t.replace('assets/dnr_reveal_app.png', 'assets/dnr_reveal_logo_app.png'))
print('ok')
