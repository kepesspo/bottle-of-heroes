#!/usr/bin/env python3
# v10.208 — logo meg egyszer +20% (fooldal + nyito kepernyo), es a splash
# logo pixelesedesenek javitasa
#
# A pixelesedes oka: a splash_logo.png csak 192x192-es volt, a CSS viszont
# 240px-en jelenitette meg (retina kijelzon meg tobbszorosen felskalazva) —
# ez mindig elmosodott lett volna, meg nagyobb kijelzomeretnel meg inkabb.
# assets/splash_logo.png mostantol UGYANAZ az 1024x1024-es fajl, mint a
# fooldal logoja (assets/dnr_logo.png) — igy barmilyen CSS meretben eles marad.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# 170 -> 204 (170 * 1.2 = 204)
sub('<Logo size={170} />', '<Logo size={204} />', 'fooldal logo')

# 240 -> 288 (240 * 1.2 = 288)
sub("""    #splash-logo {
      width:240px; height:240px; display:block;""",
    """    #splash-logo {
      width:288px; height:288px; display:block;""",
    'splash logo meret')

sub("const APP_VERSION = 'v10.207';", "const APP_VERSION = 'v10.208';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — logo meg +20%, splash logo pixelesedese javitva')
