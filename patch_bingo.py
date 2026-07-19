#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# VB Bingó — 5×5-ös, VB-döntő tematikájú bingó a főképernyőről. Először avataros
# "Ki vagy?" választó, utána profilonként saját (seedelt, stabil) kártya, koppintásra
# X-elés. A jelölések a Firestore config/bingo dokumentumban szinkronizálódnak,
# teljes sor/oszlop/átló esetén BINGÓ-ünneplés; kis állás-sáv mutatja, ki hol tart.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, 'expected %d, found %d for: %r' % (count, n, old[:80])
    src = src.replace(old, new)

# ── 1) BingoScreen komponens a Pub űrlap elé ──
MARKER = '// ── Pub: saját keverés űrlap (új / szerkesztés) — app design, EventForm mintára ──'
assert src.count(MARKER) == 1

BINGO = r'''// ── VB Bingó — 5×5, döntő tematika, profilonként saját kártya ──
const BINGO_ITEMS = [
  { e:'⚽', t:'Gól' },
  { e:'🟨', t:'Sárga lap' },
  { e:'🟥', t:'Piros lap' },
  { e:'📺', t:'VAR-vizsgálat' },
  { e:'🥅', t:'Kapufa' },
  { e:'🚩', t:'Les' },
  { e:'🧤', t:'Kapusbravúr' },
  { e:'🎯', t:'Tizenegyes' },
  { e:'🔄', t:'Csere gólt lő' },
  { e:'🤕', t:'Műesés' },
  { e:'😭', t:'Síró szurkoló' },
  { e:'🎨', t:'Arcfestés a kivetítőn' },
  { e:'🌊', t:'Mexikói hullám' },
  { e:'🤬', t:'Edző kiakad' },
  { e:'👕', t:'Mez le ünneplésnél' },
  { e:'⏱️', t:'90+5 hosszabbítás' },
  { e:'🎤', t:'„Micsoda meccs!"' },
  { e:'⭐', t:'Celeb a lelátón' },
  { e:'🍺', t:'Valaki kört hoz' },
  { e:'🥂', t:'Gól-koccintás' },
  { e:'📣', t:'Kiabálás a TV-vel' },
  { e:'🆓', t:'Veszélyes szabadrúgás' },
  { e:'😱', t:'Öngól' },
  { e:'🤝', t:'Fair play pillanat' },
];
function bingoCardFor(pid) {
  // determinisztikus keverés a profil id-ből — mindenkinek saját, de stabil kártya
  let s = 2166136261;
  const key = 'boh-bingo-' + pid;
  for (let i = 0; i < key.length; i++) { s ^= key.charCodeAt(i); s = Math.imul(s, 16777619); }
  s >>>= 0; if (!s) s = 88172645;
  const rnd = () => { s ^= s << 13; s ^= s >>> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  const arr = BINGO_ITEMS.map((_, i) => i);
  for (let i = arr.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); const t = arr[i]; arr[i] = arr[j]; arr[j] = t; }
  return arr;
}
const BINGO_LINES = (() => {
  const L = [];
  for (let r = 0; r < 5; r++) L.push([0,1,2,3,4].map(c => r * 5 + c));
  for (let c = 0; c < 5; c++) L.push([0,1,2,3,4].map(r => r * 5 + c));
  L.push([0,6,12,18,24]); L.push([4,8,12,16,20]);
  return L;
})();

function BingoScreen({ go }) {
  const [profiles, setProfiles] = React.useState([]);
  const [who, setWho] = React.useState(() => { try { return localStorage.getItem('boh_bingo_who') || null; } catch(e) { return null; } });
  const [marksAll, setMarksAll] = React.useState({});
  const [loaded, setLoaded] = React.useState(false);
  const [celebrate, setCelebrate] = React.useState(null);
  const [confirmReset, setConfirmReset] = React.useState(false);
  const prevBingos = React.useRef(null);
  const db = (typeof firebase !== 'undefined') ? firebase.firestore() : null;

  React.useEffect(() => {
    if (typeof window.getProfiles === 'function') window.getProfiles().then(ps => setProfiles(ps || [])).catch(() => {});
    if (!db) { setLoaded(true); return; }
    const un = db.collection('config').doc('bingo').onSnapshot(d => { setMarksAll((d && d.exists && d.data()) || {}); setLoaded(true); }, () => setLoaded(true));
    return () => { try { un(); } catch(e) {} };
  }, []);

  const pickWho = id => { setWho(id); prevBingos.current = null; setConfirmReset(false); try { localStorage.setItem('boh_bingo_who', id || ''); } catch(e) {} };
  const card = who ? bingoCardFor(who) : null;
  const myMarks = new Set(marksAll[who] || []);
  const persist = arr => { if (db && who) db.collection('config').doc('bingo').set({ [who]: arr }, { merge: true }).catch(() => {}); };
  const toggle = c => {
    if (c === 12 || !who) return;
    const n = new Set(myMarks);
    if (n.has(c)) n.delete(c); else n.add(c);
    const arr = Array.from(n).sort((a, b) => a - b);
    setMarksAll(prev => ({ ...prev, [who]: arr }));
    persist(arr);
  };
  const bingosOf = set => BINGO_LINES.filter(l => l.every(c => c === 12 || set.has(c))).length;
  const myBingos = who ? bingosOf(myMarks) : 0;
  React.useEffect(() => {
    if (!who || !loaded) return;
    if (prevBingos.current === null) { prevBingos.current = myBingos; return; }
    if (myBingos > prevBingos.current) {
      setCelebrate(myBingos);
      try { if (typeof window.bohHaptic === 'function') window.bohHaptic('success'); } catch(e) {}
      try { if (typeof window.bohSound === 'function') window.bohSound('zsulli'); } catch(e) {}
    }
    prevBingos.current = myBingos;
  }, [myBingos, who, loaded]);

  const whoProf = profiles.find(p => p.id === who) || null;
  const board = profiles
    .map(p => ({ p, n: (marksAll[p.id] || []).length, b: bingosOf(new Set(marksAll[p.id] || [])) }))
    .filter(x => x.n > 0)
    .sort((a, b) => (b.b - a.b) || (b.n - a.n));

  const Avatar = ({ pr, size }) => (
    <div style={{ width:size, height:size, borderRadius:'50%', background:(pr && pr.color) || '#98A2B3', overflow:'hidden', display:'grid', placeItems:'center', flexShrink:0 }}>
      {pr && pr.img ? <img src={pr.img} style={{ width:'100%', height:'100%', objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:size*0.42, color:'#fff' }}>{((pr && pr.name) || '?').charAt(0).toUpperCase()}</span>}
    </div>
  );

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="VB Bingó ⚽" onBack={() => go('home')} right={who ? (
        <button onClick={() => pickWho(null)} style={{ border:'none', background:T.surfaceMuted, color:T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:11.5, borderRadius:999, padding:'7px 12px', cursor:'pointer' }}>Váltás</button>
      ) : null} />
      <div style={{ flex:1, overflowY:'auto', WebkitOverflowScrolling:'touch', padding:'14px 16px max(40px, calc(env(safe-area-inset-bottom) + 24px))', maxWidth:560, width:'100%', margin:'0 auto', boxSizing:'border-box' }}>
        {!who ? (
          <div style={{ background:T.surface, borderRadius:20, padding:'24px 18px', boxShadow:T.shadow, textAlign:'center' }}>
            <div style={{ fontSize:42, lineHeight:1, marginBottom:10 }}>🏆</div>
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink, marginBottom:5 }}>Ki vagy?</div>
            <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkSoft, lineHeight:1.5, marginBottom:18 }}>Válaszd ki magad — mindenki saját kártyát kap, és X-elheti, ami a döntőben megtörténik.</div>
            {profiles.length ? (
              <div style={{ display:'flex', flexWrap:'wrap', gap:16, justifyContent:'center' }}>
                {profiles.map(pr => (
                  <button key={pr.id} onClick={() => pickWho(pr.id)} style={{ display:'flex', flexDirection:'column', alignItems:'center', gap:5, border:'none', background:'transparent', cursor:'pointer', padding:0, WebkitTapHighlightColor:'transparent' }}>
                    <Avatar pr={pr} size={58} />
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.ink, maxWidth:70, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{pr.name}</span>
                  </button>
                ))}
              </div>
            ) : (
              <div style={{ fontFamily:T.font, fontSize:12.5, color:T.inkMute }}>Nincs profil — hozz létre egyet a Statisztika oldalon.</div>
            )}
          </div>
        ) : (
          <React.Fragment>
            {/* Saját sáv */}
            <div style={{ display:'flex', alignItems:'center', gap:9, marginBottom:12 }}>
              <Avatar pr={whoProf} size={30} />
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13.5, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{(whoProf && whoProf.name) || '—'} kártyája</div>
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:10.5, color:T.inkSoft }}>{myMarks.size}/24 kipipálva{myBingos ? ` · ${myBingos} bingó 🏆` : ''}</div>
              </div>
            </div>
            {/* 5×5 rács */}
            <div style={{ display:'grid', gridTemplateColumns:'repeat(5, 1fr)', gap:6 }}>
              {Array.from({ length: 25 }).map((_, c) => {
                const free = c === 12;
                const item = free ? null : BINGO_ITEMS[card[c < 12 ? c : c - 1]];
                const on = free || myMarks.has(c);
                return (
                  <button key={c} data-bingo={c} onClick={() => toggle(c)} style={{ position:'relative', aspectRatio:'1', border:'none', borderRadius:12, cursor: free ? 'default' : 'pointer', background: free ? (T.yellow || '#F4C95A') : on ? T.mint : T.surface, boxShadow: on ? 'none' : T.shadow, padding:3, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:2, overflow:'hidden', WebkitTapHighlightColor:'transparent' }}>
                    <span style={{ fontSize:15, lineHeight:1, opacity: on && !free ? 0.3 : 1 }}>{free ? '🏆' : item.e}</span>
                    <span style={{ fontFamily:T.font, fontWeight:800, fontSize:7.6, lineHeight:1.12, textAlign:'center', color: free ? '#1A2A4A' : on ? 'rgba(255,255,255,0.6)' : T.ink, wordBreak:'break-word' }}>{free ? 'DÖNTŐ' : item.t}</span>
                    {on && !free && <span style={{ position:'absolute', inset:0, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:30, color:'#fff', textShadow:'0 2px 6px rgba(0,0,0,0.25)' }}>✕</span>}
                  </button>
                );
              })}
            </div>
            <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, textAlign:'center', marginTop:10 }}>Koppints a mezőre, ha megtörtént — teljes sor, oszlop vagy átló = BINGÓ! 🍻</div>
            {/* Állás */}
            {board.length > 0 && (
              <div style={{ background:T.surface, borderRadius:16, padding:'12px 14px', boxShadow:T.shadow, marginTop:14 }}>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:9 }}>Állás</div>
                <div style={{ display:'flex', flexDirection:'column', gap:7 }}>
                  {board.map(({ p, n, b }) => (
                    <div key={p.id} style={{ display:'flex', alignItems:'center', gap:8 }}>
                      <Avatar pr={p} size={22} />
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12.5, color:T.ink, flex:1, minWidth:0, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}{p.id === who ? ' (te)' : ''}</span>
                      {b > 0 && <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11.5, color:T.coral }}>{b}× BINGÓ 🏆</span>}
                      <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft }}>{n}/24</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
            {/* Újrakezdés */}
            <button onClick={() => { if (confirmReset) { setMarksAll(prev => ({ ...prev, [who]: [] })); persist([]); prevBingos.current = 0; setConfirmReset(false); } else setConfirmReset(true); }} style={{ width:'100%', marginTop:14, padding:'12px 0', borderRadius:13, border:'none', background: confirmReset ? T.coral : T.surfaceMuted, color: confirmReset ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmReset ? 'Biztos? A kártyád törlődik!' : 'Kártya újrakezdése'}</button>
          </React.Fragment>
        )}
      </div>
      {/* BINGÓ ünneplés */}
      {celebrate && (
        <div onClick={() => setCelebrate(null)} style={{ position:'fixed', top:'calc(-1 * env(safe-area-inset-top))', left:0, right:0, bottom:'calc(-1 * env(safe-area-inset-bottom))', background:'rgba(14,14,24,0.72)', zIndex:70, display:'flex', alignItems:'center', justifyContent:'center', padding:'calc(env(safe-area-inset-top) + 24px) 24px calc(env(safe-area-inset-bottom) + 24px)', boxSizing:'border-box', animation:'fadeIn .2s' }}>
          <div onClick={e => e.stopPropagation()} style={{ background:T.surface, borderRadius:28, padding:'26px 24px 22px', width:'100%', maxWidth:340, display:'flex', flexDirection:'column', alignItems:'center', gap:10, boxShadow:'0 24px 64px rgba(0,0,0,0.3)', animation:'popIn .3s cubic-bezier(.2,.9,.3,1.3)' }}>
            <BottleHero pose="win" size={72} style={{ animation:'floatBob 2.6s ease-in-out infinite' }} />
            <div style={{ fontFamily:T.font, fontWeight:900, fontSize:30, color:T.ink, letterSpacing:'0.04em' }}>BINGÓ! 🏆</div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:13.5, color:T.inkSoft, textAlign:'center' }}>{celebrate}. sorod jött össze — ezt meg kell ünnepelni! 🍻</div>
            <button onClick={() => setCelebrate(null)} style={{ marginTop:6, width:'100%', padding:'13px 0', borderRadius:14, border:'none', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:15, cursor:'pointer' }}>Fenékig! 🍻</button>
          </div>
        </div>
      )}
    </div>
  );
}

'''

