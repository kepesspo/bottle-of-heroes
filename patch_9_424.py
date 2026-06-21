#!/usr/bin/env python3
"""v9.424 — BeerPong tábló: canvas fix + pontosabb layout"""

NEW_TABLEAU = r"""function BeerPongTableau({ champion, players, tournamentName, tournament, seRounds, rrMatches, tsGroups, drinkMap, onClose }) {
END = '\nfunction BeerPongObserverView('
assert START in src
assert END in src
s = src.index(START)
e = src.index(END)
src = src[:s] + NEW_TABLEAU + '\n' + src[e:]

assert "const APP_VERSION = 'v9.423';" in src
src = src.replace("const APP_VERSION = 'v9.423';", "const APP_VERSION = 'v9.424';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print('v9.424 OK')

NEW_TABLEAU = r"""function BeerPongTableau({ champion, players, tournamentName, tournament, seRounds, rrMatches, tsGroups, drinkMap, onClose }) {
  const F = "'Nunito','Inter',sans-serif";
  const GOLD='#F59E0B', SILVER='#94A3B8', BRONZE='#CD7C3A';
  const BG='#0F1A30', SURF='#1A2B4B', SURF2='#243555';
  const canvasRef = React.useRef(null);
  const [imgUrl, setImgUrl] = React.useState(null);

  const allMatches = React.useMemo(() => {
    const ms = [];
    if (tournament === 'se') {
      (seRounds||[]).forEach((rnd,ri) => rnd.forEach(m => { if(m.winner||m.draw) ms.push({...m,label:'Kör '+(ri+1)}); }));
    } else if (tournament === 'rr') {
      (rrMatches||[]).forEach(m => { if(m.winner||m.draw) ms.push({...m,label:'Körmérkőző'}); });
    } else {
      (tsGroups||[]).forEach(g => (g.matches||[]).forEach(m => { if(m.winner||m.draw) ms.push({...m,label:g.label||''}); }));
    }
    return ms;
  }, [tournament, seRounds, rrMatches, tsGroups]);

  const standings = React.useMemo(() => {
    const st = {};
    players.forEach(p => { st[p.id]={player:p,W:0,D:0,L:0,Pp:0,Pm:0}; });
    allMatches.forEach(m => {
      const [s1,s2] = (m.score||'0-0').split('-').map(Number);
      if(st[m.p1?.id]){st[m.p1.id].Pp+=s1;st[m.p1.id].Pm+=s2;}
      if(st[m.p2?.id]){st[m.p2.id].Pp+=s2;st[m.p2.id].Pm+=s1;}
      if(m.draw){if(st[m.p1?.id])st[m.p1.id].D++;if(st[m.p2?.id])st[m.p2.id].D++;}
      else if(m.winner){
        const lid=m.p1?.id===m.winner.id?m.p2?.id:m.p1?.id;
        if(st[m.winner.id])st[m.winner.id].W++;
        if(st[lid])st[lid].L++;
      }
    });
    const arr=Object.values(st).sort((a,b)=>b.W-a.W||(b.Pp-b.Pm)-(a.Pp-a.Pm));
    const ci=arr.findIndex(x=>x.player.id===champion?.id);
    if(ci>0){const c=arr.splice(ci,1);arr.unshift(c[0]);}
    return arr;
  }, [players, allMatches, champion]);

  React.useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    setTimeout(() => {
      try { drawTableau(canvas); } catch(e){ console.error('Tábló hiba:',e); }
    }, 50);
  }, []);

  function drawTableau(canvas) {
    const W=1400, H=990;
    canvas.width=W; canvas.height=H;
    const ctx=canvas.getContext('2d');

    function rrect(x,y,w,h,r){
      ctx.beginPath();
      ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.arcTo(x+w,y,x+w,y+r,r);
      ctx.lineTo(x+w,y+h-r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
      ctx.lineTo(x+r,y+h); ctx.arcTo(x,y+h,x,y+h-r,r);
      ctx.lineTo(x,y+r); ctx.arcTo(x,y,x+r,y,r);
      ctx.closePath();
    }

    // Background
    ctx.fillStyle=BG; ctx.fillRect(0,0,W,H);

    // ── HEADER ──────────────────────────────────────────────────────────
    ctx.fillStyle=SURF; rrect(0,0,W,70,0); ctx.fill();
    // Left: logo
    ctx.fillStyle=GOLD; ctx.font='bold 20px '+F; ctx.textAlign='left';
    ctx.fillText('🏓 Bottle of Heroes',20,42);
    // Center: tournament name
    ctx.fillStyle='#fff'; ctx.font='bold 22px '+F; ctx.textAlign='center';
    ctx.fillText((tournamentName||'Beer Pong Torna').toUpperCase(), W/2, 30);
    // Center sub: date + counts
    const now=new Date(); const dateStr=now.toLocaleDateString('hu-HU',{year:'numeric',month:'long',day:'numeric'});
    ctx.fillStyle='#94A3B8'; ctx.font='13px '+F;
    ctx.fillText(dateStr+' · '+players.length+' játékos · '+allMatches.length+' meccs', W/2, 54);
    // Right: app version
    ctx.fillStyle='#94A3B8'; ctx.font='12px '+F; ctx.textAlign='right';
    ctx.fillText('Bottle of Heroes', W-16, 42);

    const TOP=82, PAD=14;

    // ── LEFT COLUMN: groups + matches ───────────────────────────────────
    const LW=370;
    let cy=TOP;

    const drawGroupTable = (g) => {
      // Header
      ctx.fillStyle=GOLD+'33'; rrect(PAD,cy,LW,26,7); ctx.fill();
      ctx.fillStyle=GOLD; ctx.font='bold 13px '+F; ctx.textAlign='left';
      ctx.fillText(g.label||'Csoport', PAD+10, cy+18);
      cy+=30;
      // Column headers
      const names=['J','Gy','D','V','P+','P-'];
      const nameW=130, colW=(LW-nameW)/6;
      ctx.fillStyle='#94A3B8'; ctx.font='bold 11px '+F;
      names.forEach((n,i)=>{ ctx.textAlign='center'; ctx.fillText(n,PAD+nameW+i*colW+colW/2,cy+12); });
      cy+=16;
      // Rows
      const st={};
      (g.players||[]).forEach(p=>{st[p.id]={p,J:0,Gy:0,D:0,V:0,Pp:0,Pm:0};});
      (g.matches||[]).forEach(m=>{
        if(!m.winner&&!m.draw)return;
        const[s1,s2]=(m.score||'0-0').split('-').map(Number);
        if(st[m.p1?.id]){st[m.p1.id].J++;st[m.p1.id].Pp+=s1;st[m.p1.id].Pm+=s2;}
        if(st[m.p2?.id]){st[m.p2.id].J++;st[m.p2.id].Pp+=s2;st[m.p2.id].Pm+=s1;}
        if(m.draw){if(st[m.p1?.id])st[m.p1.id].D++;if(st[m.p2?.id])st[m.p2.id].D++;}
        else if(m.winner){
          const lid=m.p1?.id===m.winner.id?m.p2?.id:m.p1?.id;
          if(st[m.winner.id])st[m.winner.id].Gy++;
          if(st[lid])st[lid].V++;
        }
      });
      const rows=Object.values(st).sort((a,b)=>b.Gy-a.Gy||(b.Pp-b.Pm)-(a.Pp-a.Pm));
      rows.forEach((r,ri)=>{
        const ry=cy+ri*20;
        if(ri%2===0){ctx.fillStyle='rgba(255,255,255,.05)';rrect(PAD,ry,LW,20,4);ctx.fill();}
        ctx.fillStyle='#fff'; ctx.font='13px '+F; ctx.textAlign='left';
        ctx.fillText(r.p.name, PAD+8, ry+14);
        [r.J,r.Gy,r.D,r.V,r.Pp,r.Pm].forEach((v,i)=>{
          ctx.textAlign='center'; ctx.fillText(v,PAD+nameW+i*colW+colW/2,ry+14);
        });
      });
      cy+=rows.length*20+10;
    };

    if(tsGroups&&tsGroups.length>0){
      tsGroups.forEach(g=>drawGroupTable(g));
      cy+=8;
    }

    // Match results
    ctx.fillStyle=GOLD; ctx.font='bold 12px '+F; ctx.textAlign='left';
    ctx.fillText('MECCSEREDMÉNYEK', PAD, cy+13); cy+=20;
    const maxM=Math.floor((H-cy-16)/20);
    allMatches.slice(0,maxM).forEach((m,i)=>{
      const ry=cy+i*20;
      if(i%2===0){ctx.fillStyle='rgba(255,255,255,.04)';rrect(PAD,ry,LW,20,4);ctx.fill();}
      const p1n=m.p1?.name||'?', p2n=m.p2?.name||'?';
      const sc=m.score||''; const wid=m.winner?.id;
      ctx.fillStyle=wid===m.p1?.id?GOLD:'#fff'; ctx.font=(wid===m.p1?.id?'bold ':'')+'12px '+F; ctx.textAlign='left';
      ctx.fillText(p1n, PAD+6, ry+14);
      ctx.fillStyle='#94A3B8'; ctx.font='12px '+F; ctx.textAlign='center';
      ctx.fillText(sc||'vs', PAD+LW/2, ry+14);
      ctx.fillStyle=wid===m.p2?.id?GOLD:'#fff'; ctx.font=(wid===m.p2?.id?'bold ':'')+'12px '+F; ctx.textAlign='right';
      ctx.fillText(p2n, PAD+LW-6, ry+14);
    });

    // ── RIGHT COLUMN ─────────────────────────────────────────────────────
    const RX=PAD+LW+16, RW=W-RX-PAD;
    const BRACKET_H=Math.floor(H*0.56);

    // Bracket box
    ctx.fillStyle=SURF; rrect(RX,TOP,RW,BRACKET_H,14); ctx.fill();
    ctx.fillStyle=GOLD; ctx.font='bold 13px '+F; ctx.textAlign='left';
    ctx.fillText('ÁGRAJZ', RX+14, TOP+20);

    // Draw SE bracket
    const drawSERounds = (rounds, bx, by, bw, bh) => {
      if(!rounds||!rounds.length)return;
      const nr=rounds.length;
      const cw=bw/nr;
      rounds.forEach((rnd,ri)=>{
        const nm=rnd.length;
        const sh=bh/nm;
        rnd.forEach((m,mi)=>{
          const mx=bx+ri*cw+4, my=by+mi*sh+4;
          const mw=cw-8, mh=sh-8;
          // Card bg
          ctx.fillStyle=m.winner?'#1A3A5C':'#243555'; rrect(mx,my,mw,mh,8); ctx.fill();
          // Label
          let lbl='';
          if(ri===nr-1) lbl='DÖNTŐ';
          else if(nr>1&&ri===nr-2&&nm===1) lbl='ELŐDÖNTŐ';
          else lbl='Kör '+(ri+1);
          ctx.fillStyle='#94A3B8'; ctx.font='10px '+F; ctx.textAlign='left';
          ctx.fillText(lbl, mx+6, my+13);
          // P1
          const p1w=m.winner?.id===m.p1?.id;
          ctx.fillStyle=p1w?GOLD:'#fff'; ctx.font=(p1w?'bold ':'')+'13px '+F;
          ctx.fillText(m.p1?.name||'TBD', mx+6, my+mh/2-2);
          const sc=m.score||''; const[s1,s2]=sc.split('-');
          if(s1){ctx.fillStyle='#94A3B8';ctx.font='11px '+F;ctx.textAlign='right';ctx.fillText(s1,mx+mw-6,my+mh/2-2);}
          // Divider
          ctx.strokeStyle='#2D4A6B';ctx.lineWidth=1;
          ctx.beginPath();ctx.moveTo(mx+4,my+mh/2+4);ctx.lineTo(mx+mw-4,my+mh/2+4);ctx.stroke();
          // P2
          const p2w=m.winner?.id===m.p2?.id;
          ctx.fillStyle=p2w?GOLD:'#fff'; ctx.font=(p2w?'bold ':'')+'13px '+F; ctx.textAlign='left';
          ctx.fillText(m.p2?.name||'TBD', mx+6, my+mh-8);
          if(s2){ctx.fillStyle='#94A3B8';ctx.font='11px '+F;ctx.textAlign='right';ctx.fillText(s2,mx+mw-6,my+mh-8);}
          // Connector
          if(ri<nr-1){
            const nr2=rounds[ri+1];
            if(nr2){
              const nm2=nr2.length, sh2=bh/nm2, mi2=Math.floor(mi/2);
              const ty=by+mi2*sh2+4+sh2/2;
              ctx.strokeStyle='#2D4A6B';ctx.lineWidth=1.5;
              ctx.beginPath();
              ctx.moveTo(mx+mw,my+mh/2);
              ctx.lineTo(mx+mw+cw/2,my+mh/2);
              ctx.lineTo(mx+mw+cw/2,ty);
              ctx.lineTo(mx+cw,ty);
              ctx.stroke();
            }
          }
        });
      });
    };

    if(tournament==='se'){
      drawSERounds(seRounds, RX+8, TOP+28, RW-16, BRACKET_H-36);
    } else if(tournament&&tournament.startsWith('grp_')&&seRounds&&seRounds.length>0){
      drawSERounds(seRounds, RX+8, TOP+28, RW-16, BRACKET_H-36);
    } else {
      ctx.fillStyle='#94A3B8';ctx.font='14px '+F;ctx.textAlign='center';
      ctx.fillText('Körmérkőzéses rendszer', RX+RW/2, TOP+BRACKET_H/2);
    }

    // ── DOBOGÓ (bottom right) ─────────────────────────────────────────────
    const PY=TOP+BRACKET_H+12, PH=H-PY-PAD;
    ctx.fillStyle=SURF; rrect(RX,PY,RW,PH,14); ctx.fill();
    ctx.fillStyle=GOLD; ctx.font='bold 13px '+F; ctx.textAlign='left';
    ctx.fillText('DOBOGÓ', RX+14, PY+20);

    // Podium visual: 2nd left, 1st center, 3rd right
    const p1=standings[0], p2=standings[1], p3=standings[2];
    const podOrder=[p2,p1,p3];
    const podColors=[SILVER,GOLD,BRONZE];
    const podH=[55,80,40];
    const podLabels=['2.','1.','3.'];
    const podW=Math.min(110,(RW*0.4)/3);
    const podStartX=RX+RW*0.08;
    const baseY=PY+PH-16;

    podOrder.forEach((p,i)=>{
      if(!p)return;
      const bx=podStartX+i*(podW+14);
      // Bar
      ctx.fillStyle=podColors[i]+'44'; rrect(bx,baseY-podH[i],podW,podH[i],6); ctx.fill();
      ctx.fillStyle=podColors[i]; ctx.font='bold 14px '+F; ctx.textAlign='center';
      ctx.fillText(podLabels[i], bx+podW/2, baseY-podH[i]+18);
      // Avatar
      ctx.fillStyle=p.player?.color||p.color||'#6366F1';
      ctx.beginPath();ctx.arc(bx+podW/2,baseY-podH[i]-24,22,0,Math.PI*2);ctx.fill();
      ctx.fillStyle='#fff';ctx.font='bold 18px '+F;
      ctx.fillText((p.player?.name||p.name||'').charAt(0).toUpperCase(),bx+podW/2,baseY-podH[i]-17);
      ctx.fillStyle='#fff';ctx.font='12px '+F;
      ctx.fillText(p.player?.name||p.name||'',bx+podW/2,baseY-podH[i]+36);
      const wl=p.W+'/'+p.L;
      ctx.fillStyle='#94A3B8';ctx.font='11px '+F;
      ctx.fillText(wl+' ('+p.Pp+'-'+p.Pm+')',bx+podW/2,baseY-podH[i]+50);
    });

    // 4th-6th place list
    const listX=RX+RW*0.55, listY=PY+32;
    standings.slice(3).forEach((s,i)=>{
      ctx.fillStyle='#94A3B8'; ctx.font='bold 12px '+F; ctx.textAlign='left';
      ctx.fillText((i+4)+'. '+( s.player?.name||s.name||'?')+' — '+s.W+'gy/'+s.L+'v', listX, listY+i*22);
    });

    setImgUrl(canvas.toDataURL('image/png'));
  }

  const handleShare = () => {
    if(!imgUrl)return;
    const a=document.createElement('a'); a.href=imgUrl; a.download='beerpong_tabló.png'; a.click();
    if(navigator.share){
      fetch(imgUrl).then(r=>r.blob()).then(blob=>{
        const f=new File([blob],'beerpong_tabló.png',{type:'image/png'});
        if(navigator.canShare&&navigator.canShare({files:[f]}))
          navigator.share({files:[f],title:'Beer Pong Tábló'}).catch(()=>{});
      });
    }
  };

  return (
    <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,.88)',zIndex:9999,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:12,overflowY:'auto'}}>
      <canvas ref={canvasRef} style={{display:'none'}} />
      <div style={{background:'#1A2B4B',borderRadius:20,padding:14,width:'100%',maxWidth:500,display:'flex',flexDirection:'column',gap:10}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <span style={{fontFamily:"'Nunito',sans-serif",fontWeight:900,fontSize:17,color:'#fff'}}>📊 Tábló</span>
          <button onClick={onClose} style={{background:'none',border:'none',fontSize:22,cursor:'pointer',color:'#94A3B8',lineHeight:1}}>✕</button>
        </div>
        {imgUrl ? (
          <>
            <img src={imgUrl} style={{width:'100%',borderRadius:10,border:'1px solid #243555'}} alt="Tábló" />
            <button onClick={handleShare} style={{padding:'12px',borderRadius:13,border:'none',background:'#F59E0B',color:'#fff',fontFamily:"'Nunito',sans-serif",fontWeight:900,fontSize:15,cursor:'pointer'}}>
              ⬇️ Letöltés / Megosztás
            </button>
          </>
        ) : (
          <div style={{color:'#94A3B8',textAlign:'center',padding:40,fontFamily:"'Nunito',sans-serif"}}>
            Tábló generálása...
          </div>
        )}
      </div>
    </div>
  );
}
"""
