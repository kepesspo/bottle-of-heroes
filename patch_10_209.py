#!/usr/bin/env python3
# v10.209 — logo meg egyszer +20% (fooldal + nyito kepernyo)
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# 204 -> 245 (204 * 1.2 = 244.8, kerekitve)
sub('<Logo size={204} />', '<Logo size={245} />', 'fooldal logo')

# 288 -> 346 (288 * 1.2 = 345.6, kerekitve)
sub("""    #splash-logo {
      width:288px; height:288px; display:block;""",
    """    #splash-logo {
      width:346px; height:346px; display:block;""",
    'splash logo meret')

sub("const APP_VERSION = 'v10.208';", "const APP_VERSION = 'v10.209';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — logo meg +20%')
