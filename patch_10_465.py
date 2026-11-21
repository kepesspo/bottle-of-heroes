# v10.465 — Gender Reveal: bélyegkép a listákban, teljes méret csak igény szerint
#  - feltöltéskor KÉT kép: bélyeg (≤ 800 px, ≤ 150 000 karakter) a revealPhotos/<id>.src-be,
#    a teljes (≤ 1920 px) a revealFull/<id>.src-be; a fő dokumentumon `full:true`
#  - a revealPhotos figyelő (vetítő, élő nézők, operátor, vendég, album) így csak bélyeget tart
#  - teljes méret: a vetítő falán lévő lapok, az operátor nagyítása, az album nagyítása, a ZIP
#  - régi (full nélküli) dokumentum: az `src` maga a teljes kép — változatlanul működik
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.464';", "const APP_VERSION = 'v10.465';")

rep("const REVEAL_MAX_SIDE = 1920, REVEAL_MAX_CHARS = 900000, REVEAL_WISH_MAX = 140;",
    "const REVEAL_MAX_SIDE = 1920, REVEAL_MAX_CHARS = 900000, REVEAL_WISH_MAX = 140;\n"
    "// v10.465: a listákba csak BÉLYEG kerül (a revealPhotos figyelője mindent a memóriában tart);\n"
    "// a teljes kép a revealFull/<id>-ben ül, és csak akkor töltődik, amikor tényleg kell.\n"
    "const REVEAL_THUMB_SIDE = 800, REVEAL_THUMB_CHARS = 150000, REVEAL_FULL_CACHE = 8;")

# ── tömörítés: teljes + bélyeg ──
rep("""    if (img.close) { try { img.close(); } catch(e) {} }
    if (out.length > REVEAL_MAX_CHARS) throw new Error('size');
    return { src:out, w, h };""",
"""    // v10.465: bélyeg ugyanabból a képből (≤ 800 px) — a listák és a nézők ezt tartják a memóriában
    let tside = REVEAL_THUMB_SIDE, tq = 0.74, thumb = '';
    for (let i = 0; i < 6; i++) {
      const k = Math.min(1, tside / Math.max(W, H)), tw = Math.max(1, Math.round(W * k)), th = Math.max(1, Math.round(H * k));
      const c = document.createElement('canvas'); c.width = tw; c.height = th;
      const ctx = c.getContext('2d'); ctx.fillStyle = '#000'; ctx.fillRect(0, 0, tw, th); ctx.drawImage(img, 0, 0, tw, th);
      thumb = canvasToCompressedURL(c, tq);
      if (thumb.length <= REVEAL_THUMB_CHARS) break;
      tside = Math.round(tside * 0.85); tq = Math.max(0.5, tq - 0.06);
    }
    if (img.close) { try { img.close(); } catch(e) {} }
    if (out.length > REVEAL_MAX_CHARS) throw new Error('size');
    return { src:out, w, h, thumb: thumb.length < out.length ? thumb : out };""")

