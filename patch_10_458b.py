# v10.458b — Gender Reveal: saját ZENE a visszaszámlálásra (a dobpergés helyett), ugyanazon a darabolt úton
import re
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

# ── a darabolt feltöltés/letöltés általános lesz: `coll` = gyűjtemény ÉS a config/<coll> meta ──
rep("function revealWipeVideo(db) { return db.collection('revealVideo').get()",
    "const REVEAL_MUSIC_MAX = 20 * 1024 * 1024;   // v10.458: a visszaszámlálás zenéje (pár perces mp3 is bőven belefér)\n"
    "function revealWipeVideo(db, coll) { return db.collection(coll || 'revealVideo').get()")
rep("""function revealUploadVideo(file, onProg) {
  const db = revealDb(); if (!db) return Promise.reject(new Error('nincs adatbázis'));
  if (file.size > REVEAL_VIDEO_MAX) return Promise.reject(new Error('A videó legfeljebb ' + Math.round(REVEAL_VIDEO_MAX / 1048576) + ' MB lehet'));
  const vid = revealToken(), meta = db.collection('config').doc('revealVideo');
  return meta.set({ vid:null, uploading:true, at:Date.now() })
    .then(() => revealWipeVideo(db))""",
"""function revealUploadVideo(file, onProg, coll, max, what) {
  coll = coll || 'revealVideo'; max = max || REVEAL_VIDEO_MAX; what = what || 'A videó';
  const db = revealDb(); if (!db) return Promise.reject(new Error('nincs adatbázis'));
  if (file.size > max) return Promise.reject(new Error(what + ' legfeljebb ' + Math.round(max / 1048576) + ' MB lehet'));
  const vid = revealToken(), meta = db.collection('config').doc(coll);
  return meta.set({ vid:null, uploading:true, at:Date.now() })
    .then(() => revealWipeVideo(db, coll))""")
rep(".then(b => { const d = revealB64(new Uint8Array(b)); return revealRetry(() => db.collection('revealVideo').doc(revealVideoPartId(vid, i)).set({ vid, i, d }), 3); })",
    ".then(b => { const d = revealB64(new Uint8Array(b)); return revealRetry(() => db.collection(coll).doc(revealVideoPartId(vid, i)).set({ vid, i, d }), 3); })")
rep("return p.then(() => meta.set({ vid, n, name: file.name || 'videó', type: file.type || 'video/mp4', size, at: Date.now(), uploading:false }));",
    "return p.then(() => meta.set({ vid, n, name: file.name || 'fájl', type: file.type || (coll === 'revealVideo' ? 'video/mp4' : 'audio/mpeg'), size, at: Date.now(), uploading:false }));")
rep("function revealDeleteVideo() { const db = revealDb(); if (!db) return Promise.resolve(); return db.collection('config').doc('revealVideo').set({ vid:null, uploading:false, at:Date.now() }).then(() => revealWipeVideo(db)); }",
    "function revealDeleteVideo(coll) { coll = coll || 'revealVideo'; const db = revealDb(); if (!db) return Promise.resolve(); return db.collection('config').doc(coll).set({ vid:null, uploading:false, at:Date.now() }).then(() => revealWipeVideo(db, coll)); }")
rep("""function useRevealVideo() {
  const meta = useRevealDoc('revealVideo');""",
"""function useRevealVideo(coll) {
  coll = coll || 'revealVideo';
  const meta = useRevealDoc(coll);""")
rep("return revealRetry(() => db.collection('revealVideo').doc(revealVideoPartId(m.vid, i)).get(), 3).then(snap => {",
    "return revealRetry(() => db.collection(coll).doc(revealVideoPartId(m.vid, i)).get(), 3).then(snap => {")

