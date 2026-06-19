#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. html2canvas CDN hozzáadása
old_cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>'
new_cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>\n<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>'
assert old_cdn in html, "FAIL: CDN anchor"
html = html.replace(old_cdn, new_cdn, 1)

# ── 2. shareCard teljes csere — hidden DOM div + html2canvas
old_sharecard = """  const shareCard = () => {
    const W = 800, H = Math.max(400, 140 + Math.min(sorted.length, 6) * 72 + 40);
    const canvas = document.createElement('canvas');
    canvas.width = W; canvas.height = H;
    const ctx = canvas.getContext('2d');
    // Background
    const grad = ctx.createLinearGradient(0, 0, W, H);
    grad.addColorStop(0, '#0F172A'); grad.addColorStop(1, '#1E3A5F');
    ctx.fillStyle = grad; ctx.fillRect(0, 0, W, H);
    // Decorative top bar
    const topGrad = ctx.createLinearGradient(0, 0, W, 0);
    topGrad.addColorStop(0, '#4FC2A0'); topGrad.addColorStop(1, '#6366F1');
    ctx.fillStyle = topGrad; ctx.fillRect(0, 0, W, 6);
    // Title
    ctx.fillStyle = '#FFFFFF'; ctx.font = 'bold 32px system-ui,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('🍺 Bottle of Heroes', W/2, 56);
    ctx.fillStyle = '#94A3B8'; ctx.font = '16px system-ui,sans-serif';
    ctx.fillText(`${sorted.length} játékos · ${lastRound || '?'} kör`, W/2, 84);
    ctx.strokeStyle = 'rgba(255,255,255,0.1)'; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(40, 104); ctx.lineTo(W-40, 104); ctx.stroke();
    // Players
    const topN = sorted.slice(0, Math.min(6, sorted.length));
    const cols = topN.length > 3 ? 2 : 1;
    const colW = (W - 80) / cols;
    topN.forEach((p, i) => {
      const col = cols === 2 ? i % 2 : 0;
      const row = cols === 2 ? Math.floor(i / 2) : i;
      const x = 40 + col * colW, y = 120 + row * 72;
      const rank = i + 1;
      const medal = rank === 1 ? '🥇' : rank === 2 ? '🥈' : rank === 3 ? '🥉' : `${rank}.`;
      // Avatar
      ctx.beginPath(); ctx.arc(x+26, y+26, 22, 0, Math.PI*2);
      ctx.fillStyle = p.color; ctx.fill();
      ctx.fillStyle = '#FFF'; ctx.font = 'bold 18px system-ui,sans-serif'; ctx.textAlign = 'center';
      ctx.fillText(p.name.charAt(0).toUpperCase(), x+26, y+33);
      // Medal & name
      ctx.textAlign = 'left';
      ctx.font = '20px system-ui,sans-serif'; ctx.fillText(medal, x+58, y+20);
      ctx.fillStyle = '#F1F5F9'; ctx.font = 'bold 18px system-ui,sans-serif';
      ctx.fillText(p.name.length > 18 ? p.name.slice(0,17)+'…' : p.name, x+58, y+42);
      ctx.fillStyle = '#64748B'; ctx.font = '14px system-ui,sans-serif';
      ctx.fillText(`⭐ ${p.points} pont   🍺 ${p.drinks} korty`, x+58, y+60);
    });
    // Footer URL
    ctx.fillStyle = 'rgba(255,255,255,0.25)'; ctx.font = '13px system-ui,sans-serif'; ctx.textAlign = 'center';
    ctx.fillText('kepesspo.github.io/bottle-of-heroes', W/2, H-16);
    // Share / download
    canvas.toBlob(async (blob) => {
      const file = new File([blob], 'bottle-of-heroes.png', { type:'image/png' });
      if (navigator.share && navigator.canShare && navigator.canShare({ files:[file] })) {
        try { await navigator.share({ files:[file], title:'Bottle of Heroes — Végeredmény' }); return; } catch(e) {}
      }
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download='bottle-of-heroes.png'; a.click();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
    });
  };"""

new_sharecard = """  const [showShareSheet, setShowShareSheet] = React.useState(false);
  const shareCardRef = React.useRef(null);
  const [shareLoading, setShareLoading] = React.useState(false);
  const shareCard = () => setShowShareSheet(true);
  const doShare = async () => {
    if (!shareCardRef.current || !window.html2canvas) return;
    setShareLoading(true);
    try {
      const canvas = await window.html2canvas(shareCardRef.current, {
        scale: 2, useCORS: true, backgroundColor: null, logging: false,
      });
      canvas.toBlob(async (blob) => {
        setShareLoading(false);
        const file = new File([blob], 'bottle-of-heroes.png', { type:'image/png' });
        if (navigator.share && navigator.canShare && navigator.canShare({ files:[file] })) {
          try { await navigator.share({ files:[file], title:'Bottle of Heroes — Végeredmény' }); return; } catch(e) {}
        }
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a'); a.href=url; a.download='bottle-of-heroes.png'; a.click();
        setTimeout(()=>URL.revokeObjectURL(url),1000);
      });
    } catch(e) { setShareLoading(false); }
  };"""
