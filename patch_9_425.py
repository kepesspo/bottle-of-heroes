#!/usr/bin/env python3
"""v9.425 — BeerPong: tábló score fix (obj helyett {p1,p2}), scroll fix"""

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# 1. Tábló score kezelés javítása: (m.score||'0-0').split('-') → helper
# A BeerPongTableau-ban replace minden score parsing-ot
OLD_TABLEAU_START = 'function BeerPongTableau({'
END_MARKER = '\nfunction BeerPongObserverView('
assert OLD_TABLEAU_START in src
assert END_MARKER in src
t_start = src.index(OLD_TABLEAU_START)
t_end = src.index(END_MARKER)

NEW_TABLEAU = r"""function BeerPongTableau({ champion, players, tournamentName, tournament, seRounds, rrMatches, tsGroups, drinkMap, onClose }) {
  const F = "'Nunito','Inter',sans-serif";
  const GOLD='#F59E0B', SILVER='#94A3B8', BRONZE='#CD7C3A';
  const BG='#0F1A30', SURF='#1A2B4B';
  const canvasRef = React.useRef(null);
  const [imgUrl, setImgUrl] = React.useState(null);

  // score lehet {p1,p2} objektum vagy "N-N" string
  const getScore = (sc) => {
    if (!sc) return [0,0];
    if (typeof sc === 'object') return [sc.p1||0, sc.p2||0];
    const parts = String(sc).split('-');
    return [parseInt(parts[0])||0, parseInt(parts[1])||0];
  };
  const scoreStr = (sc) => { const [a,b]=getScore(sc); return a+'-'+b; };

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
      const [s1,s2] = getScore(m.score);
      if(st[m.p1?.id]){st[m.p1.id].Pp+=s1;st[m.p1.id].Pm+=s2;}
      if(st[m.p2?.id]){st[m.p2.id].Pp+=s2;st[m.p2.id].Pm+=s1;}
      if(m.draw){if(st[m.p1?.id])st[m.p1.id].D++;if(st[m.p2?.id])st[m.p2.id].D++;}
      else if(m.winner){
        const lid=m.p1?.id===m.winner.id?m.p2?.id:m.p1?.id;
        if(st[m.winner.id])st[m.winner.id].W++;
        if(lid&&st[lid])st[lid].L++;
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
      try {
        const W=1400, H=990;
        canvas.width=W; canvas.height=H;
        const ctx=canvas.getContext('2d');

        function rrect(x,y,w,h,r){
          if(w<=0||h<=0)return;
          r=Math.min(r,w/2,h/2);
          ctx.beginPath();
          ctx.moveTo(x+r,y); ctx.lineTo(x+w-r,y); ctx.arcTo(x+w,y,x+w,y+r,r);
          ctx.lineTo(x+w,y+h-r); ctx.arcTo(x+w,y+h,x+w-r,y+h,r);
          ctx.lineTo(x+r,y+h); ctx.arcTo(x,y+h,x,y+h-r,r);
          ctx.lineTo(x,y+r); ctx.arcTo(x,y,x+r,y,r);
          ctx.closePath();
        }

        ctx.fillStyle=BG; ctx.fillRect(0,0,W,H);

        // Header
        ctx.fillStyle=SURF; ctx.fillRect(0,0,W,70);
        ctx.fillStyle=GOLD; ctx.font='bold 20px '+F; ctx.textAlign='left';
        ctx.fillText('Bottle of Heroes', 20, 44);
        ctx.fillStyle='#fff'; ctx.font='bold 22px '+F; ctx.textAlign='center';
        ctx.fillText((tournamentName||'Beer Pong Torna').toUpperCase(), W/2, 30);
        const now=new Date();
        const dateStr=now.toLocaleDateString('hu-HU',{year:'numeric',month:'long',day:'numeric'});
        ctx.fillStyle='#94A3B8'; ctx.font='13px '+F;
        ctx.fillText(dateStr+' · '+players.length+' játékos · '+allMatches.length+' meccs', W/2, 54);

        const TOP=82, PAD=14, LW=370;
        let cy=TOP;

        // Csoport táblák
        if(tsGroups&&tsGroups.length>0){
          tsGroups.forEach(g=>{
            ctx.fillStyle=GOLD+'33'; rrect(PAD,cy,LW,26,7); ctx.fill();
            ctx.fillStyle=GOLD; ctx.font='bold 13px '+F; ctx.textAlign='left';
            ctx.fillText(g.label||'Csoport', PAD+10, cy+18); cy+=30;
            const nameW=130, cols=['J','Gy','D','V','P+','P-'], cw=(LW-nameW)/6;
            ctx.fillStyle='#94A3B8'; ctx.font='bold 11px '+F;
            cols.forEach((n,i)=>{ ctx.textAlign='center'; ctx.fillText(n,PAD+nameW+i*cw+cw/2,cy+12); });
            cy+=16;
            const gst={};
            (g.players||[]).forEach(p=>{gst[p.id]={p,J:0,Gy:0,D:0,V:0,Pp:0,Pm:0};});
            (g.matches||[]).forEach(m=>{
              if(!m.winner&&!m.draw)return;
              const[s1,s2]=getScore(m.score);
              if(gst[m.p1?.id]){gst[m.p1.id].J++;gst[m.p1.id].Pp+=s1;gst[m.p1.id].Pm+=s2;}
              if(gst[m.p2?.id]){gst[m.p2.id].J++;gst[m.p2.id].Pp+=s2;gst[m.p2.id].Pm+=s1;}
              if(m.draw){if(gst[m.p1?.id])gst[m.p1.id].D++;if(gst[m.p2?.id])gst[m.p2.id].D++;}
              else if(m.winner){const lid=m.p1?.id===m.winner.id?m.p2?.id:m.p1?.id;if(gst[m.winner.id])gst[m.winner.id].Gy++;if(lid&&gst[lid])gst[lid].V++;}
            });
            const rows=Object.values(gst).sort((a,b)=>b.Gy-a.Gy||(b.Pp-b.Pm)-(a.Pp-a.Pm));
            rows.forEach((r,ri)=>{
              const ry=cy+ri*20;
              if(ri%2===0){ctx.fillStyle='rgba(255,255,255,.05)';rrect(PAD,ry,LW,20,4);ctx.fill();}
              ctx.fillStyle='#fff'; ctx.font='13px '+F; ctx.textAlign='left';
              ctx.fillText(r.p.name, PAD+8, ry+14);
              [r.J,r.Gy,r.D,r.V,r.Pp,r.Pm].forEach((v,i)=>{ctx.textAlign='center';ctx.fillText(v,PAD+nameW+i*cw+cw/2,ry+14);});
            });
            cy+=rows.length*20+10;
          });
          cy+=6;
        }

        // Meccsek listája
        ctx.fillStyle=GOLD; ctx.font='bold 12px '+F; ctx.textAlign='left';
        ctx.fillText('MECCSEREDMÉNYEK', PAD, cy+13); cy+=20;
        const maxM=Math.floor((H-cy-16)/20);
        allMatches.slice(0,maxM).forEach((m,i)=>{
          const ry=cy+i*20;
          if(i%2===0){ctx.fillStyle='rgba(255,255,255,.04)';rrect(PAD,ry,LW,20,4);ctx.fill();}
          const p1n=m.p1?.name||'?', p2n=m.p2?.name||'?';
          const sc=scoreStr(m.score); const wid=m.winner?.id;
          ctx.fillStyle=wid===m.p1?.id?GOLD:'#fff'; ctx.font=(wid===m.p1?.id?'bold ':'')+'12px '+F; ctx.textAlign='left';
          ctx.fillText(p1n, PAD+6, ry+14);
          ctx.fillStyle='#94A3B8'; ctx.font='12px '+F; ctx.textAlign='center';
          ctx.fillText(sc, PAD+LW/2, ry+14);
          ctx.fillStyle=wid===m.p2?.id?GOLD:'#fff'; ctx.font=(wid===m.p2?.id?'bold ':'')+'12px '+F; ctx.textAlign='right';
          ctx.fillText(p2n, PAD+LW-6, ry+14);
        });

        // Jobb oszlop
        const RX=PAD+LW+16, RW=W-RX-PAD;
        const BRACH=Math.floor(H*0.56);

        ctx.fillStyle=SURF; rrect(RX,TOP,RW,BRACH,14); ctx.fill();
        ctx.fillStyle=GOLD; ctx.font='bold 13px '+F; ctx.textAlign='left';
        ctx.fillText('AGRAJZ', RX+14, TOP+20);

        const drawSE=(rounds,bx,by,bw,bh)=>{
          if(!rounds||!rounds.length)return;
          const nr=rounds.length, cw=bw/nr;
          rounds.forEach((rnd,ri)=>{
            const nm=rnd.length, sh=bh/nm;
            rnd.forEach((m,mi)=>{
              const mx=bx+ri*cw+4, my=by+mi*sh+4, mw=cw-8, mh=sh-8;
              if(mw<10||mh<10)return;
              ctx.fillStyle=m.winner?'#1A3A5C':'#243555'; rrect(mx,my,mw,mh,8); ctx.fill();
              let lbl=ri===nr-1?'DONTO':nm===1?'ELODONTOS':'Kor '+(ri+1);
              ctx.fillStyle='#94A3B8'; ctx.font='10px '+F; ctx.textAlign='left';
              ctx.fillText(lbl, mx+6, my+13);
              const p1w=m.winner?.id===m.p1?.id;
              ctx.fillStyle=p1w?GOLD:'#fff'; ctx.font=(p1w?'bold ':'')+'13px '+F;
              ctx.fillText(m.p1?.name||'TBD', mx+6, my+mh/2-2);
              const [s1,s2]=getScore(m.score);
              if(m.score){ctx.fillStyle='#94A3B8';ctx.font='11px '+F;ctx.textAlign='right';ctx.fillText(s1,mx+mw-6,my+mh/2-2);}
              ctx.strokeStyle='#2D4A6B';ctx.lineWidth=1;
              ctx.beginPath();ctx.moveTo(mx+4,my+mh/2+4);ctx.lineTo(mx+mw-4,my+mh/2+4);ctx.stroke();
              const p2w=m.winner?.id===m.p2?.id;
              ctx.fillStyle=p2w?GOLD:'#fff'; ctx.font=(p2w?'bold ':'')+'13px '+F; ctx.textAlign='left';
              ctx.fillText(m.p2?.name||'TBD', mx+6, my+mh-8);
              if(m.score){ctx.fillStyle='#94A3B8';ctx.font='11px '+F;ctx.textAlign='right';ctx.fillText(s2,mx+mw-6,my+mh-8);}
              if(ri<nr-1){
                const rn2=rounds[ri+1]; if(!rn2)return;
                const nm2=rn2.length, sh2=bh/nm2, mi2=Math.floor(mi/2);
                const ty=by+mi2*sh2+4+(sh2-8)/2;
                ctx.strokeStyle='#2D4A6B';ctx.lineWidth=1.5;
                ctx.beginPath();ctx.moveTo(mx+mw,my+mh/2);ctx.lineTo(mx+mw+cw/2,my+mh/2);ctx.lineTo(mx+mw+cw/2,ty);ctx.lineTo(mx+cw,ty);ctx.stroke();
              }
            });
          });
        };

        if((tournament==='se'||tournament?.startsWith('grp_'))&&seRounds&&seRounds.length>0){
          drawSE(seRounds, RX+8, TOP+28, RW-16, BRACH-36);
        } else {
          ctx.fillStyle='#94A3B8';ctx.font='14px '+F;ctx.textAlign='center';
          ctx.fillText('Kormerkozes', RX+RW/2, TOP+BRACH/2);
        }

        // Dobogo
        const PY=TOP+BRACH+12, PH=H-PY-PAD;
        ctx.fillStyle=SURF; rrect(RX,PY,RW,PH,14); ctx.fill();
        ctx.fillStyle=GOLD; ctx.font='bold 13px '+F; ctx.textAlign='left';
        ctx.fillText('DOBOGO', RX+14, PY+20);

        const podData=[standings[1],standings[0],standings[2]];
        const podColors=[SILVER,GOLD,BRONZE], podH=[55,80,40], podLbls=['2.','1.','3.'];
        const podW=Math.min(110,(RW*0.42)/3);
        const podStartX=RX+RW*0.06, baseY=PY+PH-16;
        podData.forEach((s,i)=>{
          if(!s)return;
          const bx=podStartX+i*(podW+14);
          ctx.fillStyle=podColors[i]+'44'; rrect(bx,baseY-podH[i],podW,podH[i],6); ctx.fill();
          ctx.fillStyle=podColors[i]; ctx.font='bold 14px '+F; ctx.textAlign='center';
          ctx.fillText(podLbls[i], bx+podW/2, baseY-podH[i]+18);
          ctx.fillStyle=s.player?.color||'#6366F1';
          ctx.beginPath();ctx.arc(bx+podW/2,baseY-podH[i]-24,22,0,Math.PI*2);ctx.fill();
          ctx.fillStyle='#fff';ctx.font='bold 18px '+F;
          ctx.fillText((s.player?.name||'?').charAt(0).toUpperCase(),bx+podW/2,baseY-podH[i]-17);
          ctx.fillStyle='#fff';ctx.font='12px '+F;
          ctx.fillText(s.player?.name||'?',bx+podW/2,baseY-podH[i]+36);
          ctx.fillStyle='#94A3B8';ctx.font='11px '+F;
          ctx.fillText(s.W+'gy '+s.L+'v ('+s.Pp+'-'+s.Pm+')',bx+podW/2,baseY-podH[i]+50);
        });

        const listX=RX+RW*0.52, listY=PY+36;
        standings.slice(3).forEach((s,i)=>{
          ctx.fillStyle='#94A3B8'; ctx.font='bold 12px '+F; ctx.textAlign='left';
          ctx.fillText((i+4)+'. '+(s.player?.name||'?')+' - '+s.W+'gy/'+s.L+'v', listX, listY+i*22);
        });

        if(champion){
          ctx.fillStyle=GOLD+'22'; rrect(RX+14,PY+44,RW-28,32,10); ctx.fill();
          ctx.fillStyle=GOLD; ctx.font='bold 14px '+F; ctx.textAlign='center';
          ctx.fillText('Bajnok: '+champion.name+' - Beer Pong Bajnok!', RX+RW/2, PY+65);
        }

        setImgUrl(canvas.toDataURL('image/png'));
      } catch(err) { console.error('Canvas hiba:', err); }
    }, 80);
  }, []);

  const handleShare = () => {
    if(!imgUrl)return;
    const a=document.createElement('a'); a.href=imgUrl; a.download='beerpong_tabló.png'; a.click();
  };

  return (
    <div style={{position:'fixed',inset:0,background:'rgba(0,0,0,.88)',zIndex:9999,display:'flex',flexDirection:'column',alignItems:'center',justifyContent:'center',padding:12,overflowY:'auto'}}>
      <canvas ref={canvasRef} style={{display:'none'}} />
      <div style={{background:'#1A2B4B',borderRadius:20,padding:14,width:'100%',maxWidth:500,display:'flex',flexDirection:'column',gap:10}}>
        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
          <span style={{fontFamily:"'Nunito',sans-serif",fontWeight:900,fontSize:17,color:'#fff'}}>Tablo</span>
          <button onClick={onClose} style={{background:'none',border:'none',fontSize:22,cursor:'pointer',color:'#94A3B8',lineHeight:1}}>X</button>
        </div>
        {imgUrl ? (
          <>
            <img src={imgUrl} style={{width:'100%',borderRadius:10,border:'1px solid #243555'}} alt="Tabló" />
            <button onClick={handleShare} style={{padding:'12px',borderRadius:13,border:'none',background:'#F59E0B',color:'#fff',fontFamily:"'Nunito',sans-serif",fontWeight:900,fontSize:15,cursor:'pointer'}}>
              Letoltes / Megosztás
            </button>
          </>
        ) : (
          <div style={{color:'#94A3B8',textAlign:'center',padding:40,fontFamily:"'Nunito',sans-serif"}}>Tablo generalása...</div>
        )}
      </div>
    </div>
  );
}
"""

