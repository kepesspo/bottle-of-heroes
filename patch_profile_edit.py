with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add editingProfile + profile edit field states after savedStats state
OLD1 = """  const [savingStats, setSavingStats] = React.useState(false);
  const [savedStats, setSavedStats] = React.useState(null);

  const STAT_FIELDS = ["""
NEW1 = """  const [savingStats, setSavingStats] = React.useState(false);
  const [savedStats, setSavedStats] = React.useState(null);
  const [editingProfile, setEditingProfile] = React.useState(null);
  const [epName, setEpName] = React.useState('');
  const [epNickname, setEpNickname] = React.useState('');
  const [epPhone, setEpPhone] = React.useState('');
  const [epBirthday, setEpBirthday] = React.useState('');
  const [epColor, setEpColor] = React.useState('#E8631A');
  const [epAvatarId, setEpAvatarId] = React.useState(null);
  const [savingProfile, setSavingProfile] = React.useState(false);

  const STAT_FIELDS = ["""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Add startEditProfile + saveProfileEdit functions after deleteProfile
OLD2 = """  function deleteProfile(id) {
    if (typeof firebase === 'undefined') return;
    setDeleting(id);
    firebase.firestore().collection('profiles').doc(id).delete().then(() => { setDeleting(null); load(); }).catch(() => setDeleting(null));
  }"""
