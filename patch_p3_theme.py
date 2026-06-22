# -*- coding: utf-8 -*-
# P3 theme fix: replace hardcoded colors with T.* variables in all game components
with open('index.html','r',encoding='utf-8') as f: src=f.read()
orig_len = len(src)

def rep(old, new, count=None):
    global src
    if count:
        assert src.count(old) >= count, f'Expected >={count} occurrences of: {old[:60]!r}'
        src = src.replace(old, new, count)
    else:
        assert old in src, f'Not found: {old[:80]!r}'
        src = src.replace(old, new)

# ── ZeneGame (line ~40580) ─────────────────────────────────────────────────
# Dark buttons with #1B2340
rep("style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>",
    "style={{ width:'100%', padding:'14px 0', background:T.ink, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>", 1)

rep("style={{ width:'100%', padding:'14px 0', background:'#1B2340', border:'none', borderRadius:16, color:'#F0C040', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>",
    "style={{ width:'100%', padding:'14px 0', background:T.ink, border:'none', borderRadius:16, color:T.yellow, fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:10 }}>", 1)

rep("style={{ width:'100%', padding:'13px 0', background:'#fff', border:'none', borderRadius:16, color:'#1B2340', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', boxShadow:'0 2px 10px rgba(0,0,0,0.14)', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>",
    "style={{ width:'100%', padding:'13px 0', background:T.surface, border:'none', borderRadius:16, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer', boxShadow:T.shadow, display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>", 1)

rep("color:'#1B2340', letterSpacing:'-0.01em', lineHeight:1.15 }}>{song.artist}",
    "color:T.ink, letterSpacing:'-0.01em', lineHeight:1.15 }}>{song.artist}", 1)

rep('fill="#1B2340" stroke="#E0D8C8" strokeWidth="2.5"',
    'fill={T.ink} stroke={T.bgSoft} strokeWidth="2.5"', 1)

rep("background:'#EDE5CF', borderRadius:20, border:'2.5px solid #1B2340'",
    "background:T.bgSoft, borderRadius:20, border:'2.5px solid '+T.ink", 1)

rep("border:'3px solid #9aabb8', borderTopColor:'#1B2340'",
    "border:'3px solid '+T.inkMute, borderTopColor:T.ink", 1)

rep("fontFamily:T.font, fontWeight:700, fontSize:13, color:'#1B2340', lineHeight:1.3 }}>{celeb.name}",
    "fontFamily:T.font, fontWeight:700, fontSize:13, color:T.ink, lineHeight:1.3 }}>{celeb.name}", 1)

rep("fontSize:12, color:'#1B2340' }}>{lifespan}",
    "fontSize:12, color:T.ink }}>{lifespan}", 1)

rep("fontSize:12, color:'#1B2340' }}>{occupation}",
    "fontSize:12, color:T.ink }}>{occupation}", 1)

rep("background:'#1B2340', borderRadius:10, display:'flex', alignItems:'center', justifyContent:'center' }}>",
    "background:T.ink, borderRadius:10, display:'flex', alignItems:'center', justifyContent:'center' }}>", 1)

rep("background:'#1B2340', border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>",
    "background:T.ink, border:'none', borderRadius:14, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:16, cursor:'pointer', display:'flex', alignItems:'center', justifyContent:'center', gap:8 }}>", 1)

# KivagyokGame timer color
rep("color:'#1B2340', textAlign:'center', lineHeight:1.45, marginTop:32 }}>",
    "color:T.ink, textAlign:'center', lineHeight:1.45, marginTop:32 }}>", 1)

# ── ImposztorGame (line ~42144) ────────────────────────────────────────────
rep("background:'#1B2340', borderRadius:20, padding:'20px 18px 16px', display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>",
    "background:T.surface, borderRadius:20, padding:'20px 18px 16px', display:'flex', flexDirection:'column', alignItems:'center', gap:14 }}>", 1)

