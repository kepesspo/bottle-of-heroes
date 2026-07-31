#!/usr/bin/env python3
# v10.207 — a fooldal es a nyito-kepernyo logoja 20%-kal nagyobb
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# 142 -> 170 (142 * 1.2 = 170.4, kerekitve)
sub('<Logo size={142} />', '<Logo size={170} />', 'fooldal logo')

# 200 -> 240 (200 * 1.2 = 240)
sub("""    #splash-logo {
      width:200px; height:200px; display:block;""",
    """    #splash-logo {
      width:240px; height:240px; display:block;""",
    'splash logo meret')

sub("const APP_VERSION = 'v10.206';", "const APP_VERSION = 'v10.207';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — logo +20% a fooldalon es a nyito kepernyon')
