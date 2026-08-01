#!/usr/bin/env python3
# v10.263 — Result Banner: ne írjunk ki „0 KORTY"-t
#
# A Büntetés (és minden más, ahol fejenként MÁS az összeg — Sohanem, Fingerit)
# `drinks:0`-val hívja az onResult-ot, és a tényleges mennyiségeket a
# jegyzet-sor sorolja fel nevenként („Sere 2🍺, Kecsi 1🍺").
#
# A régi banner ezt kezelte: a nagy számot csak `drinks > 0` esetén rajzolta ki.
# Az új kártyán viszont a metrika feltétel nélkül futott, így „0 KORTY" állt ott.
#
# Javítás: az ivó sor csak akkor kapja meg a szám-oszlopot, ha van mit kiírni.
# A kicsi sávnál ugyanez: 0 kortynál nem esik vissza „+1 pont"-ra, hanem nem
# mutat számot — a nevek és a jegyzet mondja el, mi történt.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

def sub(old, new, what):
    global src
    assert src.count(old) == 1, '%s: %d talalat' % (what, src.count(old))
    src = src.replace(old, new, 1)

# ── 1. a nagy kartya ivo sora ──
sub("""          const value = kind === 'win' ? '+1' : String(drinks);
          const unit = kind === 'win' ? 'PONT' : 'KORTY';""",
    """          const value = kind === 'win' ? '+1' : String(drinks);
          const unit = kind === 'win' ? 'PONT' : 'KORTY';
          // Ha fejenkent MAS az osszeg (Buntetes, Sohanem, Fingerit), a jatek
          // drinks:0-t kuld, es a jegyzet sorolja fel nevenkent. Ilyenkor nincs
          // mit kiirni a szam-oszlopba — a "0 KORTY" hazugsag lenne.
          const showMetric = kind === 'win' || drinks > 0;""",
    'showMetric')

sub("""                {Pile({ list, max:1, size:av, overlap:0, borderW:3 })}
                <div style={{ flex:1, minWidth:0 }}>
                  {kickerEl}
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize: soloCard ? 27 : 20, color:T.ink, lineHeight:1.15, letterSpacing:'-0.02em', marginTop:4, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{list[0].name}</div>
                </div>
                {Metric({ value, unit, color:col })}""",
    """                {Pile({ list, max:1, size:av, overlap:0, borderW:3 })}
                <div style={{ flex:1, minWidth:0 }}>
                  {kickerEl}
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize: soloCard ? 27 : 20, color:T.ink, lineHeight:1.15, letterSpacing:'-0.02em', marginTop:4, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{list[0].name}</div>
                </div>
                {showMetric && Metric({ value, unit, color:col })}""",
    'egy fos sor metrika')

sub("""                <div style={{ flex:1, minWidth:0 }}>{kickerEl}</div>
                {Metric({ value, unit, color:col })}""",
    """                <div style={{ flex:1, minWidth:0 }}>{kickerEl}</div>
                {showMetric && Metric({ value, unit, color:col })}""",
    'tobb fos sor metrika')

# ── 2. a kicsi sav ──
sub("""              <div style={{ flexShrink:0, display:'flex', alignItems:'baseline', gap:5 }}>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:24, letterSpacing:'-0.03em', color:miniCol, fontVariantNumeric:'tabular-nums' }}>{drinks ? drinks : '+1'}</span>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, letterSpacing:'0.13em', color:T.inkMute }}>{drinks ? 'KORTY' : 'PONT'}</span>
              </div>""",
    """              {/* 0 kortynal nincs szam: nem esunk vissza "+1 pont"-ra, mert az
                  mast allitana, mint ami tortent (lasd patch_10_263.py). */}
              {(drinks > 0 || (hasWin && !hasLose)) && (
                <div style={{ flexShrink:0, display:'flex', alignItems:'baseline', gap:5 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:24, letterSpacing:'-0.03em', color:miniCol, fontVariantNumeric:'tabular-nums' }}>{drinks ? drinks : '+1'}</span>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:9, letterSpacing:'0.13em', color:T.inkMute }}>{drinks ? 'KORTY' : 'PONT'}</span>
                </div>
              )}""",
    'kicsi sav metrika')

sub("const APP_VERSION = 'v10.262';", "const APP_VERSION = 'v10.263';", 'verzio')
open(P, 'w', encoding='utf-8').write(src)
print('OK — nincs tobb "0 KORTY"')
