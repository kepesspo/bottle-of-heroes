# v10.457 — Gender Reveal: nagy (80 MB+) leleplező videó
#  - REVEAL_VIDEO_MAX 60 → 200 MB
#  - feltöltés darabonként olvas (file.slice), nem az egész fájlt egyszerre; darabonként 3 próba
#  - a vetítő id alapján, 4 párhuzamos szállal tölti a darabokat, százalékkal
import re, sys
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:80])
    s = s.replace(old, new)

rep("const APP_VERSION = 'v10.456';", "const APP_VERSION = 'v10.457';")
rep("const REVEAL_VIDEO_MAX = 60 * 1024 * 1024;",
    "const REVEAL_VIDEO_MAX = 200 * 1024 * 1024;   // v10.457: 60 → 200 MB (egy 80 MB-os videó ~117 darab)\n"
    "function revealVideoPartId(vid, i) { return vid + '_' + String(i).padStart(3, '0'); }\n"
    "// hálózati hibánál (telefonos net) egy darab 3-szor is próbálkozik, mielőtt az egész elbukna\n"
    "function revealRetry(fn, tries) { return fn().catch(e => (tries > 1 ? new Promise(r => setTimeout(r, 800)).then(() => revealRetry(fn, tries - 1)) : Promise.reject(e))); }")

old_up = """    .then(() => file.arrayBuffer())
    .then(buf => {
      const u8 = new Uint8Array(buf), CH = REVEAL_VIDEO_CHUNK, n = Math.max(1, Math.ceil(u8.length / CH));
      let p = Promise.resolve();
      for (let i = 0; i < n; i++) p = p.then(() => db.collection('revealVideo').doc(vid + '_' + String(i).padStart(3, '0')).set({ vid, i, d: revealB64(u8.subarray(i * CH, (i + 1) * CH)) })).then(() => onProg && onProg(i + 1, n));
      return p.then(() => meta.set({ vid, n, name: file.name || 'videó', type: file.type || 'video/mp4', size: u8.length, at: Date.now(), uploading:false }));
    })"""
new_up = """    .then(() => {
      // ⚠️ darabonként olvasunk (file.slice) — egy 80 MB-os fájl egyben + base64-ben a telefon memóriáját vinné el
      const CH = REVEAL_VIDEO_CHUNK, size = file.size, n = Math.max(1, Math.ceil(size / CH));
      let p = Promise.resolve();
      for (let i = 0; i < n; i++) p = p
        .then(() => file.slice(i * CH, Math.min(size, (i + 1) * CH)).arrayBuffer())
        .then(b => { const d = revealB64(new Uint8Array(b)); return revealRetry(() => db.collection('revealVideo').doc(revealVideoPartId(vid, i)).set({ vid, i, d }), 3); })
        .then(() => onProg && onProg(i + 1, n));
      return p.then(() => meta.set({ vid, n, name: file.name || 'videó', type: file.type || 'video/mp4', size, at: Date.now(), uploading:false }));
    })"""
rep(old_up, new_up)

old_dl = """    setSt(o => Object.assign({}, o, { loading:true }));
    db.collection('revealVideo').get().then(snap => {
      if (dead) return;
      const parts = snap.docs.map(d => d.data()).filter(x => x.vid === m.vid).sort((a, b) => a.i - b.i);
      if (parts.length !== m.n) throw new Error('hiányos');
      const url = URL.createObjectURL(new Blob(parts.map(x => revealUnB64(x.d)), { type: m.type || 'video/mp4' }));
      setSt(o => { if (o.url) try { URL.revokeObjectURL(o.url); } catch(e) {} return { id:m.vid, url, name:m.name || 'videó', loading:false }; });
    }).catch(() => { if (!dead) setSt(o => Object.assign({}, o, { loading:false })); });"""
new_dl = """    setSt(o => Object.assign({}, o, { loading:true, pct:0 }));
    // id alapján, 4 szálon, darabonként rögtön visszafejtve — nem egy ~110 MB-os lekérdezés egyben
    const n = m.n || 0, bins = new Array(n); let next = 0, done = 0;
    const worker = () => {
      if (dead || next >= n) return Promise.resolve();
      const i = next++;
      return revealRetry(() => db.collection('revealVideo').doc(revealVideoPartId(m.vid, i)).get(), 3).then(snap => {
        const x = snap.exists ? snap.data() : null;
        if (!x || x.vid !== m.vid || !x.d) throw new Error('hiányos');
        bins[i] = revealUnB64(x.d); done++;
        if (!dead) setSt(o => Object.assign({}, o, { pct: Math.round(done * 100 / n) }));
      }).then(worker);
    };
    Promise.all([0, 1, 2, 3].map(worker)).then(() => {
      if (dead) return;
      if (!n || done !== n) throw new Error('hiányos');
      const url = URL.createObjectURL(new Blob(bins, { type: m.type || 'video/mp4' }));
      setSt(o => { if (o.url) try { URL.revokeObjectURL(o.url); } catch(e) {} return { id:m.vid, url, name:m.name || 'videó', loading:false, pct:100 }; });
    }).catch(() => { if (!dead) setSt(o => Object.assign({}, o, { loading:false, failed:true })); });"""
rep(old_dl, new_dl)

rep("{video.url ? '🎬 videó kész' : '🎬 videó töltődik…'}",
    "{video.url ? '🎬 videó kész' : `🎬 videó töltődik… ${video.pct || 0}%`}")

rep("const status = prog ? `Feltöltés… ${prog.done} / ${prog.n}` :",
    "const status = prog ? `Feltöltés… ${Math.round(prog.done * 100 / Math.max(1, prog.n))}% (${prog.done} / ${prog.n})` :")

open(P, 'w', encoding='utf-8').write(s)
print('ok')
