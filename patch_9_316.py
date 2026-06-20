#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Games empty state — animált kocka + kártyák ha nincs kiválasztva semmi
old_grid_header = """        {/* ── Összes játék ── */}
        <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:10 }}>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>Összes játék</span>
        </div>"""
new_grid_header = """        {/* ── Összes játék ── */}
        <div style={{ display:'flex', alignItems:'center', gap:6, marginBottom:10 }}>
          <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.12em' }}>Összes játék</span>
        </div>
        {!anySelected && (
          <div style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:10, padding:'18px 0 22px', pointerEvents:'none' }}>
            <div style={{ position:'relative', width:120, height:90 }}>
              <div style={{ position:'absolute', left:10, top:10, fontSize:40, animation:'floatBob 2.0s 0.1s ease-in-out infinite' }}>🎲</div>
              <div style={{ position:'absolute', left:50, top:2, fontSize:36, animation:'floatBob 2.3s 0.4s ease-in-out infinite' }}>🃏</div>
              <div style={{ position:'absolute', left:80, top:14, fontSize:32, animation:'floatBob 1.9s 0.7s ease-in-out infinite' }}>🎴</div>
              {[{l:18,s:8,d:0},{l:55,s:6,d:0.3},{l:88,s:7,d:0.6}].map((b,i)=>(
                <div key={i} style={{ position:'absolute', left:b.l, top:70, width:b.s, height:b.s, borderRadius:'50%', background:`${T.mint}50`, animation:`floatBob 1.8s ${b.d}s ease-in-out infinite` }} />
              ))}
            </div>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, textAlign:'center' }}>Válassz játékokat a kezdéshez!</div>
          </div>
        )}"""
assert old_grid_header in html, "FAIL: grid header"
html = html.replace(old_grid_header, new_grid_header, 1)

# ── 2. Statisztika empty state — animált serleg + emoji
old_stats_empty = """        {!loading && profiles.length === 0 && tab !== 'games' && (
          <div style={{ textAlign:'center', padding:40, fontFamily:T.font, color:T.inkSoft }}>
            <div style={{ fontSize:40, marginBottom:12 }}>📊</div>
            <div style={{ fontWeight:800, fontSize:16, color:T.ink }}>Még nincs adat</div>
            <div style={{ fontSize:13, marginTop:6 }}>Adj hozzá névjegyeket a Játékosok képernyőn!</div>
          </div>
        )}"""
new_stats_empty = """        {!loading && profiles.length === 0 && tab !== 'games' && (
          <div style={{ textAlign:'center', padding:'32px 20px', fontFamily:T.font, color:T.inkSoft }}>
            <div style={{ position:'relative', width:120, height:110, margin:'0 auto 16px' }}>
              <div style={{ position:'absolute', left:'50%', top:0, transform:'translateX(-50%)', fontSize:64, animation:'floatBob 2.2s ease-in-out infinite', filter:'drop-shadow(0 6px 12px rgba(0,0,0,0.15))' }}>🏆</div>
              <div style={{ position:'absolute', left:4, bottom:16, fontSize:28, animation:'floatBob 1.9s 0.35s ease-in-out infinite' }}>🥂</div>
              <div style={{ position:'absolute', right:4, bottom:12, fontSize:26, animation:'floatBob 2.3s 0.6s ease-in-out infinite' }}>🍺</div>
              {[{l:15,s:7,d:0},{l:52,s:5,d:0.25},{l:90,s:8,d:0.5}].map((b,i)=>(
                <div key={i} style={{ position:'absolute', left:b.l, top:20+(i%2)*15, width:b.s, height:b.s, borderRadius:'50%', background:`${T.mint}40`, animation:`floatBob 2.0s ${b.d}s ease-in-out infinite` }} />
              ))}
            </div>
            <div style={{ fontWeight:900, fontSize:17, color:T.ink, marginBottom:6 }}>Még nincs statisztika</div>
            <div style={{ fontSize:13, lineHeight:1.5 }}>Játék után adj hozzá névjegyet<br/>a Játékosok képernyőn!</div>
          </div>
        )}"""
assert old_stats_empty in html, "FAIL: stats empty"
html = html.replace(old_stats_empty, new_stats_empty, 1)

# ── 3. ObserverStatus — spinning esetén 📡 + 🍺 lebeg egymás mellett
old_obs_status = """function ObserverStatus({ icon, title, sub, spinning, actionLabel, onAction }) {
  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:28, gap:14, textAlign:'center' }}>
      <div style={{ fontSize:64, lineHeight:1, animation: spinning ? 'pulse 1.6s ease-in-out infinite' : 'popIn .35s' }}>{icon}</div>"""
new_obs_status = """function ObserverStatus({ icon, title, sub, spinning, actionLabel, onAction }) {
  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:28, gap:14, textAlign:'center' }}>
      {spinning ? (
        <div style={{ position:'relative', width:120, height:90 }}>
          <div style={{ position:'absolute', left:'50%', top:0, transform:'translateX(-50%)', fontSize:60, animation:'floatBob 2.0s ease-in-out infinite' }}>{icon}</div>
          <div style={{ position:'absolute', left:12, bottom:0, fontSize:32, animation:'floatBob 1.8s 0.4s ease-in-out infinite' }}>🍺</div>
          <div style={{ position:'absolute', right:12, bottom:4, fontSize:28, animation:'floatBob 2.2s 0.7s ease-in-out infinite' }}>🥂</div>
        </div>
      ) : (
        <div style={{ fontSize:64, lineHeight:1, animation:'popIn .35s' }}>{icon}</div>
      )}"""
