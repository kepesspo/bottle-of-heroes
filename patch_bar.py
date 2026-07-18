#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Beépített bár: Koktél + Shot fül, recept arányokkal, "Mi van itthon?" szűrő,
# és profil-alapú csillagos értékelés (Firestore: config/drinkRatings).
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

BAR = r'''function BarScreen({ go }) {
  const [tab, setTab] = React.useState('cocktail');
  const [avail, setAvail] = React.useState(() => new Set());
  const [profiles, setProfiles] = React.useState([]);
  const [rater, setRater] = React.useState(() => { try { return localStorage.getItem('boh_bar_rater') || null; } catch(e) { return null; } });
  const [ratings, setRatings] = React.useState({});
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(ps => setProfiles(ps || [])).catch(() => {});
    if (!db) return;
    const unsub = db.collection('config').doc('drinkRatings').onSnapshot(d => setRatings((d && d.exists && d.data()) || {}), () => {});
    return () => { try { unsub(); } catch(e) {} };
  }, []);

  const CHIPS = [
    ['vodka','Vodka','🍶'],['rum','Rum','🥃'],['gin','Gin','🍸'],['tequila','Tequila','🌵'],
    ['whisky','Whisky','🥃'],['jager','Jäger','🦌'],['aperol','Aperol','🍹'],['pezsgo','Pezsgő','🍾'],
    ['sor','Sör','🍺'],['bor','Bor','🍷'],['kola','Kóla','🥤'],['narancsle','Narancslé','🍊'],
    ['tonik','Tonik','💧'],['energiaital','Energiaital','⚡'],['szoda','Szóda','🫧'],['citrom','Citrom','🍋'],
  ];
  const DRINKS = [
    { id:'vodkanarancs', type:'cocktail', name:'Vodka-narancs', emoji:'🍊', str:2, need:['vodka','narancsle'], ing:['4 cl vodka','1,5 dl narancslé','jég'], step:'Jeges pohárban összeöntöd, megkevered.' },
    { id:'cubalibre', type:'cocktail', name:'Cuba Libre', emoji:'🥤', str:2, need:['rum','kola'], ing:['4 cl rum','1 dl kóla','lime','jég'], step:'Rum jégre, kólával fel, lime beléfacsarva.' },
    { id:'gintonik', type:'cocktail', name:'Gin-tonik', emoji:'🍸', str:2, need:['gin','tonik'], ing:['4 cl gin','1,5 dl tonik','lime','jég'], step:'Gin jégre, tonikkal feltöltöd, lime karika.' },
    { id:'vodkaenergia', type:'cocktail', name:'Vodka-energia', emoji:'⚡', str:2, need:['vodka','energiaital'], ing:['4 cl vodka','2 dl energiaital','jég'], step:'Jégre öntöd össze. Óvatosan!' },
    { id:'tequilasunrise', type:'cocktail', name:'Tequila Sunrise', emoji:'🌅', str:2, need:['tequila','narancsle'], ing:['4 cl tequila','1,5 dl narancslé','1 cl grenadine'], step:'Tequila + narancs, a grenadine a tetejéről lecsorog.' },
    { id:'mojito', type:'cocktail', name:'Mojito', emoji:'🌿', str:2, need:['rum','szoda'], ing:['5 cl rum','fél lime','2 tk cukor','menta','szóda'], step:'Menta+lime+cukor összetöröd, rum, jég, szódával fel.' },
    { id:'mimosa', type:'cocktail', name:'Mimosa', emoji:'🥂', str:1, need:['pezsgo','narancsle'], ing:['fél pohár pezsgő','fél pohár narancslé'], step:'Hideg pezsgő + friss narancslé, fele-fele.' },
    { id:'aperol', type:'cocktail', name:'Aperol Spritz', emoji:'🍹', str:1, need:['aperol','pezsgo','szoda'], ing:['6 cl Aperol','9 cl pezsgő','egy löket szóda','narancs'], step:'3 rész pezsgő – 2 rész Aperol – 1 rész szóda, sok jég.' },
    { id:'whiskykola', type:'cocktail', name:'Whisky-kóla', emoji:'🥃', str:2, need:['whisky','kola'], ing:['4 cl whisky','1,5 dl kóla','jég'], step:'Whisky jégre, kólával feltöltöd.' },
    { id:'froccs', type:'cocktail', name:'Fröccs', emoji:'🍷', str:1, need:['bor','szoda'], ing:['2 dl bor','1 dl szóda'], step:'Hideg bor + szóda. A nagyfröccs 2 dl bor, 1 dl szóda.' },
    { id:'radler', type:'cocktail', name:'Radler', emoji:'🍺', str:1, need:['sor','citrom'], ing:['fél sör','fél limonádé / citromos víz'], step:'Fele sör, fele limonádé — könnyű és szomjoltó.' },
    { id:'longisland', type:'cocktail', name:'Long Island', emoji:'🧨', str:3, need:['vodka','rum','gin','tequila','kola'], ing:['2 cl vodka','2 cl rum','2 cl gin','2 cl tequila','2 cl triple sec','citrom','kóla'], step:'Minden jégre, kólával csak színezed. Erős!' },
    { id:'vodkalime', type:'cocktail', name:'Vodka-lime szóda', emoji:'🍋', str:2, need:['vodka','szoda'], ing:['4 cl vodka','fél lime','szóda','jég'], step:'Vodka jégre, lime, szódával fel — friss és pörgős.' },
    { id:'kamikaze', type:'shot', name:'Kamikaze', emoji:'🎌', str:3, need:['vodka'], ing:['2 cl vodka','2 cl triple sec','2 cl lime'], step:'Jéggel felrázod, felesbe töltöd, egyben.' },
    { id:'jagerbomb', type:'shot', name:'Jägerbomb', emoji:'🦌', str:3, need:['jager','energiaital'], ing:['1 feles Jägermeister','1 pohár energiaital'], step:'A felest az energiaitalba ejtve — egyben lehúzod.' },
    { id:'boilermaker', type:'shot', name:'Sör + feles', emoji:'💣', str:3, need:['sor','vodka'], ing:['1 korsó sör','1 feles vodka v. whisky'], step:'A felest a sörbe ejtve — és fenékig!' },
    { id:'tequilashot', type:'shot', name:'Tequila (feles)', emoji:'🌵', str:3, need:['tequila','citrom'], ing:['4 cl tequila','só','citrom'], step:'Só a kézfejre, tequila egyben, citrom utána.' },
    { id:'b52', type:'shot', name:'B52', emoji:'🔥', str:2, need:[], ing:['2 cl kávélikőr','2 cl Baileys','2 cl narancslikőr'], step:'Rétegezve töltöd (nehéztől a könnyűig). Meggyújtható!' },
    { id:'palinka', type:'shot', name:'Pálinka', emoji:'🍐', str:3, need:[], ing:['4 cl pálinka'], step:'Hidegen, egyben. Egészségedre!' },
  ];

  const toggle = k => setAvail(s => { const n = new Set(s); n.has(k) ? n.delete(k) : n.add(k); return n; });
  const canMake = d => d.need.length > 0 && d.need.every(k => avail.has(k));
  const pickRater = id => { setRater(id); try { localStorage.setItem('boh_bar_rater', id || ''); } catch(e) {} };
  const rate = (drinkId, stars) => {
    if (!rater) return;
    setRatings(prev => ({ ...prev, [drinkId]: { ...(prev[drinkId] || {}), [rater]: stars } }));
    if (db) db.collection('config').doc('drinkRatings').set({ [drinkId]: { [rater]: stars } }, { merge: true }).catch(() => {});
  };
  const avgOf = id => { const v = Object.values(ratings[id] || {}); return v.length ? { avg: v.reduce((a,b) => a+b, 0) / v.length, n: v.length } : { avg: 0, n: 0 }; };

  const strColor = s => s >= 3 ? T.coral : s === 2 ? (T.yellow || '#F4C95A') : T.mint;
  let list = DRINKS.filter(d => d.type === tab);
  if (avail.size) list = [...list].sort((a,b) => (canMake(b) - canMake(a)));

  const Stars = ({ value, onPick, size }) => (
    <div style={{ display:'flex', gap:2 }}>
      {[1,2,3,4,5].map(i => (
        <span key={i} onClick={onPick ? (e => { e.stopPropagation(); onPick(i); }) : undefined} style={{ cursor: onPick ? 'pointer' : 'default', fontSize: size || 15, lineHeight:1, color: i <= Math.round(value) ? (T.yellow || '#F4C95A') : T.inkMute + '44' }}>★</span>
      ))}
    </div>
  );

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Bár" onBack={() => go('home')} />
      <div style={{ padding:'10px 16px 0', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
        <div style={{ display:'flex', background:T.surface, borderRadius:16, padding:5, gap:4, boxShadow:T.shadow }}>
          {[['cocktail','Koktél 🍹'],['shot','Shot 🥃']].map(([k,l]) => (
            <button key={k} onClick={() => setTab(k)} style={{ flex:1, padding:'11px 0', border:'none', borderRadius:12, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:14, background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .15s' }}>{l}</button>
          ))}
        </div>
      </div>
      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px 40px', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
        {/* Mi van itthon? szűrő */}
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, marginBottom:2 }}>Mi van itthon?</div>
        <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:10 }}>Koppints, amid van — kiemeljük, mit tudsz kikeverni.</div>
        <div style={{ display:'flex', flexWrap:'wrap', gap:7, marginBottom:16 }}>
          {CHIPS.map(([k,l,e]) => { const on = avail.has(k); return (
            <button key={k} onClick={() => toggle(k)} style={{ display:'flex', alignItems:'center', gap:5, padding:'7px 11px', borderRadius:999, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, background: on ? T.mint : T.surface, color: on ? '#fff' : T.ink, boxShadow: on ? `0 3px 0 ${T.mintDeep||T.mint}66, 0 6px 14px ${T.mint}33` : T.shadow }}>
              <span style={{ fontSize:13, lineHeight:1 }}>{e}</span>{l}
            </button>
          ); })}
          {avail.size > 0 && <button onClick={() => setAvail(new Set())} style={{ padding:'7px 11px', borderRadius:999, border:`1.5px solid ${T.inkMute}44`, background:'transparent', cursor:'pointer', fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.inkSoft }}>Törlés</button>}
        </div>
        {/* Ki értékel? */}
        {profiles.length > 0 && (
          <div style={{ background:T.surface, borderRadius:14, padding:'10px 12px', boxShadow:T.shadow, marginBottom:16 }}>
            <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:8 }}>Ki értékel?</div>
            <div style={{ display:'flex', gap:8, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:2 }}>
              {profiles.map(pr => { const on = rater === pr.id; return (
                <button key={pr.id} onClick={() => pickRater(on ? null : pr.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:3, border:'none', background:'transparent', cursor:'pointer', flexShrink:0, padding:0 }}>
                  <div style={{ width:40, height:40, borderRadius:'50%', background:pr.color||'#888', overflow:'hidden', display:'grid', placeItems:'center', border: on ? `2.5px solid ${T.mint}` : '2.5px solid transparent', boxSizing:'border-box' }}>
                    {pr.img ? <img src={pr.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{(pr.name||'?').charAt(0).toUpperCase()}</span>}
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color: on ? T.mintDeep||T.mint : T.inkSoft, maxWidth:52, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{pr.name}</span>
                </button>
              ); })}
            </div>
          </div>
        )}
        {/* Italok */}
        <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
          {list.map(d => {
            const mk = avail.size > 0 && canMake(d);
            const dim = avail.size > 0 && !canMake(d);
            const { avg, n } = avgOf(d.id);
            const myRating = rater ? (ratings[d.id] || {})[rater] || 0 : 0;
            return (
              <div key={d.id} style={{ background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, opacity: dim ? 0.45 : 1, border: mk ? `2px solid ${T.mint}` : '2px solid transparent' }}>
                <div style={{ display:'flex', alignItems:'center', gap:10 }}>
                  <span style={{ fontSize:26, lineHeight:1, flexShrink:0 }}>{d.emoji}</span>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink }}>{d.name}</div>
                    <div style={{ display:'flex', gap:3, marginTop:4, alignItems:'center' }}>
                      {[0,1,2].map(i => <span key={i} style={{ width:7, height:7, borderRadius:'50%', background: i < d.str ? strColor(d.str) : T.inkMute+'33' }} />)}
                      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute, marginLeft:4, textTransform:'uppercase', letterSpacing:'0.05em' }}>{d.str >= 3 ? 'Erős' : d.str === 2 ? 'Közepes' : 'Könnyű'}</span>
                    </div>
                  </div>
                  {mk && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.mintDeep||T.mint, background:T.mintSoft, borderRadius:999, padding:'3px 9px', flexShrink:0 }}>✓ Kikeverhető</span>}
                </div>
                <div style={{ display:'flex', flexWrap:'wrap', gap:'3px 12px', marginTop:9 }}>
                  {d.ing.map((it,i) => <span key={i} style={{ fontFamily:T.font, fontSize:12.5, fontWeight:700, color:T.inkSoft }}>• {it}</span>)}
                </div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginTop:7, lineHeight:1.45 }}>{d.step}</div>
                {/* Értékelés */}
                <div style={{ display:'flex', alignItems:'center', gap:10, marginTop:10, paddingTop:9, borderTop:`1px solid ${T.inkMute}1f` }}>
                  <div style={{ display:'flex', alignItems:'center', gap:5 }}>
                    <Stars value={avg} size={14} />
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.inkSoft }}>{n ? avg.toFixed(1) : '—'}</span>
                    <span style={{ fontFamily:T.font, fontSize:11, color:T.inkMute }}>({n})</span>
                  </div>
                  <div style={{ flex:1 }} />
                  {rater ? (
                    <div style={{ display:'flex', alignItems:'center', gap:5 }}>
                      <span style={{ fontFamily:T.font, fontSize:11, fontWeight:700, color:T.inkMute }}>Te:</span>
                      <Stars value={myRating} size={18} onPick={s => rate(d.id, s)} />
                    </div>
                  ) : (
                    <span style={{ fontFamily:T.font, fontSize:11, color:T.inkMute }}>Válassz profilt az értékeléshez</span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:20, lineHeight:1.5 }}>Idd felelősséggel! A mennyiségek csak irányadóak. 🍸</div>
      </div>
    </div>
  );
}

'''