src = src.replace(MARKER, BINGO + MARKER)

# ── 2) Router: képernyő + irány ──
rep("  const order = ['home','stats','bar','players','games','play','end','observer'];",
    "  const order = ['home','stats','bingo','bar','players','games','play','end','observer'];")

rep("        {screen==='bar'      && <BarScreen      go={go} deepLink={_barApp} />}",
"""        {screen==='bar'      && <BarScreen      go={go} deepLink={_barApp} />}
        {screen==='bingo'    && <BingoScreen    go={go} />}""")

# ── 3) Főképernyő: VB Bingó banner a Csatlakozás/Quick Game sor alá ──
rep("""                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9.5, color:T.inkSoft }}>{t('quickGameSub')}</span>
              </button>
            </div>""",
"""                <span style={{ fontFamily:T.font, fontWeight:700, fontSize:9.5, color:T.inkSoft }}>{t('quickGameSub')}</span>
              </button>
            </div>
            <button onClick={() => go('bingo')} style={{ position:'relative', overflow:'hidden', display:'flex', alignItems:'center', gap:12, border:'none', background:'linear-gradient(115deg, #1E7A46, #2FA35F 55%, #1E7A46)', borderRadius:18, padding:'13px 16px', cursor:'pointer', boxShadow:'0 4px 0 rgba(20,83,45,0.6), 0 11px 24px rgba(20,83,45,0.35)', transform:'rotate(0.5deg)', WebkitTapHighlightColor:'transparent', textAlign:'left' }}>
              <span style={{ fontSize:26, lineHeight:1 }}>⚽</span>
              <span style={{ flex:1, minWidth:0 }}>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:900, fontSize:15.5, color:'#fff' }}>VB Bingó 🏆</span>
                <span style={{ display:'block', fontFamily:T.font, fontWeight:700, fontSize:10.5, color:'rgba(255,255,255,0.85)', marginTop:1 }}>X-eld ki, ami megtörténik a döntőben!</span>
              </span>
              <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'rgba(255,255,255,0.9)' }}>›</span>
              <span style={{ position:'absolute', right:-18, top:-18, width:70, height:70, border:'2.5px solid rgba(255,255,255,0.16)', borderRadius:'50%', pointerEvents:'none' }} />
              <span style={{ position:'absolute', right:16, bottom:-30, width:60, height:60, border:'2.5px solid rgba(255,255,255,0.1)', borderRadius:'50%', pointerEvents:'none' }} />
            </button>""")

# ── 4) Verziobump ──
rep("const APP_VERSION = 'v9.988';", "const APP_VERSION = 'v9.989';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — VB Bingó applied')
