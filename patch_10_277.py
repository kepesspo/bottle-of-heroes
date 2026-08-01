#!/usr/bin/env python3
# v10.277 — a Collect & Boom korty-plafonja lejjebb: 4 / 8 / 12
#
#   4×4: 10 -> 4      5×5: 15 -> 8      6×6: 20 -> 12
#
# Egyetlen helyen kell atirni: a v10.276 ota a config-lap, a jatek es a
# tet-korong (`stakeOf`) is a kozos COLLECT_MAX_POT-bol olvas. Igy a "Max korty"
# sor, a jatek `Math.min(pot+v, MAX_POT)` vagasa es a fejlec korongja egyszerre
# valtozik — nem tud szetcsuszni.
#
# Amit ez a fejlecben jelent (Nehez, ×3):
#   4×4: 3–30 -> 3–12      5×5: 3–45 -> 3–24      6×6: 3–60 -> 3–36
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub("const COLLECT_MAX_POT = { 4: 10, 5: 15, 6: 20 };",
    "const COLLECT_MAX_POT = { 4: 4, 5: 8, 6: 12 };",
    'plafon')

sub("const APP_VERSION = 'v10.276';", "const APP_VERSION = 'v10.277';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — 4 / 8 / 12')
