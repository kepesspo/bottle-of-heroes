#!/usr/bin/env python3
"""v9.423 — BeerPong: töröl BeerPongTournamentScreen, tábló gomb a champion screenen"""

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# ── 1. Töröljük a HomeScreen Beerpong Bajnokság gombját ──────────────────────
OLD_BP_BTN = """            <button onClick={() => go('beerpong')} style={{ display:'flex', alignItems:'center', gap:12, width:'100%', padding:'12px 16px', background:T.surface, border:'1.5px solid #F59E0B55', borderRadius:18, cursor:'pointer', textAlign:'left', boxShadow:T.shadow, marginTop:8 }}>
              <div style={{ width:36, height:36, borderRadius:10, background:'#F59E0B22', display:'grid', placeItems:'center', flexShrink:0 }}>
                <span style={{ fontSize:20 }}>🏆</span>
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:'#F59E0B' }}>Beerpong Bajnokság</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:1 }}>Tábló, ágrajz, eredmények</div>
              </div>
              <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M7 4l5 5-5 5" stroke={T.inkSoft} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>
            </button>"""
assert OLD_BP_BTN in src, 'BP bajnokság gomb not found'
src = src.replace(OLD_BP_BTN, '', 1)
print('HomeScreen BP bajnokság gomb eltávolítva')

# ── 2. Töröljük a BottleApp routing sort ─────────────────────────────────────
OLD_ROUTE = "\n        {screen==='beerpong' && <BeerPongTournamentScreen go={go} players={players} />}"
assert OLD_ROUTE in src, 'BP route not found'
src = src.replace(OLD_ROUTE, '', 1)
print('BottleApp BP route eltávolítva')

# ── 3. Töröljük a BeerPongTournamentScreen függvényt ─────────────────────────
MARKER_START = '\n// ─── BEERPONG BAJNOKSÁG ───────────────────────────────────────────────────────\nfunction BeerPongTournamentScreen('
assert MARKER_START in src, 'BeerPongTournamentScreen start not found'
start_idx = src.index(MARKER_START)
# The function ends just before ReactDOM.createRoot
END_MARKER = '\nReactDOM.createRoot('
end_idx = src.index(END_MARKER)
# Everything between start_idx and end_idx is the tournament screen
src = src[:start_idx] + '\n' + src[end_idx:]
print('BeerPongTournamentScreen törölve')

# ── 4. Tábló gomb a champion card-ra ─────────────────────────────────────────
# Insert a "Tábló" button and a tableau overlay into the champion block
OLD_CHAMPION_CARD = """      return (
        <div style={{ width:'100%', background:T.surface, borderRadius:22, padding:'28px 20px', textAlign:'center', boxShadow:T.shadow, display:'flex', flexDirection:'column', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>
          <BeerPongConfetti />
          {showQR && <QRModal url={joinUrl} onClose={() => setShowQR(false)} />}
          <div style={{ fontFamily:T.font, fontSize:32 }}>🏆</div>
          <div style={{ width:88, height:88, borderRadius:'50%', background:champion.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:38, color:'#fff', boxShadow:'0 6px 24px ' + champion.color + '55' }}>
            {champion.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink }}>{champion.name}</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Beer Pong Bajnok! 🍺</div>
          {TOURNAMENT_NAME ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkMute, marginTop:-4 }}>{TOURNAMENT_NAME}</div> : null}
        </div>
      );"""