rep("fontFamily:T.font, fontWeight:800, fontSize:22, color:'#EF4444', letterSpacing:'0.05em' }}>IMPOSZTOR",
    "fontFamily:T.font, fontWeight:800, fontSize:22, color:T.coral, letterSpacing:'0.05em' }}>IMPOSZTOR", 1)

rep("background: holding ? '#8C7AE6' : '#6C5CE7'",
    "background: holding ? T.mint+'cc' : T.mint", 1)

rep("background:'#1B2340', border:'none', borderRadius:14, color:'rgba(255,255,255,0.9)'",
    "background:T.ink, border:'none', borderRadius:14, color:'#fff'", 1)

rep("background:'#1B2340', borderRadius:16, padding:'16px', width:'100%', display:'flex', flexDirection:'column', gap:12, alignItems:'center' }}>",
    "background:T.surface, borderRadius:16, padding:'16px', width:'100%', display:'flex', flexDirection:'column', gap:12, alignItems:'center' }}>", 1)

rep("background:'#1B2340', borderRadius:12, padding:'10px 16px', width:'100%', textAlign:'center' }}>",
    "background:T.bgSoft, borderRadius:12, padding:'10px 16px', width:'100%', textAlign:'center' }}>", 1)

rep("fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:'#EF4444' }}>{impostor.name}",
    "fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.coral }}>{impostor.name}", 1)

# ── RulettGame (line ~43049) ───────────────────────────────────────────────
rep("background:'#1B2340', color:'#fff', padding:'3px 16px', borderRadius:20, fontFamily:T.font, fontWeight:700, fontSize:11, letterSpacing:'0.12em' }}>",
    "background:T.ink, color:'#fff', padding:'3px 16px', borderRadius:20, fontFamily:T.font, fontWeight:700, fontSize:11, letterSpacing:'0.12em' }}>", 1)

rep("border: isSelected ? '3px solid #1B2340' : '3px solid rgba(255,255,255,0.82)'",
    "border: isSelected ? '3px solid '+T.ink : '3px solid '+T.inkMute+'44'", 1)

rep("background:'#fff', border:'2.5px solid #1B2340', boxShadow:'0 1px 5px rgba(0,0,0,0.25)' }}/>",
    "background:T.surface, border:'2.5px solid '+T.ink, boxShadow:T.shadow }}/>", 1)

# Spin button
rep("background: spinning ? 'rgba(255,255,255,0.45)' : '#1B2340'",
    "background: spinning ? T.bgSoft : T.ink", 1)

# Roulette SVG circle
rep("<circle r=\"68\" fill=\"#F4C95A\" stroke=\"#1B2340\" strokeWidth=\"5.5\"/>",
    "<circle r=\"68\" fill={T.yellow} stroke={T.ink} strokeWidth=\"5.5\"/>", 1)

rep("<circle r=\"54\" fill=\"none\" stroke=\"#1B2340\" strokeWidth=\"1.5\" strokeDasharray=\"6 4\" opacity=\"0.5\"/>",
    "<circle r=\"54\" fill=\"none\" stroke={T.ink} strokeWidth=\"1.5\" strokeDasharray=\"6 4\" opacity=\"0.5\"/>", 1)

rep("<circle cy=\"-14\" r=\"18\" fill=\"#1B2340\"/>",
    "<circle cy=\"-14\" r=\"18\" fill={T.ink}/>", 1)

rep("fill=\"#1B2340\"/>",
    "fill={T.ink}/>", 1)

rep("stroke=\"#1B2340\" strokeWidth=\"3.5\" strokeLinecap=\"round\"/>",
    "stroke={T.ink} strokeWidth=\"3.5\" strokeLinecap=\"round\"/>", 2)

rep("background:T.yellow, borderRadius:12, padding:'4px 10px', fontFamily:T.font, fontWeight:800, fontSize:12, color:'#1B2340' }}>",
    "background:T.yellow, borderRadius:12, padding:'4px 10px', fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink }}>", 1)

