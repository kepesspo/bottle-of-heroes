#!/usr/bin/env python3
"""
patch_8_50.py — v8.50: Profil rendszer + statisztikák (Beer Pong + Busz)
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ── 1. Firebase helper functions ──────────────────────────────────────────────
OLD1 = """  window.popPendingDrinks = function(code) {
    return db.collection('rooms').doc(code).collection('pendingDrinks').get().then(function(snap) {
      var items = [];
      snap.forEach(function(doc) { items.push(doc.data()); });
      if (items.length === 0) return [];
      var batch = db.batch();
      snap.forEach(function(doc) { batch.delete(doc.ref); });
      return batch.commit().then(function() { return items; });
    }).catch(function(e){ console.warn('popPendingDrinks', e); return []; });
  };
})();"""

NEW1 = """  window.popPendingDrinks = function(code) {
    return db.collection('rooms').doc(code).collection('pendingDrinks').get().then(function(snap) {
      var items = [];
      snap.forEach(function(doc) { items.push(doc.data()); });
      if (items.length === 0) return [];
      var batch = db.batch();
      snap.forEach(function(doc) { batch.delete(doc.ref); });
      return batch.commit().then(function() { return items; });
    }).catch(function(e){ console.warn('popPendingDrinks', e); return []; });
  };
  window.getProfiles = function() {
    return db.collection('profiles').orderBy('name').get().then(function(snap) {
      return snap.docs.map(function(d) { return Object.assign({ id: d.id }, d.data()); });
    }).catch(function() { return []; });
  };
  window.saveProfile = function(profile) {
    var ref = profile.id ? db.collection('profiles').doc(profile.id) : db.collection('profiles').doc();
    var data = { name: profile.name, color: profile.color };
    return ref.set(data, { merge: true }).then(function() { return ref.id; });
  };
  window.getStats = function(profileId) {
    return db.collection('stats').doc(profileId).get().then(function(d) {
      return d.exists ? d.data() : {};
    }).catch(function() { return {}; });
  };
  window.getAllStats = function() {
    return db.collection('stats').get().then(function(snap) {
      var result = {};
      snap.docs.forEach(function(d) { result[d.id] = d.data(); });
      return result;
    }).catch(function() { return {}; });
  };
  window.updateStats = function(profileId, updates) {
    return db.collection('stats').doc(profileId).set(updates, { merge: true }).catch(function(e) { console.warn('updateStats', e); });
  };
})();"""

assert OLD1 in html, "ASSERT FAILED: Firebase insertion point not found"
html = html.replace(OLD1, NEW1, 1)
print("✓ Step 1: Firebase helper functions added")

# ── 2. StatsScreen component ──────────────────────────────────────────────────
STATS_SCREEN = """function StatsScreen({ go }) {
  const [profiles, setProfiles] = React.useState([]);
  const [stats, setStats] = React.useState({});
  const [loading, setLoading] = React.useState(true);
  const [tab, setTab] = React.useState('bp'); // 'bp' | 'busz'

  React.useEffect(() => {
    Promise.all([
      typeof window.getProfiles === 'function' ? window.getProfiles() : Promise.resolve([]),
      typeof window.getAllStats === 'function' ? window.getAllStats() : Promise.resolve({}),
    ]).then(([profs, st]) => {
      setProfiles(profs);
      setStats(st);
      setLoading(false);
    });
  }, []);

  const bpRows = [...profiles].sort((a, b) => {
    const aw = stats[a.id]?.bp_wins || 0, bw = stats[b.id]?.bp_wins || 0;
    return bw - aw;
  });
  const buszRows = [...profiles].sort((a, b) => {
    const ap = stats[a.id]?.busz_played || 0, bp2 = stats[b.id]?.busz_played || 0;
    return bp2 - ap;
  });

  const winRate = (id) => {
    const s = stats[id] || {};
    const played = (s.bp_wins || 0) + (s.bp_losses || 0);
    return played > 0 ? Math.round((s.bp_wins || 0) / played * 100) : null;
  };

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Statisztika" onBack={() => go('home')} />
      {/* Tab bar */}
      <div style={{ padding:'8px 16px 0' }}>
        <div style={{ display:'flex', background:T.surfaceMuted, padding:4, borderRadius:14, gap:4 }}>
          {[{k:'bp',l:'🍺 Beer Pong'},{k:'busz',l:'🚌 Busz'}].map(t => (
            <button key={t.k} onClick={() => setTab(t.k)} style={{ flex:1, padding:'10px 6px', borderRadius:10, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:13, background: tab===t.k ? T.mint : 'transparent', color: tab===t.k ? '#fff' : T.inkSoft, transition:'all .15s' }}>{t.l}</button>
          ))}
        </div>
      </div>

      <div style={{ flex:1, overflowY:'auto', padding:'12px 16px 40px' }}>
        {loading && <div style={{ textAlign:'center', padding:40, fontFamily:T.font, color:T.inkSoft }}>Betöltés…</div>}

        {!loading && tab === 'bp' && (
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {bpRows.map((p, i) => {
              const s = stats[p.id] || {};
              const wr = winRate(p.id);
              const played = (s.bp_wins || 0) + (s.bp_losses || 0);
              return (
                <div key={p.id} style={{ background:T.surface, borderRadius:18, padding:'14px 16px', display:'flex', alignItems:'center', gap:12, boxShadow:T.shadow }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color: i===0?'#F59E0B':i===1?T.inkSoft:T.inkMute, minWidth:24, textAlign:'center' }}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':i+1}</div>
                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {played} meccs · {s.bp_wins||0} győzelem · {s.bp_losses||0} vereség
                    </div>
                  </div>
                  <div style={{ textAlign:'right', flexShrink:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color: wr>=50 ? T.mint : T.coral }}>{wr !== null ? wr+'%' : '–'}</div>
                    <div style={{ fontFamily:T.font, fontSize:10, color:T.inkMute }}>win rate</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {!loading && tab === 'busz' && (
          <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
            {buszRows.map((p, i) => {
              const s = stats[p.id] || {};
              return (
                <div key={p.id} style={{ background:T.surface, borderRadius:18, padding:'14px 16px', display:'flex', alignItems:'center', gap:12, boxShadow:T.shadow }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color: i===0?'#F59E0B':i===1?T.inkSoft:T.inkMute, minWidth:24, textAlign:'center' }}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':i+1}</div>
                  <div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:18, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{p.name}</div>
                    <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2 }}>
                      {s.busz_played||0} játék · {s.busz_completions||0} teljesítve
                    </div>
                  </div>
                  <div style={{ textAlign:'right', flexShrink:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.coral }}>{s.busz_total_drinks||0}</div>
                    <div style={{ fontFamily:T.font, fontSize:10, color:T.inkMute }}>korty ivott</div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {!loading && profiles.length === 0 && (
          <div style={{ textAlign:'center', padding:40, fontFamily:T.font, color:T.inkSoft }}>
            <div style={{ fontSize:40, marginBottom:12 }}>📊</div>
            <div style={{ fontWeight:800, fontSize:16, color:T.ink }}>Még nincs adat</div>
            <div style={{ fontSize:13, marginTop:6 }}>Adj hozzá névjegyeket a Játékosok képernyőn!</div>
          </div>
        )}
      </div>
    </div>
  );
}

"""

OLD2 = "function HomeScreen("
assert OLD2 in html, "ASSERT FAILED: HomeScreen function not found"
html = html.replace(OLD2, STATS_SCREEN + OLD2, 1)
print("✓ Step 2: StatsScreen component added")

# ── 3. HomeScreen: stats button top-left ──────────────────────────────────────
OLD3 = """        {resumeRoomData && onResume && (
          <div style={{ position:'absolute', top:14, left:18, zIndex:10 }}>
            <button onClick={() => onResume(resumeRoomData)} style={{ display:'flex', alignItems:'center', gap:7, padding:'8px 14px', borderRadius:999, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer', boxShadow:T.shadowLift, animation:'pulse 2s infinite' }}>
              <span style={{ fontSize:16 }}>🏓</span> Folytatás
            </button>
          </div>
        )}"""

NEW3 = """        <div style={{ position:'absolute', top:14, left:18, zIndex:10, display:'flex', gap:8 }}>
          {resumeRoomData && onResume && (
            <button onClick={() => onResume(resumeRoomData)} style={{ display:'flex', alignItems:'center', gap:7, padding:'8px 14px', borderRadius:999, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer', boxShadow:T.shadowLift, animation:'pulse 2s infinite' }}>
              <span style={{ fontSize:16 }}>🏓</span> Folytatás
            </button>
          )}
          <button onClick={() => go('stats')} style={{ width:42, height:42, borderRadius:'50%', border:'none', background:T.surface, boxShadow:T.shadow, cursor:'pointer', display:'grid', placeItems:'center', fontSize:20 }}>🕐</button>
        </div>"""

assert OLD3 in html, "ASSERT FAILED: HomeScreen resume block not found"
html = html.replace(OLD3, NEW3, 1)
print("✓ Step 3: HomeScreen stats button added")

# ── 4. PlayersScreen: profileMode state + useEffect ──────────────────────────
OLD4 = "  const secretTimerRef = React.useRef(null);"
NEW4 = """  const secretTimerRef = React.useRef(null);
  const [profileMode, setProfileMode] = React.useState(false);
  const [profileList, setProfileList] = React.useState([]);
  const [loadingProfiles, setLoadingProfiles] = React.useState(false);"""

assert OLD4 in html, "ASSERT FAILED: secretTimerRef not found"
html = html.replace(OLD4, NEW4, 1)
print("✓ Step 4a: PlayersScreen profile state added")

# Add useEffect for loading profiles — insert after PRESET_PLAYERS block
OLD4B = """  const handleSecretTap = () => {"""
NEW4B = """  React.useEffect(() => {
    if (!profileMode) return;
    setLoadingProfiles(true);
    if (typeof window.getProfiles === 'function') {
      window.getProfiles().then(profs => { setProfileList(profs); setLoadingProfiles(false); });
    } else { setLoadingProfiles(false); }
  }, [profileMode]);

  const handleSecretTap = () => {"""

assert OLD4B in html, "ASSERT FAILED: handleSecretTap not found"
html = html.replace(OLD4B, NEW4B, 1)
print("✓ Step 4b: PlayersScreen profileMode useEffect added")

# Replace the scroll container + grid section in PlayersScreen
OLD4C = """      <div style={{ flex:1, overflowY:'auto', minHeight:0, WebkitOverflowScrolling:'touch' }}>
        <div className="screen-wide screen-pad" style={{ paddingTop:20, paddingBottom:20 }}>
        <div className="grid-players">
          {players.map(p =>
            <PlayerCard key={p.id} p={p} onEdit={() => setEditing(p.id)} onRemove={() => removePlayer(p.id)} />
          )}
          <button onClick={addPlayer} style={{"""

NEW4C = """      {/* Névjegyek toggle */}
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

assert OLD4C in html, "ASSERT FAILED: PlayersScreen scroll container not found"
html = html.replace(OLD4C, NEW4C, 1)
print("✓ Step 4c: PlayersScreen Névjegyek toggle + profile grid added")

# ── 5. Beer Pong finishSE stat save ───────────────────────────────────────────
OLD5 = """  const finishSE = (champ, dm) => {
    if (doneRef.current) return;
    doneRef.current = true;
    setChampion(champ);
    const finalDm = {};
    Object.entries(dm).forEach(([id, cnt]) => { finalDm[id] = cnt; });
    onAdvance && onAdvance(finalDm);
  };"""

NEW5 = """  const finishSE = (champ, dm) => {
    if (doneRef.current) return;
    doneRef.current = true;
    setChampion(champ);
    const finalDm = {};
    Object.entries(dm).forEach(([id, cnt]) => { finalDm[id] = cnt; });
    onAdvance && onAdvance(finalDm);
    // Save BP stats for profile players
    if (typeof window.updateStats === 'function') {
      players.forEach(p => {
        if (!p.profileId) return;
        const isWinner = champ && champ.id === p.id;
        window.updateStats(p.profileId, {
          bp_wins: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
          bp_losses: firebase.firestore.FieldValue.increment(isWinner ? 0 : 1),
          bp_played: firebase.firestore.FieldValue.increment(1),
        });
      });
    }
  };"""

assert OLD5 in html, "ASSERT FAILED: finishSE not found"
html = html.replace(OLD5, NEW5, 1)
print("✓ Step 5: finishSE BP stats added")

# ── 6. Beer Pong finishRR stat save ───────────────────────────────────────────
OLD6 = """  const finishRR = (matches, dm, parts) => {
    if (doneRef.current) return;
    doneRef.current = true;
    setRrDone(true);
    const standings = getRRStandings(parts, matches);
    const champ = standings[0]?.player;
    setChampion(champ);
    const finalDm = {};
    Object.entries(dm).forEach(([id, cnt]) => { finalDm[id] = cnt; });
    onAdvance && onAdvance(finalDm);
  };"""

NEW6 = """  const finishRR = (matches, dm, parts) => {
    if (doneRef.current) return;
    doneRef.current = true;
    setRrDone(true);
    const standings = getRRStandings(parts, matches);
    const champ = standings[0]?.player;
    setChampion(champ);
    const finalDm = {};
    Object.entries(dm).forEach(([id, cnt]) => { finalDm[id] = cnt; });
    onAdvance && onAdvance(finalDm);
    if (typeof window.updateStats === 'function') {
      players.forEach(p => {
        if (!p.profileId) return;
        const isWinner = champ && champ.id === p.id;
        window.updateStats(p.profileId, {
          bp_wins: firebase.firestore.FieldValue.increment(isWinner ? 1 : 0),
          bp_losses: firebase.firestore.FieldValue.increment(isWinner ? 0 : 1),
          bp_played: firebase.firestore.FieldValue.increment(1),
        });
      });
    }
  };"""

assert OLD6 in html, "ASSERT FAILED: finishRR not found"
html = html.replace(OLD6, NEW6, 1)
print("✓ Step 6: finishRR BP stats added")

# ── 7. Busz fail stat save ────────────────────────────────────────────────────
OLD7 = "    if (!myRes.correct && myStep === busStepsCount - 1) setTimeout(() => { setGuessResult(null); setLastCardFail(true); setTimeout(() => setLastCardFail(false), 3000); }, 1000);"

NEW7 = """    if (!myRes.correct && myStep === busStepsCount - 1) {
      setTimeout(() => {
        setGuessResult(null); setLastCardFail(true); setTimeout(() => setLastCardFail(false), 3000);
        // Save busz fail stat
        if (typeof window.updateStats === 'function' && players[turn]?.profileId) {
          window.updateStats(players[turn].profileId, {
            busz_played: firebase.firestore.FieldValue.increment(1),
            busz_fails: firebase.firestore.FieldValue.increment(1),
            busz_total_drinks: firebase.firestore.FieldValue.increment(1),
          });
        }
      }, 1000);
    }"""

assert OLD7 in html, "ASSERT FAILED: busz fail condition not found"
html = html.replace(OLD7, NEW7, 1)
print("✓ Step 7: Busz fail stat save added")

# ── 8. Busz done stat save (phase='done' useEffect) ──────────────────────────
OLD8 = """    if (buszState?.phase === 'done') {
      onAdvance && onAdvance({});
    }
  }, [buszState?.phase]);"""

NEW8 = """    if (buszState?.phase === 'done') {
      // Save busz completion stats for profile players
      if (typeof window.updateStats === 'function' && buszState?.busRiderDrinks) {
        players.forEach(p => {
          if (!p.profileId) return;
          const drinks = buszState.busRiderDrinks[p.id] || 0;
          window.updateStats(p.profileId, {
            busz_played: firebase.firestore.FieldValue.increment(1),
            busz_completions: firebase.firestore.FieldValue.increment(1),
            busz_total_drinks: firebase.firestore.FieldValue.increment(drinks),
          });
        });
      }
      onAdvance && onAdvance({});
    }
  }, [buszState?.phase]);"""

assert OLD8 in html, "ASSERT FAILED: busz done phase useEffect not found"
html = html.replace(OLD8, NEW8, 1)
print("✓ Step 8: Busz done stat save added")

# ── 9. Wire up StatsScreen in router ─────────────────────────────────────────
OLD9 = "        {screen==='home'     && <HomeScreen     go={go} mode={mode} setMode={setMode} onStartGame={onStartGame} setTheme={handleSetTheme} currentTheme={appTheme} resumeRoomData={resumeRoomData} onResume={goResume} />}"
NEW9 = """        {screen==='home'     && <HomeScreen     go={go} mode={mode} setMode={setMode} onStartGame={onStartGame} setTheme={handleSetTheme} currentTheme={appTheme} resumeRoomData={resumeRoomData} onResume={goResume} />}
        {screen==='stats'    && <StatsScreen    go={go} />}"""

assert OLD9 in html, "ASSERT FAILED: HomeScreen router line not found"
html = html.replace(OLD9, NEW9, 1)
print("✓ Step 9: StatsScreen wired into router")

# ── 10. Update screen order array ────────────────────────────────────────────
OLD10 = "  const order = ['home','players','games','play','end','observer'];"
NEW10 = "  const order = ['home','stats','players','games','play','end','observer'];"

assert OLD10 in html, "ASSERT FAILED: screen order array not found"
html = html.replace(OLD10, NEW10, 1)
print("✓ Step 10: Screen order updated")

# ── 11. Seed profiles useEffect in PlayersScreen ─────────────────────────────
OLD11 = "  const handleSecretTap = () => {"
NEW11 = """  // Seed Firestore profiles from PRESET_PLAYERS if empty
  React.useEffect(() => {
    if (typeof window.getProfiles !== 'function' || typeof window.saveProfile !== 'function') return;
    window.getProfiles().then(existing => {
      if (existing.length > 0) return; // already seeded
      const PRESET_COLORS = ['#4FC3A1','#F87171','#60A5FA','#FBBF24','#A78BFA','#34D399','#F472B6','#FB923C','#818CF8'];
      PRESET_PLAYERS.forEach((p, i) => {
        window.saveProfile({ name: p.name, color: PRESET_COLORS[i % PRESET_COLORS.length] });
      });
    });
  }, []);

  const handleSecretTap = () => {"""

assert OLD11 in html, "ASSERT FAILED: handleSecretTap (2nd occurrence) not found"
# This OLD11 string appears once after we already replaced it above in step 4b — so this would be the remaining occurrence
# Let's count occurrences
count11 = html.count(OLD11)
assert count11 >= 1, f"ASSERT FAILED: handleSecretTap not found (count={count11})"
html = html.replace(OLD11, NEW11, 1)
print("✓ Step 11: Seed profiles useEffect added")

# ── 12. Version bump ──────────────────────────────────────────────────────────
OLD12 = "const APP_VERSION = 'v8.49';"
NEW12 = "const APP_VERSION = 'v8.50';"

assert OLD12 in html, "ASSERT FAILED: version string v8.49 not found"
html = html.replace(OLD12, NEW12, 1)
print("✓ Step 12: Version bumped to v8.50")

# ── Write output ──────────────────────────────────────────────────────────────
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ All steps complete! File size: {len(html):,} bytes (was {original_len:,})")
