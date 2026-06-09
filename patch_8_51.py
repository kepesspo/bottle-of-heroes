#!/usr/bin/env python3
"""v8.51: Profil picker a PlayerEditSheet-ben + badge a PlayerCard-on"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Eltávolítjuk a Névjegyek toggle + profile grid blokkot ─────────────────
OLD_TOGGLE_BLOCK = """      {/* Névjegyek toggle */}
      <div style={{ padding:'8px 16px 0' }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow }}>
          <div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Névjegyek</div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft }}>Rögzített profilokból választás</div>
          </div>
          <div onClick={() => setProfileMode(m => !m)}
            style={{ width:48, height:28, borderRadius:14, background:profileMode?T.mint:T.surfaceMuted, cursor:'pointer', position:'relative', transition:'background .2s', flexShrink:0 }}>
            <div style={{ position:'absolute', top:3, left:profileMode?22:3, width:22, height:22, borderRadius:'50%', background:'#fff', boxShadow:'0 1px 4px rgba(0,0,0,0.2)', transition:'left .2s' }} />
          </div>
        </div>
      </div>

      <div style={{ flex:1, overflowY:'auto', minHeight:0, WebkitOverflowScrolling:'touch' }}>
        <div className="screen-wide screen-pad" style={{ paddingTop:20, paddingBottom:20 }}>

        {/* Profile mode: show profile cards */}
        {profileMode && (
          <div style={{ marginBottom:16 }}>
            {loadingProfiles && <div style={{ textAlign:'center', padding:20, fontFamily:T.font, color:T.inkSoft }}>Betöltés…</div>}
            {!loadingProfiles && (
              <div className="grid-players">
                {profileList.map(prof => {
                  const alreadyIn = players.some(p => p.profileId === prof.id);
                  return (
                    <div key={prof.id} onClick={() => {
                      if (alreadyIn) { setPlayers(players.filter(p => p.profileId !== prof.id)); return; }
                      const np = { id:'p'+Date.now(), name:prof.name, color:prof.color, drinks:0, points:0, profileId:prof.id };
                      setPlayers([...players, np]);
                    }} style={{
                      position:'relative', background: alreadyIn ? T.mintSoft : T.surface,
                      borderRadius:18, padding:'10px 8px 10px',
                      boxShadow: alreadyIn ? `0 4px 16px ${T.mint}33` : T.shadow,
                      border: alreadyIn ? `2px solid ${T.mint}` : '2px solid transparent',
                      cursor:'pointer', display:'flex', flexDirection:'column', alignItems:'center', gap:6,
                      transition:'all .15s', aspectRatio:'1/1.18', minHeight:120,
                    }}>
                      <div style={{ width:56, height:56, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:24, color:'#fff' }}>{prof.name.charAt(0).toUpperCase()}</div>
                      <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color: alreadyIn ? T.mintDeep : T.ink, textAlign:'center', width:'100%', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', padding:'0 4px' }}>{prof.name}</div>
                      {alreadyIn && <div style={{ position:'absolute', top:6, right:6, width:20, height:20, borderRadius:'50%', background:T.mint, display:'grid', placeItems:'center' }}><svg width="11" height="11" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg></div>}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        )}

        {/* Normal mode: current players + add button */}
        <div className="grid-players">
          {players.map(p =>
            <PlayerCard key={p.id} p={p} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} />
          )}
          <button onClick={addPlayer} style={{"""

NEW_TOGGLE_BLOCK = """      <div style={{ flex:1, overflowY:'auto', minHeight:0, WebkitOverflowScrolling:'touch' }}>
        <div className="screen-wide screen-pad" style={{ paddingTop:20, paddingBottom:20 }}>
        <div className="grid-players">
          {players.map(p =>
            <PlayerCard key={p.id} p={p} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} />
          )}
          <button onClick={addPlayer} style={{"""

assert OLD_TOGGLE_BLOCK in content, "toggle block not found"
content = content.replace(OLD_TOGGLE_BLOCK, NEW_TOGGLE_BLOCK, 1)
print("✓ Névjegyek toggle eltávolítva")

# ── 2. profileMode/profileList state + useEffect eltávolítása ─────────────────
OLD_PROFILE_STATE = """  const [profileMode, setProfileMode] = React.useState(false);
  const [profileList, setProfileList] = React.useState([]);
  const [loadingProfiles, setLoadingProfiles] = React.useState(false);"""
assert OLD_PROFILE_STATE in content, "profile state not found"
content = content.replace(OLD_PROFILE_STATE, '', 1)
print("✓ profileMode state eltávolítva")

OLD_PROFILE_EFFECT = """  React.useEffect(() => {
    if (!profileMode) return;
    setLoadingProfiles(true);
    if (typeof window.getProfiles === 'function') {
      window.getProfiles().then(profs => { setProfileList(profs); setLoadingProfiles(false); });
    } else { setLoadingProfiles(false); }
  }, [profileMode]);"""
assert OLD_PROFILE_EFFECT in content, "profile effect not found"
content = content.replace(OLD_PROFILE_EFFECT, '', 1)
print("✓ profileMode useEffect eltávolítva")

# ── 3. PlayerCard: badge ha profileId van ────────────────────────────────────
OLD_PLAYER_CARD = """function PlayerCard({ p, onEdit, onRemove }) {
  return (
    <div onClick={onEdit} style={{
      position:'relative', background:T.surface, borderRadius:18,
      padding:'10px 8px 10px', boxShadow:T.shadow,
      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6,
      cursor:'pointer', aspectRatio:'1/1.18', minHeight:120,
    }}>
      <button onClick={e => { e.stopPropagation(); onRemove(); }} style={{
        position:'absolute', top:-6, right:-6, width:24, height:24,
        borderRadius:'50%', background:T.surface, color:T.inkSoft,
        border:'1.5px solid rgba(20,30,50,0.12)',
        boxShadow:'0 1px 3px rgba(0,0,0,0.1)',
        cursor:'pointer', display:'grid', placeItems:'center', padding:0,
      }}>{Icon.close(T.inkSoft)}</button>
      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center' }}>{Icon.user('#fff')}</div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, textAlign:'center', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'100%' }}>{p.name || 'Új játékos'}</div>
      <div style={{ width:22, height:2, background:p.color, borderRadius:1, opacity:0.5 }} />
    </div>
  );
}"""

NEW_PLAYER_CARD = """function PlayerCard({ p, onEdit, onRemove }) {
  return (
    <div onClick={onEdit} style={{
      position:'relative', background:T.surface, borderRadius:18,
      padding:'10px 8px 10px', boxShadow:T.shadow,
      display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:6,
      cursor:'pointer', aspectRatio:'1/1.18', minHeight:120,
    }}>
      <button onClick={e => { e.stopPropagation(); onRemove(); }} style={{
        position:'absolute', top:-6, right:-6, width:24, height:24,
        borderRadius:'50%', background:T.surface, color:T.inkSoft,
        border:'1.5px solid rgba(20,30,50,0.12)',
        boxShadow:'0 1px 3px rgba(0,0,0,0.1)',
        cursor:'pointer', display:'grid', placeItems:'center', padding:0,
      }}>{Icon.close(T.inkSoft)}</button>
      {/* Profile badge */}
      {p.profileId && (
        <div style={{ position:'absolute', top:6, left:6, width:18, height:18, borderRadius:'50%', background:T.mint, display:'grid', placeItems:'center', boxShadow:'0 1px 4px rgba(0,0,0,0.15)' }}>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
        </div>
      )}
      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center' }}>{Icon.user('#fff')}</div>
      <div style={{ fontFamily:T.font, fontWeight:T.weightTitle, fontSize:14, color:T.ink, textAlign:'center', whiteSpace:'nowrap', overflow:'hidden', textOverflow:'ellipsis', maxWidth:'100%' }}>{p.name || 'Új játékos'}</div>
      <div style={{ width:22, height:2, background:p.color, borderRadius:1, opacity:0.5 }} />
    </div>
  );
}"""

assert OLD_PLAYER_CARD in content, "PlayerCard not found"
content = content.replace(OLD_PLAYER_CARD, NEW_PLAYER_CARD, 1)
print("✓ PlayerCard: profil badge hozzáadva")

# ── 4. PlayerEditSheet: profil picker dropdown ────────────────────────────────
OLD_EDIT_SHEET = """function PlayerEditSheet({ player, onClose, onChange, usedColors }) {
  const [kbH, setKbH] = useState(0);
  useEffect(() => {
    const vv = window.visualViewport;
    if (!vv) return;
    const upd = () => setKbH(Math.max(0, window.innerHeight - vv.height));
    vv.addEventListener('resize', upd);
    vv.addEventListener('scroll', upd);
    upd();
    return () => { vv.removeEventListener('resize', upd); vv.removeEventListener('scroll', upd); };
  }, []);
  return (
    <div onClick={onClose} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.45)', zIndex:40, animation:'fadeIn .2s', display:'flex', alignItems:'flex-end', justifyContent:'center', paddingLeft:20, paddingRight:20, paddingBottom: kbH > 0 ? kbH + 20 : '32vh', transition:'padding-bottom .2s ease-out' }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:'100%', maxWidth:340,
        background:T.surface, borderRadius:24,
        boxShadow:'0 12px 48px rgba(0,0,0,0.22)', animation:'popIn .25s cubic-bezier(.2,.9,.3,1.4)',
        padding:'24px 22px 22px',
      }}>
        <div style={{ display:'flex', flexDirection:'column', gap:16 }}>
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center' }}>
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <input autoFocus value={player.name} onChange={e => onChange({ name:e.target.value.slice(0,14) })}
              placeholder="Játékos neve…"
              onFocus={e => { setTimeout(() => e.target.scrollIntoView({ behavior:'smooth', block:'center' }), 300); }}
              style={{
                flex:1, boxSizing:'border-box',
                background:T.bgSoft, border:'none', borderRadius:14,
                padding:'12px 14px', fontFamily:T.font, fontWeight:T.weightTitle,
                fontSize:17, color:T.ink, outline:'none',
              }} />
          </div>
          <div style={{ display:'grid', gridTemplateColumns:'repeat(8, 1fr)', gap:10 }}>
            {PLAYER_COLORS.map(c => {
              const used = usedColors.has(c) && c !== player.color;
              const active = c === player.color;
              return (
                <button key={c} disabled={used} onClick={() => onChange({ color:c })} style={{
                  aspectRatio:'1/1', borderRadius:'50%', background:c, padding:0,
                  border: active ? `3px solid ${T.ink}` : '2px solid transparent',
                  cursor: used ? 'default' : 'pointer',
                  opacity: used ? 0.25 : 1,
                  transform: active ? 'scale(1.15)' : 'scale(1)',
                  transition:'transform .15s',
                }} />
              );
            })}
          </div>
          <PrimaryButton onClick={onClose} disabled={!player.name.trim()}>Mehet</PrimaryButton>
        </div>
      </div>
    </div>
  );"""

NEW_EDIT_SHEET = """function PlayerEditSheet({ player, onClose, onChange, usedColors }) {
  const [kbH, setKbH] = useState(0);
  const [profiles, setProfiles] = React.useState([]);
  const [showDropdown, setShowDropdown] = React.useState(false);

  useEffect(() => {
    const vv = window.visualViewport;
    if (!vv) return;
    const upd = () => setKbH(Math.max(0, window.innerHeight - vv.height));
    vv.addEventListener('resize', upd);
    vv.addEventListener('scroll', upd);
    upd();
    return () => { vv.removeEventListener('resize', upd); vv.removeEventListener('scroll', upd); };
  }, []);

  useEffect(() => {
    if (typeof window.getProfiles === 'function') {
      window.getProfiles().then(profs => setProfiles(profs));
    }
  }, []);

  const selectProfile = (prof) => {
    onChange({ name: prof.name, color: prof.color, profileId: prof.id });
    setShowDropdown(false);
  };
  const clearProfile = () => {
    onChange({ profileId: null });
  };

  return (
    <div onClick={onClose} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.45)', zIndex:40, animation:'fadeIn .2s', display:'flex', alignItems:'flex-end', justifyContent:'center', paddingLeft:20, paddingRight:20, paddingBottom: kbH > 0 ? kbH + 20 : '32vh', transition:'padding-bottom .2s ease-out' }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:'100%', maxWidth:340,
        background:T.surface, borderRadius:24,
        boxShadow:'0 12px 48px rgba(0,0,0,0.22)', animation:'popIn .25s cubic-bezier(.2,.9,.3,1.4)',
        padding:'24px 22px 22px',
      }}>
        <div style={{ display:'flex', flexDirection:'column', gap:14 }}>

          {/* Profil választó dropdown */}
          <div style={{ position:'relative' }}>
            <div onClick={() => setShowDropdown(d => !d)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', background:T.bgSoft, borderRadius:14, cursor:'pointer', border: player.profileId ? `1.5px solid ${T.mint}` : '1.5px solid transparent' }}>
              {player.profileId ? (
                <>
                  <div style={{ width:32, height:32, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.mintDeep, flex:1 }}>{player.name}</span>
                  <button onClick={e => { e.stopPropagation(); clearProfile(); }} style={{ background:'none', border:'none', cursor:'pointer', color:T.inkMute, fontSize:16, padding:0, lineHeight:1 }}>✕</button>
                </>
              ) : (
                <>
                  <div style={{ width:32, height:32, borderRadius:'50%', background:T.surfaceMuted, display:'grid', placeItems:'center', flexShrink:0 }}>
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" stroke={T.inkMute} strokeWidth="2"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke={T.inkMute} strokeWidth="2" strokeLinecap="round"/></svg>
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.inkSoft, flex:1 }}>Válassz névjegyet…</span>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" style={{ flexShrink:0 }}><path d="M6 9l6 6 6-6" stroke={T.inkMute} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
                </>
              )}
            </div>
            {showDropdown && profiles.length > 0 && (
              <div style={{ position:'absolute', top:'calc(100% + 6px)', left:0, right:0, background:T.surface, borderRadius:14, boxShadow:'0 8px 32px rgba(0,0,0,0.18)', zIndex:10, overflow:'hidden', maxHeight:220, overflowY:'auto' }}>
                {profiles.map(prof => (
                  <div key={prof.id} onClick={() => selectProfile(prof)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 14px', cursor:'pointer', borderBottom:`1px solid ${T.surfaceMuted}`, background: player.profileId===prof.id ? T.mintSoft : 'transparent' }}>
                    <div style={{ width:30, height:30, borderRadius:'50%', background:prof.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
                    </div>
                    <span style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color: player.profileId===prof.id ? T.mintDeep : T.ink }}>{prof.name}</span>
                    {player.profileId===prof.id && <svg style={{ marginLeft:'auto' }} width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M5 13l4 4L19 7" stroke={T.mint} strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/></svg>}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Név input */}
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>
            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center' }}>
              <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
              </svg>
            </div>
            <input autoFocus value={player.name} onChange={e => onChange({ name:e.target.value.slice(0,14) })}
              placeholder="Játékos neve…"
              onFocus={e => { setTimeout(() => e.target.scrollIntoView({ behavior:'smooth', block:'center' }), 300); }}
              style={{
                flex:1, boxSizing:'border-box',
                background:T.bgSoft, border:'none', borderRadius:14,
                padding:'12px 14px', fontFamily:T.font, fontWeight:T.weightTitle,
                fontSize:17, color:T.ink, outline:'none',
              }} />
          </div>

          {/* Szín választó */}
          <div style={{ display:'grid', gridTemplateColumns:'repeat(8, 1fr)', gap:10 }}>
            {PLAYER_COLORS.map(c => {
              const used = usedColors.has(c) && c !== player.color;
              const active = c === player.color;
              return (
                <button key={c} disabled={used} onClick={() => onChange({ color:c })} style={{
                  aspectRatio:'1/1', borderRadius:'50%', background:c, padding:0,
                  border: active ? `3px solid ${T.ink}` : '2px solid transparent',
                  cursor: used ? 'default' : 'pointer',
                  opacity: used ? 0.25 : 1,
                  transform: active ? 'scale(1.15)' : 'scale(1)',
                  transition:'transform .15s',
                }} />
              );
            })}
          </div>
          <PrimaryButton onClick={onClose} disabled={!player.name.trim()}>Mehet</PrimaryButton>
        </div>
      </div>
    </div>
  );"""

assert OLD_EDIT_SHEET in content, "PlayerEditSheet not found"
content = content.replace(OLD_EDIT_SHEET, NEW_EDIT_SHEET, 1)
print("✓ PlayerEditSheet: profil picker dropdown hozzáadva")

# ── 5. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.50';"
NEW_VER = "const APP_VERSION = 'v8.51';"
assert OLD_VER in content, "version not found"
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.51 saved")
