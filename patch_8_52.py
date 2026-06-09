#!/usr/bin/env python3
"""v8.52: Teljes nevek + becenevek a profilokban"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. saveProfile: nickname mező támogatás ───────────────────────────────────
OLD_SAVE_PROFILE = """  window.saveProfile = function(profile) {
    var ref = profile.id ? db.collection('profiles').doc(profile.id) : db.collection('profiles').doc();
    var data = { name: profile.name, color: profile.color };
    return ref.set(data, { merge: true }).then(function() { return ref.id; });
  };"""

NEW_SAVE_PROFILE = """  window.saveProfile = function(profile) {
    var ref = profile.id ? db.collection('profiles').doc(profile.id) : db.collection('profiles').doc();
    var data = { name: profile.name, color: profile.color };
    if (profile.nickname) data.nickname = profile.nickname;
    return ref.set(data, { merge: true }).then(function() { return ref.id; });
  };"""

assert OLD_SAVE_PROFILE in content, "saveProfile not found"
content = content.replace(OLD_SAVE_PROFILE, NEW_SAVE_PROFILE, 1)
print("✓ saveProfile: nickname mező")

# ── 2. PRESET_PLAYERS: teljes nevek + becenevek ───────────────────────────────
OLD_PRESET = """  const PRESET_PLAYERS = [
    { name:'Sere' }, { name:'Kecsi' }, { name:'Luca' }, { name:'Tóth' },
    { name:'Márk' }, { name:'Dani' }, { name:'KKK' }, { name:'Vivi' }, { name:'Balázs' }
  ];"""

NEW_PRESET = """  const PRESET_PLAYERS = [
    { id:'preset_sere',   name:'Sere Bence',       nickname:'Sere',   color:'#4FC3A1' },
    { id:'preset_kecsi',  name:'Kecskés Dániel',   nickname:'Kecsi',  color:'#F87171' },
    { id:'preset_luca',   name:'Monoki Luca',       nickname:'Luca',   color:'#F472B6' },
    { id:'preset_toth',   name:'Tóth Bence',        nickname:'Tóth',   color:'#60A5FA' },
    { id:'preset_mark',   name:'Szécsi Márk',       nickname:'Márk',   color:'#FBBF24' },
    { id:'preset_dani',   name:'Szentpáli Dániel',  nickname:'Dani',   color:'#A78BFA' },
    { id:'preset_kkk',    name:'Tóth Gergő',        nickname:'KKK',    color:'#34D399' },
    { id:'preset_vivi',   name:'Kiss Vivien',        nickname:'Vivi',   color:'#FB923C' },
    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8' },
  ];"""

assert OLD_PRESET in content, "PRESET_PLAYERS not found"
content = content.replace(OLD_PRESET, NEW_PRESET, 1)
print("✓ PRESET_PLAYERS: teljes nevek + becenevek")

# ── 3. Seed logic: fix ID-vel, mindig frissít ─────────────────────────────────
OLD_SEED = """  // Seed Firestore profiles from PRESET_PLAYERS if empty
  React.useEffect(() => {
    if (typeof window.getProfiles !== 'function' || typeof window.saveProfile !== 'function') return;
    window.getProfiles().then(existing => {
      if (existing.length > 0) return; // already seeded
      const PRESET_COLORS = ['#4FC3A1','#F87171','#60A5FA','#FBBF24','#A78BFA','#34D399','#F472B6','#FB923C','#818CF8'];
      PRESET_PLAYERS.forEach((p, i) => {
        window.saveProfile({ name: p.name, color: PRESET_COLORS[i % PRESET_COLORS.length] });
      });
    });
  }, []);"""

NEW_SEED = """  // Seed/sync Firestore profiles from PRESET_PLAYERS (fix ID-vel, mindig frissít)
  React.useEffect(() => {
    if (typeof window.saveProfile !== 'function') return;
    PRESET_PLAYERS.forEach(p => {
      window.saveProfile({ id: p.id, name: p.name, nickname: p.nickname, color: p.color });
    });
  }, []);"""

assert OLD_SEED in content, "seed logic not found"
content = content.replace(OLD_SEED, NEW_SEED, 1)
print("✓ Seed: fix ID, mindig frissít")

# ── 4. Secret tap: becenév a játékban ────────────────────────────────────────
OLD_SECRET = """        return { id:'p'+Date.now()+i, name:p.name, color, drinks:0, points:0 };"""
NEW_SECRET = """        return { id:'p'+Date.now()+i, name:p.nickname||p.name, color, drinks:0, points:0, profileId:p.id };"""

assert OLD_SECRET in content, "secret tap not found"
content = content.replace(OLD_SECRET, NEW_SECRET, 1)
print("✓ Secret tap: becenév + profileId")

# ── 5. Dropdown: teljes név + becenév megjelenítés ────────────────────────────
OLD_DROPDOWN_ITEM = """                {profiles.map(prof => (
                  <div key={prof.id} onClick={() => selectProfile(prof)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', cursor:'pointer', borderBottom:`1px solid ${T.surfaceMuted}`, background: player.profileId===prof.id ? T.mintSoft : 'transparent' }}>
                    <div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
                    </div>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color: player.profileId===prof.id ? T.mintDeep : T.ink }}>{prof.name}</span>
                    {player.profileId===prof.id && <svg style={{ marginLeft:'auto' }} width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  </div>
                ))}"""

NEW_DROPDOWN_ITEM = """                {profiles.map(prof => (
                  <div key={prof.id} onClick={() => selectProfile(prof)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', cursor:'pointer', borderBottom:`1px solid ${T.surfaceMuted}`, background: player.profileId===prof.id ? T.mintSoft : 'transparent' }}>
                    <div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
                    </div>
                    <div style={{ flex:1, minWidth:0 }}>
                      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color: player.profileId===prof.id ? T.mintDeep : T.ink }}>{prof.name}</div>
                      {prof.nickname && <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>{prof.nickname}</div>}
                    </div>
                    {player.profileId===prof.id && <svg style={{ flexShrink:0 }} width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  </div>
                ))}"""

assert OLD_DROPDOWN_ITEM in content, "dropdown item not found"
content = content.replace(OLD_DROPDOWN_ITEM, NEW_DROPDOWN_ITEM, 1)
print("✓ Dropdown: teljes név + becenév")

# ── 6. selectProfile: becenevet tölti be játékosnévnek ───────────────────────
OLD_SELECT = """  const selectProfile = (prof) => {
    onChange({ name: prof.name, color: prof.color, profileId: prof.id });
    setShowDropdown(false);
  };"""

NEW_SELECT = """  const selectProfile = (prof) => {
    onChange({ name: prof.nickname || prof.name, color: prof.color, profileId: prof.id });
    setShowDropdown(false);
  };"""

assert OLD_SELECT in content, "selectProfile not found"
content = content.replace(OLD_SELECT, NEW_SELECT, 1)
print("✓ selectProfile: becenév a játékban")

# ── 7. Kiválasztott profil fejléc: becenév mutatása ──────────────────────────
OLD_SELECTED_HEADER = """                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.mintDeep, flex:1 }}>{player.name}</span>"""
NEW_SELECTED_HEADER = """                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color:T.mintDeep }}>{player.name}</div>
                  </div>"""

assert OLD_SELECTED_HEADER in content, "selected header not found"
content = content.replace(OLD_SELECTED_HEADER, NEW_SELECTED_HEADER, 1)
print("✓ Kiválasztott fejléc frissítve")

# ── 8. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.51';"
NEW_VER = "const APP_VERSION = 'v8.52';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.52 saved")
