with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

old = '''function EndScreen({ players, go, resetGame }) {
  const sorted = [...players].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));
  const drunkSorted = [...players].sort((a,b) => (b.drinks-a.drinks)||(a.points-b.points));
  const maxScore = Math.max(1, ...players.map(p=>p.points));
  const podium = sorted.slice(0,3);
  // Display order: [2nd left, 1st center, 3rd right]
  const podiumOrder = podium.length >= 3 ? [podium[1], podium[0], podium[2]] : podium.length === 2 ? [podium[1], podium[0]] : [podium[0]];
  const podiumHeights = [75, 115, 55]; // left=2nd, center=1st, right=3rd
  const podiumLabels = ['2.', '1.', '3.'];
  const podiumTones = ['#C0C0C0', T.yellow, '#CD7F32'];
  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <Confetti />
      <AppBar title="Játék vége! 🎉" />
      <div style={{ flex:1, overflowY:'auto', minHeight:0, WebkitOverflowScrolling:'touch' }}>
      <div className="content-box screen-pad" style={{ paddingTop:20, paddingBottom:24, display:'flex', flexDirection:'column', gap:18 }}>

        {/* Podium */}
        <div style={{ display:'flex', alignItems:'flex-end', justifyContent:'center', gap:6, paddingTop:8 }}>
          {podiumOrder.map((p, i) => {
            const h = podiumHeights[i] ?? 55;
            const tone = podiumTones[i] ?? '#aaa';
            const lbl = podiumLabels[i] ?? '';
            return (
              <div key={p.id} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:4, flex:1 }}>
                <div style={{ width: lbl==='1.' ? 64 : 48, height: lbl==='1.' ? 64 : 48, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize: lbl==='1.' ? 26 : 20, color:'#fff', boxShadow:`0 0 0 3px ${tone}`, animation:'popIn .4s cubic-bezier(.2,.9,.3,1.4)' }}>{p.name.charAt(0).toUpperCase()}</div>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink, textOverflow:'ellipsis', overflow:'hidden', whiteSpace:'nowrap', maxWidth:80, textAlign:'center' }}>{p.name}</div>
                <div style={{ width:'100%', height:h, background:tone, borderRadius:'10px 10px 0 0', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'flex-start', paddingTop:8, gap:2 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:'#fff', lineHeight:1 }}>{lbl}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.8)' }}>{p.points} pt</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Stats cards */}
        <div style={{ display:'flex', gap:10 }}>
          <div style={{ flex:1, background:T.surface, borderRadius:18, boxShadow:T.shadowLift, padding:'14px 10px', display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
            <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>Pont Győztes</div>
            <div style={{ color:T.yellow }}>{Icon.trophy(T.yellow)}</div>
            <div style={{ width:48, height:48, borderRadius:'50%', background:sorted[0].color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:'#fff' }}>{sorted[0].name.charAt(0).toUpperCase()}</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:'100%' }}>{sorted[0].name}</div>
            <Stat value={sorted[0].points} label="pont" tone={T.mint}/>
          </div>
          <div style={{ flex:1, background:T.surface, borderRadius:18, boxShadow:T.shadowLift, padding:'14px 10px', display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
            <div style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>Legtöbb Korty</div>
            <div style={{ color:T.coral, lineHeight:0 }}>{Icon.beer(T.coral)}</div>
            <div style={{ width:48, height:48, borderRadius:'50%', background:drunkSorted[0].color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:'#fff' }}>{drunkSorted[0].name.charAt(0).toUpperCase()}</div>
            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:'100%' }}>{drunkSorted[0].name}</div>
            <Stat value={drunkSorted[0].drinks} label="korty" tone={T.coral}/>
          </div>
        </div>

        {/* Full leaderboard */}
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {sorted.map((p,i) => <LeaderRow key={p.id} p={p} rank={i+1} maxScore={maxScore} />)}
        </div>
      </div>
      </div>
      <BottomBar>
        <div style={{ display:'flex', gap:10 }}>
          <button onClick={resetGame} style={{ flex:1, minHeight:56, border:`2px solid ${T.ink}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:14, cursor:'pointer' }}>Új meccs</button>
          <button onClick={() => go('home')} style={{ flex:1, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>Főmenü</button>
        </div>
      </BottomBar>
    </div>
  );
}'''

