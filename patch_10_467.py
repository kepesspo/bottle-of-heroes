# v10.467 — Gender Reveal: választható visszaszámlálás (Szülők → Leleplezés)
#  - 10 mp: a mostani óra-zene (REVEAL_DEFAULT_MUSIC)
#  - 20 mp: „Legyen Ön is milliomos" (assets/reveal_countdown_milliomos.mp3), a vetítő 20-tól számol
#  - a beállítás a közös config/revealProjector.countdown (hiányzó = 10); a vetítő CSAK olvassa
#  - az időzített indítás is a választott hosszal előbb indul, hogy a „0" az időpontra essen
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.466';", "const APP_VERSION = 'v10.467';")

rep("const REVEAL_COUNT_FROM = 10;",
"""const REVEAL_COUNT_FROM = 10;
// v10.467: a visszaszámlálás hossza választható (Szülők → Leleplezés), és mindkettőhöz saját
// beépített zene tartozik. A beállítás a config/revealProjector.countdown (hiányzó = 10).
const REVEAL_COUNTDOWNS = [
  { s:10, music:'assets/reveal_countdown_music.mp3',     name:'Óra' },
  { s:20, music:'assets/reveal_countdown_milliomos.mp3', name:'Legyen Ön is milliomos' },
];
function revealCountdownOf(v) { const n = +((v || {}).countdown); return REVEAL_COUNTDOWNS.find(c => c.s === n) || REVEAL_COUNTDOWNS[0]; }""")

# ── a beépített zene a választott visszaszámláláshoz ──
rep("""function useRevealMusic() {
  const up = useRevealVideo('revealAudio');
  const useDef = up.metaLoaded && !up.has && !up.uploading;
  const [def, setDef] = React.useState({ url:null, loading:false });
  React.useEffect(() => {
    if (!useDef || def.url) return;
    let dead = false; setDef({ url:null, loading:true, pct:0 });
    fetch(REVEAL_DEFAULT_MUSIC).then(r => { if (!r.ok) throw new Error('http'); return r.blob(); })
      .then(b => { if (!dead) setDef({ url: URL.createObjectURL(b.type ? b : new Blob([b], { type:'audio/mpeg' })), loading:false, pct:100, builtin:true }); })
      .catch(() => { if (!dead) setDef({ url: REVEAL_DEFAULT_MUSIC, loading:false, pct:100, builtin:true }); });
    return () => { dead = true; };
  }, [useDef]);
  return useDef ? def : up;
}""",
"""// v10.467: `path` = a választott visszaszámlálás beépített zenéje — váltáskor újratölt.
function useRevealMusic(path) {
  path = path || REVEAL_DEFAULT_MUSIC;
  const up = useRevealVideo('revealAudio');
  const useDef = up.metaLoaded && !up.has && !up.uploading;
  const [def, setDef] = React.useState({ url:null, loading:false });
  React.useEffect(() => {
    if (!useDef || (def.url && def.path === path)) return;
    let dead = false, made = '';
    setDef({ url:null, loading:true, pct:0, path });
    fetch(path).then(r => { if (!r.ok) throw new Error('http'); return r.blob(); })
      .then(b => { if (dead) return; made = URL.createObjectURL(b.type ? b : new Blob([b], { type:'audio/mpeg' })); setDef({ url: made, loading:false, pct:100, builtin:true, path }); })
      .catch(() => { if (!dead) setDef({ url: path, loading:false, pct:100, builtin:true, path }); });
    return () => { dead = true; };
  }, [useDef, path]);
  // a régi blob felszabadítása, ha a zene cserélődött
  const prevBlob = React.useRef('');
  React.useEffect(() => { const u = def.url || ''; if (prevBlob.current && prevBlob.current !== u && /^blob:/.test(prevBlob.current)) { try { URL.revokeObjectURL(prevBlob.current); } catch(e) {} } prevBlob.current = u; }, [def.url]);
  return useDef ? def : up;
}""")

# ── a show a választott hosszal számol ──
rep("function RevealShow({ show, video, music, onDone, onLand, volume, vEl, aEl }) {",
    "function RevealShow({ show, video, music, onDone, onLand, volume, vEl, aEl, countFrom }) {\n"
    "  const CF = [10, 20].includes(+countFrom) ? +countFrom : REVEAL_COUNT_FROM;   // v10.467: 10 vagy 20 mp")