# ── a Szülők sora is általános: RevealMediaRow, a videó és a zene ugyanazt viszi ──
rep("""function RevealVideoRow() {
  const meta = useRevealDoc('revealVideo');""",
"""function RevealVideoRow() { return <RevealMediaRow />; }
// v10.458: a visszaszámlálás zenéje — ha van, a dobpergés HELYETT szól, a „0" előtt elhalkul
function RevealMusicRow() {
  return <RevealMediaRow coll="revealAudio" dp="music" icon="timer" title="Visszaszámlálás zenéje" accept="audio/*" max={REVEAL_MUSIC_MAX} what="A zene"
    emptyText="Nincs — a dobpergés szól" delTitle="Zene törlése" delText="A visszaszámlálás alatt a dobpergés fog szólni." gone="Zene törölve" />;
}
function RevealMediaRow({ coll, dp, icon, title, accept, max, what, emptyText, delTitle, delText, gone }) {
  coll = coll || 'revealVideo'; dp = dp || 'video'; max = max || REVEAL_VIDEO_MAX;
  const meta = useRevealDoc(coll);""")

# a RevealMediaRow törzse: a fix 'video' attribútumok/feliratok → paraméter
start = s.index("function RevealMediaRow(")
end = s.index("\n}\n", start) + 3
body = s[start:end]
reps = [
  ("revealUploadVideo(f, (done, n) => setProg({ done, n }))", "revealUploadVideo(f, (done, n) => setProg({ done, n }), coll, max, what)"),
  (": `Nincs — max. ${Math.round(REVEAL_VIDEO_MAX / 1048576)} MB, a visszaszámlálás után megy`;",
   ": (emptyText ? `${emptyText} · max. ${Math.round(max / 1048576)} MB` : `Nincs — max. ${Math.round(max / 1048576)} MB, a visszaszámlálás után megy`);"),
  ("data-reveal-p-video data-has", "{...{ ['data-reveal-p-' + dp]: '' }} data-has"),
  ("{rvIconBox('video', m.vid ? 'ok' : 'warn')}", "{rvIconBox(icon || 'video', m.vid ? 'ok' : (dp === 'video' ? 'warn' : 'info'))}"),
  (">Leleplező videó</div>", ">{title || 'Leleplező videó'}</div>"),
  ("<div data-reveal-p-videostatus ", "<div {...{ ['data-reveal-p-' + dp + 'status']: '' }} "),
  ("rvMsg(msg, 'data-reveal-p-videomsg')", "rvMsg(msg, 'data-reveal-p-' + dp + 'msg')"),
  ("<button type=\"button\" data-reveal-p-videopick ", "<button type=\"button\" {...{ ['data-reveal-p-' + dp + 'pick']: '' }} "),
  ("<button type=\"button\" data-reveal-p-videodel ", "<button type=\"button\" {...{ ['data-reveal-p-' + dp + 'del']: '' }} "),
  ("<input ref={ref} data-reveal-p-videoinput type=\"file\" accept=\"video/*\"", "<input ref={ref} {...{ ['data-reveal-p-' + dp + 'input']: '' }} type=\"file\" accept={accept || 'video/*'}"),
  ("<ActionModal kicker=\"Videó törlése\"", "<ActionModal kicker={delTitle || 'Videó törlése'}"),
  ("revealDeleteVideo().then(() => flash('Videó törölve'))", "revealDeleteVideo(coll).then(() => flash(gone || 'Videó törölve'))"),
  ("A leleplezéskor nem lesz videó (csak az admin linkje, ha van).", "{delText || 'A leleplezéskor nem lesz videó.'}"),
]
for a, b in reps:
    assert body.count(a) == 1, ('body', a[:70], body.count(a))
    body = body.replace(a, b)
s = s[:start] + body + s[end:]

rep("""        <RevealVideoRow />
        <RevealVolumeRow />""",
"""        <RevealMusicRow />
        <RevealVideoRow />
        <RevealVolumeRow />""")
# a hangerő a zenére is vonatkozik → a sor akkor is kell, ha csak zene van
rep("""  const meta = useRevealDoc('revealVideo'), ctl = useRevealDoc('revealProjector');
  const [msg, flash] = useRevealFlash();
  if (!(meta.v || {}).vid) return null;""",
"""  const meta = useRevealDoc('revealVideo'), mus = useRevealDoc('revealAudio'), ctl = useRevealDoc('revealProjector');
  const [msg, flash] = useRevealFlash();
  if (!(meta.v || {}).vid && !(mus.v || {}).vid) return null;""")
