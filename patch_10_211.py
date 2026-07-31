#!/usr/bin/env python3
# v10.211 — a logo koruli szovegek meg kozelebb
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

sub('.home-brand      { display:flex; flex-direction:column; align-items:center; gap:10px; }',
    '.home-brand      { display:flex; flex-direction:column; align-items:center; gap:4px; }',
    'home-brand gap')
sub('''      .home-brand { gap:6px; }''',
    '''      .home-brand { gap:2px; }''',
    'home-brand gap (alacsony kepernyo)')

sub('''    #splash-title-wrap {
      position:relative; z-index:2; margin-top:10px;''',
    '''    #splash-title-wrap {
      position:relative; z-index:2; margin-top:4px;''',
    'splash cim tavolsaga')
sub('''    #splash-tagline {
      margin-top:6px;''',
    '''    #splash-tagline {
      margin-top:3px;''',
    'splash szlogen tavolsaga')

sub("const APP_VERSION = 'v10.210';", "const APP_VERSION = 'v10.211';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — a logo koruli szovegek meg kozelebb')
