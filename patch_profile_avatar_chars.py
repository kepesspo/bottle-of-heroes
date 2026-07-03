import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Replace avatarImg state with avatarId state
OLD1 = "  const [avatarImg, setAvatarImg] = React.useState(null);"
NEW1 = "  const [avatarId, setAvatarId] = React.useState(null);"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Update save() to use avatarId -> img lookup
OLD2 = """    const prof = { name: name.trim(), color };
    if (avatarImg) prof.img = avatarImg;
    window.saveProfile(prof).then(() => {
      setSaving(false); setShowForm(false); setName(''); setColor('#E8631A'); setAvatarImg(null); load();"""
NEW2 = """    const prof = { name: name.trim(), color };
    if (avatarId) { const av = CHAR_AVATARS.find(a => a.id === avatarId); if (av) { prof.img = av.img; prof.avatarId = av.id; } }
    window.saveProfile(prof).then(() => {
      setSaving(false); setShowForm(false); setName(''); setColor('#E8631A'); setAvatarId(null); load();"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Replace the avatar grid (friendship icons -> CHAR_AVATARS)
OLD3 = """          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Avatar</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:8, marginBottom:14 }}>
            {[null,'00fb8bff7_030-dependable.png','03d87dd1b_014-sharing.png','0be64fa0c_033-reunion.png','1b1a4e166_041-shaka.png','21cd10e7c_034-chat.png','30be0a7f6_022-bracelet.png','4d3e02af9_016-best-friend.png','6c2a1444c_002-mad.png','717d78f62_026-fist.png','7721960ea_024-friendship-1.png','8892f3ea4_017-origami.png','955f768b7_006-loyalty.png','a6501c235_011-friendship.png','b2b517b2a_005-promise.png','b3ebed6db_012-beer.png','c08054bde_008-puzzle.png','c6e7b8a7f_021-listener.png','c7dd9fd19_018-social-media.png','e20faaaa0_048-letter.png','ed7ba4369_013-laugh.png','f52ad051b_035-friend.png','fbae429ac_025-add-friend.png','fd5a5b716_007-connection.png'].map((key, i) => {
              const isNone = key === null;
              const src = isNone ? null : IMGS[key];
              const sel = isNone ? !avatarImg : avatarImg === src;
              return (
                <div key={i} onClick={() => setAvatarImg(isNone ? null : src)} style={{ width:'100%', aspectRatio:'1', borderRadius:12, overflow:'hidden', cursor:'pointer', border:`2.5px solid ${sel ? T.mint : 'transparent'}`, background: isNone ? T.border : 'transparent', display:'grid', placeItems:'center', boxSizing:'border-box', transition:'border-color .15s' }}>
                  {isNone ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  ) : src ? (
                    <img src={src} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                  ) : null}
                </div>
              );
            })}
          </div>"""
NEW3 = """          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Avatar</div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:8, marginBottom:14 }}>
            {[null, ...CHAR_AVATARS].map((av, i) => {
              const isNone = av === null;
              const sel = isNone ? !avatarId : avatarId === av.id;
              return (
                <div key={i} onClick={() => setAvatarId(isNone ? null : av.id)} style={{ width:'100%', aspectRatio:'1', borderRadius:'50%', overflow:'hidden', cursor:'pointer', outline: sel ? `2.5px solid ${isNone ? T.sub : (av.color || T.mint)}` : '2.5px solid transparent', outlineOffset:2, background: isNone ? T.border : 'transparent', display:'grid', placeItems:'center', boxSizing:'border-box', transition:'outline-color .15s' }}>
                  {isNone ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  ) : (
                    <img src={av.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
                  )}
                </div>
              );
            })}
          </div>"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

content = re.sub(r'v9\.721', 'v9.722', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.722")
