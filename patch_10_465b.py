# v10.465b — a néző döntése a bélyeg VALÓDI méretéhez mér (tw), a régi kép mindig „teljes"
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:90]); s = s.replace(old, new)
rep("""    let tside = REVEAL_THUMB_SIDE, tq = 0.74, thumb = '';
    for (let i = 0; i < 6; i++) {
      const k = Math.min(1, tside / Math.max(W, H)), tw = Math.max(1, Math.round(W * k)), th = Math.max(1, Math.round(H * k));""",
"""    let tside = REVEAL_THUMB_SIDE, tq = 0.74, thumb = '', tw = 0;
    for (let i = 0; i < 6; i++) {
      const k = Math.min(1, tside / Math.max(W, H)), th = Math.max(1, Math.round(H * k)); tw = Math.max(1, Math.round(W * k));""")
rep("    return { src:out, w, h, thumb: thumb.length < out.length ? thumb : out };",
    "    return { src:out, w, h, thumb: thumb.length < out.length ? thumb : out, tw: thumb.length < out.length ? tw : w };")
rep(".then(() => ref.set(Object.assign({ src:r.thumb, full:true, w:r.w, h:r.h, at:Date.now(), hidden:false, pending:false }, extra || {})))",
    ".then(() => ref.set(Object.assign({ src:r.thumb, full:true, tw:r.tw, w:r.w, h:r.h, at:Date.now(), hidden:false, pending:false }, extra || {})))")
rep("  return { src: (want === false ? null : src) || (p && p.src), isFull: want !== false && !!src && (!p.full || src !== p.src) };",
    "  // a régi (full nélküli) képnél az `src` maga a teljes kép\n"
    "  return { src: (want === false ? null : src) || (p && p.src), isFull: !!p && (!p.full || (want !== false && !!src && src !== p.src)) };")
rep("hiRes={!watch || g.iw * (window.devicePixelRatio || 1) > REVEAL_THUMB_SIDE} />; })}",
    "hiRes={!watch || g.iw * (window.devicePixelRatio || 1) > (it.tw || REVEAL_THUMB_SIDE) * 1.05} />; })}")
rep("(!watch || vp.w * (window.devicePixelRatio || 1) > REVEAL_THUMB_SIDE * 1.5)) revealFetchFull(seq.upcoming);",
    "(!watch || vp.w * (window.devicePixelRatio || 1) > (seq.upcoming.tw || REVEAL_THUMB_SIDE) * 1.5)) revealFetchFull(seq.upcoming);")
open(P, 'w', encoding='utf-8').write(s); print('ok')