src = src[:t_start] + NEW_TABLEAU + '\n' + src[t_end:]
print('Tablo replaced')

# 2. BeerPong scroll fix: a PlayScreen scrollable div-jének overflow:hidden-jét fixáljuk
# A BeerPongGame maga kezeli a scroll-t onSetHideFooter-rel
# A GameContent wrapper div-et kell scrollolhatóvá tenni beerpong esetén
OLD_GAME_WRAP = "        <div style={{ display:'flex', flexDirection:'column' }}>\n          <GameContent key={currentGameId + gameIdx + '_' + gameRestartKey}"
NEW_GAME_WRAP = "        <div style={{ display:'flex', flexDirection:'column', flex: currentGameId==='beerpong' ? '1 1 0' : 'unset', minHeight: currentGameId==='beerpong' ? 0 : 'unset' }}>\n          <GameContent key={currentGameId + gameIdx + '_' + gameRestartKey}"
assert OLD_GAME_WRAP in src, 'game wrap not found'
src = src.replace(OLD_GAME_WRAP, NEW_GAME_WRAP, 1)
print('Game wrap updated')

# Fix scrollable container for beerpong
OLD_SCROLL = "      <div style={{ flex:'1 1 0', minHeight:0, overflowY:'scroll', WebkitOverflowScrolling:'touch', background:'transparent', overflow:'hidden' }}>"
NEW_SCROLL = "      <div style={{ flex:'1 1 0', minHeight:0, overflowY: currentGameId==='beerpong' ? 'auto' : 'scroll', WebkitOverflowScrolling:'touch', background:'transparent', overflow: currentGameId==='beerpong' ? 'auto' : 'hidden' }}>"
assert OLD_SCROLL in src, 'scroll div not found'
src = src.replace(OLD_SCROLL, NEW_SCROLL, 1)
print('Scroll div updated')

# 3. Version bump
assert "const APP_VERSION = 'v9.424';" in src
src = src.replace("const APP_VERSION = 'v9.424';", "const APP_VERSION = 'v9.425';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print('v9.425 OK')
