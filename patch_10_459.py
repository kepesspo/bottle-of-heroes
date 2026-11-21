# v10.459 — Gender Reveal: a hang ELŐRE, a leleplezés előtt dől el — nincs nagy „Hang bekapcsolása" gomb
#  - a vetítő SAJÁT, állandó <video>/<audio> elemet tart (nem a show mountolja), és minden
#    koppintásnál / betöltésnél csendben kipróbálja, megy-e hanggal (élesítés)
#  - a bal alsó szervezői csipben 🔊/🔇 jelzi az állapotot
#  - újratöltött vetítőn (nincs még koppintás) egy „Vetítő indítása" kapu kéri az egy kattintást
#  - ha a leleplezéskor mégsem engedné: némítva megy, a nagy gomb helyett csak egy kis jel
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.458';", "const APP_VERSION = 'v10.459';")

# ── RevealShow: a vetítő állandó elemeit használja ─────────────────────────────
rep("function RevealShow({ show, video, music, onDone, onLand, volume }) {",
    "function RevealShow({ show, video, music, onDone, onLand, volume, vEl, aEl }) {")
rep("  const vref = React.useRef(null), vBad = React.useRef(false), fadeRef = React.useRef(null), landed = React.useRef(false);",
"""  // v10.459: a <video> a VETÍTŐÉ (`vEl`), nem a show-é — azt a vetítő már a leleplezés ELŐTT
  // élesítette egy koppintással, így a „0"-nál hanggal indul, interakció nélkül.
  const ownV = React.useRef(null);
  const vref = vEl || ownV, vBad = React.useRef(false), fadeRef = React.useRef(null), landed = React.useRef(false);""")
rep("""      const a = new Audio(music); musRef.current = a; a.volume = vol;""",
"""      const own = aEl && aEl.current, a = (own && own.getAttribute('src')) ? own : new Audio(music); musRef.current = a;
      try { a.currentTime = 0; } catch(e) {} a.muted = false; a.volume = vol;""")
rep("""    return () => { clearInterval(iv); clearInterval(fiv); const a = musRef.current; if (a) try { a.pause(); } catch(e) {} };
  }, []);""",
"""    return () => { clearInterval(iv); clearInterval(fiv); const a = musRef.current; if (a) try { a.pause(); } catch(e) {} };
  }, []);
  // a vetítő állandó <video>-ja: a régi (link-alapú) videónál itt kapja meg a forrást, és a
  // vég / hiba eseményt is itt kötjük rá. Lebontáskor megáll és elrejtőzik.
  const finRef = React.useRef(null); finRef.current = finishVideo;
  React.useEffect(() => {
    const v = vref.current; if (!v || !vidSrc) return;
    if (v.getAttribute('src') !== vidSrc) { v.setAttribute('src', vidSrc); try { v.load(); } catch(e) {} }
    else if (v.error) vBad.current = true;
    const onEnd = () => finRef.current && finRef.current();
    const onErr = () => { vBad.current = true; setStage(st => st === 'video' ? 'boom' : st); };
    v.addEventListener('ended', onEnd); v.addEventListener('error', onErr);
    return () => { v.removeEventListener('ended', onEnd); v.removeEventListener('error', onErr); try { v.pause(); } catch(e) {} v.style.display = 'none'; };
  }, []);""")
rep("""    const v = vref.current; if (!v) { setStage('boom'); return; }
    try { v.currentTime = 0; } catch(e) {}""",
"""    const v = vref.current; if (!v) { setStage('boom'); return; }
    v.style.display = 'block';
    try { v.currentTime = 0; } catch(e) {}""")
rep("    return () => cancelAnimationFrame(raf);\n  }, [stage]);",
    "    return () => { cancelAnimationFrame(raf); v.style.display = 'none'; };\n  }, [stage]);")
rep("background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : stage === 'outro' ? 'transparent' : REVEAL_PAPER, transition:'background .5s' }}>",
    "background: stage === 'boom' ? `radial-gradient(circle at 50% 55%, ${R.c2}, ${R.c1} 70%)` : (stage === 'outro' || stage === 'video') ? 'transparent' : REVEAL_PAPER, transition:'background .5s' }}>")
