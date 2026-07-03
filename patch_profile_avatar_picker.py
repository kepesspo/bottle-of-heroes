import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove the pickAvatar function and replace with nothing (avatarImg state stays)
OLD1 = """  function pickAvatar(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => setAvatarImg(ev.target.result);
    reader.readAsDataURL(file);
  }"""
NEW1 = ""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Replace the avatar picker UI with a grid of pre-loaded avatars
OLD2 = """          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Avatar kép (opcionális)</div>
          <label style={{ display:'flex', alignItems:'center', gap:12, marginBottom:14, cursor:'pointer' }}>
            <div style={{ width:56, height:56, borderRadius:14, background: avatarImg ? 'transparent' : T.border, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, border:`2px dashed ${avatarImg ? T.mint : T.border}` }}>
              {avatarImg ? <img src={avatarImg} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>}
            </div>
            <div style={{ flex:1 }}>
              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.mint }}>Kép kiválasztása</div>
              <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:2 }}>JPG, PNG — a készülékről</div>
            </div>
            {avatarImg && <button type="button" onClick={e => { e.preventDefault(); setAvatarImg(null); }} style={{ width:28, height:28, borderRadius:8, border:'none', background:'#fef2f2', display:'grid', placeItems:'center', cursor:'pointer' }}><svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg></button>}
            <input type="file" accept="image/*" onChange={pickAvatar} style={{ display:'none' }} />
          </label>"""
NEW2 = """          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Avatar</div>
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
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Version bump
content = re.sub(r'v9\.709', 'v9.710', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.710")
