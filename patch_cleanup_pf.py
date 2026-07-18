#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# usePfTokens + pf.* maradványok kitakarítása (a wildcard/csoportos ivászat overlay-ekben).
# Minden pf.playful classic ágra oldva; a pf token-mezők konkrét classic értékre.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

CARD_SH = "'0 24px 64px rgba(0,0,0,0.3)'"

# 55514 — wildcard sáv
rep("""          <div style={{ display:'flex', alignItems:'center', gap:10, background: pf.playful ? T.surfaceMuted : T.surface, border:pf.borderThin, borderLeft: pf.playful ? `2px solid ${T.ink}` : `4px solid ${T.yellow}`, borderRadius:14, padding:'7px 12px', boxShadow: pf.playful ? `0 3px 0 ${T.ink}` : '0 3px 12px rgba(20,30,50,0.10)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>""",
    """          <div style={{ display:'flex', alignItems:'center', gap:10, background: T.surface, border:'none', borderLeft: `4px solid ${T.yellow}`, borderRadius:14, padding:'7px 12px', boxShadow: '0 3px 12px rgba(20,30,50,0.10)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>""")

# 55517 — Szabályszegő gomb
rep("""            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:pf.borderThin, borderRadius:10, background: pf.playful ? T.yellow : T.ink, color: pf.playful ? T.ink : T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding: pf.playful ? '6px 10px' : '8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>""",
    """            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:'none', borderRadius:10, background: T.ink, color: T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding: '8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>""")

# 55664 — wildcard popup kártya
rep("""                <div style={{ background: pf.playful ? T.surfaceMuted : T.surface, border:pf.border, borderRadius: pf.playful ? 24 : 28, padding:'22px 22px 24px', boxShadow: pf.playful ? pf.shadowCard : '0 18px 48px rgba(0,0,0,0.28)', position:'relative', overflow:'visible' }}>""",
    """                <div style={{ background: T.surface, border:'none', borderRadius: 28, padding:'22px 22px 24px', boxShadow: '0 18px 48px rgba(0,0,0,0.28)', position:'relative', overflow:'visible' }}>""")

# 55667 — WILDCARD KÖR pill
rep("""                  <div style={{ display:'inline-block', fontFamily:T.font, fontWeight:900, fontSize:11, color:T.ink, textTransform:'uppercase', letterSpacing:'0.16em', background:T.yellow, border:pf.borderThin, borderRadius:999, padding:'5px 12px' }}>{t('wildcardRound')}</div>""",
    """                  <div style={{ display:'inline-block', fontFamily:T.font, fontWeight:900, fontSize:11, color:T.ink, textTransform:'uppercase', letterSpacing:'0.16em', background:T.yellow, border:'none', borderRadius:999, padding:'5px 12px' }}>{t('wildcardRound')}</div>""")

# 55974 — csoportos ivászat kártya
rep("""          <div style={{ background: pf.playful ? T.surfaceMuted : T.surface, border:pf.border, borderRadius: pf.playful ? 24 : 28, padding:'32px 28px 28px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:16, boxShadow:pf.shadowCard, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""",
    """          <div style={{ background: T.surface, border:'none', borderRadius: 28, padding:'32px 28px 28px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:16, boxShadow:""" + CARD_SH + """, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""")

# 55989 — szabályszegő-választó kártya
rep("""          <div onClick={e => e.stopPropagation()} style={{ background: pf.playful ? T.surfaceMuted : T.surface, border:pf.border, borderRadius: pf.playful ? 24 : 28, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:pf.shadowCard, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""",
    """          <div onClick={e => e.stopPropagation()} style={{ background: T.surface, border:'none', borderRadius: 28, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:""" + CARD_SH + """, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""")

# 55995 — játékos sor a választóban
rep("""                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:pf.borderThin, background: pf.playful ? T.surface : T.surfaceMuted, boxShadow: pf.playful ? `0 2px 0 ${T.ink}` : 'none', cursor:'pointer', textAlign:'left' }}>""",
    """                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:'none', background: T.surfaceMuted, boxShadow: 'none', cursor:'pointer', textAlign:'left' }}>""")

# 56002 — Mégse gomb
rep("""            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border: pf.playful ? `2px solid ${T.ink}55` : 'none', background: pf.playful ? 'transparent' : T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>""",
    """            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border: 'none', background: T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>""")

# const pf = usePfTokens(); törlése
rep("  const pf = usePfTokens();\n", "")

# usePfTokens függvény törlése
rep("""function usePfTokens() {
  const playful = useAppDesign() === 'playful';
  return {
    playful,
    border: playful ? `2.5px solid ${T.ink}` : 'none',
    borderThin: playful ? `2px solid ${T.ink}` : 'none',
    shadowCard: playful ? `0 6px 0 ${T.ink}` : '0 24px 64px rgba(0,0,0,0.3)',
    shadow: playful ? `0 4px 0 ${T.ink}` : T.shadow,
    shadowSm: playful ? `0 3px 0 ${T.ink}` : T.shadow,
  };
}

""", "")

assert 'usePfTokens' not in src
assert 'pf.playful' not in src and 'pf.border' not in src and 'pf.shadow' not in src

# Verziobump
rep("const APP_VERSION = 'v9.973';", "const APP_VERSION = 'v9.974';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — usePfTokens + pf.* cleaned')
