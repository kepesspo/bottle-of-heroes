# v10.462 — Gender Reveal: élő vetítés-link azoknak, akik nem tudnak eljönni
#  - ?screen=reveal&live=<liveKey> → jelszó nélkül, CSAK a vetítő (nézőként)
#  - a néző semmit nem ír: nincs időzített indítás, nincs szünet/kvíz-lapozás billentyűvel,
#    nincs kulcs-pótlás, nincs ‹ Vissza, nem látszik a jóváhagyásra várók száma
#  - telefonon is vetít (a buli telefonos „Vetítő" szerepe tájékoztató marad)
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.461';", "const APP_VERSION = 'v10.462';")

# ── kulcs + URL ──
rep("""function revealEnsureKeys(cfg) {
  if (!cfg || (cfg.guestKey && cfg.albumKey)) return;
  const db = revealDb(); if (!db) return;
  const patch = {}; if (!cfg.guestKey) patch.guestKey = revealKeyGen(); if (!cfg.albumKey) patch.albumKey = revealKeyGen();""",
"""function revealEnsureKeys(cfg) {
  if (!cfg || (cfg.guestKey && cfg.albumKey && cfg.liveKey)) return;
  const db = revealDb(); if (!db) return;
  const patch = {}; if (!cfg.guestKey) patch.guestKey = revealKeyGen(); if (!cfg.albumKey) patch.albumKey = revealKeyGen();
  if (!cfg.liveKey) patch.liveKey = revealKeyGen();   // v10.462: élő vetítés-link""")
rep("function revealAlbumUrl(cfg) { return cfg && cfg.albumKey ? revealBaseUrl() + '?screen=reveal&album=' + cfg.albumKey : ''; }",
    "function revealAlbumUrl(cfg) { return cfg && cfg.albumKey ? revealBaseUrl() + '?screen=reveal&album=' + cfg.albumKey : ''; }\n"
    "// v10.462: akik nem tudnak eljönni — csak a vetítő, élőben, jelszó nélkül, nézőként\n"
    "function revealLiveUrl(cfg) { return cfg && cfg.liveKey ? revealBaseUrl() + '?screen=reveal&live=' + cfg.liveKey : ''; }")

# ── a vetítő néző-módja ──
rep("function RevealProjector({ title, cfg, onExit }) {",
    "// v10.462: `watch` = az élő vetítés-link nézője. Ugyanazt látja, de SEMMIT nem ír a közös\n"
    "// dokumentumokba (nem indít időzített leleplezést, nem állít szünetet, nem lapoz kvízt).\n"
    "function RevealProjector({ title, cfg, onExit, watch }) {")
rep("  const pendingN = allItems.filter(p => p.pending).length;",
    "  const pendingN = watch ? 0 : allItems.filter(p => p.pending).length;   // a várakozók száma a szervezőké")
rep("  const togglePause = () => { const v = !pausedRef.current; setPaused(v); revealCtlWrite({ paused:v }); };",
    "  const togglePause = () => { if (watch) return; const v = !pausedRef.current; setPaused(v); revealCtlWrite({ paused:v }); };")
rep("  React.useEffect(() => { if (cfg) revealEnsureKeys(cfg); }, [cfg && cfg.guestKey, cfg && cfg.albumKey, !!cfg]);",
    "  React.useEffect(() => { if (cfg && !watch) revealEnsureKeys(cfg); }, [cfg && cfg.guestKey, cfg && cfg.albumKey, !!cfg]);")
rep("""    const v = rstate.v || {};
    if (v.phase !== 'armed' || !v.run || firedRef.current === v.run) return;""",
"""    const v = rstate.v || {};
    if (watch) return;   // v10.462: az időzített indítást a buli vetítője végzi, nem a távoli néző
    if (v.phase !== 'armed' || !v.run || firedRef.current === v.run) return;""")
rep("""      if (e.key === 'ArrowRight') { if (qz.on) qz.step(1); else seq.next(); }
      else if (e.key === 'ArrowLeft') { if (qz.on) qz.step(-1); }
      else if (e.key === ' ') { e.preventDefault(); if (qz.on) qz.step(1); else togglePause(); }
      else if (e.key === 'f' || e.key === 'F') toggleFs();""",
"""      if (e.key === 'f' || e.key === 'F') { toggleFs(); return; }
      if (watch) return;   // v10.462: a néző nem lapozza a közös kvízt és nem állít szünetet
      if (e.key === 'ArrowRight') { if (qz.on) qz.step(1); else seq.next(); }
      else if (e.key === 'ArrowLeft') { if (qz.on) qz.step(-1); }
      else if (e.key === ' ') { e.preventDefault(); if (qz.on) qz.step(1); else togglePause(); }""")
