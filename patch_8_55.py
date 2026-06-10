#!/usr/bin/env python3
"""v8.55: Molnár Balázs profilkép beágyazása"""

with open('/tmp/balazs_photo.b64', 'r') as f:
    b64 = f.read().strip()

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. IMGS dict-be beágyazás ─────────────────────────────────────────────────
# Az IMGS dict végét keressük — az utolsó bejegyzés után szúrjuk be
OLD_IMGS_END = """const IMG = '';  // images embedded below"""
NEW_IMGS_END = f"""const IMG = '';  // images embedded below"""

# Valójában az IMGS dict-et az előtte lévő sor alapján szúrjuk be
OLD_SZOLANC = """  'szolánc_symbol.png':"""
# Keressük az IMGS lezárását
import re
# Megkeressük az IMGS objektum záró }; sorát
imgs_close = "  'bus_custom_icon.png':"
# Keressük a megfelelő helyet — az IMGS dict végén, a const IMG = '' előtt
OLD_IMGS_MARKER = """};
const IMG = '';  // images embedded below"""
NEW_IMGS_MARKER = f"""  'profile_balazs.jpg': 'data:image/jpeg;base64,{b64}',
}};
const IMG = '';  // images embedded below"""

assert OLD_IMGS_MARKER in content, "IMGS end marker not found"
content = content.replace(OLD_IMGS_MARKER, NEW_IMGS_MARKER, 1)
print("✓ Balázs profilkép beágyazva az IMGS-be")

# ── 2. saveProfile: img mező támogatás ───────────────────────────────────────
OLD_SAVE = """    var data = { name: profile.name, color: profile.color };
    if (profile.nickname) data.nickname = profile.nickname;"""
NEW_SAVE = """    var data = { name: profile.name, color: profile.color };
    if (profile.nickname) data.nickname = profile.nickname;
    if (profile.img) data.img = profile.img;"""

assert OLD_SAVE in content, "saveProfile data not found"
content = content.replace(OLD_SAVE, NEW_SAVE, 1)
print("✓ saveProfile: img mező")

# ── 3. PRESET_PLAYERS: Balázs kap imgKey-t ───────────────────────────────────
OLD_BALAZS = """    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8' },"""
NEW_BALAZS = """    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8', imgKey:'profile_balazs.jpg' },"""

assert OLD_BALAZS in content, "Balázs preset not found"
content = content.replace(OLD_BALAZS, NEW_BALAZS, 1)
print("✓ Balázs: imgKey hozzáadva")

# ── 4. Seed: imgKey → img mentés ─────────────────────────────────────────────
OLD_SEED_SAVE = """      window.saveProfile({ id: p.id, name: p.name, nickname: p.nickname, color: p.color });"""
NEW_SEED_SAVE = """      window.saveProfile({ id: p.id, name: p.name, nickname: p.nickname, color: p.color, img: p.imgKey ? (typeof IMGS !== 'undefined' ? IMGS[p.imgKey] : null) : null });"""

assert OLD_SEED_SAVE in content, "seed saveProfile not found"
content = content.replace(OLD_SEED_SAVE, NEW_SEED_SAVE, 1)
print("✓ Seed: img mentés Firestore-ba")

# ── 5. PlayerCard: profilkép megjelenítése ────────────────────────────────────
OLD_AVATAR = """      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center' }}>{Icon.user('#fff')}</div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, textAlign:'center', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'100%' }}>{p.name || 'Új játékos'}</div>"""

NEW_AVATAR = """      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
        {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover', borderRadius:'50%' }} /> : Icon.user('#fff')}
      </div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, textAlign:'center', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'100%' }}>{p.name || 'Új játékos'}</div>"""

assert OLD_AVATAR in content, "PlayerCard avatar not found"
content = content.replace(OLD_AVATAR, NEW_AVATAR, 1)
print("✓ PlayerCard: profilkép megjelenítése")

# ── 6. PlayerEditSheet: avatar körben profilkép ──────────────────────────────
OLD_EDIT_AVATAR = """            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center' }}>
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>"""

NEW_EDIT_AVATAR = """            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
              {player.img ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} /> : (
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                  <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </div>"""

assert OLD_EDIT_AVATAR in content, "EditSheet avatar not found"
content = content.replace(OLD_EDIT_AVATAR, NEW_EDIT_AVATAR, 1)
print("✓ PlayerEditSheet: profilkép az avatarban")

# ── 7. selectProfile: img is átadódik ────────────────────────────────────────
OLD_SELECT = """    onChange({ name: prof.nickname || prof.name, color: prof.color, profileId: prof.id });"""
NEW_SELECT = """    onChange({ name: prof.nickname || prof.name, color: prof.color, profileId: prof.id, img: prof.img || null });"""

assert OLD_SELECT in content, "selectProfile onChange not found"
content = content.replace(OLD_SELECT, NEW_SELECT, 1)
print("✓ selectProfile: img átadva")

# ── 8. StatsScreen: avatar profilkép ────────────────────────────────────────
OLD_STAT_AVATAR = """                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {played} meccs · {s.bp_wins||0} győzelem · {s.bp_losses||0} vereség
                    </div>"""

NEW_STAT_AVATAR = """                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                    {p.img ? <img src={p.img} style={{ width:44, height:44, objectFit:'cover', borderRadius:'50%' }} /> : p.name.charAt(0).toUpperCase()}
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {played} meccs · {s.bp_wins||0} győzelem · {s.bp_losses||0} vereség
                    </div>"""

assert OLD_STAT_AVATAR in content, "StatsScreen BP avatar not found"
content = content.replace(OLD_STAT_AVATAR, NEW_STAT_AVATAR, 1)
print("✓ StatsScreen BP: profilkép")

# Busz tab avatar ugyanígy
OLD_BUSZ_AVATAR = """                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {s.busz_played||0} játék · {s.busz_completions||0} teljesítve"""

NEW_BUSZ_AVATAR = """                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                    {p.img ? <img src={p.img} style={{ width:44, height:44, objectFit:'cover', borderRadius:'50%' }} /> : p.name.charAt(0).toUpperCase()}
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {s.busz_played||0} játék · {s.busz_completions||0} teljesítve"""

assert OLD_BUSZ_AVATAR in content, "StatsScreen Busz avatar not found"
content = content.replace(OLD_BUSZ_AVATAR, NEW_BUSZ_AVATAR, 1)
print("✓ StatsScreen Busz: profilkép")

# ── 9. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.54';"
NEW_VER = "const APP_VERSION = 'v8.55';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.55 saved")