assert old_obs_status in html, "FAIL: ObserverStatus"
html = html.replace(old_obs_status, new_obs_status, 1)

# ── 4. Room code generálás — animált buborékok
old_creating = """      {creatingRoom && (
        <div style={{ position:'fixed', inset:0, background:T.bg, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:16, zIndex:100 }}>
          <div style={{ fontSize:52, lineHeight:1 }}>🔗</div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>Szoba létrehozása…</div>
          <div style={{ display:'flex', gap:6 }}>{[0,1,2].map(i => <span key={i} style={{ width:10, height:10, borderRadius:'50%', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>
        </div>
      )}"""
new_creating = """      {creatingRoom && (
        <div style={{ position:'fixed', inset:0, background:T.bg, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:16, zIndex:100 }}>
          <div style={{ position:'relative', width:160, height:120, marginBottom:8 }}>
            <div style={{ position:'absolute', left:'50%', top:0, transform:'translateX(-50%)', fontSize:56, animation:'floatBob 2.0s ease-in-out infinite', filter:'drop-shadow(0 6px 14px rgba(0,0,0,0.18))' }}>🔗</div>
            <div style={{ position:'absolute', left:10, bottom:10, fontSize:30, animation:'floatBob 1.8s 0.3s ease-in-out infinite' }}>🍺</div>
            <div style={{ position:'absolute', right:10, bottom:6, fontSize:28, animation:'floatBob 2.2s 0.6s ease-in-out infinite' }}>🥂</div>
            {[{l:20,s:9,d:0},{l:60,s:6,d:0.2},{l:100,s:8,d:0.5},{l:130,s:7,d:0.35}].map((b,i)=>(
              <div key={i} style={{ position:'absolute', left:b.l, top:30+(i%3)*18, width:b.s, height:b.s, borderRadius:'50%', background:`${T.mint}45`, animation:`floatBob 2.0s ${b.d}s ease-in-out infinite` }} />
            ))}
          </div>
          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay }}>Szoba létrehozása…</div>
          <div style={{ display:'flex', gap:6 }}>{[0,1,2].map(i => <span key={i} style={{ width:10, height:10, borderRadius:'50%', background:T.mint, animation:`dotBounce 1.2s ${i*0.15}s infinite ease-in-out` }}/>)}</div>
        </div>
      )}"""
assert old_creating in html, "FAIL: creatingRoom"
html = html.replace(old_creating, new_creating, 1)

# ── 5. Wildcard popup — animált pia ikonok a kártyán
old_wildcard = """                <div style={{ background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:24, padding:'20px 24px', boxShadow:'0 8px 40px rgba(0,0,0,0.4), 0 0 0 3px rgba(255,255,255,0.2)', border:'2px dashed rgba(255,255,255,0.5)' }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'rgba(0,0,0,0.5)', textTransform:'uppercase', letterSpacing:'0.18em', marginBottom:10 }}>{t('wildcardRound')}</div>
                  <div style={{ fontSize:48, marginBottom:12 }}>{roundPopup.wildcard.emoji}</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1A0A00', lineHeight:1.4 }}>{roundPopup.wildcard.text}</div>
                </div>"""
new_wildcard = """                <div style={{ background:'linear-gradient(135deg,#FFE066,#FF6B35)', borderRadius:24, padding:'20px 24px', boxShadow:'0 8px 40px rgba(0,0,0,0.4), 0 0 0 3px rgba(255,255,255,0.2)', border:'2px dashed rgba(255,255,255,0.5)', position:'relative', overflow:'visible' }}>
                  {/* Floating drink icons around card */}
                  <div style={{ position:'absolute', top:-16, left:-10, fontSize:24, animation:'floatBob 2.0s 0.1s ease-in-out infinite', pointerEvents:'none' }}>🍹</div>
                  <div style={{ position:'absolute', top:-14, right:-8, fontSize:22, animation:'floatBob 1.8s 0.45s ease-in-out infinite', pointerEvents:'none' }}>🥃</div>
                  <div style={{ position:'absolute', bottom:-12, left:10, fontSize:20, animation:'floatBob 2.2s 0.3s ease-in-out infinite', pointerEvents:'none' }}>🍺</div>
                  <div style={{ position:'absolute', bottom:-10, right:14, fontSize:18, animation:'floatBob 1.9s 0.65s ease-in-out infinite', pointerEvents:'none' }}>🥂</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'rgba(0,0,0,0.5)', textTransform:'uppercase', letterSpacing:'0.18em', marginBottom:10 }}>{t('wildcardRound')}</div>
                  <div style={{ fontSize:48, marginBottom:12, animation:'wobble 2.5s ease-in-out infinite' }}>{roundPopup.wildcard.emoji}</div>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:'#1A0A00', lineHeight:1.4 }}>{roundPopup.wildcard.text}</div>
                </div>"""
assert old_wildcard in html, "FAIL: wildcard"
html = html.replace(old_wildcard, new_wildcard, 1)

# ── 6. Dobogó 👑 — pattogó animáció az 1. helynek
old_crown = """                  ? <div style={{ fontSize:22, lineHeight:1, marginBottom:2, animation:'popIn .5s cubic-bezier(.2,.9,.3,1.4)' }}>👑</div>"""
new_crown = """                  ? <div style={{ fontSize:22, lineHeight:1, marginBottom:2, animation:'nextBounce 1.6s ease-in-out infinite' }}>👑</div>"""
assert old_crown in html, "FAIL: crown"
html = html.replace(old_crown, new_crown, 1)

html = html.replace("const APP_VERSION = 'v9.315';", "const APP_VERSION = 'v9.316';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.316 — 6 animált empty/loading state: games, stats, observer, room, wildcard, korona")
