#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pub 2.0 — a képernyő fókusza a saját (DNR-es) keverésekre kerül:
#  - főnézet: "Mi kevertük" lista (Firestore barDrinks kollekció), + Új keverés űrlappal
#  - a beépített koktél/shot receptek a "Receptek" gomb mögé kerülnek (alnézet)
#  - értékelés átdolgozva: kártyára koppintva felugró lap — átlag, név szerinti
#    értékelések, saját értékelés az elmentett profillal (nincs külön "Ki értékel?" doboz)
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

START = 'function BarScreen({ go }) {'
END = '\n\n// Google Naptár'
assert src.count(START) == 1, 'BarScreen start not found'
i1 = src.index(START)
i2 = src.index(END, i1)

NEW = r'''// ── Pub: saját keverés űrlap (új / szerkesztés) ──
function DrinkForm({ init, profiles, onSave, onCancel }) {
  const [name, setName] = React.useState(init.name || '');
  const [emoji, setEmoji] = React.useState(init.emoji || '🍹');
  const [str, setStr] = React.useState(init.str || 2);
  const [ing, setIng] = React.useState((init.ing || []).join('\n'));
  const [step, setStep] = React.useState(init.step || '');
  const [by, setBy] = React.useState(init.by || '');
  const [note, setNote] = React.useState(init.note || '');
  const valid = name.trim().length > 0;
  const inp = { boxSizing:'border-box', padding:'10px 12px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:14, color:T.ink, outline:'none' };
  const lbl = { fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:5 };
  const strColor = s => s >= 3 ? T.coral : s === 2 ? (T.yellow || '#F4C95A') : T.mint;
  return (
    <div onClick={onCancel} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:80, display:'flex', alignItems:'center', justifyContent:'center', padding:20, animation:'fadeIn .2s' }}>
      <div onClick={e => e.stopPropagation()} style={{ background:T.bg, borderRadius:24, padding:'20px 18px', width:'100%', maxWidth:420, maxHeight:'86vh', overflowY:'auto', WebkitOverflowScrolling:'touch', boxSizing:'border-box', animation:'popIn .25s cubic-bezier(.2,.9,.3,1.2)' }}>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginBottom:14 }}>{init.id ? 'Keverés szerkesztése' : 'Új keverés'}</div>
        <div style={{ display:'flex', gap:8, marginBottom:12 }}>
          <div style={{ width:64, flexShrink:0 }}>
            <div style={lbl}>Emoji</div>
            <input value={emoji} onChange={e => setEmoji(e.target.value)} style={{ ...inp, width:'100%', textAlign:'center', fontSize:20, padding:'8px 4px' }} />
          </div>
          <div style={{ flex:1, minWidth:0 }}>
            <div style={lbl}>Név *</div>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="Pl. Dini bombája" style={{ ...inp, width:'100%' }} />
          </div>
        </div>
        <div style={{ marginBottom:12 }}>
          <div style={lbl}>Erősség</div>
          <div style={{ display:'flex', gap:6 }}>
            {[[1,'Könnyű'],[2,'Közepes'],[3,'Erős']].map(([v,l]) => (
              <button key={v} onClick={() => setStr(v)} style={{ flex:1, padding:'9px 0', borderRadius:999, border: str === v ? `1.5px solid ${strColor(v)}` : `1.5px solid ${T.border}`, background: str === v ? `${strColor(v)}22` : 'transparent', color: str === v ? strColor(v) : T.inkMute, fontFamily:T.font, fontWeight:800, fontSize:12.5, cursor:'pointer' }}>{l}</button>
            ))}
          </div>
        </div>
        <div style={{ marginBottom:12 }}>
          <div style={lbl}>Hozzávalók (soronként egy)</div>
          <textarea value={ing} onChange={e => setIng(e.target.value)} rows={4} placeholder={'4 cl vodka\n1 dl áfonyalé\njég'} style={{ ...inp, width:'100%', resize:'vertical' }} />
        </div>
        <div style={{ marginBottom:12 }}>
          <div style={lbl}>Elkészítés</div>
          <textarea value={step} onChange={e => setStep(e.target.value)} rows={2} placeholder="Hogyan kevered ki?" style={{ ...inp, width:'100%', resize:'vertical' }} />
        </div>
        <div style={{ marginBottom:12 }}>
          <div style={lbl}>Ki keverte?</div>
          <input value={by} onChange={e => setBy(e.target.value)} placeholder="Név" style={{ ...inp, width:'100%' }} />
          {profiles.length > 0 && (
            <div style={{ display:'flex', gap:6, flexWrap:'wrap', marginTop:7 }}>
              {profiles.map(pr => (
                <button key={pr.id} onClick={() => setBy(pr.name || '')} style={{ padding:'5px 10px', borderRadius:999, border:`1.5px solid ${by === pr.name ? T.mint : T.border}`, background: by === pr.name ? T.mintSoft : 'transparent', color: by === pr.name ? (T.mintDeep || T.mint) : T.inkMute, fontFamily:T.font, fontWeight:800, fontSize:11.5, cursor:'pointer' }}>{pr.name}</button>
              ))}
            </div>
          )}
        </div>
        <div style={{ marginBottom:16 }}>
          <div style={lbl}>Megjegyzés (pl. melyik bulin készült)</div>
          <input value={note} onChange={e => setNote(e.target.value)} placeholder="Nem kötelező" style={{ ...inp, width:'100%' }} />
        </div>
        <div style={{ display:'flex', gap:10 }}>
          <button onClick={onCancel} style={{ flex:1, padding:'13px 0', borderRadius:14, border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:14, cursor:'pointer' }}>Mégse</button>
          <button onClick={() => { if (valid) onSave({ name:name.trim(), emoji:(emoji||'').trim()||'🍹', str, ing:ing.split('\n').map(s => s.trim()).filter(Boolean), step:step.trim(), by:by.trim(), note:note.trim() }); }} style={{ flex:1.4, padding:'13px 0', borderRadius:14, border:'none', background: valid ? T.mint : T.mintSoft, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor: valid ? 'pointer' : 'default' }}>Mentés</button>
        </div>
      </div>
    </div>
  );
}

function BarScreen({ go }) {
  const [view, setView] = React.useState('own');
  const [tab, setTab] = React.useState('cocktail');
  const [avail, setAvail] = React.useState(() => new Set());
  const [profiles, setProfiles] = React.useState([]);
  const [rater, setRater] = React.useState(() => { try { return localStorage.getItem('boh_bar_rater') || null; } catch(e) { return null; } });
  const [pickingRater, setPickingRater] = React.useState(false);
  const [ratings, setRatings] = React.useState({});
  const [own, setOwn] = React.useState(null);
  const [sheetId, setSheetId] = React.useState(null);
  const [form, setForm] = React.useState(null);
  const [confirmDel, setConfirmDel] = React.useState(false);
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(ps => setProfiles(ps || [])).catch(() => {});
    if (!db) { setOwn([]); return; }
    const unsub1 = db.collection('config').doc('drinkRatings').onSnapshot(d => setRatings((d && d.exists && d.data()) || {}), () => {});
    const unsub2 = db.collection('barDrinks').onSnapshot(qs => {
      setOwn((qs.docs || []).map(dd => ({ ...dd.data(), id: dd.id, custom: true })));
    }, () => setOwn([]));
    return () => { try { unsub1(); } catch(e) {} try { unsub2(); } catch(e) {} };
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

  const ownList = own || [];
  const toggle = k => setAvail(s => { const n = new Set(s); n.has(k) ? n.delete(k) : n.add(k); return n; });
  const canMake = d => d.need && d.need.length > 0 && d.need.every(k => avail.has(k));
  const setRaterPersist = id => { setRater(id); setPickingRater(false); try { localStorage.setItem('boh_bar_rater', id || ''); } catch(e) {} };
  const rate = (drinkId, stars) => {
    if (!rater) return;
    setRatings(prev => ({ ...prev, [drinkId]: { ...(prev[drinkId] || {}), [rater]: stars } }));
    if (db) db.collection('config').doc('drinkRatings').set({ [drinkId]: { [rater]: stars } }, { merge: true }).catch(() => {});
  };
  const avgOf = id => { const v = Object.values(ratings[id] || {}); return v.length ? { avg: v.reduce((a,b) => a+b, 0) / v.length, n: v.length } : { avg: 0, n: 0 }; };
  const strColor = s => s >= 3 ? T.coral : s === 2 ? (T.yellow || '#F4C95A') : T.mint;
  const profOf = id => profiles.find(p => p.id === id) || null;

  const saveDrink = (data) => {
    if (!db) return;
    const editing = form && form.id;
    const id = editing || ('own_' + Date.now().toString(36));
    db.collection('barDrinks').doc(id).set({ ...data, created: (editing && form.created) || Date.now() }, { merge: true }).catch(() => {});
    setForm(null); setView('own'); setSheetId(id);
  };
  const deleteDrink = (id) => { if (db) db.collection('barDrinks').doc(id).delete().catch(() => {}); setConfirmDel(false); setSheetId(null); };

  const ownSorted = [...ownList].sort((a,b) => {
    const A = avgOf(a.id), B = avgOf(b.id);
    if (A.n && B.n) return (B.avg - A.avg) || (B.n - A.n);
    if (!!A.n !== !!B.n) return B.n - A.n;
    return (b.created || 0) - (a.created || 0);
  });
  const medalFor = {};
  ownSorted.filter(d => avgOf(d.id).n > 0).slice(0, 3).forEach((d, i) => { medalFor[d.id] = ['🥇','🥈','🥉'][i]; });

  let recipeList = DRINKS.filter(d => d.type === tab);
  if (avail.size) recipeList = [...recipeList].sort((a,b) => (canMake(b) - canMake(a)));

  const sheetDrink = sheetId ? (ownList.find(d => d.id === sheetId) || DRINKS.find(d => d.id === sheetId) || null) : null;
  const openSheet = d => { setConfirmDel(false); setPickingRater(false); setSheetId(d.id); };

  const Stars = ({ value, onPick, size }) => (
    <div style={{ display:'flex', gap:2 }}>
      {[1,2,3,4,5].map(i => (
        <span key={i} onClick={onPick ? (e => { e.stopPropagation(); onPick(i); }) : undefined} style={{ cursor: onPick ? 'pointer' : 'default', fontSize: size || 15, lineHeight:1, color: i <= Math.round(value) ? (T.yellow || '#F4C95A') : T.inkMute + '44' }}>★</span>
      ))}
    </div>
  );
  const StrDots = ({ s }) => (
    <div style={{ display:'flex', gap:3, alignItems:'center' }}>
      {[0,1,2].map(i => <span key={i} style={{ width:7, height:7, borderRadius:'50%', background: i < s ? strColor(s) : T.inkMute+'33' }} />)}
      <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkMute, marginLeft:4, textTransform:'uppercase', letterSpacing:'0.05em' }}>{s >= 3 ? 'Erős' : s === 2 ? 'Közepes' : 'Könnyű'}</span>
    </div>
  );
  const Avatar = ({ pr, size }) => (
    <div style={{ width:size, height:size, borderRadius:'50%', background:(pr && pr.color) || '#98A2B3', overflow:'hidden', display:'grid', placeItems:'center', flexShrink:0 }}>
      {pr && pr.img ? <img src={pr.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:size*0.45, color:'#fff' }}>{((pr && pr.name) || '?').charAt(0).toUpperCase()}</span>}
    </div>
  );

  const DrinkCard = ({ d, mk, dim, medal }) => {
    const { avg, n } = avgOf(d.id);
    return (
      <div onClick={() => openSheet(d)} style={{ background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, cursor:'pointer', display:'flex', alignItems:'center', gap:12, opacity: dim ? 0.45 : 1, border: mk ? `2px solid ${T.mint}` : '2px solid transparent' }}>
        <span style={{ fontSize:30, lineHeight:1, flexShrink:0 }}>{d.emoji || '🍹'}</span>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ display:'flex', alignItems:'center', gap:6, minWidth:0 }}>
            <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{d.name}</span>
            {medal && <span style={{ fontSize:15, lineHeight:1, flexShrink:0 }}>{medal}</span>}
            {mk && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, color:T.mintDeep || T.mint, background:T.mintSoft, borderRadius:999, padding:'2px 8px', flexShrink:0 }}>✓ Kikeverhető</span>}
          </div>
          {d.by ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11.5, color:T.inkSoft, marginTop:2, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>Keverte: {d.by}</div> : null}
          <div style={{ marginTop:5 }}><StrDots s={d.str || 2} /></div>
        </div>
        <div style={{ display:'flex', flexDirection:'column', alignItems:'flex-end', gap:3, flexShrink:0 }}>
          <Stars value={avg} size={13} />
          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft }}>{n ? avg.toFixed(1) + ' · ' + n + ' szavazat' : '—'}</span>
        </div>
      </div>
    );
  };

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title={view === 'recipes' ? 'Receptek' : 'Pub'} onBack={() => { if (view === 'recipes') setView('own'); else go('home'); }} />
      {view === 'own' && (
        <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px 40px', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
          <div style={{ display:'flex', gap:10, marginBottom:16 }}>
            <button onClick={() => setForm({})} style={{ flex:1, padding:'13px 0', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14.5, cursor:'pointer', boxShadow:`0 4px 14px ${T.mint}44` }}>+ Új keverés</button>
            <button onClick={() => setView('recipes')} style={{ padding:'13px 16px', borderRadius:14, border:'none', background:T.surface, color:T.ink, fontFamily:T.font, fontWeight:800, fontSize:13.5, cursor:'pointer', boxShadow:T.shadow, display:'flex', alignItems:'center', gap:6 }}><span style={{ fontSize:15, lineHeight:1 }}>📖</span> Receptek</button>
          </div>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, marginBottom:2 }}>Mi kevertük 🍸</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:10 }}>A DNR-eken készült keverések — koppints egy italra a részletekhez és az értékeléshez.</div>
          {own === null ? (
            <div style={{ textAlign:'center', padding:30, fontFamily:T.font, color:T.sub }}>Betöltés…</div>
          ) : ownSorted.length === 0 ? (
            <div style={{ background:T.surface, borderRadius:20, padding:'30px 20px', boxShadow:T.shadow, textAlign:'center' }}>
              <div style={{ fontSize:44, marginBottom:10, lineHeight:1 }}>🍹</div>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:T.ink, marginBottom:6 }}>Még nincs saját keverés</div>
              <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5, marginBottom:16 }}>Vedd fel, amit a bulin kikevertetek — mindenki értékelheti, és kiderül, melyik a legendás.</div>
              <button onClick={() => setForm({})} style={{ padding:'12px 22px', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor:'pointer' }}>+ Első keverés felvétele</button>
            </div>
          ) : (
            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {ownSorted.map(d => <DrinkCard key={d.id} d={d} medal={medalFor[d.id]} />)}
            </div>
          )}
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:20, lineHeight:1.5 }}>Idd felelősséggel! 🍸</div>
        </div>
      )}
      {view === 'recipes' && (
        <React.Fragment>
          <div style={{ padding:'10px 16px 0', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
            <div style={{ display:'flex', background:T.surface, borderRadius:16, padding:5, gap:4, boxShadow:T.shadow }}>
              {[['cocktail','Koktél 🍹'],['shot','Shot 🥃']].map(([k,l]) => (
                <button key={k} onClick={() => setTab(k)} style={{ flex:1, padding:'11px 0', border:'none', borderRadius:12, cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:14, background: tab===k ? T.mint : 'transparent', color: tab===k ? '#fff' : T.inkSoft, transition:'all .15s' }}>{l}</button>
              ))}
            </div>
          </div>
          <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px 40px', maxWidth:680, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
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
            <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
              {recipeList.map(d => <DrinkCard key={d.id} d={d} mk={avail.size > 0 && canMake(d)} dim={avail.size > 0 && !canMake(d)} />)}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:20, lineHeight:1.5 }}>Idd felelősséggel! A mennyiségek csak irányadóak. 🍸</div>
          </div>
        </React.Fragment>
      )}
      {sheetDrink && (() => {
        const d = sheetDrink;
        const { avg, n } = avgOf(d.id);
        const entries = Object.entries(ratings[d.id] || {}).sort((a,b) => b[1]-a[1]);
        const my = rater ? (ratings[d.id] || {})[rater] || 0 : 0;
        const rp = rater ? profOf(rater) : null;
        return (
          <div onClick={() => setSheetId(null)} style={{ position:'fixed', inset:0, background:'rgba(14,14,24,0.72)', zIndex:70, display:'flex', alignItems:'center', justifyContent:'center', padding:20, animation:'fadeIn .2s' }}>
            <div onClick={e => e.stopPropagation()} style={{ background:T.bg, borderRadius:24, padding:'20px 18px', width:'100%', maxWidth:420, maxHeight:'86vh', overflowY:'auto', WebkitOverflowScrolling:'touch', boxSizing:'border-box', animation:'popIn .25s cubic-bezier(.2,.9,.3,1.2)' }}>
              <div style={{ display:'flex', alignItems:'flex-start', gap:12, marginBottom:4 }}>
                <span style={{ fontSize:40, lineHeight:1, flexShrink:0 }}>{d.emoji || '🍹'}</span>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:T.ink, lineHeight:1.15 }}>{d.name}</div>
                  <div style={{ marginTop:5 }}><StrDots s={d.str || 2} /></div>
                </div>
                <button onClick={() => setSheetId(null)} style={{ border:'none', background:T.surfaceMuted, color:T.inkSoft, width:32, height:32, borderRadius:'50%', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:14, flexShrink:0 }}>✕</button>
              </div>
              {d.by ? <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12.5, color:T.inkSoft, marginTop:4 }}>Keverte: {d.by}</div> : null}
              {d.note ? <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginTop:3 }}>📝 {d.note}</div> : null}
              {(d.ing && d.ing.length) ? (
                <div style={{ background:T.surface, borderRadius:14, padding:'11px 13px', boxShadow:T.shadow, marginTop:10 }}>
                  <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:6 }}>Hozzávalók</div>
                  <div style={{ display:'flex', flexDirection:'column', gap:3 }}>
                    {d.ing.map((it,i) => <span key={i} style={{ fontFamily:T.font, fontSize:13, fontWeight:700, color:T.ink }}>• {it}</span>)}
                  </div>
                  {d.step ? <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute, marginTop:8, lineHeight:1.45 }}>{d.step}</div> : null}
                </div>
              ) : (d.step ? <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute, marginTop:10, lineHeight:1.45 }}>{d.step}</div> : null)}
              <div style={{ background:T.surface, borderRadius:14, padding:'12px 13px', boxShadow:T.shadow, marginTop:10 }}>
                <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:8 }}>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em' }}>Értékelések</span>
                  <div style={{ flex:1 }} />
                  <Stars value={avg} size={15} />
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink }}>{n ? avg.toFixed(1) : '—'}</span>
                  <span style={{ fontFamily:T.font, fontSize:11, color:T.inkMute }}>({n})</span>
                </div>
                {entries.length > 0 && (
                  <div style={{ display:'flex', flexDirection:'column', gap:6, marginBottom:10 }}>
                    {entries.map(([pid, st]) => { const pr = profOf(pid); return (
                      <div key={pid} style={{ display:'flex', alignItems:'center', gap:8 }}>
                        <Avatar pr={pr} size={24} />
                        <span style={{ fontFamily:T.font, fontWeight:700, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(pr && pr.name) || 'Ismeretlen'}</span>
                        <Stars value={st} size={13} />
                      </div>
                    ); })}
                  </div>
                )}
                {rater && !pickingRater ? (
                  <div style={{ display:'flex', alignItems:'center', gap:8, paddingTop:9, borderTop:`1px solid ${T.inkMute}1f` }}>
                    <Avatar pr={rp} size={24} />
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink }}>Te{rp ? ' (' + rp.name + ')' : ''}</span>
                    <div style={{ flex:1 }} />
                    <Stars value={my} size={21} onPick={s => rate(d.id, s)} />
                    <button onClick={() => setPickingRater(true)} style={{ border:'none', background:'transparent', color:T.inkMute, fontFamily:T.font, fontWeight:700, fontSize:11, cursor:'pointer', textDecoration:'underline', padding:0, marginLeft:2 }}>váltás</button>
                  </div>
                ) : (
                  <div style={{ paddingTop:9, borderTop:`1px solid ${T.inkMute}1f` }}>
                    <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, marginBottom:7 }}>Ki vagy? Válaszd ki magad az értékeléshez:</div>
                    <div style={{ display:'flex', gap:8, overflowX:'auto', WebkitOverflowScrolling:'touch', paddingBottom:2 }}>
                      {profiles.map(pr => (
                        <button key={pr.id} onClick={() => setRaterPersist(pr.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:3, border:'none', background:'transparent', cursor:'pointer', flexShrink:0, padding:0 }}>
                          <Avatar pr={pr} size={38} />
                          <span style={{ fontFamily:T.font, fontWeight:700, fontSize:10, color:T.inkSoft, maxWidth:50, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{pr.name}</span>
                        </button>
                      ))}
                    </div>
                    {profiles.length === 0 && <div style={{ fontFamily:T.font, fontSize:11.5, color:T.inkMute }}>Nincs profil — hozz létre egyet a Statisztika oldalon.</div>}
                  </div>
                )}
              </div>
              {d.custom && (
                <div style={{ display:'flex', gap:10, marginTop:12 }}>
                  <button onClick={() => setForm(d)} style={{ flex:1, padding:'11px 0', borderRadius:12, border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>Szerkesztés</button>
                  <button onClick={() => { if (confirmDel) deleteDrink(d.id); else setConfirmDel(true); }} style={{ flex:1, padding:'11px 0', borderRadius:12, border:'none', background: confirmDel ? T.coral : T.coralSoft, color: confirmDel ? '#fff' : T.coral, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmDel ? 'Biztos? Végleg törli!' : 'Törlés'}</button>
                </div>
              )}
            </div>
          </div>
        );
      })()}
      {form && <DrinkForm init={form} profiles={profiles} onSave={saveDrink} onCancel={() => setForm(null)} />}
    </div>
  );
}'''

src = src[:i1] + NEW + src[i2:]

# Verziobump
old_v = "const APP_VERSION = 'v9.983';"
assert src.count(old_v) == 1
src = src.replace(old_v, "const APP_VERSION = 'v9.984';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — Pub 2.0 applied')
