import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add avatar state to AdminProfiles
OLD1 = "  const [saving, setSaving] = React.useState(false);\n  const [deleting, setDeleting] = React.useState(null);\n  const [hiddenProfs, setHiddenProfs] = React.useState([]);"
NEW1 = "  const [saving, setSaving] = React.useState(false);\n  const [deleting, setDeleting] = React.useState(null);\n  const [hiddenProfs, setHiddenProfs] = React.useState([]);\n  const [avatarImg, setAvatarImg] = React.useState(null);"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Pass avatarImg to saveProfile and reset on close
OLD2 = "  function save() {\n    if (!name.trim() || saving) return;\n    setSaving(true);\n    window.saveProfile({ name: name.trim(), color }).then(() => {\n      setSaving(false); setShowForm(false); setName(''); setColor('#E8631A'); load();\n    }).catch(() => setSaving(false));\n  }"
NEW2 = """  function save() {
    if (!name.trim() || saving) return;
    setSaving(true);
    const prof = { name: name.trim(), color };
    if (avatarImg) prof.img = avatarImg;
    window.saveProfile(prof).then(() => {
      setSaving(false); setShowForm(false); setName(''); setColor('#E8631A'); setAvatarImg(null); load();
    }).catch(() => setSaving(false));
  }

  function pickAvatar(e) {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = ev => setAvatarImg(ev.target.result);
    reader.readAsDataURL(file);
  }"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Add avatar picker UI in the form (between color picker and save buttons)
OLD3 = """          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Szín</div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:14 }}>
            {AVATAR_COLORS.map(c => (
              <div key={c} onClick={() => setColor(c)} style={{ width:32, height:32, borderRadius:'50%', background:c, cursor:'pointer', boxShadow: color===c ? `0 0 0 3px ${T.bg}, 0 0 0 5px ${c}` : 'none', transition:'box-shadow .15s' }} />
            ))}
          </div>
          <div style={{ display:'flex', gap:8 }}>"""
NEW3 = """          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Szín</div>
          <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:14 }}>
            {AVATAR_COLORS.map(c => (
              <div key={c} onClick={() => setColor(c)} style={{ width:32, height:32, borderRadius:'50%', background:c, cursor:'pointer', boxShadow: color===c ? `0 0 0 3px ${T.bg}, 0 0 0 5px ${c}` : 'none', transition:'box-shadow .15s' }} />
            ))}
          </div>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Avatar kép (opcionális)</div>
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
          </label>
          <div style={{ display:'flex', gap:8 }}>"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Show avatar in profile list card (replace small dot with avatar if exists)
OLD4 = """          <div style={{ width:12, height:12, borderRadius:'50%', background:p.color||'#888', flexShrink:0 }} />"""
NEW4 = """          {p.img ? (
            <div style={{ width:38, height:38, borderRadius:10, overflow:'hidden', flexShrink:0 }}>
              <img src={p.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />
            </div>
          ) : (
            <div style={{ width:12, height:12, borderRadius:'50%', background:p.color||'#888', flexShrink:0 }} />
          )}"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Version bump
content = re.sub(r'v9\.705', 'v9.706', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.706")