NEW2 = """  function deleteProfile(id) {
    if (typeof firebase === 'undefined') return;
    setDeleting(id);
    firebase.firestore().collection('profiles').doc(id).delete().then(() => { setDeleting(null); load(); }).catch(() => setDeleting(null));
  }

  function openEditProfile(p) {
    if (editingProfile === p.id) { setEditingProfile(null); return; }
    setEpName(p.name || '');
    setEpNickname(p.nickname || '');
    setEpPhone(p.phone || '');
    setEpBirthday(p.birthday || '');
    setEpColor(p.color || '#E8631A');
    setEpAvatarId(p.avatarId || null);
    // also prep stats
    const st = allStats[p.id] || {};
    const vals = {};
    STAT_FIELDS.forEach(f => { vals[f.key] = st[f.key] !== undefined ? String(st[f.key]) : '0'; });
    setEditVals(vals);
    setEditingProfile(p.id);
    setEditingStats(null);
  }

  function saveProfileEdit(p) {
    if (!epName.trim() || savingProfile) return;
    setSavingProfile(true);
    const prof = { id: p.id, name: epName.trim(), color: epColor };
    if (epNickname.trim()) prof.nickname = epNickname.trim();
    if (epPhone.trim()) prof.phone = epPhone.trim();
    if (epBirthday) prof.birthday = epBirthday;
    if (epAvatarId) {
      const av = CHAR_AVATARS.find(a => a.id === epAvatarId);
      if (av) { prof.img = av.img; prof.avatarId = av.id; }
    } else {
      prof.img = null; prof.avatarId = null;
    }
    window.saveProfile(prof).then(() => {
      setSavingProfile(false); setEditingProfile(null); load();
    }).catch(() => setSavingProfile(false));
  }

  function saveStatsInline() {
    if (savingStats || !editingProfile) return;
    setSavingStats(true);
    const updates = {};
    STAT_FIELDS.forEach(f => { updates[f.key] = Number(editVals[f.key]) || 0; });
    window.updateStats(editingProfile, updates).then(() => {
      setAllStats(prev => ({ ...prev, [editingProfile]: { ...(prev[editingProfile]||{}), ...updates } }));
      setSavingStats(false); setSavedStats(editingProfile);
      setTimeout(() => setSavedStats(null), 2000);
    }).catch(() => setSavingStats(false));
  }"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Change row click and isEd to use editingProfile
OLD3 = """        const st = allStats[p.id] || {};
        const isEd = editingStats === p.id;
        const rsvpCnt = eventsRsvp.filter(e=>(e.rsvp||{})[p.name]==='yes').length;
        return (
          <div key={p.id} style={{ background:T.surface, borderRadius:14, marginBottom:8, boxShadow:T.shadow, overflow:'hidden' }}>
            {/* Main row — clicking opens stats */}
            <div onClick={() => startEditStats(p)} style={{ display:'flex', alignItems:'center', gap:10, padding:'12px 14px', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>"""
NEW3 = """        const st = allStats[p.id] || {};
        const isEd = editingProfile === p.id;
        const rsvpCnt = eventsRsvp.filter(e=>(e.rsvp||{})[p.name]==='yes').length;
        return (
          <div key={p.id} style={{ background:T.surface, borderRadius:14, marginBottom:8, boxShadow:T.shadow, overflow:'hidden' }}>
            {/* Main row — clicking opens profile edit */}
            <div onClick={() => openEditProfile(p)} style={{ display:'flex', alignItems:'center', gap:10, padding:'12px 14px', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Replace the entire inline stats editor with the combined profile+stats editor
OLD4 = """            {/* Inline stats editor */}
            {isEd && (
              <div style={{ padding:'0 14px 14px', borderTop:`1px solid ${T.border}` }}>
                <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', margin:'10px 0 8px' }}>Statisztika szerkesztése</div>
                <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:10 }}>
                  {STAT_FIELDS.map(f => (
                    <div key={f.key}>
                      <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:4 }}>{f.label}</div>
                      <input type="number" value={editVals[f.key]||'0'} onChange={e => setEditVals(prev => ({...prev,[f.key]:e.target.value}))}
                        style={{ width:'100%', boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
                    </div>
                  ))}
                </div>
                <div style={{ display:'flex', gap:8 }}>
                  <button onClick={() => setEditingStats(null)} style={{ flex:1, padding:'10px', borderRadius:11, border:`1.5px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer' }}>Mégsem</button>
                  <button onClick={saveStats} disabled={savingStats} style={{ flex:2, padding:'10px', borderRadius:11, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer', opacity:savingStats?0.6:1 }}>{savingStats?'Mentés…':'Mentés'}</button>
                </div>
              </div>
            )}"""
NEW4 = """            {/* Inline combined editor: profile + stats */}
            {isEd && (
              <div style={{ borderTop:`1px solid ${T.border}` }}>
                {/* ── Profil adatok ── */}
                <div style={{ padding:'14px 14px 0' }}>
                  <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:10 }}>✏️ Profil szerkesztése</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:4 }}>Név</div>
                  <input value={epName} onChange={e => setEpName(e.target.value)} style={{ width:'100%', boxSizing:'border-box', padding:'10px 12px', borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none', marginBottom:10 }} />
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:4 }}>Becenév</div>
                  <input value={epNickname} onChange={e => setEpNickname(e.target.value)} style={{ width:'100%', boxSizing:'border-box', padding:'10px 12px', borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none', marginBottom:10 }} />
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:4 }}>Telefonszám</div>
                  <input value={epPhone} onChange={e => setEpPhone(e.target.value)} type="tel" style={{ width:'100%', boxSizing:'border-box', padding:'10px 12px', borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none', marginBottom:10 }} />
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:4 }}>Születésnap</div>
                  <input value={epBirthday} onChange={e => setEpBirthday(e.target.value)} type="date" style={{ width:'100%', boxSizing:'border-box', padding:'10px 12px', height:44, borderRadius:11, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none', marginBottom:10, WebkitAppearance:'none', appearance:'none', lineHeight:'normal' }} />
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:6 }}>Szín</div>
                  <div style={{ display:'flex', gap:8, flexWrap:'wrap', marginBottom:12 }}>
                    {AVATAR_COLORS.map(c => (
                      <div key={c} onClick={() => setEpColor(c)} style={{ width:28, height:28, borderRadius:'50%', background:c, cursor:'pointer', boxShadow: epColor===c ? `0 0 0 3px ${T.bg}, 0 0 0 5px ${c}` : 'none', transition:'box-shadow .15s' }} />
                    ))}
                  </div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, fontWeight:700, marginBottom:6 }}>Avatar</div>
                  <div style={{ display:'grid', gridTemplateColumns:'repeat(5,1fr)', gap:6, marginBottom:12 }}>
                    {[null, ...CHAR_AVATARS].map((av, i) => {
                      const isNone = av === null;
                      const sel = isNone ? !epAvatarId : epAvatarId === av.id;
                      return (
                        <div key={i} onClick={() => setEpAvatarId(isNone ? null : av.id)} style={{ width:'100%', aspectRatio:'1', borderRadius:'50%', overflow:'hidden', cursor:'pointer', outline: sel ? `2.5px solid ${isNone ? T.sub : (av?.color || T.mint)}` : '2.5px solid transparent', outlineOffset:2, background: isNone ? T.border : 'transparent', display:'grid', placeItems:'center', boxSizing:'border-box' }}>
                          {isNone ? <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                            : <img src={av.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} />}
                        </div>
                      );
                    })}
                  </div>
                  <div style={{ display:'flex', gap:8, marginBottom:14 }}>
                    <button onClick={() => setEditingProfile(null)} style={{ flex:1, padding:'10px', borderRadius:11, border:`1.5px solid ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:700, fontSize:13, color:T.sub, cursor:'pointer' }}>Mégsem</button>
                    <button onClick={() => saveProfileEdit(p)} disabled={savingProfile||!epName.trim()} style={{ flex:2, padding:'10px', borderRadius:11, border:'none', background:T.mint, fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', cursor:'pointer', opacity:savingProfile||!epName.trim()?0.6:1 }}>{savingProfile?'Mentés…':'Profil mentése'}</button>
                  </div>
                </div>
                {/* ── Statisztika ── */}
                <div style={{ padding:'0 14px 14px', borderTop:`1px solid ${T.border}` }}>
                  <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.07em', margin:'10px 0 8px' }}>📊 Statisztika</div>
                  <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8, marginBottom:10 }}>
                    {STAT_FIELDS.map(f => (
                      <div key={f.key}>
                        <div style={{ fontFamily:T.font, fontSize:10, color:T.sub, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:4 }}>{f.label}</div>
                        <input type="number" value={editVals[f.key]||'0'} onChange={e => setEditVals(prev => ({...prev,[f.key]:e.target.value}))}
                          style={{ width:'100%', boxSizing:'border-box', padding:'9px 10px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' }} />
                      </div>
                    ))}
                  </div>
                  <button onClick={saveStatsInline} disabled={savingStats} style={{ width:'100%', padding:'10px', borderRadius:11, border:'none', background:T.surface, fontFamily:T.font, fontWeight:900, fontSize:13, color:T.mint, cursor:'pointer', opacity:savingStats?0.6:1, border:`1.5px solid ${T.mint}` }}>{savingStats?'Mentés…':savedStats===p.id?'✅ Elmentve':'Statisztika mentése'}</button>
                </div>
              </div>
            )}"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

import re
content = re.sub(r'v9\.765', 'v9.766', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.766")
