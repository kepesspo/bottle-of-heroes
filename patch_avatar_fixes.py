#!/usr/bin/env python3
"""
v9.594 — Avatar picker UI javítások:
1. Avatar scroll sor: padding a scale clip ellen
2. Szín picker: 8 szín (16 helyett)
3. Profile picker: avatar kép megjelenítés
4. Bottom sheet profil gombok: avatar kép + avatarId átadás
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.593') >= 1
html = html.replace('v9.593', 'v9.594', 1)

# ── 1. Avatar scroll sor: padding a scale(1.1) clip ellen ──────────────────
OLD_SCROLL = "display:'flex', gap:8, overflowX:'auto', paddingBottom:4, WebkitOverflowScrolling:'touch', scrollbarWidth:'none'"
NEW_SCROLL = "display:'flex', gap:8, overflowX:'auto', padding:'6px 4px 10px', WebkitOverflowScrolling:'touch', scrollbarWidth:'none'"
assert html.count(OLD_SCROLL) == 1
html = html.replace(OLD_SCROLL, NEW_SCROLL, 1)

# ── 2. Szín picker: 8 szín ──────────────────────────────────────────────────
OLD_COLORS = """const PLAYER_COLORS = [
  '#4FC2A0','#E985B8','#F4C95A','#5BA0DB','#A88AE8','#F97316',
  '#EF4444','#06B6D4','#84CC16','#F59E0B','#8B5CF6','#EC4899',
  '#14B8A6','#64748B','#D946EF','#0EA5E9',
];"""
NEW_COLORS = """const PLAYER_COLORS = [
  '#4FC2A0','#E985B8','#F4C95A','#5BA0DB','#A88AE8','#F97316','#EF4444','#06B6D4',
];"""
assert html.count(OLD_COLORS) == 1
html = html.replace(OLD_COLORS, NEW_COLORS, 1)

# ── 3. Profile picker listában avatar kép ────────────────────────────────────
OLD_PROF_ICON = """<div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
                      </div>"""
NEW_PROF_ICON = """<div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0, overflow:'hidden' }}>
                        {(prof.img || (prof.avatarId && CHAR_AVATARS.find(a=>a.id===prof.avatarId)?.img))
                          ? <img src={prof.img || CHAR_AVATARS.find(a=>a.id===prof.avatarId).img} style={{ width:30, height:30, objectFit:'cover' }} />
                          : <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>}
                      </div>"""
assert html.count(OLD_PROF_ICON) == 1, f"prof icon: {html.count(OLD_PROF_ICON)}"
html = html.replace(OLD_PROF_ICON, NEW_PROF_ICON, 1)

# ── 4. Bottom sheet profil gombok: avatar kép + avatarId ────────────────────
OLD_BOTTOM_NEW = "const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, img:pr.img||null };"
NEW_BOTTOM_NEW = """const _bsAv = pr.avatarId ? CHAR_AVATARS.find(a=>a.id===pr.avatarId) : null;
                              const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, avatarId:pr.avatarId||null, img:pr.img||(_bsAv?_bsAv.img:null) };"""
assert html.count(OLD_BOTTOM_NEW) == 1, f"bottom new: {html.count(OLD_BOTTOM_NEW)}"
html = html.replace(OLD_BOTTOM_NEW, NEW_BOTTOM_NEW, 1)

OLD_BOTTOM_IMG = """<div style={{ width:26, height:26, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                                {pr.img ? <img src={pr.img} style={{ width:26, height:26, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                              </div>"""
NEW_BOTTOM_IMG = """<div style={{ width:26, height:26, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                                {(pr.img||(pr.avatarId&&CHAR_AVATARS.find(a=>a.id===pr.avatarId)?.img)) ? <img src={pr.img||CHAR_AVATARS.find(a=>a.id===pr.avatarId).img} style={{ width:26, height:26, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                              </div>"""
assert html.count(OLD_BOTTOM_IMG) == 1, f"bottom img: {html.count(OLD_BOTTOM_IMG)}"
html = html.replace(OLD_BOTTOM_IMG, NEW_BOTTOM_IMG, 1)

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
