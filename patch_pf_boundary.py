#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Éles Classic/Playful határ:
#  - usePfTokens() közös mód-token helper (kontúr/árnyék egy helyen definiálva)
#  - Wildcard felületek (popup kártya, kör alatti sáv, szabályszegő-választó)
#    mód-követők: Playful = ink kontúr + kemény árnyék, Classic = lágy árnyék
#  - Csoportos ivászat kártya is mód-követő
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:90])
    src = src.replace(old, new)

# 1) usePfTokens a useAppDesign mellé
rep("""function useAppDesign() {
  const [d, setD] = React.useState(_appDesign);
  React.useEffect(() => {
    _appDesignSubs.add(setD);
    setD(_appDesign);
    if (!_appDesignInit && typeof window.onHomeDesign === 'function') {
      _appDesignInit = true;
      window.onHomeDesign(x => _setAppDesign(x));
    }
    return () => { _appDesignSubs.delete(setD); };
  }, []);
  return d;
}""",
"""function useAppDesign() {
  const [d, setD] = React.useState(_appDesign);
  React.useEffect(() => {
    _appDesignSubs.add(setD);
    setD(_appDesign);
    if (!_appDesignInit && typeof window.onHomeDesign === 'function') {
      _appDesignInit = true;
      window.onHomeDesign(x => _setAppDesign(x));
    }
    return () => { _appDesignSubs.delete(setD); };
  }, []);
  return d;
}

// Mód-függő kontúr/árnyék tokenek EGY helyen definiálva.
// Szabály: ink kontúr + kemény eltolt árnyék = Playful; lágy szórt árnyék = Classic.
// (Az ikonok és a kabala márkaelemek — mindkét módban azonosak.)
function usePfTokens() {
  const playful = useAppDesign() === 'playful';
  return {
    playful,
    border: playful ? `2.5px solid ${T.ink}` : 'none',
    borderThin: playful ? `2px solid ${T.ink}` : 'none',
    shadowCard: playful ? `0 6px 0 ${T.ink}` : '0 24px 64px rgba(0,0,0,0.3)',
    shadow: playful ? `0 4px 0 ${T.ink}` : T.shadow,
    shadowSm: playful ? `0 3px 0 ${T.ink}` : T.shadow,
  };
}""")

# 2) PlayScreen: pf tokenek
rep("""  const [roundPopup, setRoundPopup] = useState(null); // {round, wildcard, leaving}
  const [activeWildcard, setActiveWildcard] = useState(null); // {emoji, text, round} — a kör alatt végig látható szabály""",
"""  const pf = usePfTokens();
  const [roundPopup, setRoundPopup] = useState(null); // {round, wildcard, leaving}
  const [activeWildcard, setActiveWildcard] = useState(null); // {emoji, text, round} — a kör alatt végig látható szabály""")

# 3) Wildcard popup kártya mód-követő
rep("""                <div style={{ background:T.surfaceMuted, border:`2.5px solid ${T.ink}`, borderRadius:24, padding:'22px 22px 24px', boxShadow:`0 6px 0 ${T.ink}`, position:'relative', overflow:'visible' }}>""",
"""                <div style={{ background: pf.playful ? T.surfaceMuted : T.surface, border:pf.border, borderRadius: pf.playful ? 24 : 28, padding:'22px 22px 24px', boxShadow: pf.playful ? pf.shadowCard : '0 18px 48px rgba(0,0,0,0.28)', position:'relative', overflow:'visible' }}>""")
rep("""                  <div style={{ display:'inline-block', fontFamily:T.font, fontWeight:900, fontSize:11, color:T.ink, textTransform:'uppercase', letterSpacing:'0.16em', background:T.yellow, border:`2px solid ${T.ink}`, borderRadius:999, padding:'5px 12px' }}>{t('wildcardRound')}</div>""",
"""                  <div style={{ display:'inline-block', fontFamily:T.font, fontWeight:900, fontSize:11, color:T.ink, textTransform:'uppercase', letterSpacing:'0.16em', background:T.yellow, border:pf.borderThin, borderRadius:999, padding:'5px 12px' }}>{t('wildcardRound')}</div>""")

# 4) Kör alatti sáv mód-követő
rep("""          <div style={{ display:'flex', alignItems:'center', gap:10, background:T.surfaceMuted, border:`2px solid ${T.ink}`, borderRadius:14, padding:'7px 12px', boxShadow:`0 3px 0 ${T.ink}`, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>""",
"""          <div style={{ display:'flex', alignItems:'center', gap:10, background: pf.playful ? T.surfaceMuted : T.surface, border:pf.borderThin, borderLeft: pf.playful ? `2px solid ${T.ink}` : `4px solid ${T.yellow}`, borderRadius:14, padding:'7px 12px', boxShadow: pf.playful ? `0 3px 0 ${T.ink}` : '0 3px 12px rgba(20,30,50,0.10)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.2)' }}>""")
rep("""            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:`2px solid ${T.ink}`, borderRadius:10, background:T.yellow, color:T.ink, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding:'6px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>""",
"""            <button onClick={() => setWcPunishOpen(true)} style={{ flexShrink:0, border:pf.borderThin, borderRadius:10, background: pf.playful ? T.yellow : T.ink, color: pf.playful ? T.ink : T.yellow, fontFamily:T.font, fontWeight:900, fontSize:11.5, padding: pf.playful ? '6px 10px' : '8px 10px', cursor:'pointer', display:'flex', alignItems:'center', gap:5 }}>""")

# 5) Szabályszegő-választó mód-követő
rep("""          <div onClick={e => e.stopPropagation()} style={{ background:T.surfaceMuted, border:`2.5px solid ${T.ink}`, borderRadius:24, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:`0 6px 0 ${T.ink}`, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""",
"""          <div onClick={e => e.stopPropagation()} style={{ background: pf.playful ? T.surfaceMuted : T.surface, border:pf.border, borderRadius: pf.playful ? 24 : 28, padding:'26px 22px 22px', width:'100%', maxWidth:340, boxShadow:pf.shadowCard, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>""")
rep("""                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:`2px solid ${T.ink}`, background:T.surface, boxShadow:`0 2px 0 ${T.ink}`, cursor:'pointer', textAlign:'left' }}>""",
"""                <button key={p.id} onClick={() => punishWildcard(p.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', borderRadius:14, border:pf.borderThin, background: pf.playful ? T.surface : T.surfaceMuted, boxShadow: pf.playful ? `0 2px 0 ${T.ink}` : 'none', cursor:'pointer', textAlign:'left' }}>""")
rep("""            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border:`2px solid ${T.ink}55`, background:'transparent', color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>""",
"""            <button onClick={() => setWcPunishOpen(false)} style={{ width:'100%', marginTop:12, padding:'12px 0', borderRadius:14, border: pf.playful ? `2px solid ${T.ink}55` : 'none', background: pf.playful ? 'transparent' : T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>""")

# 6) Csoportos ivászat kártya mód-követő
rep("""          <div style={{ background:T.surface, borderRadius:28, padding:'32px 28px 28px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:16, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <BohIcon name="beer" size={48} />""",
"""          <div style={{ background: pf.playful ? T.surfaceMuted : T.surface, border:pf.border, borderRadius: pf.playful ? 24 : 28, padding:'32px 28px 28px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:16, boxShadow:pf.shadowCard, animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <BohIcon name="beer" size={48} />""")

# 7) Verziobump
rep("const APP_VERSION = 'v9.954';", "const APP_VERSION = 'v9.955';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — pf boundary applied')