# ── 1) BarScreen a bohGCalUrl elé ──
rep('// Google Naptár "esemény hozzáadása" template URL — nincs OAuth, egy koppintással',
    BAR + '// Google Naptár "esemény hozzáadása" template URL — nincs OAuth, egy koppintással')

# ── 2) Router ──
rep("        {screen==='stats'    && <StatsScreen    go={go} onOpenObserver={openObserver} />}",
    "        {screen==='stats'    && <StatsScreen    go={go} onOpenObserver={openObserver} />}\n        {screen==='bar'      && <BarScreen      go={go} />}")

# ── 3) Home jobb felső pill: koktél belépő ──
rep("""          <div style={{ width:1, background:T.inkMute+'25', margin:'12px 0' }} />
          <button onClick={() => go('stats')} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </button>
        </div>""",
"""          <div style={{ width:1, background:T.inkMute+'25', margin:'12px 0' }} />
          <button onClick={() => go('stats')} style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer' }}>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </button>
          <div style={{ width:1, background:T.inkMute+'25', margin:'12px 0' }} />
          <button onClick={() => go('bar')} title="Koktél-súgó" style={{ display:'flex', alignItems:'center', justifyContent:'center', width:52, height:52, border:'none', background:'transparent', cursor:'pointer' }}>
            <svg width="23" height="23" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4h16l-8 9-8-9z"/><line x1="12" y1="13" x2="12" y2="20"/><line x1="8.5" y1="20" x2="15.5" y2="20"/></svg>
          </button>
        </div>""")

# ── 4) order tömb ──
rep("  const order = ['home','stats','players','games','play','end','observer'];",
    "  const order = ['home','stats','bar','players','games','play','end','observer'];")

# ── 5) Verziobump ──
rep("const APP_VERSION = 'v9.978';", "const APP_VERSION = 'v9.979';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — bar screen (tabs + ratings) applied')
