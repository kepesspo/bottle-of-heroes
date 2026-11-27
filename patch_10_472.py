# v10.472 — három tulajdonosi kérés
#  1) A DNR központ NEM ugrik át magától a Games-re, ha csak az az egy app látszik —
#     különben a központ (és vele az admin) elérhetetlen volt, a „‹ DNR" gomb azonnal
#     visszadobott a Games-re.
#  2) A DNR Games is kikapcsolható a központban (homeConfig.dnrApps.home). Ha egy app
#     sem látszik, a központ üres-állapotot mutat — az admin gomb ott is elérhető.
#  3) DNR Bingó „Ki vagy?": lenyitható Profilok rész + Vendég rész (név, vagy üresen
#     „Vendég N"). A vendégek a config/bingo `_guests` térképében ülnek.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.471';", "const APP_VERSION = 'v10.472';")

# ── 1+2: központ ──
rep("""  const apps = [DNR_GAMES_APP].concat(others.slice().sort((a, b) => _ord(a.screen) - _ord(b.screen)));
  // Egyetlen engedélyezett app (csak a Games) mellett a központ fölösleges lépés:
  // a betöltött config után egyenesen a DNR Games nyílik.
  React.useEffect(() => { if (homeCfg.loaded && bingoDoc.loaded && others.length === 0) onOpen('home'); }, [homeCfg.loaded, bingoDoc.loaded, others.length]);
""",
"""  // v10.472: a DNR Games is kikapcsolható (homeConfig.dnrApps.home) — a mester-kapcsoló
  // („DNR appok a központban") NEM rejti, az csak a többi appra vonatkozik.
  const gamesOn = dnrAppEnabled(hc, 'home');
  const apps = (gamesOn ? [DNR_GAMES_APP] : []).concat(others.slice().sort((a, b) => _ord(a.screen) - _ord(b.screen)));
  // ⚠️ v10.472: NINCS automatikus átugrás a Games-re, ha csak az az egy app látszik.
  // Korábban ilyenkor a központ elérhetetlen lett (és vele az admin gomb), a Games
  // „‹ DNR" gombja pedig rögtön visszadobott a Games-re.
""")
rep("""          <HubGreeting />
          <HubAnnouncement />

            <React.Fragment>""",
"""          <HubGreeting />
          <HubAnnouncement />

            {apps.length === 0 ? (
              <div data-hub-empty style={{ flex:1, minHeight:0, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:8, textAlign:'center', padding:'0 24px' }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.ink }}>Nincs bekapcsolt app</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13.5, color:T.inkSoft, lineHeight:1.45, maxWidth:320 }}>Az appokat a jobb felső fogaskerékkel érheted el: Admin → Általános → DNR központ.</div>
              </div>
            ) : (
            <React.Fragment>""")
rep("""                <button aria-label="Következő app" data-hub-next onClick={() => step(1)} disabled={cur === apps.length - 1} style={{ width:44, height:44, borderRadius:'50%', border:'none', background:T.surface, boxShadow:T.shadowPill, cursor: cur === apps.length - 1 ? 'default' : 'pointer', opacity: cur === apps.length - 1 ? 0.35 : 1, display:'grid', placeItems:'center' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
                </button>
              </div>
            </React.Fragment>""",
"""                <button aria-label="Következő app" data-hub-next onClick={() => step(1)} disabled={cur === apps.length - 1} style={{ width:44, height:44, borderRadius:'50%', border:'none', background:T.surface, boxShadow:T.shadowPill, cursor: cur === apps.length - 1 ? 'default' : 'pointer', opacity: cur === apps.length - 1 ? 0.35 : 1, display:'grid', placeItems:'center' }}>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg>
                </button>
              </div>
            </React.Fragment>
            )}""")
# a sáv mérése a ref-hez kötött: üres állapotból visszatérve is mérjen
rep("""    if (typeof ResizeObserver === 'function') { const ro = new ResizeObserver(m); ro.observe(el); return () => ro.disconnect(); }
    window.addEventListener('resize', m); return () => window.removeEventListener('resize', m);
  }, []);
  // Magas kijelzőn kicsit nőhet is""",
"""    if (typeof ResizeObserver === 'function') { const ro = new ResizeObserver(m); ro.observe(el); return () => ro.disconnect(); }
    window.addEventListener('resize', m); return () => window.removeEventListener('resize', m);
  }, [apps.length === 0]);
  // Magas kijelzőn kicsit nőhet is""")

