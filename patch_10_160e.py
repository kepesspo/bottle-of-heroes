# v10.160 (e) — maga a SetupScreen
import io

P = 'app.src.html'
s = io.open(P, encoding='utf-8').read()
orig = s

# a profil kortyolasi limitjenek celzott irasa (a saveProfile nevet/szint is
# varna, reszleges hivassal felulirna oket)
anchor = "  window.saveProfile = function(profile) {"
assert s.count(anchor) == 1
s = s.replace(anchor, """  window.setProfileDrinkLimit = function(profileId, limit) {
    if (!profileId) return Promise.resolve();
    var v = Number(limit) > 0 ? Number(limit) : firebase.firestore.FieldValue.delete();
    return db.collection('profiles').doc(profileId).set({ drinkLimit: v }, { merge: true })
      .catch(function(e) { console.warn('setProfileDrinkLimit', e); });
  };
""" + anchor)

SCREEN = '''
// ─── JATEKMENET OLDAL ──────────────────────────────────────────
// A jatekvalasztas UTAN jon, mert a jatek-beallitasok csak akkor ertelmesek,
// ha mar tudjuk, mit jatszunk. Adminbol kapcsolhato (setupFlowEnabled);
// kikapcsolva a Jatekok oldalrol indul a parti, mint korabban.
function SetupScreen({ go, players, selectedGames, gameMeta, setGameMeta }) {
  const [openCfg, setOpenCfg] = React.useState(null);
  const [limits, setLimits] = React.useState({});   // profileId -> limit (szam vagy '')
  const [limitsLoaded, setLimitsLoaded] = React.useState(false);

  const games = (selectedGames || []).map(id => GAMES.find(g => g.id === id)).filter(Boolean);
  const configurable = games.filter(g => hasGameConfig(g.id));
  const minutes = Math.max(5, Math.round((selectedGames || []).length * 2.5 / 5) * 5);
  const withProfile = (players || []).filter(p => p.profileId);

  React.useEffect(() => {
    if (!withProfile.length || typeof window.getProfiles !== 'function') { setLimitsLoaded(true); return; }
    let alive = true;
    window.getProfiles().then(list => {
      if (!alive) return;
      const map = {};
      (list || []).forEach(pr => { if (pr.drinkLimit) map[pr.id] = pr.drinkLimit; });
      setLimits(map); setLimitsLoaded(true);
    }, () => setLimitsLoaded(true));
    return () => { alive = false; };
  }, [players]);

  const writeLimit = (profileId, raw) => {
    const v = raw.replace(/[^0-9]/g, '');
    setLimits(m => Object.assign({}, m, { [profileId]: v }));
    if (typeof window.setProfileDrinkLimit === 'function') window.setProfileDrinkLimit(profileId, v);
  };

  const Section = ({ title, sub, children }) => (
    <div style={{ marginTop:18 }}>
      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, letterSpacing:'0.1em',
        textTransform:'uppercase', color:T.inkMute, marginBottom:8 }}>{title}</div>
      {sub && <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginBottom:10, lineHeight:1.5 }}>{sub}</div>}
      {children}
    </div>
  );

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Játékmenet" onBack={() => go('games')} right={<StepDots active={3} />} />

      <div className="screen-wide screen-pad" style={{ flex:1, overflowY:'auto', paddingTop:14, paddingBottom:110 }}>

        {/* Osszefoglalo — mi var ra, mielott belemegy a reszletekbe */}
        <div style={{ display:'flex', gap:10, background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow }}>
          {[
            { v: (players || []).length, l: 'játékos' },
            { v: games.length,          l: 'játék' },
            { v: '~' + minutes,         l: 'perc' },
          ].map((x, i) => (
            <div key={i} style={{ flex:1, minWidth:0, textAlign:'center' }}>
              <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:T.ink, lineHeight:1 }}>{x.v}</div>
              <div style={{ fontFamily:T.font, fontWeight:800, fontSize:10.5, letterSpacing:'0.08em',
                textTransform:'uppercase', color:T.inkMute, marginTop:4 }}>{x.l}</div>
            </div>
          ))}
        </div>

        <Section title="Játékmenet">
          <div style={{ background:T.surface, borderRadius:16, padding:'4px 14px 14px', boxShadow:T.shadow }}>
            <GameSettingsContent meta={gameMeta} setMeta={setGameMeta} />
          </div>
        </Section>

        <Section title="A játékok beállításai"
          sub={configurable.length
            ? 'Ezeknek a kiválasztott játékoknak van saját beállítása.'
            : undefined}>
          {configurable.length === 0 ? (
            <div style={{ background:T.surface, borderRadius:16, padding:16, boxShadow:T.shadow,
              fontFamily:T.font, fontSize:13, color:T.inkMute, lineHeight:1.6 }}>
              A kiválasztott játékokhoz nincs külön beállítás — mehet az indítás.
            </div>
          ) : (
            <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
              {configurable.map(g => (
                <button key={g.id} onClick={() => setOpenCfg(g.id)} style={{
                  display:'flex', alignItems:'center', gap:12, width:'100%', textAlign:'left',
                  background:T.surface, border:'none', borderRadius:16, padding:'12px 14px',
                  boxShadow:T.shadow, cursor:'pointer', minHeight:64,
                }}>
                  <div style={{ width:44, height:44, borderRadius:13, flexShrink:0, display:'grid', placeItems:'center',
                    background: g.color ? g.color + '22' : T.surfaceMuted }}>
                    {g.img ? <img src={g.img} style={{ width:30, height:30, objectFit:'contain' }} />
                           : <span style={{ fontSize:22 }}>{g.emoji}</span>}
                  </div>
                  <div style={{ flex:1, minWidth:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{tg(g, 'name')}</div>
                    <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, marginTop:2 }}>Beállítások megnyitása</div>
                  </div>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:18, color:T.mintDeep, flexShrink:0 }}>›</span>
                </button>
              ))}
            </div>
          )}
        </Section>

        {withProfile.length > 0 && (
          <Section title="Kortyolási limit"
            sub="Ha valaki eléri a sajátját, a kör végén figyelmeztetünk. Üresen hagyva nincs limit. A profilhoz mentődik, tehát a következő bulira is megmarad.">
            <div style={{ display:'flex', flexDirection:'column', gap:8 }}>
              {withProfile.map(p => (
                <div key={p.id} style={{ display:'flex', alignItems:'center', gap:12,
                  background:T.surface, borderRadius:16, padding:'10px 14px', boxShadow:T.shadow, minHeight:60 }}>
                  <div style={{ width:36, height:36, borderRadius:'50%', background:p.color || T.mint, flexShrink:0,
                    display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>
                    {(p.name || '?').charAt(0).toUpperCase()}
                  </div>
                  <div style={{ flex:1, minWidth:0, fontFamily:T.font, fontWeight:800, fontSize:14.5, color:T.ink,
                    overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
                  <input value={limits[p.profileId] == null ? '' : String(limits[p.profileId])}
                    onChange={e => writeLimit(p.profileId, e.target.value)}
                    placeholder={limitsLoaded ? 'nincs' : '…'} inputMode="numeric" type="number"
                    style={{ width:76, flexShrink:0, textAlign:'center', padding:'9px 6px', borderRadius:11,
                      border:`2px solid ${T.inkMute}28`, background:T.bgSoft, color:T.ink,
                      fontFamily:T.font, fontWeight:900, fontSize:15, outline:'none' }} />
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkMute, flexShrink:0 }}>korty</span>
                </div>
              ))}
            </div>
          </Section>
        )}
      </div>

      <BottomBar>
        <PrimaryButton disabled={(selectedGames || []).length < 1} onClick={() => go('play')}>
          <span>{t('startGame')} ({(selectedGames || []).length})</span>
          <span style={{ display:'block', fontWeight:600, fontSize:12, opacity:0.75, marginTop:2 }}>⏱ kb. {minutes} perc</span>
        </PrimaryButton>
      </BottomBar>

      <GameConfigHost openId={openCfg} onClose={() => setOpenCfg(null)}
        gameMeta={gameMeta} setGameMeta={setGameMeta} playerCount={(players || []).length} />
    </div>
  );
}

'''

marker = "// A fuggveny-deklaraciok hoistolodnak,"
assert s.count(marker) == 1
s = s.replace(marker, SCREEN.lstrip('\n') + marker)

assert s != orig
io.open(P, 'w', encoding='utf-8').write(s)
print('OK — SetupScreen letrehozva')