rep("<span style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>A videó mindig hanggal megy</span>",
    "<span style={{ display:'block', fontWeight:700, fontSize:12, color:T.inkSoft, marginTop:2 }}>Zene és videó — mindig hanggal megy</span>")

# ── RevealShow: a zene a dobpergés helyett, a „0" előtt elhalkul ──
rep("function RevealShow({ show, video, onDone, onLand, volume }) {", "function RevealShow({ show, video, music, onDone, onLand, volume }) {")
rep("""  React.useEffect(() => {
    revealDrumroll(REVEAL_COUNT_FROM * sp);
    let k = REVEAL_COUNT_FROM;
    const iv = setInterval(() => { k--; if (k > 0) setN(k); else { clearInterval(iv); setStage(vidSrc && !vBad.current ? 'video' : 'boom'); } }, 1000 * sp);
    return () => clearInterval(iv);
  }, []);""",
"""  // v10.458: saját zene (Szülők → Leleplezés) a dobpergés HELYETT. Az elejéről indul, az utolsó
  // ~1,2 mp-ben elhalkul, így a videó / robbanás tiszta hanggal kezdődik. Ha nem indul el, dobpergés.
  const musRef = React.useRef(null);
  React.useEffect(() => {
    const total = REVEAL_COUNT_FROM * sp, fade = Math.min(1.2, total / 4), t0 = performance.now();
    let fiv = 0;
    if (music) {
      const a = new Audio(music); musRef.current = a; a.volume = vol;
      const p = a.play(); if (p && p.catch) p.catch(() => { musRef.current = null; revealDrumroll(total); });
      fiv = setInterval(() => { const left = total - (performance.now() - t0) / 1000; try { a.volume = Math.max(0, vol * Math.min(1, left / fade)); } catch(e) {} }, 50);
    } else revealDrumroll(total);
    let k = REVEAL_COUNT_FROM;
    const iv = setInterval(() => { k--; if (k > 0) setN(k); else { clearInterval(iv); clearInterval(fiv); const a = musRef.current; if (a) try { a.pause(); } catch(e) {} setStage(vidSrc && !vBad.current ? 'video' : 'boom'); } }, 1000 * sp);
    return () => { clearInterval(iv); clearInterval(fiv); const a = musRef.current; if (a) try { a.pause(); } catch(e) {} };
  }, []);""")
rep("<div data-reveal-show={stage} data-reveal-countdown={stage === 'count' ? n : ''}",
    "<div data-reveal-show={stage} data-reveal-music={music ? '1' : '0'} data-reveal-countdown={stage === 'count' ? n : ''}")

# ── vetítő: a zene előtöltése és átadása ──
rep("  const video = useRevealVideo();                          // a Szülők feltöltött videója (v10.439)",
    "  const video = useRevealVideo();                          // a Szülők feltöltött videója (v10.439)\n"
    "  const music = useRevealVideo('revealAudio');             // v10.458: a visszaszámlálás zenéje")
rep("{show && <RevealShow key={show.run} show={show} video={video && video.url} volume=",
    "{show && <RevealShow key={show.run} show={show} video={video && video.url} music={music && music.url} volume=")
rep("{(video.url || video.loading) && <span data-reveal-videoready",
    "{(music.url || music.loading) && <span data-reveal-musicready={music.url ? '1' : '0'} style={{ flexShrink:0, whiteSpace:'nowrap', fontFamily:T.font, fontWeight:800, fontSize:13, color:REVEAL_INK, opacity:0.7 }}>{music.url ? '🎵 zene kész' : `🎵 zene töltődik… ${music.pct || 0}%`}</span>}\n        {(video.url || video.loading) && <span data-reveal-videoready")
rep("{needTap && video.url && <span data-reveal-needtap", "{needTap && (video.url || music.url) && <span data-reveal-needtap")
rep("🔇 koppints egyet a videó hangjáért", "🔇 koppints egyet a hangért")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