# admin: DNR Games sor + a mester-kapcsoló felirata
rep("""      <div style={{ display:'flex', alignItems:'center', gap:12 }}>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>DNR appok a központban</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>
            Kikapcsolva a központban csak a DNR Games marad — ilyenkor az app egyenesen a Games-szel nyit.
          </div>
        </div>""",
"""      {/* v10.472: a DNR Games is kikapcsolható — a mester-kapcsoló ettől független */}
      <div data-admin-games-row style={{ display:'flex', alignItems:'center', gap:11, marginBottom:12 }}>
        <img src={DNR_GAMES_APP.icon} style={{ width:30, height:30, borderRadius:9, flexShrink:0 }} />
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>DNR Games</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>A partijátékok kártyája a központban.</div>
        </div>
        <Toggle on={dnrAppEnabled(cfg, 'home')} onChange={() => write({ dnrApps: Object.assign({}, (cfg && cfg.dnrApps) || {}, { home: !dnrAppEnabled(cfg, 'home') }) })} />
      </div>
      <div style={{ display:'flex', alignItems:'center', gap:12 }}>
        <div style={{ flex:1, minWidth:0 }}>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>DNR appok a központban</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>
            Kikapcsolva a többi app (Events, Pub, Bingó…) egyszerre eltűnik a központból.
          </div>
        </div>""")

# ── 3: Bingó vendég ──
rep("""  const pickWho = id => { setWho(id); prevBingos.current = null; setConfirmReset(false); setGateEmail(''); setGateCode(''); setGateSent(false); setGateErr(''); try { localStorage.setItem(whoKey, id || ''); } catch(e) {} };
  const whoProf = profiles.find(p => p.id === who) || null;""",
"""  const pickWho = id => { setWho(id); prevBingos.current = null; setConfirmReset(false); setGateEmail(''); setGateCode(''); setGateSent(false); setGateErr(''); try { localStorage.setItem(whoKey, id || ''); } catch(e) {} };
  // v10.472: Bingó-vendégek — akik nincsenek a profilok között. A config/bingo `_guests`
  // térképében ülnek (ugyanabban a doksiban, mint a kártyák jelölései), és csak a
  // Bingóban élnek: a Tipp és a Tortán profilhoz (e-mailes kódhoz, csapathoz) kötött.
  const guestMap = (mode === 'bingo' && marksAll && marksAll._guests && typeof marksAll._guests === 'object') ? marksAll._guests : {};
  const guestList = Object.keys(guestMap).map(id => Object.assign({ id, guest:true }, guestMap[id])).sort((a, b) => (a.at || 0) - (b.at || 0));
  const people = mode === 'bingo' ? profiles.concat(guestList) : profiles;
  const whoProf = people.find(p => p.id === who) || null;
  const [profOpen, setProfOpen] = React.useState(false);
  const [guestName, setGuestName] = React.useState('');
  const enterGuest = () => {
    let gid = null;
    try { gid = localStorage.getItem('boh_bingo_guest'); } catch(e) {}
    const reuse = !!(gid && guestMap[gid]);
    if (!reuse) gid = 'g_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
    const typed = guestName.trim().slice(0, 24);
    const name = typed || (reuse ? guestMap[gid].name : 'Vendég ' + (guestList.length + 1));
    const color = reuse && guestMap[gid].color ? guestMap[gid].color : BINGO_GUEST_COLORS[guestList.length % BINGO_GUEST_COLORS.length];
    const rec = { name, color, at: reuse ? (guestMap[gid].at || Date.now()) : Date.now() };
    setMarksAll(prev => Object.assign({}, prev, { _guests: Object.assign({}, (prev && prev._guests) || {}, { [gid]: rec }) }));
    if (db) db.collection('config').doc('bingo').set({ _guests: { [gid]: rec } }, { merge:true }).catch(() => {});
    try { localStorage.setItem('boh_bingo_guest', gid); } catch(e) {}
    setGuestName('');
    pickWho(gid);
  };""")
rep("""  const bingoBoard = profiles
    .map(p => ({ p, n: (marksAll[p.id] || []).length, b: bingosOf(new Set(marksAll[p.id] || [])) }))""",
    """  const bingoBoard = people
    .map(p => ({ p, n: (marksAll[p.id] || []).length, b: bingosOf(new Set(marksAll[p.id] || [])) }))""")
