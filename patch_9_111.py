#!/usr/bin/env python3
"""patch_9_111.py — Fix crash: song undefined when filteredSongs empty during check"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.110';" in content
content = content.replace("const APP_VERSION = 'v9.110';", "const APP_VERSION = 'v9.111';")

# ── Fix: guard song/nextSong + useEffect ────────────────────────
OLD_SONG_DEFS = """  const song     = filteredSongs[gameIdx % filteredSongs.length];
  const nextSong = filteredSongs[(gameIdx + 1) % filteredSongs.length];

  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [skipped, setSkipped] = React.useState(false);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setSkipped(false);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    window.getSpotifyCCToken().then(token => {
      if (!token) { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } return; }
      fetch('https://api.spotify.com/v1/tracks/' + song.spotifyId + '?market=US', {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(r => r.json()).then(d => {
        const url = d.preview_url || null;
        if (url) { setPreviewUrl(url); setLoading(false); }
        else { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } }
      }).catch(() => { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } });
    });

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song.spotifyId]);"""

NEW_SONG_DEFS = """  const song     = filteredSongs.length > 0 ? filteredSongs[gameIdx % filteredSongs.length] : null;
  const nextSong = filteredSongs.length > 0 ? filteredSongs[(gameIdx + 1) % filteredSongs.length] : null;

  const [playing, setPlaying] = React.useState(false);
  const [revealed, setRevealed] = React.useState(false);
  const [previewUrl, setPreviewUrl] = React.useState(null);
  const [loading, setLoading] = React.useState(true);
  const [skipped, setSkipped] = React.useState(false);
  const audioRef    = React.useRef(null);
  const advancedRef = React.useRef(false);

  React.useEffect(() => {
    if (!song) return;
    setPlaying(false);
    setRevealed(false);
    setLoading(true);
    setSkipped(false);
    setPreviewUrl(null);
    advancedRef.current = false;
    if (audioRef.current) { audioRef.current.pause(); audioRef.current.src = ''; }

    window.getSpotifyCCToken().then(token => {
      if (!token) { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } return; }
      fetch('https://api.spotify.com/v1/tracks/' + song.spotifyId + '?market=US', {
        headers: { 'Authorization': 'Bearer ' + token }
      }).then(r => r.json()).then(d => {
        const url = d.preview_url || null;
        if (url) { setPreviewUrl(url); setLoading(false); }
        else { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } }
      }).catch(() => { setLoading(false); setSkipped(true); if (!advancedRef.current) { advancedRef.current = true; onAdvance && onAdvance({}, {}); } });
    });

    return () => { if (audioRef.current) audioRef.current.pause(); };
  }, [song?.spotifyId]);"""

assert OLD_SONG_DEFS in content, "song defs block not found"
content = content.replace(OLD_SONG_DEFS, NEW_SONG_DEFS, 1)

# ── Fix: handlePlay/handleStop/handleResult guard song ───────────
OLD_HANDLE_PLAY = """  const handlePlay = () => {
    if (!audioRef.current || !previewUrl) return;
    audioRef.current.currentTime = song.start || 0;"""

NEW_HANDLE_PLAY = """  const handlePlay = () => {
    if (!audioRef.current || !previewUrl || !song) return;
    audioRef.current.currentTime = song.start || 0;"""

assert OLD_HANDLE_PLAY in content
content = content.replace(OLD_HANDLE_PLAY, NEW_HANDLE_PLAY, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.111 ready")
