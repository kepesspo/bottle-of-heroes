#!/usr/bin/env python3
"""
v9.595 — Avatar fix: PRESET_PLAYERS fallback minden profil megjelenítésnél
A Firestore-ban régi adatok vannak avatarId nélkül — a kód most a PRESET_PLAYERS-ből
keresi ki az avatart ha a Firestore-profil nem tartalmazza.
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.594') >= 1
html = html.replace('v9.594', 'v9.595', 1)

# ── 1. selectProfile: PRESET_PLAYERS fallback ────────────────────────────────
OLD_SELECT = """  const selectProfile = (prof) => {
    onChange({ name: prof.nickname || prof.name, color: prof.color, profileId: prof.id, img: prof.img || null, avatarId: prof.avatarId || null });
    setShowDropdown(false);
  };"""
NEW_SELECT = """  const selectProfile = (prof) => {
    const preset = PRESET_PLAYERS.find(p => p.id === prof.id);
    const avatarId = prof.avatarId || preset?.avatarId || null;
    const charAv = avatarId ? CHAR_AVATARS.find(a => a.id === avatarId) : null;
    onChange({ name: prof.nickname || prof.name, color: prof.color, profileId: prof.id,
               img: prof.img || (charAv ? charAv.img : null), avatarId });
    setShowDropdown(false);
  };"""
assert html.count(OLD_SELECT) == 1, f"selectProfile: {html.count(OLD_SELECT)}"
html = html.replace(OLD_SELECT, NEW_SELECT, 1)

# ── 2. Profile picker lista: PRESET_PLAYERS fallback ─────────────────────────
OLD_PROF_ICON = """<div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0, overflow:'hidden' }}>
                        {(prof.img || (prof.avatarId && CHAR_AVATARS.find(a=>a.id===prof.avatarId)?.img))
                          ? <img src={prof.img || CHAR_AVATARS.find(a=>a.id===prof.avatarId).img} style={{ width:30, height:30, objectFit:'cover' }} />
                          : <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>}
                      </div>"""
NEW_PROF_ICON = """<div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0, overflow:'hidden' }}>
                        {(() => { const _pid = prof.avatarId || PRESET_PLAYERS.find(p=>p.id===prof.id)?.avatarId; const _pimg = prof.img || (_pid ? CHAR_AVATARS.find(a=>a.id===_pid)?.img : null); return _pimg ? <img src={_pimg} style={{ width:30, height:30, objectFit:'cover' }} /> : <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>; })()}
                      </div>"""
assert html.count(OLD_PROF_ICON) == 1, f"prof icon: {html.count(OLD_PROF_ICON)}"
html = html.replace(OLD_PROF_ICON, NEW_PROF_ICON, 1)

# ── 3. Bottom sheet: PRESET_PLAYERS fallback a megjelenítéshez ───────────────
OLD_BOTTOM_IMG = """<div style={{ width:26, height:26, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                                {(pr.img||(pr.avatarId&&CHAR_AVATARS.find(a=>a.id===pr.avatarId)?.img)) ? <img src={pr.img||CHAR_AVATARS.find(a=>a.id===pr.avatarId).img} style={{ width:26, height:26, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                              </div>"""
NEW_BOTTOM_IMG = """<div style={{ width:26, height:26, borderRadius:'50%', background:pr.color||T.mint, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
                                {(() => { const _aid = pr.avatarId || PRESET_PLAYERS.find(p=>p.id===pr.id)?.avatarId; const _im = pr.img || (_aid ? CHAR_AVATARS.find(a=>a.id===_aid)?.img : null); return _im ? <img src={_im} style={{ width:26, height:26, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>; })()}
                              </div>"""
assert html.count(OLD_BOTTOM_IMG) == 1, f"bottom img: {html.count(OLD_BOTTOM_IMG)}"
html = html.replace(OLD_BOTTOM_IMG, NEW_BOTTOM_IMG, 1)

# ── 4. Bottom sheet: PRESET_PLAYERS fallback az új játékos létrehozásához ────
OLD_BOTTOM_NEW = """const _bsAv = pr.avatarId ? CHAR_AVATARS.find(a=>a.id===pr.avatarId) : null;
                              const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, avatarId:pr.avatarId||null, img:pr.img||(_bsAv?_bsAv.img:null) };"""
NEW_BOTTOM_NEW = """const _bsAid = pr.avatarId || PRESET_PLAYERS.find(p=>p.id===pr.id)?.avatarId || null;
                              const _bsAv = _bsAid ? CHAR_AVATARS.find(a=>a.id===_bsAid) : null;
                              const newP = { id:Date.now().toString(), name:pr.nickname||pr.name, drinks:0, points:0, color:pr.color||PLAYER_COLORS[players.length%PLAYER_COLORS.length], profileId:pr.id, avatarId:_bsAid, img:pr.img||(_bsAv?_bsAv.img:null) };"""
assert html.count(OLD_BOTTOM_NEW) == 1, f"bottom new: {html.count(OLD_BOTTOM_NEW)}"
html = html.replace(OLD_BOTTOM_NEW, NEW_BOTTOM_NEW, 1)

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