assert old_sharecard in html, "FAIL: shareCard fn"
html = html.replace(old_sharecard, new_sharecard, 1)

# ── 3. Share sheet overlay + share card div hozzáadása az EndScreen return-jébe
old_endscreen_return = "    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>\n      <Confetti originY={confettiOriginY} />\n      <AppBar title=\"Játék vége! 🎉\" />"
new_endscreen_return = """    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      {/* Share card sheet */}
      {showShareSheet && (
        <SheetOverlay onClose={() => setShowShareSheet(false)}>
          <div style={{ padding:'0 16px 20px' }}>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, textAlign:'center', marginBottom:14 }}>Megosztás</div>
            {/* The actual card — this is what gets captured */}
            <div ref={shareCardRef} style={{ background:T.bg, borderRadius:20, overflow:'hidden', padding:'16px 12px 12px' }}>
              {/* Header */}
              <div style={{ height:5, background:`linear-gradient(90deg,${T.mint},${T.coral})`, borderRadius:4, marginBottom:14 }} />
              <div style={{ textAlign:'center', marginBottom:14 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:20, color:T.ink }}>🍺 Bottle of Heroes</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{sorted.length} játékos · {lastRound || '?'} kör</div>
              </div>
              {/* Podium */}
              {(() => {
                const pod = sorted.slice(0,3);
                const order = pod.length>=3?[pod[1],pod[0],pod[2]]:pod.length===2?[pod[1],pod[0]]:[pod[0]];
                const heights=[64,96,48], ranks=[2,1,3], tones=['#C0C0C0',T.yellow||'#F4C95A','#CD7F32'];
                return (
                  <div style={{ display:'flex', alignItems:'flex-end', justifyContent:'center', gap:6, marginBottom:14 }}>
                    {order.map((p,i) => {
                      const h=heights[i]??40, tone=tones[i]??'#aaa', rank=ranks[i]??(i+1), isFirst=rank===1;
                      return (
                        <div key={p.id} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:0, flex:1 }}>
                          {isFirst?<div style={{ fontSize:18, lineHeight:1, marginBottom:2 }}>👑</div>:<div style={{ height:22 }} />}
                          <div style={{ width:isFirst?52:40, height:isFirst?52:40, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:isFirst?20:15, color:'#fff', boxShadow:`0 0 0 2.5px ${tone}`, marginBottom:4 }}>{p.name.charAt(0).toUpperCase()}</div>
                          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap', maxWidth:80, textAlign:'center', marginBottom:4 }}>{p.name}</div>
                          <div style={{ width:'100%', height:h, background:tone, borderRadius:'8px 8px 0 0', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:1 }}>
                            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:isFirst?22:18, color:'#fff' }}>{rank}</div>
                            <div style={{ fontFamily:T.font, fontSize:10, fontWeight:700, color:'rgba(255,255,255,0.85)' }}>{p.points}pt</div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                );
              })()}
              {/* Leaderboard */}
              <div style={{ display:'flex', flexDirection:'column', gap:6, marginBottom:10 }}>
                {sorted.map((p,i) => (
                  <div key={p.id} style={{ display:'flex', alignItems:'center', gap:10, background:T.surface, borderRadius:12, padding:'8px 12px' }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.inkMute, width:18, textAlign:'center' }}>{i===0?'🥇':i===1?'🥈':i===2?'🥉':`${i+1}`}</div>
                    <div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>
                    <div style={{ flex:1, fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                    <div style={{ display:'flex', gap:8 }}>
                      <span style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.mint }}>⭐{p.points}</span>
                      <span style={{ fontFamily:T.font, fontSize:12, fontWeight:700, color:T.coral }}>🍺{p.drinks}</span>
                    </div>
                  </div>
                ))}
              </div>
              {/* Footer */}
              <div style={{ textAlign:'center' }}>
                <div style={{ fontFamily:T.font, fontSize:10, color:T.inkMute }}>kepesspo.github.io/bottle-of-heroes</div>
              </div>
            </div>
            {/* Action button */}
            <button onClick={doShare} disabled={shareLoading} style={{ width:'100%', marginTop:14, padding:'16px 0', borderRadius:999, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:800, fontSize:16, cursor:'pointer', boxShadow:`0 4px 16px ${T.mint}55`, opacity: shareLoading ? 0.7 : 1 }}>
              {shareLoading ? 'Generálás…' : '📤 Megosztás / Letöltés'}
            </button>
          </div>
        </SheetOverlay>
      )}
      <Confetti originY={confettiOriginY} />
      <AppBar title="Játék vége! 🎉" />"""
assert old_endscreen_return in html, "FAIL: EndScreen return"
html = html.replace(old_endscreen_return, new_endscreen_return, 1)

html = html.replace("const APP_VERSION = 'v9.313';", "const APP_VERSION = 'v9.314';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.314 — Share kártya EndScreen stílusban (html2canvas + sheet preview)")