# ── KisebbGame pot counter (line ~43313) ───────────────────────────────────
rep("background:'#1B2340', boxShadow:'0 6px 22px rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center', position:'relative', flexShrink:0 }}>",
    "background:T.ink, boxShadow:'0 6px 22px rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center', position:'relative', flexShrink:0 }}>", 1)

rep("color: pot>=3 ? '#D05040' : pot>=2 ? '#E0A030' : '#1B2340'",
    "color: pot>=3 ? T.coral : pot>=2 ? T.yellow : T.ink", 1)

rep("border: isW ? `3.5px solid #1B2340` : `3px solid #fff`",
    "border: isW ? `3.5px solid ${T.ink}` : `3px solid ${T.surface}`", 1)

# SVG icon fallback — keep static color, skip

# ── TicktakGame (line ~43583) selected border ──────────────────────────────
rep("border:`2px solid ${selected ? '#F87171' : 'transparent'}`",
    "border:`2px solid ${selected ? T.coral : 'transparent'}`", 1)

# ── AnagrammaGame (line ~44031) ────────────────────────────────────────────
rep("const timerColor = countdown < 1 ? '#F4704A' : countdown < 2.5 ? '#F0C840' : '#50C882';",
    "const timerColor = countdown < 1 ? T.coral : countdown < 2.5 ? T.yellow : T.mint;", 1)

rep("const TILE_COLORS = ['#4A90D9','#50C882','#F4A4A0','#F0C840'];",
    "const TILE_COLORS = [T.mint, T.mint, T.coral, T.yellow];", 1)

rep("const timerColor = timeLeft > 3 ? '#50C882' : timeLeft > 1.5 ? '#F0C840' : '#F4704A';",
    "const timerColor = timeLeft > 3 ? T.mint : timeLeft > 1.5 ? T.yellow : T.coral;", 1)

rep("border: `2px solid ${i < pressed.length ? '#50C882' : 'rgba(0,0,0,0.12)'}`",
    "border: `2px solid ${i < pressed.length ? T.mint : T.inkMute+'20'}`", 1)

rep("fontFamily:'Georgia,serif', fontWeight:800, fontSize:24, color:'#1B2340'",
    "fontFamily:'Georgia,serif', fontWeight:800, fontSize:24, color:T.ink", 1)

rep("width:70, height:78, borderRadius:10, background:'#1B2340', boxShadow:'0 4px 0 rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center' }}>",
    "width:70, height:78, borderRadius:10, background:T.ink, boxShadow:'0 4px 0 rgba(0,0,0,0.22)', display:'flex', alignItems:'center', justifyContent:'center' }}>", 1)

# RingFireGame card back
rep("width:118, height:164, borderRadius:14, background:'#1B2340'",
    "width:118, height:164, borderRadius:14, background:T.ink", 1)

# ── PowerHourGame / BuszGame gradient buttons ──────────────────────────────
rep("background:`linear-gradient(135deg,#F59E0B,#F87171)`",
    "background:`linear-gradient(135deg,${T.yellow},${T.coral})`", 3)

rep("color:maxTimer<=30?T.coral:maxTimer<=60?'#F59E0B':T.ink",
    "color:maxTimer<=30?T.coral:maxTimer<=60?T.yellow:T.ink", 1)

rep("color:localTimer<=30?T.coral:localTimer<=60?'#F59E0B':T.ink",
    "color:localTimer<=30?T.coral:localTimer<=60?T.yellow:T.ink", 1)

rep("stroke={nextDrinkIn<=10?T.coral:'#F59E0B'}",
    "stroke={nextDrinkIn<=10?T.coral:T.yellow}", 1)

rep("color:nextDrinkIn<=10?T.coral:'#F59E0B'",
    "color:nextDrinkIn<=10?T.coral:T.yellow", 1)

rep("background:'linear-gradient(90deg,#F59E0B,#F87171)'",
    "background:`linear-gradient(90deg,${T.yellow},${T.coral})`", 1)

