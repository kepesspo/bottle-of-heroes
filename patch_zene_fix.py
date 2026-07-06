import re
with open('index.html', encoding='utf-8') as f:
    c = f.read()

# ═══ A. getZenePreviewUrl: hálózati hiba ≠ "nincs preview" (ne cache-eljük, ne tiltsuk) ═══
OLD = """      var timer = setTimeout(function() {
        if (!done) { done = true; delete window[cbName]; if (sc.parentNode) sc.parentNode.removeChild(sc); _dzCache[spotifyId] = null; resolve(null); }
      }, 6000);"""
NEW = """      var timer = setTimeout(function() {
        if (!done) { done = true; delete window[cbName]; if (sc.parentNode) sc.parentNode.removeChild(sc); resolve('__ERR__'); }
      }, 6000);"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """      sc.onerror = function() {
        if (!done) { done = true; clearTimeout(timer); delete window[cbName]; _dzCache[spotifyId] = null; resolve(null); }"""
NEW = """      sc.onerror = function() {
        if (!done) { done = true; clearTimeout(timer); delete window[cbName]; resolve('__ERR__'); }"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ B. State deklarációk a useMemo elé (TDZ fix) ═══
OLD = """  const selectedEras   = gameMeta?.zeneConfig?.eras   || [];
  const selectedGenres = gameMeta?.zeneConfig?.genres || [];



  const filteredSongs = React.useMemo(() => {"""
NEW = """  const selectedEras   = gameMeta?.zeneConfig?.eras   || [];
  const selectedGenres = gameMeta?.zeneConfig?.genres || [];

  const [songOffset, setSongOffset] = React.useState(0);
  const [blacklistVersion, setBlacklistVersion] = React.useState(0);
  const [debugOpen, setDebugOpen] = React.useState(false);
  const [allExhausted, setAllExhausted] = React.useState(false);

  const filteredSongs = React.useMemo(() => {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

OLD = """  const [songOffset, setSongOffset] = React.useState(0);
  const [blacklistVersion, setBlacklistVersion] = React.useState(0);
  const [debugOpen, setDebugOpen] = React.useState(false);
  const [allExhausted, setAllExhausted] = React.useState(false);
  const song = (!allExhausted && filteredSongs.length > 0) ? filteredSongs[(gameIdx + songOffset) % filteredSongs.length] : null;"""
NEW = """  const song = (!allExhausted && filteredSongs.length > 0) ? filteredSongs[(gameIdx + songOffset) % filteredSongs.length] : null;"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ C. Skip-számlálók + reset körváltásnál ═══
OLD = """  // Reset offset when turn changes
  React.useEffect(() => { setSongOffset(0); setAllExhausted(false); }, [gameIdx]);"""
NEW = """  const errSkipsRef = React.useRef(0);
  const sessionSkipRef = React.useRef(new Set());

  // Reset offset when turn changes
  React.useEffect(() => { setSongOffset(0); setAllExhausted(false); errSkipsRef.current = 0; sessionSkipRef.current = new Set(); }, [gameIdx]);"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ D. tryNextSong: hiba-skip ≠ tiltólista, kimerülés-érzékelés ═══
OLD = """    const tryNextSong = () => {
      window.markZeneBad && window.markZeneBad(song.spotifyId);
      // Bump blacklistVersion → filteredSongs re-shuffles without this song
      // Reset offset to 0 so we start fresh from the new filtered list
      setBlacklistVersion(v => v + 1);
      setSongOffset(0);
      setAllExhausted(false);
    };"""
NEW = """    const anyPlayableLeft = () => ZENE_SONGS.some(s => {
      if (sessionSkipRef.current.has(s.spotifyId)) return false;
      try { if (localStorage.getItem('znobad_' + s.spotifyId)) return false; } catch(e) {}
      return !(window._zeneBadIds && window._zeneBadIds.has(s.spotifyId));
    });

    // isError=true → hálózati hiba (timeout/offline): NEM kerül végleges tiltólistára
    const tryNextSong = (isError) => {
      if (isError) {
        sessionSkipRef.current.add(song.spotifyId);
        errSkipsRef.current += 1;
      } else {
        window.markZeneBad && window.markZeneBad(song.spotifyId);
      }
      if (errSkipsRef.current >= 6 || !anyPlayableLeft()) {
        setLoading(false);
        setAllExhausted(true);
        return;
      }
      if (isError) {
        setSongOffset(o => o + 1); // lépés a lista következő számára
      } else {
        setBlacklistVersion(v => v + 1); // újraszűrés a tiltott szám nélkül
        setSongOffset(0);
      }
    };"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# a lassú-betöltés timeout hiba-skipnek számít, nem tiltásnak
OLD = "    const skipTimer = setTimeout(tryNextSong, isCached ? 2000 : 4000);"
NEW = "    const skipTimer = setTimeout(() => tryNextSong(true), isCached ? 2000 : 4000);"
assert OLD in c
c = c.replace(OLD, NEW, 1)

# __ERR__ kezelés a preview válasznál
OLD = """    window.getZenePreviewUrl(song.spotifyId, song.artist, song.title).then(url => {
      clearTimeout(skipTimer);
      if (url) {"""
NEW = """    window.getZenePreviewUrl(song.spotifyId, song.artist, song.title).then(url => {
      clearTimeout(skipTimer);
      if (url === '__ERR__') { tryNextSong(true); return; }
      if (url) {"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ E. Lejárt/hibás audio URL kezelése ═══
OLD = """        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)} />"""
NEW = """        <audio ref={audioRef} src={previewUrl}
          onPlay={() => setPlaying(true)}
          onPause={() => setPlaying(false)}
          onEnded={() => setPlaying(false)}
          onError={() => {
            // lejárt/hibás preview URL — cache törlés és következő szám
            try { localStorage.removeItem('zdz_' + (song?.spotifyId || '')); } catch(e) {}
            setPreviewUrl(null); setLoading(true);
            sessionSkipRef.current.add(song?.spotifyId);
            setSongOffset(o => o + 1);
          }} />"""
assert OLD in c
c = c.replace(OLD, NEW, 1)

# ═══ F. Kimerült állapot: Újrapróbálás + Kihagyás gombok ═══
OLD = """        {allExhausted ? (
          <div style={{ width:'100%', padding:'14px 0', borderRadius:16, display:'flex', alignItems:'center', justifyContent:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft }}>😕 Nincs elérhető szám ebben a szűrőben</span>
          </div>
        ) : loading ? ("""
NEW = """        {allExhausted ? (
          <div style={{ width:'100%', display:'flex', flexDirection:'column', gap:8, alignItems:'center' }}>
            <span style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, padding:'4px 0', textAlign:'center' }}>😕 Nem sikerült számot betölteni — nincs net, vagy elfogytak a számok</span>
            <div style={{ display:'flex', gap:8, width:'100%' }}>
              <button onClick={() => { sessionSkipRef.current = new Set(); errSkipsRef.current = 0; setAllExhausted(false); setLoading(true); setSongOffset(o => o + 1); setBlacklistVersion(v => v + 1); }}
                style={{ flex:1, padding:'13px 0', background:T.blue, border:'none', borderRadius:16, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>🔄 Újrapróbálás</button>
              <button onClick={() => { if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } }}
                style={{ flex:1, padding:'13px 0', background:T.surface, border:`1.5px solid ${T.inkMute}40`, borderRadius:16, color:T.ink, fontFamily:T.font, fontWeight:700, fontSize:15, cursor:'pointer' }}>Kihagyás →</button>
            </div>
          </div>
        ) : loading ? ("""
assert OLD in c
c = c.replace(OLD, NEW, 1)

c = re.sub(r'v9\.785', 'v9.786', c, count=2)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print("Done v9.786")