new = '''function EndScreen({ players, go, resetGame }) {
  const sorted = [...players].sort((a,b) => (b.points-a.points)||(a.drinks-b.drinks));
  const drunkSorted = [...players].sort((a,b) => (b.drinks-a.drinks)||(a.points-b.points));
  const maxScore = Math.max(1, ...players.map(p=>p.points));
  const podium = sorted.slice(0,3);
  const podiumOrder = podium.length >= 3 ? [podium[1], podium[0], podium[2]] : podium.length === 2 ? [podium[1], podium[0]] : [podium[0]];
  const podiumHeights = [80, 120, 60];
  const podiumRanks = [2, 1, 3];
  const podiumTones = ['#C0C0C0', T.yellow, '#CD7F32'];
  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <Confetti />
      <AppBar title="Játék vége! 🎉" />
      <div style={{ flex:1, overflowY:'auto', minHeight:0, WebkitOverflowScrolling:'touch' }}>
      <div className="content-box screen-pad" style={{ paddingTop:20, paddingBottom:24, display:'flex', flexDirection:'column', gap:18 }}>

        {/* Podium */}
        <div style={{ display:'flex', alignItems:'flex-end', justifyContent:'center', gap:6, paddingTop:12 }}>
          {podiumOrder.map((p, i) => {
            const h = podiumHeights[i] ?? 55;
            const tone = podiumTones[i] ?? '#aaa';
            const rank = podiumRanks[i] ?? (i+1);
            const isFirst = rank === 1;
            const avatarSize = isFirst ? 68 : 50;
            const avatarFontSize = isFirst ? 28 : 20;
            return (
              <div key={p.id} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:0, flex:1 }}>
                {/* Crown for 1st */}
                {isFirst
                  ? <div style={{ fontSize:22, lineHeight:1, marginBottom:2, animation:'popIn .5s cubic-bezier(.2,.9,.3,1.4)' }}>👑</div>
                  : <div style={{ height:26 }} />
                }
                {/* Avatar */}
                <div style={{ width:avatarSize, height:avatarSize, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:avatarFontSize, color:'#fff', boxShadow:`0 0 0 3px ${tone}, 0 4px 14px rgba(0,0,0,0.18)`, animation:'popIn .4s cubic-bezier(.2,.9,.3,1.4)', marginBottom:6 }}>{p.name.charAt(0).toUpperCase()}</div>
                {/* Name */}
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink, textOverflow:'ellipsis', overflow:'hidden', whiteSpace:'nowrap', maxWidth:90, textAlign:'center', marginBottom:6 }}>{p.name}</div>
                {/* Podium block */}
                <div style={{ width:'100%', height:h, background:tone, borderRadius:'10px 10px 0 0', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:isFirst?28:22, color:'#fff', lineHeight:1 }}>{rank}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:'rgba(255,255,255,0.85)' }}>{p.points} pt</div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Stats cards */}
        <div style={{ display:'flex', gap:10 }}>
          {[
            { label:'Pont győztes', icon:'🏆', tone:T.yellow, player:sorted[0], stat:sorted[0].points, statLabel:'pont' },
            { label:'Legtöbb korty', icon:'🍺', tone:T.coral, player:drunkSorted[0], stat:drunkSorted[0].drinks, statLabel:'korty' },
          ].map(({ label, icon, tone, player, stat, statLabel }) => (
            <div key={label} style={{ flex:1, background:T.surface, borderRadius:18, boxShadow:T.shadowLift, overflow:'hidden', display:'flex', flexDirection:'column' }}>
              <div style={{ height:6, background:tone }} />
              <div style={{ padding:'12px 10px 14px', display:'flex', flexDirection:'column', alignItems:'center', gap:6 }}>
                <div style={{ display:'flex', alignItems:'center', gap:4 }}>
                  <span style={{ fontSize:13 }}>{icon}</span>
                  <span style={{ fontFamily:T.font, fontSize:9, fontWeight:700, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em' }}>{label}</span>
                </div>
                <div style={{ width:52, height:52, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{player.name.charAt(0).toUpperCase()}</div>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:15, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:'100%', textAlign:'center' }}>{player.name}</div>
                <div style={{ display:'flex', alignItems:'baseline', gap:5, padding:'5px 14px', borderRadius:999, background:`${tone}22` }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:tone, lineHeight:1 }}>{stat}</span>
                  <span style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.inkSoft, textTransform:'uppercase' }}>{statLabel}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Full leaderboard */}
        <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
          {sorted.map((p,i) => <LeaderRow key={p.id} p={p} rank={i+1} maxScore={maxScore} />)}
        </div>
      </div>
      </div>
      <BottomBar>
        <div style={{ display:'flex', gap:10 }}>
          <button onClick={resetGame} style={{ flex:1, minHeight:56, border:`2px solid ${T.ink}`, background:'transparent', color:T.ink, fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:14, cursor:'pointer' }}>Új meccs</button>
          <button onClick={() => go('home')} style={{ flex:1, minHeight:56, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:T.weightTitle, fontSize:16, borderRadius:14, cursor:'pointer', boxShadow:T.shadow }}>Főmenü</button>
        </div>
      </BottomBar>
    </div>
  );
}'''

assert old in html, "EndScreen not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