rep("<div ref={rootRef} data-reveal-projector data-reveal-current=",
    "<div ref={rootRef} data-reveal-projector data-reveal-watch={watch ? '1' : '0'} data-reveal-current=")
rep("""        <button data-reveal-exit onClick={() => { try { if (document.fullscreenElement) document.exitFullscreen(); } catch(e) {} onExit(); }} aria-label="Vissza" style={chip(false)}>‹ Vissza</button>""",
"""        {watch ? <span data-reveal-livebadge style={{ flexShrink:0, whiteSpace:'nowrap', display:'inline-flex', alignItems:'center', gap:6, fontFamily:T.font, fontWeight:900, fontSize: narrow ? 12 : 13, color:'#A3342C' }}>
            <span aria-hidden="true" style={{ width:8, height:8, borderRadius:99, background:'#E0453B' }} />ÉLŐ</span>
          : <button data-reveal-exit onClick={() => { try { if (document.fullscreenElement) document.exitFullscreen(); } catch(e) {} onExit(); }} aria-label="Vissza" style={chip(false)}>‹ Vissza</button>}""")
rep("""          <span style={{ fontWeight:900, fontSize:'clamp(22px, 4vh, 44px)' }}>Vetítő indítása</span>
          <span style={{ fontWeight:700, fontSize:'clamp(13px, 1.9vh, 20px)', opacity:0.7 }}>Egy kattintás, hogy a leleplezés hanggal menjen</span>""",
"""          <span style={{ fontWeight:900, fontSize:'clamp(22px, 4vh, 44px)' }}>{watch ? 'Élő vetítés indítása' : 'Vetítő indítása'}</span>
          <span style={{ fontWeight:700, fontSize:'clamp(13px, 1.9vh, 20px)', opacity:0.7, padding:'0 16px' }}>{watch ? (title || 'Gender Reveal') + ' · koppints, hogy a leleplezést hanggal lásd' : 'Egy kattintás, hogy a leleplezés hanggal menjen'}</span>""")

# ── belépés a linkkel ──
rep("  const albumParam = React.useMemo(() => revealParam('album'), []);",
    "  const albumParam = React.useMemo(() => revealParam('album'), []);\n"
    "  const liveParam = React.useMemo(() => revealParam('live'), []);")
rep("""  if ((gParam || albumParam) && cfg.loaded) {
    const v = cfg.v || {};""",
"""  if ((gParam || albumParam || liveParam) && cfg.loaded) {
    const v = cfg.v || {};
    // v10.462: élő vetítés-link — telefonon is vetít (nem a buli „Vetítő" szerepének tájékoztatója)
    if (liveParam && v.liveKey && liveParam === v.liveKey) return <RevealProjector watch title={title} cfg={v} onExit={() => {}} />;""")

# ── Szülők → Esemény: a harmadik link ──
rep("""        {linkRow('Galéria-link', 'Csak nézhető · a buli után', revealAlbumUrl(v), 'data-reveal-p-albumurl', 'gallery', 'pink')}""",
"""        {linkRow('Élő vetítés', 'Akik nem tudnak eljönni · csak a vetítő, élőben', revealLiveUrl(v), 'data-reveal-p-liveurl', 'video', 'warn')}
        {linkRow('Galéria-link', 'Csak nézhető · a buli után', revealAlbumUrl(v), 'data-reveal-p-albumurl', 'gallery', 'pink')}""")
rep("React.useEffect(() => { if (cfg.loaded) revealEnsureKeys(cfg.v || {}); }, [cfg.loaded, cfg.v && cfg.v.guestKey, cfg.v && cfg.v.albumKey]);",
    "React.useEffect(() => { if (cfg.loaded) revealEnsureKeys(cfg.v || {}); }, [cfg.loaded, cfg.v && cfg.v.guestKey, cfg.v && cfg.v.albumKey, cfg.v && cfg.v.liveKey]);")
rep("set({ guestKey: revealKeyGen(), albumKey: revealKeyGen() }, { merge:true }).then(() => flash('Új linkek kész'))",
    "set({ guestKey: revealKeyGen(), albumKey: revealKeyGen(), liveKey: revealKeyGen() }, { merge:true }).then(() => flash('Új linkek kész'))")
rep("A mostani vendég-link és QR-kód, valamint a galéria-link megszűnik.",
    "A mostani vendég-link és QR-kód, az élő vetítés-link és a galéria-link is megszűnik.")
rep("//   config/revealConfig    = { password, title, guestKey, albumKey }",
    "//   config/revealConfig    = { password, title, guestKey, albumKey, liveKey }")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