NEW_CHAMPION_CARD = """      return (
        <div style={{ width:'100%', background:T.surface, borderRadius:22, padding:'28px 20px', textAlign:'center', boxShadow:T.shadow, display:'flex', flexDirection:'column', alignItems:'center', gap:12, position:'relative', overflow:'hidden' }}>
          <BeerPongConfetti />
          {showQR && <QRModal url={joinUrl} onClose={() => setShowQR(false)} />}
          {showTableau && <BeerPongTableau
            champion={champion}
            players={players}
            tournamentName={TOURNAMENT_NAME}
            tournament={TOURNAMENT}
            seRounds={seRounds}
            rrMatches={rrMatches}
            tsGroups={tsGroups}
            drinkMap={drinkMap}
            onClose={() => setShowTableau(false)}
          />}
          <div style={{ fontFamily:T.font, fontSize:32 }}>🏆</div>
          <div style={{ width:88, height:88, borderRadius:'50%', background:champion.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:38, color:'#fff', boxShadow:'0 6px 24px ' + champion.color + '55' }}>
            {champion.name.charAt(0).toUpperCase()}
          </div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:24, color:T.ink }}>{champion.name}</div>
          <div style={{ fontFamily:T.font, fontSize:14, color:T.inkSoft }}>Beer Pong Bajnok! 🍺</div>
          {TOURNAMENT_NAME ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13, color:T.inkMute, marginTop:-4 }}>{TOURNAMENT_NAME}</div> : null}
          <button onClick={() => setShowTableau(true)} style={{ marginTop:4, padding:'10px 28px', borderRadius:14, border:'none', background:'#F59E0B', color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer', display:'flex', alignItems:'center', gap:8 }}>
            <span>📊</span> Tábló megosztása
          </button>
        </div>
      );"""

assert OLD_CHAMPION_CARD in src, 'champion card not found'
src = src.replace(OLD_CHAMPION_CARD, NEW_CHAMPION_CARD, 1)
print('champion card tábló gombbal bővítve')

# ── 5. showTableau state hozzáadása a BeerPongGame-hez ───────────────────────
OLD_DONE_REF = "  const doneRef = React.useRef(false);"
NEW_DONE_REF = "  const doneRef = React.useRef(false);\n  const [showTableau, setShowTableau] = React.useState(false);"
assert OLD_DONE_REF in src, 'doneRef not found'
src = src.replace(OLD_DONE_REF, NEW_DONE_REF, 1)
print('showTableau state hozzáadva')