# ── feltöltés: előbb a teljes kép, aztán a fő (bélyeges) dokumentum ──
rep("""    return db.collection('revealPhotos').add(Object.assign({ src:r.src, w:r.w, h:r.h, at:Date.now(), hidden:false, pending:false }, extra || {}));
  });
}""",
"""    // ⚠️ előbb a teljes kép: amikor a fő dokumentum megjelenik, a teljes már ott van
    const ref = db.collection('revealPhotos').doc();
    return revealRetry(() => db.collection('revealFull').doc(ref.id).set({ src:r.src, at:Date.now() }), 3)
      .then(() => ref.set(Object.assign({ src:r.thumb, full:true, w:r.w, h:r.h, at:Date.now(), hidden:false, pending:false }, extra || {})))
      .then(() => ref);
  });
}
// v10.465: a teljes kép igény szerint, kis LRU-gyorsítótárral (csak a falon lévők és a következő).
// Régi dokumentumnál (`full` nélkül) az `src` maga a teljes kép.
const revealFullCache = new Map(), revealFullWait = new Map();
function revealFullCached(p) { return !p ? null : !p.full ? p.src : (revealFullCache.get(p.id) || null); }
function revealFetchFull(p) {
  if (!p || !p.full) return Promise.resolve(p ? p.src : null);
  const hit = revealFullCache.get(p.id);
  if (hit) { revealFullCache.delete(p.id); revealFullCache.set(p.id, hit); return Promise.resolve(hit); }
  if (revealFullWait.has(p.id)) return revealFullWait.get(p.id);
  const db = revealDb(); if (!db) return Promise.resolve(p.src);
  const pr = revealRetry(() => db.collection('revealFull').doc(p.id).get(), 3).then(d => {
    const src = d && d.exists && d.data() && d.data().src;
    if (!src) return p.src;                                  // nincs teljes → marad a bélyeg
    revealFullCache.set(p.id, src);
    while (revealFullCache.size > REVEAL_FULL_CACHE) revealFullCache.delete(revealFullCache.keys().next().value);
    return src;
  }).catch(() => p.src).then(src => { revealFullWait.delete(p.id); return src; });
  revealFullWait.set(p.id, pr);
  return pr;
}
// A teljes kép, amint megjött — addig a bélyeg (soha nincs üres kép).
function useRevealFullSrc(p, want) {
  const [src, setSrc] = React.useState(() => revealFullCached(p));
  React.useEffect(() => {
    if (!p || want === false) return;
    const c = revealFullCached(p); if (c) { setSrc(c); return; }
    let dead = false; revealFetchFull(p).then(x => { if (!dead) setSrc(x); });
    return () => { dead = true; };
  }, [p && p.id, p && p.full, want]);
  return { src: (want === false ? null : src) || (p && p.src), isFull: want !== false && !!src && (!p.full || src !== p.src) };
}
function RevealFullImg({ p, want, style, alt }) {
  const r = useRevealFullSrc(p, want);
  return <img src={r.src} alt={alt || ''} data-reveal-full={r.isFull ? '1' : '0'} style={style} />;
}
// A ZIP-hez minden jóváhagyott kép teljes méretben (4 szálon)
function revealWithFull(items) {
  const list = items.slice(), idx = list.map((p, i) => (p && p.full && !p.hidden && !p.pending) ? i : -1).filter(i => i >= 0);
  let next = 0;
  const worker = () => next >= idx.length ? Promise.resolve() : (i => revealFetchFull(list[i]).then(src => { list[i] = Object.assign({}, list[i], { src }); }).then(worker))(idx[next++]);
  return Promise.all([0, 1, 2, 3].map(worker)).then(() => list);
}""")

rep("function revealRemove(p) { const db = revealDb(); if (db && p) db.collection('revealPhotos').doc(p.id).delete().catch(() => {}); }",
    "function revealRemove(p) {\n"
    "  const db = revealDb(); if (!db || !p) return;\n"
    "  db.collection('revealPhotos').doc(p.id).delete().catch(() => {});\n"
    "  if (p.full) { revealFullCache.delete(p.id); db.collection('revealFull').doc(p.id).delete().catch(() => {}); }   // v10.465\n"
    "}")

rep("""function revealDownloadAlbum(items) {
  const r = revealBuildAlbum(items);
  revealDownload(r.blob, 'gender_reveal_album.zip');
  return r.count;
}""",
"""function revealDownloadAlbum(items) {
  // v10.465: a listában csak bélyeg van — a ZIP-be a teljes képek kerülnek
  return revealWithFull(items).then(full => {
    const r = revealBuildAlbum(full);
    revealDownload(r.blob, 'gender_reveal_album.zip');
    return r.count;
  });
}""")
rep("""      const n = revealDownloadAlbum(snap.docs.map(d => Object.assign({ id:d.id }, d.data()))); flash(`Album letöltve (${n} fájl)`);
    }).catch(() => flash('Az album nem sikerült'));""",
"""      return revealDownloadAlbum(snap.docs.map(d => Object.assign({ id:d.id }, d.data()))).then(n => flash(`Album letöltve (${n} fájl)`));
    }).catch(() => flash('Az album nem sikerült'));""")