rep("""      {vidSrc && (
        <video ref={vref} data-reveal-video src={vidSrc} preload="auto" playsInline onEnded={finishVideo}
          onError={() => { vBad.current = true; if (stage === 'video') setStage('boom'); }}
          style={{ position:'absolute', inset:0, width:'100%', height:'100%', objectFit:'contain', background:'#000', display: stage === 'video' ? 'block' : 'none' }} />
      )}
""", "")
rep("""      {stage === 'video' && muted && (
        // ⚠️ Hang NÉLKÜL nem mehet le: ha a böngésző nem engedte a hangos indítást, nagy gomb középen
        <button data-reveal-unmute onClick={() => { const v = vref.current; if (v) { v.muted = false; v.volume = vol; v.play().catch(() => {}); } setMuted(false); }}
          style={{ position:'absolute', left:'50%', top:'50%', transform:'translate(-50%,-50%)', padding:'18px 30px', borderRadius:999, border:'none', cursor:'pointer', background:'#fff', color:'#1B1830',
            fontFamily:T.font, fontWeight:900, fontSize:'clamp(18px, 3vh, 30px)', boxShadow:'0 10px 40px rgba(0,0,0,0.45)', animation:'revealBeat 1.4s ease-in-out infinite' }}>🔊 Hang bekapcsolása</button>
      )}""",
"""      {stage === 'video' && muted && (
        // v10.459: NINCS nagy gomb a videó közepén — a hangot a vetítő a leleplezés ELŐTT élesíti.
        // Ha mégis némítva indult, csak egy kis, halk jel a bal alsó sarokban (a szervezőnek).
        <button data-reveal-unmute aria-label="Hang bekapcsolása" onClick={() => { const v = vref.current; if (v) { v.muted = false; v.volume = vol; v.play().catch(() => {}); } setMuted(false); }}
          style={{ position:'absolute', left:18, bottom:18, padding:'5px 10px', borderRadius:999, border:'none', cursor:'pointer', background:'rgba(255,255,255,0.16)', color:'#fff', opacity:0.7,
            fontFamily:T.font, fontWeight:800, fontSize:12 }}>🔇</button>
      )}""")

# ── vetítő: állandó médiaelemek + élesítés + állapot ─────────────────────────────
rep("""  // v10.458: a böngésző CSAK felhasználói koppintás után enged hangos lejátszást. Ha a vetítő
  // oldalát újratöltötték és még senki nem nyúlt hozzá, a szervezői csip szól (`data-reveal-needtap`).
  const [needTap, setNeedTap] = React.useState(() => { try { return !!(navigator.userActivation && !navigator.userActivation.hasBeenActive); } catch(e) { return false; } });
  React.useEffect(() => {
    if (!needTap) return;
    const off = () => setNeedTap(false);
    addEventListener('pointerdown', off, true); addEventListener('keydown', off, true);
    return () => { removeEventListener('pointerdown', off, true); removeEventListener('keydown', off, true); };
  }, [needTap]);""",
"""  // v10.459: a böngésző CSAK felhasználói koppintás után enged hangos lejátszást (Safarin
  // ráadásul elemenként). Ezért a vetítő SAJÁT, állandó <video>/<audio> elemet tart, és minden
  // koppintásnál, illetve amikor a média betöltött, csendben kipróbálja: megy-e hanggal
  // (hangerő 0, azonnal megállítva). Az eredmény (`snd[src]`) a bal alsó csipben látszik.
  const vEl = React.useRef(null), aEl = React.useRef(null), showRef = React.useRef(null);
  const [snd, setSnd] = React.useState({});
  const [activated, setActivated] = React.useState(() => { try { return !navigator.userActivation || navigator.userActivation.hasBeenActive; } catch(e) { return true; } });
  const probeEl = el => {
    if (!el || showRef.current) return;
    const src = el.getAttribute('src'); if (!src || !el.paused) return;
    el.muted = false; el.volume = 0;
    let p; try { p = el.play(); } catch(e) { p = null; }
    const done = ok => { if (!showRef.current) { try { el.pause(); el.currentTime = 0; } catch(e) {} } el.volume = 1; setSnd(m => m[src] === ok ? m : Object.assign({}, m, { [src]: ok })); };
    if (p && p.then) p.then(() => done(true), () => done(false)); else done(false);
  };
  const probeAll = () => { probeEl(vEl.current); probeEl(aEl.current); };
  React.useEffect(() => {
    const on = () => { setActivated(true); probeAll(); };
    addEventListener('pointerdown', on, true); addEventListener('keydown', on, true);
    return () => { removeEventListener('pointerdown', on, true); removeEventListener('keydown', on, true); };
  }, []);""")