# ── 6. BeerPongTableau komponens ─────────────────────────────────────────────
TABLEAU_COMPONENT = r"""
function BeerPongTableau({ champion, players, tournamentName, tournament, seRounds, rrMatches, tsGroups, drinkMap, onClose }) {
  const font = "'Nunito', 'Inter', sans-serif";
  const GOLD = '#F59E0B';
  const SILVER = '#94A3B8';
  const BRONZE = '#CD7C3A';
  const INK = '#1A1A2E';
  const BG = '#0F1A30';
  const SURFACE = '#1A2B4B';
  const canvasRef = React.useRef(null);
  const [imgUrl, setImgUrl] = React.useState(null);

  // Collect all matches with results
  const allMatches = React.useMemo(() => {
    const ms = [];
    if (tournament === 'se') {
      seRounds.forEach((round, ri) => {
        round.forEach(m => {
          if (m.winner) ms.push({ ...m, label: 'Kör ' + (ri+1) });
        });
      });
    } else if (tournament === 'rr') {
      rrMatches.forEach(m => {
        if (m.winner || m.draw) ms.push({ ...m, label: 'Körmérkőző' });
      });
    } else if (tournament && tournament.startsWith('grp_')) {
      (tsGroups||[]).forEach(g => {
        (g.matches||[]).forEach(m => {
          if (m.winner || m.draw) ms.push({ ...m, label: g.label });
        });
      });
    }
    return ms;
  }, [tournament, seRounds, rrMatches, tsGroups]);

  // Get top 3 from results
  const podium = React.useMemo(() => {
    const wins = {};
    players.forEach(p => { wins[p.id] = 0; });
    allMatches.forEach(m => {
      if (m.winner && wins[m.winner.id] !== undefined) wins[m.winner.id]++;
    });
    const sorted = [...players].sort((a,b) => (wins[b.id]||0) - (wins[a.id]||0));
    // Champion always #1
    const champIdx = sorted.findIndex(p => p.id === champion?.id);
    if (champIdx > 0) { const c = sorted.splice(champIdx, 1); sorted.unshift(c[0]); }
    return sorted.slice(0, 3);
  }, [players, allMatches, champion]);

  // Fun stats
  const funStats = React.useMemo(() => {
    let totalDrinks = 0;
    Object.values(drinkMap||{}).forEach(n => { totalDrinks += (n||0); });
    return [
      { label: 'Meccsek száma', value: allMatches.length },
      { label: 'Összes korty', value: totalDrinks },
      { label: 'Játékosok', value: players.length },
    ];
  }, [allMatches, drinkMap, players]);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    // A4 landscape ratio ~1.414:1, use 1400x990
    const W = 1400, H = 990;
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');

    // Background
    ctx.fillStyle = BG;
    ctx.fillRect(0, 0, W, H);

    const round = (x,y,w,h,r) => {
      ctx.beginPath();
      ctx.moveTo(x+r, y);
      ctx.lineTo(x+w-r, y); ctx.quadraticCurveTo(x+w, y, x+w, y+r);
      ctx.lineTo(x+w, y+h-r); ctx.quadraticCurveTo(x+w, y+h, x+w-r, y+h);
      ctx.lineTo(x+r, y+h); ctx.quadraticCurveTo(x, y+h, x, y+h-r);
      ctx.lineTo(x, y+r); ctx.quadraticCurveTo(x, y, x+r, y);
      ctx.closePath();
    };

    // ── Header ────────────────────────────────────────────────────────────────
    ctx.fillStyle = SURFACE;
    round(0, 0, W, 72, 0); ctx.fill();

    ctx.fillStyle = GOLD;
    ctx.font = 'bold 22px ' + font;
    ctx.textAlign = 'left';
    ctx.fillText('🏓 Bottle of Heroes', 24, 44);

    ctx.fillStyle = '#fff';
    ctx.font = 'bold 20px ' + font;
    ctx.textAlign = 'center';
    ctx.fillText((tournamentName || 'Beer Pong Torna').toUpperCase(), W/2, 44);

    ctx.fillStyle = '#94A3B8';
    ctx.font = '14px ' + font;
    ctx.textAlign = 'right';
    ctx.fillText(new Date().toLocaleDateString('hu-HU'), W-24, 44);

    // Fun stats row
    funStats.forEach((s, i) => {
      const x = 24 + i * 160;
      ctx.fillStyle = '#fff';
      ctx.font = 'bold 14px ' + font;
      ctx.textAlign = 'left';
      ctx.fillText(s.value + ' ' + s.label, x, 62);
    });

    // ── Left column: groups + matches ─────────────────────────────────────────
    const LW = 370, COL_X = 16, TOP = 88;
    let cy = TOP;

    if (tournament && tournament.startsWith('grp_') && tsGroups && tsGroups.length > 0) {
      tsGroups.forEach(g => {
        // Group header
        ctx.fillStyle = '#F59E0B22';
        round(COL_X, cy, LW, 28, 8); ctx.fill();
        ctx.fillStyle = GOLD;
        ctx.font = 'bold 13px ' + font;
        ctx.textAlign = 'left';
        ctx.fillText(g.label || 'Csoport', COL_X+10, cy+19);
        cy += 34;

        // Standings header
        const cols = ['J','Gy','D','V','P+','P-'];
        const colW = (LW - 120) / cols.length;
        ctx.fillStyle = '#94A3B8';
        ctx.font = '11px ' + font;
        cols.forEach((c,i) => {
          ctx.textAlign = 'center';
          ctx.fillText(c, COL_X + 120 + i*colW + colW/2, cy+12);
        });
        cy += 16;

        // Standings rows
        const st = {};
        (g.players||[]).forEach(p => { st[p.id]={player:p,J:0,Gy:0,D:0,V:0,Pp:0,Pm:0}; });
        (g.matches||[]).forEach(m => {
          if (!m.score && !m.winner && !m.draw) return;
          const [s1,s2] = (m.score||'0-0').split('-').map(Number);
          if (st[m.p1?.id]) { st[m.p1.id].J++; st[m.p1.id].Pp+=s1; st[m.p1.id].Pm+=s2; }
          if (st[m.p2?.id]) { st[m.p2.id].J++; st[m.p2.id].Pp+=s2; st[m.p2.id].Pm+=s1; }
          if (m.draw) {
            if (st[m.p1?.id]) st[m.p1.id].D++;
            if (st[m.p2?.id]) st[m.p2.id].D++;
          } else if (m.winner) {
            const loserId = m.p1?.id===m.winner.id ? m.p2?.id : m.p1?.id;
            if (st[m.winner.id]) st[m.winner.id].Gy++;
            if (st[loserId]) st[loserId].V++;
          }
        });
        const rows = Object.values(st).sort((a,b)=>b.Gy-a.Gy);
        rows.forEach((r,ri) => {
          const ry = cy + ri*20;
          if (ri%2===0) { ctx.fillStyle='rgba(255,255,255,.04)'; round(COL_X,ry,LW,20,4); ctx.fill(); }
          ctx.fillStyle='#fff'; ctx.font='12px '+font; ctx.textAlign='left';
          ctx.fillText(r.player.name, COL_X+8, ry+14);
          [r.J,r.Gy,r.D,r.V,r.Pp,r.Pm].forEach((v,i) => {
            ctx.textAlign='center';
            ctx.fillText(v, COL_X+120+i*colW+colW/2, ry+14);
          });
        });
        cy += rows.length*20 + 12;
      });
    }

    // Match results list
    ctx.fillStyle = GOLD;
    ctx.font = 'bold 13px ' + font;
    ctx.textAlign = 'left';
    ctx.fillText('MECCSEREDMÉNYEK', COL_X, cy+14);
    cy += 22;

    allMatches.slice(0,18).forEach((m,i) => {
      const ry = cy + i*22;
      if (i%2===0) { ctx.fillStyle='rgba(255,255,255,.04)'; round(COL_X,ry,LW,22,4); ctx.fill(); }
      const wname = m.winner?.name || (m.draw ? 'Döntetlen' : '?');
      const lname = m.p1?.id===m.winner?.id ? m.p2?.name : m.p1?.name;
      ctx.fillStyle='#fff'; ctx.font='12px '+font; ctx.textAlign='left';
      ctx.fillText((m.label||'') + ': ' + (m.p1?.name||'?') + ' vs ' + (m.p2?.name||'?'), COL_X+6, ry+15);
      ctx.fillStyle=GOLD; ctx.font='bold 11px '+font; ctx.textAlign='right';
      ctx.fillText(m.score || (m.draw?'D':wname||''), COL_X+LW-6, ry+15);
    });
    cy += Math.min(allMatches.length,18)*22;

    // ── Right top: SE bracket ─────────────────────────────────────────────────
    const RX = COL_X + LW + 16;
    const RW = W - RX - 16;
    const BRACKET_H = Math.floor(H * 0.55);

    ctx.fillStyle = SURFACE;
    round(RX, TOP, RW, BRACKET_H, 12); ctx.fill();

    ctx.fillStyle = GOLD;
    ctx.font = 'bold 13px ' + font;
    ctx.textAlign = 'left';
    ctx.fillText('ÁGRAJZ', RX+14, TOP+20);

    if (tournament === 'se' && seRounds.length > 0) {
      const numRounds = seRounds.length;
      const colW2 = (RW - 28) / numRounds;
      seRounds.forEach((round, ri) => {
        const cx2 = RX + 14 + ri * colW2;
        const numM = round.length;
        const slotH = (BRACKET_H - 50) / (numM || 1);
        round.forEach((m, mi) => {
          const my = TOP + 34 + mi * slotH;
          // Card
          ctx.fillStyle = m.winner ? '#1E3A5F' : '#243555';
          round(cx2, my, colW2-8, slotH-8, 8); ctx.fill();
          // P1
          ctx.fillStyle = m.winner?.id === m.p1?.id ? GOLD : '#fff';
          ctx.font = (m.winner?.id===m.p1?.id ? 'bold ' : '') + '12px ' + font;
          ctx.textAlign = 'left';
          ctx.fillText(m.p1?.name || 'TBD', cx2+8, my+18);
          if (m.score) { ctx.fillStyle='#94A3B8'; ctx.font='11px '+font; ctx.fillText(m.score.split('-')[0], cx2+colW2-24, my+18); }
          // Divider
          ctx.strokeStyle = '#2D4A6B'; ctx.lineWidth = 1;
          ctx.beginPath(); ctx.moveTo(cx2+4, my+slotH/2-4); ctx.lineTo(cx2+colW2-12, my+slotH/2-4); ctx.stroke();
          // P2
          ctx.fillStyle = m.winner?.id === m.p2?.id ? GOLD : '#fff';
          ctx.font = (m.winner?.id===m.p2?.id ? 'bold ' : '') + '12px ' + font;
          ctx.fillText(m.p2?.name || 'TBD', cx2+8, my+slotH-14);
          if (m.score) { ctx.fillStyle='#94A3B8'; ctx.font='11px '+font; ctx.fillText(m.score.split('-')[1]||'', cx2+colW2-24, my+slotH-14); }
          // Connector line to next round
          if (ri < numRounds-1) {
            const nextRound = seRounds[ri+1];
            if (nextRound) {
              const nextNumM = nextRound.length;
              const nextSlotH = (BRACKET_H - 50) / (nextNumM || 1);
              const nextMi = Math.floor(mi/2);
              const ny = TOP + 34 + nextMi * nextSlotH + nextSlotH/2 - 4;
              ctx.strokeStyle = '#2D4A6B'; ctx.lineWidth = 1.5;
              ctx.beginPath();
              ctx.moveTo(cx2 + colW2 - 8, my + slotH/2 - 4);
              ctx.lineTo(cx2 + colW2 + 4, my + slotH/2 - 4);
              ctx.lineTo(cx2 + colW2 + 4, ny);
              ctx.lineTo(cx2 + colW2 + 8, ny);
              ctx.stroke();
            }
          }
        });
      });
    } else {
      // RR or groups — just show title
      ctx.fillStyle = '#94A3B8'; ctx.font = '13px '+font; ctx.textAlign='center';
      ctx.fillText('Körmérkőzéses rendszer', RX+RW/2, TOP+BRACKET_H/2);
    }

    // ── Right bottom: Podium + fun stats ─────────────────────────────────────
    const PY = TOP + BRACKET_H + 12;
    const PH = H - PY - 16;

    ctx.fillStyle = SURFACE;
    round(RX, PY, RW, PH, 12); ctx.fill();

    // Podium title
    ctx.fillStyle = GOLD;
    ctx.font = 'bold 13px ' + font;
    ctx.textAlign = 'left';
    ctx.fillText('DOBOGÓ', RX+14, PY+20);

    // Podium bars
    const podiumOrder = [podium[1], podium[0], podium[2]].filter(Boolean);
    const podiumColors = [SILVER, GOLD, BRONZE];
    const barW = Math.min(100, (RW-60) / 3);
    const barBaseY = PY + PH - 16;
    const podiumHeights = [55, 80, 40];
    const podiumNums = ['2.', '1.', '3.'];
    const podiumStartX = RX + (RW - podiumOrder.length * (barW+12)) / 2;

    podiumOrder.forEach((p, i) => {
      if (!p) return;
      const bx = podiumStartX + i*(barW+12);
      const bh = podiumHeights[i];
      ctx.fillStyle = podiumColors[i] + '33';
      round(bx, barBaseY-bh, barW, bh, 8); ctx.fill();
      ctx.fillStyle = podiumColors[i];
      ctx.font = 'bold 11px '+font; ctx.textAlign='center';
      ctx.fillText(podiumNums[i], bx+barW/2, barBaseY-bh+16);
      // Avatar circle
      ctx.fillStyle = p.color||'#6366F1';
      ctx.beginPath(); ctx.arc(bx+barW/2, barBaseY-bh-24, 20, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle='#fff'; ctx.font='bold 16px '+font;
      ctx.fillText(p.name.charAt(0).toUpperCase(), bx+barW/2, barBaseY-bh-18);
      ctx.fillStyle='#fff'; ctx.font='12px '+font;
      ctx.fillText(p.name, bx+barW/2, barBaseY-bh+32);
    });

    // Fun stats row
    const fsY = PY + 28;
    funStats.forEach((s,i) => {
      const fx = RX + RW - 200 + i*60;
      ctx.fillStyle = GOLD; ctx.font='bold 18px '+font; ctx.textAlign='center';
      ctx.fillText(s.value, fx, fsY+16);
      ctx.fillStyle='#94A3B8'; ctx.font='10px '+font;
      ctx.fillText(s.label, fx, fsY+30);
    });

    // Champion highlight
    if (champion) {
      ctx.fillStyle = GOLD+'22';
      round(RX+14, PY+44, RW-28, 36, 10); ctx.fill();
      ctx.fillStyle = GOLD; ctx.font='bold 15px '+font; ctx.textAlign='center';
      ctx.fillText('🏆 ' + champion.name + ' — Beer Pong Bajnok!', RX+RW/2, PY+67);
    }

    setImgUrl(canvas.toDataURL('image/png'));
  }, []);

  const handleShare = () => {
    if (!imgUrl) return;
    if (navigator.share && navigator.canShare) {
      fetch(imgUrl).then(r=>r.blob()).then(blob => {
        const file = new File([blob],'beerpong_tabló.png',{type:'image/png'});
        if (navigator.canShare({files:[file]})) {
          navigator.share({ files:[file], title:'Beer Pong Tábló' }).catch(()=>{});
        } else {
          const a = document.createElement('a'); a.href=imgUrl; a.download='beerpong_tabló.png'; a.click();
        }
      });
    } else {
      const a = document.createElement('a'); a.href=imgUrl; a.download='beerpong_tabló.png'; a.click();
    }
  };

  return (
    <div style={{ position:'fixed', inset:0, background:'rgba(0,0,0,.85)', zIndex:9999, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:16 }}>
      <canvas ref={canvasRef} style={{ display:'none' }} />
      <div style={{ background:'#1A2B4B', borderRadius:20, padding:16, width:'100%', maxWidth:480, display:'flex', flexDirection:'column', gap:12 }}>
        <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
          <span style={{ fontFamily:"'Nunito',sans-serif", fontWeight:900, fontSize:18, color:'#fff' }}>📊 Tábló</span>
          <button onClick={onClose} style={{ background:'none', border:'none', fontSize:22, cursor:'pointer', color:'#94A3B8' }}>✕</button>
        </div>
        {imgUrl ? (
          <>
            <img src={imgUrl} style={{ width:'100%', borderRadius:12, border:'1px solid #243555' }} alt="Tábló" />
            <button onClick={handleShare} style={{ padding:'13px', borderRadius:14, border:'none', background:'#F59E0B', color:'#fff', fontFamily:"'Nunito',sans-serif", fontWeight:900, fontSize:16, cursor:'pointer' }}>
              ⬇️ Letöltés / Megosztás
            </button>
          </>
        ) : (
          <div style={{ color:'#94A3B8', textAlign:'center', padding:40 }}>Tábló generálása...</div>
        )}
      </div>
    </div>
  );
}
"""

# Insert before BeerPongObserverView
INSERT_BEFORE = '\nfunction BeerPongObserverView('
assert INSERT_BEFORE in src, 'BeerPongObserverView not found'
idx = src.index(INSERT_BEFORE)
src = src[:idx] + TABLEAU_COMPONENT + src[idx:]
print('BeerPongTableau komponens hozzáadva')

# ── 7. Version bump ───────────────────────────────────────────────────────────
assert "const APP_VERSION = 'v9.422';" in src
src = src.replace("const APP_VERSION = 'v9.422';", "const APP_VERSION = 'v9.423';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('v9.423 OK')
