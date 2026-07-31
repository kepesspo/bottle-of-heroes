#!/usr/bin/env python3
# v10.236 — térköz a Statisztika szűrősora ALATT is
#
# A szűrő-pirulák fölött 10 px hézag volt, alattuk viszont semmi: a lista
# első kártyája nekiment a piruláknak. Az ok, hogy a hézag eddig csak a
# GÖRGETHETŐ konténer padding-top-ja volt — amint a felhasználó megmozdította
# a listát, el is tűnt.
#
# Javítás: a hézag a szűrő-blokk padding-bottom-jába kerül (az a sáv nem
# görgethető, tehát mindig ott marad), a görgethető rész teteje csak annyi
# levegőt kap, hogy a kártyák árnyéka ne vágódjon le.
# Ugyanez a "Múlt" fülre is kell, ahol nincs szűrősor.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. fülsor: a "Múlt" fülön nincs szűrősor, ott a fülsor adja a hézagot ──
sub("""      <div style={{ padding:'10px 16px 0', display:'flex', alignItems:'center', gap:10, maxWidth:1180, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    """      <div style={{ padding: tab === 'history' ? '10px 16px 10px' : '10px 16px 0', display:'flex', alignItems:'center', gap:10, maxWidth:1180, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    'fulsor padding')

# ── 2. szűrő-blokk: alul ugyanannyi hézag, mint fölül ──
sub("""        <div style={{ padding:'10px 16px 0', maxWidth:1180, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    """        <div style={{ padding:'10px 16px 10px', maxWidth:1180, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>""",
    'szurosor padding')

# ── 3. a görgethető lista teteje: csak az árnyéknak hagyott levegő ──
sub("""        <div style={{ position:'absolute', inset:0, overflowY:'auto', padding:'10px 16px 40px' }}><div style={{ maxWidth:1180, width:'100%', margin:'0 auto' }}>""",
    """        <div style={{ position:'absolute', inset:0, overflowY:'auto', padding:'2px 16px 40px' }}><div style={{ maxWidth:1180, width:'100%', margin:'0 auto' }}>""",
    'lista padding')

sub("const APP_VERSION = 'v10.235';", "const APP_VERSION = 'v10.236';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — terkoz a szurosor alatt is')