rep("    wipe('revealPhotos').then(n => wipe('revealQuizAns').then(() => n))",
    "    wipe('revealPhotos').then(n => wipe('revealFull').then(() => wipe('revealQuizAns')).then(() => n))")

# ── vetítő: a falon a teljes kép (a nézőnél csak ha a lap nagyobb a bélyegnél) ──
rep("function RevealBoardCard({ item, g, z, isNew, isCur, hideVotes }) {",
    "function RevealBoardCard({ item, g, z, isNew, isCur, hideVotes, hiRes }) {")
rep("""        <img src={item.src} alt="" style={{ display:'block', width: g.iw, height: g.ih, objectFit:'cover', borderRadius:2 }} />""",
    """        <RevealFullImg p={item} want={hiRes !== false} style={{ display:'block', width: g.iw, height: g.ih, objectFit:'cover', borderRadius:2 }} />""")
rep("""          return <RevealBoardCard key={s.key} item={it} g={revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key, topEdge > 0 || boardH < vp.h)} z={s.z} isNew={s.isNew} isCur={s.key === seq.cur.key} hideVotes={!showVotes} />; })}""",
"""          const g = revealCardGeom(i, nSlots, vp.w, Math.max(1, boardH - topEdge), it, s.key, topEdge > 0 || boardH < vp.h);
          // v10.465: a buli vetítője mindig teljes képet tesz ki; a távoli néző csak akkor, ha a lap nagyobb a bélyegnél
          return <RevealBoardCard key={s.key} item={it} g={g} z={s.z} isNew={s.isNew} isCur={s.key === seq.cur.key} hideVotes={!showVotes} hiRes={!watch || g.iw * (window.devicePixelRatio || 1) > REVEAL_THUMB_SIDE} />; })}""")

# a következő kép előre — hogy a lap ne bélyeggel érkezzen a falra
rep("  const next = React.useCallback(() => advRef.current(), []);\n  return { cur, photo: cur ? byId[cur.id] : null, next };",
    "  const next = React.useCallback(() => advRef.current(), []);\n"
    "  // v10.465: ki jön legközelebb (az előtöltéshez) — a sor eleje, vagy a kör következője\n"
    "  const s0 = st.current, qi = s0.queue.find(id => byId[id]);\n"
    "  const ri = s0.lastRegular ? photos.findIndex(p => p.id === s0.lastRegular) : -1;\n"
    "  const upcoming = qi ? byId[qi] : (photos.length ? photos[(ri + 1) % photos.length] : null);\n"
    "  return { cur, photo: cur ? byId[cur.id] : null, next, upcoming };")
rep("  const seq = useRevealSequence(photos, loaded, secs, paused || !!show || !!qstate);",
    "  const seq = useRevealSequence(photos, loaded, secs, paused || !!show || !!qstate);\n"
    "  // v10.465: a következő lap teljes képe előre (a buli vetítőjén; a néző a lapmérettől függően)\n"
    "  React.useEffect(() => { if (seq.upcoming && seq.upcoming.full && (!watch || vp.w * (window.devicePixelRatio || 1) > REVEAL_THUMB_SIDE * 1.5)) revealFetchFull(seq.upcoming); }, [seq.upcoming && seq.upcoming.id]);")

# ── operátor nagyítása és az album nagyítása: teljes kép ──
rep("""          <img src={zoom.src} alt="" style={{ maxWidth:'100%', maxHeight:'100%', objectFit:'contain', display:'block' }} />""",
    """          <RevealFullImg p={zoom} style={{ maxWidth:'100%', maxHeight:'100%', objectFit:'contain', display:'block' }} />""")
rep("""          <img src={photos[open].src} alt="" style={{ maxWidth:'96vw', maxHeight:'90vh', objectFit:'contain' }} />""",
    """          <RevealFullImg key={photos[open].id} p={photos[open]} style={{ maxWidth:'96vw', maxHeight:'90vh', objectFit:'contain' }} />""")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