rep("  const music = useRevealVideo('revealAudio');             // v10.458: a visszaszámlálás zenéje",
"""  const music = useRevealVideo('revealAudio');             // v10.458: a visszaszámlálás zenéje
  const medSrcs = [video.url, music.url].filter(Boolean);
  const soundOk = medSrcs.length > 0 && medSrcs.every(u => snd[u] === true);""")
rep("""          {needTap && (video.url || music.url) && <span data-reveal-needtap style={{ color:'#A3342C' }}><span aria-hidden="true" style={{ opacity:0.35, color:REVEAL_INK }}> · </span>🔇 koppints egyet a hangért</span>}""",
"""          {medSrcs.length > 0 && <span data-reveal-sound={soundOk ? 'ok' : 'off'} title={soundOk ? 'A videó / zene hanggal fog menni' : 'Kattints egyet a vetítőn, hogy legyen hang'} style={{ color: soundOk ? '#1F6B50' : '#A3342C' }}>
            <span aria-hidden="true" style={{ opacity:0.35, color:REVEAL_INK }}>· </span>{soundOk ? '🔊 hang kész' : '🔇 kattints egyet a hangért'}</span>}""")
rep("""      {show && <RevealShow key={show.run} show={show} video={video && video.url} music={music && music.url} volume={revealVolOf(ctl.v)} onDone={finishShow}""",
"""      {/* v10.459: a vetítő ÁLLANDÓ médiaelemei (a show használja őket) — így a hang a leleplezés
          ELŐTT élesíthető. A videó a show „video" szakaszában válik láthatóvá (a show kapcsolja). */}
      <video ref={vEl} data-reveal-video src={video.url || undefined} preload="auto" playsInline onLoadedData={e => probeEl(e.currentTarget)}
        style={{ position:'absolute', inset:0, width:'100%', height:'100%', objectFit:'contain', background:'#000', zIndex:39, display:'none' }} />
      <audio ref={aEl} data-reveal-musicel src={music.url || undefined} preload="auto" onLoadedData={e => probeEl(e.currentTarget)} />
      {!activated && !show && medSrcs.length > 0 && (
        // újratöltött vetítő, még senki nem nyúlt hozzá: EGY kattintás most, hogy később ne kelljen
        <button data-reveal-startgate onClick={() => { setActivated(true); probeAll(); try { if (!document.fullscreenElement) document.documentElement.requestFullscreen(); } catch(e) {} }}
          style={{ position:'absolute', inset:0, zIndex:80, border:'none', cursor:'pointer', background:'rgba(255,248,240,0.94)', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', gap:14, fontFamily:T.font, color:REVEAL_INK }}>
          <span style={{ fontSize:'min(12vh, 90px)' }}>▶</span>
          <span style={{ fontWeight:900, fontSize:'clamp(22px, 4vh, 44px)' }}>Vetítő indítása</span>
          <span style={{ fontWeight:700, fontSize:'clamp(13px, 1.9vh, 20px)', opacity:0.7 }}>Egy kattintás, hogy a leleplezés hanggal menjen</span>
        </button>
      )}
      {show && <RevealShow key={show.run} show={show} video={video && video.url} music={music && music.url} volume={revealVolOf(ctl.v)} onDone={finishShow} vEl={vEl} aEl={aEl}""")
# a showRef kövesse a show-t (a próba ne állítsa meg a már induló leleplezést)
rep("  const finishShow = () => { setShow(s => {", "  showRef.current = show;\n  const finishShow = () => { setShow(s => {")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