rep("  const [n, setN] = React.useState(REVEAL_COUNT_FROM);", "  const [n, setN] = React.useState(CF);")
rep("    const total = REVEAL_COUNT_FROM * sp, fade = Math.min(1.2, total / 4), t0 = performance.now();",
    "    const total = CF * sp, fade = Math.min(1.2, total / 4), t0 = performance.now();")
rep("    let k = REVEAL_COUNT_FROM;\n", "    let k = CF;\n")

# ── a vetítő ──
rep("  const music = useRevealMusic();                          // v10.458: a visszaszámlálás zenéje (v10.461: beépített is)",
    "  const cdown = revealCountdownOf(ctl.v);                  // v10.467: 10 vagy 20 mp, saját beépített zenével\n"
    "  const music = useRevealMusic(cdown.music);               // v10.458: a visszaszámlálás zenéje (v10.461: beépített is)")
rep("    if (revealAt && now < revealAt - REVEAL_COUNT_FROM * 1000 * revealSpeed()) return;",
    "    if (revealAt && now < revealAt - cdown.s * 1000 * revealSpeed()) return;   // v10.467: a választott hossz")
rep("  }, [rstate, now, revealAt]);", "  }, [rstate, now, revealAt, cdown.s]);")
rep("volume={revealVolOf(ctl.v)} onDone={finishShow} vEl={vEl} aEl={aEl}",
    "volume={revealVolOf(ctl.v)} countFrom={cdown.s} onDone={finishShow} vEl={vEl} aEl={aEl}")
rep("  // ⚠️ A nagy 10-es visszaszámlálás az időpont ELŐTT 10 mp-cel indul, hogy a „0\" pont az",
    "  // ⚠️ A nagy (10 vagy 20 mp-es) visszaszámlálás az időpont ELŐTT ennyivel indul, hogy a „0\" pont az")

# ── Szülők → Leleplezés: a választó ──
rep("""        <RevealMusicRow />
""", """        <RevealCountdownRow />
        <RevealMusicRow />
""")
rep("""function RevealVideoRow() { return <RevealMediaRow />; }""",
"""function RevealVideoRow() { return <RevealMediaRow />; }
// v10.467: a visszaszámlálás hossza — 10 mp (óra) vagy 20 mp (Legyen Ön is milliomos). A vetítő
// ennyitől számol vissza, és a választott beépített zene szól (feltöltött saját zene felülírja).
function RevealCountdownRow() {
  const ctl = useRevealDoc('revealProjector');
  const [msg, flash] = useRevealFlash();
  const cur = revealCountdownOf(ctl.v);
  return rvRow({ tight:true, data:{ 'data-reveal-p-countrow':'', 'data-cur': String(cur.s) },
    label: <span>Visszaszámlálás{msg ? <span style={{ display:'block', marginTop:2 }}>{rvMsg(msg)}</span> : <span style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>{cur.s} mp · {cur.name}</span>}</span>,
    right: rvSeg(REVEAL_COUNTDOWNS.map(c => ({ v:c.s, t: c.s + ' mp' })), cur.s, n => { revealCtlWrite({ countdown:n }); flash('Mentve'); }, 'data-reveal-p-countfrom', 'Visszaszámlálás hossza') });
}""")
rep("""function RevealMusicRow() {
  return <RevealMediaRow coll="revealAudio" dp="music" icon="timer" title="Visszaszámlálás zenéje" accept="audio/*" max={REVEAL_MUSIC_MAX} what="A zene"
    emptyText="Beépített visszaszámláló zene" """,
"""function RevealMusicRow() {
  const ctl = useRevealDoc('revealProjector'), cur = revealCountdownOf(ctl.v);   // v10.467
  return <RevealMediaRow coll="revealAudio" dp="music" icon="timer" title="Visszaszámlálás zenéje" accept="audio/*" max={REVEAL_MUSIC_MAX} what="A zene"
    emptyText={'Beépített: ' + cur.name} """)

rep("//   config/revealConfig    = { password, title, guestKey, albumKey, liveKey }",
    "//   config/revealConfig    = { password, title, guestKey, albumKey, liveKey }\n"
    "//   config/revealProjector.countdown = 10 | 20  (v10.467: a visszaszámlálás hossza)")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