rep("""<span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}{p.id === who ? ' (te)' : ''}</span>""",
    """<span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}{p.guest ? <span style={{ fontWeight:700, color:T.inkMute }}> · vendég</span> : null}{p.id === who ? ' (te)' : ''}</span>""", 2)   # a Tipp állása is ezt a sort használja — ott p.guest sosem igaz

# a választó: Bingóban két rész
rep("""            {pickProfiles.length ? (
              <div style={{ display:'flex', flexWrap:'wrap', gap:16, justifyContent:'center' }}>""",
"""            {mode === 'bingo' ? (
              <div data-who-split style={{ display:'flex', flexDirection:'column', gap:12, textAlign:'left' }}>
                {/* v10.472: 1. lenyitható — a profilok */}
                <div style={{ border:`1.5px solid ${T.border}`, borderRadius:16, overflow:'hidden' }}>
                  <button type="button" data-who-profiles aria-expanded={profOpen} onClick={() => setProfOpen(o => !o)}
                    style={{ width:'100%', display:'flex', alignItems:'center', gap:10, padding:'13px 14px', border:'none', background:'transparent', cursor:'pointer', fontFamily:T.font, WebkitTapHighlightColor:'transparent' }}>
                    <span style={{ fontSize:20, lineHeight:1 }}>👥</span>
                    <span style={{ flex:1, minWidth:0, textAlign:'left' }}>
                      <span style={{ display:'block', fontWeight:900, fontSize:14.5, color:T.ink }}>Profilok</span>
                      <span style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft }}>{profiles.length ? profiles.length + ' mentett profil' : 'Még nincs profil'}</span>
                    </span>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke={T.inkSoft} strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" style={{ transform: profOpen ? 'rotate(180deg)' : 'none', transition:'transform .2s' }}><path d="M6 9l6 6 6-6"/></svg>
                  </button>
                  {profOpen && (profiles.length ? (
                    <div style={{ display:'flex', flexWrap:'wrap', gap:16, justifyContent:'center', padding:'4px 12px 16px' }}>
                      {profiles.map(pr => (
                        <button key={pr.id} data-who-pick={pr.id} onClick={() => pickWho(pr.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:'none', background:'transparent', cursor:'pointer', padding:0, WebkitTapHighlightColor:'transparent' }}>
                          <Avatar pr={pr} size={58} />
                          <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink, maxWidth:70, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{pr.name}</span>
                        </button>
                      ))}
                    </div>
                  ) : <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute, padding:'0 14px 14px' }}>Nincs profil — lépj be vendégként.</div>)}
                </div>
                {/* v10.472: 2. vendég — név, vagy üresen „Vendég N" */}
                <div data-who-guestbox style={{ border:`1.5px solid ${T.border}`, borderRadius:16, padding:'13px 14px' }}>
                  <div style={{ display:'flex', alignItems:'center', gap:10, marginBottom:10 }}>
                    <span style={{ fontSize:20, lineHeight:1 }}>🙋</span>
                    <span style={{ flex:1, minWidth:0 }}>
                      <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:14.5, color:T.ink }}>Vendég</span>
                      <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft }}>Nincs profilod? Írd be a neved — vagy hagyd üresen.</span>
                    </span>
                  </div>
                  <input data-who-guestname value={guestName} maxLength={24} onChange={e => setGuestName(e.target.value)} onKeyDown={e => { if (e.key === 'Enter') enterGuest(); }}
                    placeholder={'Vendég ' + (guestList.length + 1)} aria-label="Vendég neve"
                    style={{ width:'100%', boxSizing:'border-box', height:46, borderRadius:12, border:`1.5px solid ${T.border}`, background:T.bg, padding:'0 12px', fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink, outline:'none' }} />
                  <button type="button" data-who-guest onClick={enterGuest}
                    style={{ width:'100%', height:46, marginTop:9, borderRadius:12, border:'none', cursor:'pointer', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15 }}>Belépés vendégként</button>
                </div>
              </div>
            ) : pickProfiles.length ? (
              <div style={{ display:'flex', flexWrap:'wrap', gap:16, justifyContent:'center' }}>""")

# a vendég-színek
rep("function BingoScreen({ go, deepLink, app }) {",
    "// v10.472: a Bingó-vendégek színe (sorban osztva) — a kezdőbetűs korong háttere\n"
    "const BINGO_GUEST_COLORS = ['#E07A5F', '#4FC2A0', '#A78BFA', '#5BA0DB', '#F2A93B', '#E86A92', '#3FA7A0', '#8C7AE6'];\n"
    "function BingoScreen({ go, deepLink, app }) {")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