# ── CollectBoomGame (line ~45270) ─────────────────────────────────────────
rep("background: pot>=7 ? '#FFF0EE' : pot>=4 ? '#FFFBE6' : 'rgba(255,255,255,0.92)', borderRadius:14, padding:'8px 14px', boxShadow:T.shadow, flexShrink:0, minWidth:64, border:`2px solid ${pot>=7?'#F87171':pot>=4?'#F0C840':'transparent'}`",
    "background: pot>=7 ? T.coral+'18' : pot>=4 ? T.yellow+'18' : T.surface, borderRadius:14, padding:'8px 14px', boxShadow:T.shadow, flexShrink:0, minWidth:64, border:`2px solid ${pot>=7?T.coral:pot>=4?T.yellow:'transparent'}`", 1)

rep("border: `2px solid ${isBombCell?'#F87171':isDrink?'#50C882':'transparent'}`",
    "border: `2px solid ${isBombCell?T.coral:isDrink?T.mint:'transparent'}`", 1)

rep("color:'#50C882'}}>+{cell.v}",
    "color:T.mint}}>+{cell.v}", 1)

# KategoriaGame selected border
rep("border:`2px solid ${selected ? '#F87171' : 'transparent'}`",
    "border:`2px solid ${selected ? T.coral : 'transparent'}`", 1)

# ── MemoriaGame (line ~45513) ─────────────────────────────────────────────
rep("background: isMatched ? `${T.mint}22` : isMiss ? '#FFF0EE' : isFaceUp ? '#fff' : '#1B2340'",
    "background: isMatched ? `${T.mint}22` : isMiss ? T.coral+'18' : isFaceUp ? T.surface : T.ink", 1)

rep("border:`2px solid ${isMatched ? T.mint : isMiss ? '#F87171' : isFaceUp ? '#E8E0D4' : 'transparent'}`",
    "border:`2px solid ${isMatched ? T.mint : isMiss ? T.coral : isFaceUp ? T.inkMute+'30' : 'transparent'}`", 1)

# ── SzolancGame (line ~45771) ─────────────────────────────────────────────
rep("  const SZ_GREEN = '#4CAF50';",
    "  const SZ_GREEN = T.mint;", 1)

rep("  const SZ_RED   = '#E85C4A';",
    "  const SZ_RED   = T.coral;", 1)

rep("background: i<S.showIdx ? SZ_GREEN : i===S.showIdx ? '#F59E0B' : SZ_DOT_OFF",
    "background: i<S.showIdx ? SZ_GREEN : i===S.showIdx ? T.yellow : SZ_DOT_OFF", 1)

# ── CardBattleGame (line ~46108) ──────────────────────────────────────────
rep("  const CB_GREEN = '#4CAF50';",
    "  const CB_GREEN = T.mint;", 1)

rep("  const CB_RED   = '#E85C4A';",
    "  const CB_RED   = T.coral;", 1)

# ── IdoparbajGame (line ~46446) ───────────────────────────────────────────
rep("background:'#1B2340', borderRadius:16, padding:'16px 24px', width:'100%', textAlign:'center', boxSizing:'border-box'",
    "background:T.surface, borderRadius:16, padding:'16px 24px', width:'100%', textAlign:'center', boxSizing:'border-box'", 1)

# ── BeerPong tableau button (line ~39446) ─────────────────────────────────
rep("background:'#F59E0B', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', gap:8 }}>",
    "background:T.yellow, color:T.ink, fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', gap:8 }}>", 1)

# BeerPong stop timer button (wrong answer red)
rep("background:'#F4A0A0', color:'#fff', whiteSpace:'nowrap'",
    "background:T.coral+'44', color:T.coral, whiteSpace:'nowrap'", 1)

# ── EmojiKvizGame + TabuGame — nothing extra needed (already caught above)

# ── version bump ──────────────────────────────────────────────────────────
assert 'v9.450' in src, 'version not found'
src = src.replace('v9.450', 'v9.451', 1)

with open('index.html','w',encoding='utf-8') as f: f.write(src)
print(f'OK — {orig_len} → {len(src)} chars')
