// v10.465 — Gender Reveal: bélyegkép a listákban, teljes méret csak igény szerint
//
// Fogódzók:
//  1) feltöltéskor a revealPhotos/<id>.src BÉLYEG (≤ 150 000 karakter, ≤ 800 px), a teljes
//     kép a revealFull/<id>.src-ben; a fő dokumentumon full:true. ⚠️ A mérés a STORE-ra
//     megy: a felület mindkét esetben ugyanúgy „képet mutat", a memória-különbség csak itt látszik
//  2) a buli vetítője a falon a TELJES képet teszi ki (data-reveal-full="1", src = revealFull);
//     a régi, full nélküli dokumentum változatlanul megy (kontroll)
//  3) az élő link nézője telefonon a BÉLYEGET kapja (a lap kisebb a bélyegnél)
//  4) az operátor nagyítása a teljes képet tölti be
//  5) törlés: a fő dokumentum ÉS a revealFull is eltűnik; ürítés: a revealFull is üres
//  6) a ZIP a teljes képeket viszi, nem a bélyeget
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const PX = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 720 } });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.addInitScript(`(function(){ try { var s = JSON.parse(sessionStorage.getItem('__rv') || 'null'); if (s) Object.keys(s).forEach(function(k){ window.__fbStore[k] = s[k]; }); } catch(e) {}
    window.__rvSave = function(){ sessionStorage.setItem('__rv', JSON.stringify({ config: window.__fbStore.config || {}, revealPhotos: window.__fbStore.revealPhotos || {}, revealFull: window.__fbStore.revealFull || {} })); }; })();`);
  const go = async q => { await p.goto('file://' + ROOT + '/index.html?screen=reveal' + (q || ''), { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(2600); };
  const has = sel => p.evaluate(s => !!document.querySelector(s), sel);
  const login = async () => { await p.waitForSelector('[data-reveal-key]', { timeout: 5000 }); await p.keyboard.type('1234'); await p.waitForTimeout(350); };

  console.log('\n===== 1. FELTÖLTÉS: BÉLYEG + TELJES =====');
  await go();
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealConfig').set({ password: '1234', title: 'Teszt', guestKey: 'gk', albumKey: 'ak', liveKey: 'lk' }, { merge: true }));
  // egy régi (full nélküli) kép — kontroll: annak az src-je maga a teljes kép
  await p.evaluate(px => firebase.firestore().collection('revealPhotos').doc('old').set({ src: px, w: 1, h: 1, at: 1, hidden: false, pending: false }), PX);
  // valódi, zajos, nagy kép (4000×3000) — a tömörítő a legrosszabb esetet kapja
  const ids = await p.evaluate(async () => {
    const out = [];
    for (let k = 0; k < 2; k++) {
      const c = document.createElement('canvas'); c.width = 4000; c.height = 3000;
      const x = c.getContext('2d'), d = x.createImageData(4000, 3000);
      for (let i = 0; i < d.data.length; i += 4) { d.data[i] = (Math.random() * 255) | 0; d.data[i + 1] = (i / 4000) % 255; d.data[i + 2] = k * 120; d.data[i + 3] = 255; }
      x.putImageData(d, 0, 0);
      const blob = await new Promise(r => c.toBlob(r, 'image/png'));
      const ref = await revealUpload(new File([blob], 'zaj' + k + '.png', { type: 'image/png' }));
      out.push(ref.id);
    }
    return out;
  });
  const st = await p.evaluate(ids => ids.map(id => { const m = window.__fbStore.revealPhotos[id], f = (window.__fbStore.revealFull || {})[id];
    return { full: m.full, thumb: m.src.length, big: f ? f.src.length : 0, w: m.w, h: m.h }; }), ids);
  ok(st.every(x => x.full === true && x.big > 0), 'a fő dokumentum full:true, a teljes kép a revealFull-ban', JSON.stringify(st));
  ok(st.every(x => x.thumb <= 150000 && x.big <= 900000 && x.thumb * 3 < x.big), 'a listába csak bélyeg kerül (≤ 150 000 kar., a teljesnek legfeljebb harmada)', JSON.stringify(st.map(x => x.thumb + ' / ' + x.big)));
  ok(st.every(x => Math.max(x.w, x.h) <= 1920 && Math.max(x.w, x.h) > 800), 'a w/h a TELJES kép mérete (a fal aránya ebből jön)', JSON.stringify(st.map(x => x.w + '×' + x.h)));
  const dims = await p.evaluate(src => new Promise(r => { const i = new Image(); i.onload = () => r(Math.max(i.naturalWidth, i.naturalHeight)); i.src = src; }), await p.evaluate(id => window.__fbStore.revealPhotos[id].src, ids[0]));
  ok(dims <= 800, 'a bélyeg legfeljebb 800 px', dims);
  const tot = await p.evaluate(() => Object.values(window.__fbStore.revealPhotos).reduce((s, x) => s + (x.src || '').length, 0));
  console.log('       (a revealPhotos figyelő által tartott képadat: ' + tot + ' karakter)');

  console.log('\n===== 2. A BULI VETÍTŐJE: TELJES KÉP A FALON =====');
  await p.evaluate(() => { localStorage.setItem('boh_reveal_slots', '3'); localStorage.setItem('boh_reveal_secs', '3'); window.__rvSave(); });
  await go(); await login();
  await p.evaluate(() => { window.__revealSpeed = 0.1; });
  await p.click('[data-reveal-role="projector"]');
  // a lapok fokozatosan kerülnek a falra — megvárjuk, amíg mind a három kint van, és betöltött
  await p.waitForFunction(() => document.querySelectorAll('[data-reveal-polaroid]').length >= 3, null, { timeout: 8000 }).catch(() => {});
  await p.evaluate(() => { window.__revealSpeed = 1000; }); await p.waitForTimeout(600);
  const wall = await p.evaluate(() => [...document.querySelectorAll('[data-reveal-polaroid]')].map(e => { const im = e.querySelector('img'); const id = e.getAttribute('data-reveal-polaroid');
    const f = (window.__fbStore.revealFull || {})[id]; return { id, full: im.getAttribute('data-reveal-full'), isFullSrc: f ? im.src === f.src : im.src === window.__fbStore.revealPhotos[id].src }; }));
  ok(wall.length === 3 && wall.every(x => x.full === '1' && x.isFullSrc), 'mind a 3 lap a teljes képet mutatja (a régi is — kontroll)', JSON.stringify(wall));

  console.log('\n===== 3. ÉLŐ LINK TELEFONON: BÉLYEG =====');
  // a régi kontroll-kép kikerül, hogy a nézőnél biztosan új (bélyeges) kép legyen a falon
  await p.evaluate(() => { delete window.__fbStore.revealPhotos.old; window.__rvSave(); });
  await p.setViewportSize({ width: 390, height: 844 });
  await go('&live=lk'); await p.waitForTimeout(800);
  const ph = await p.evaluate(() => [...document.querySelectorAll('[data-reveal-polaroid]')].map(e => { const im = e.querySelector('img'), id = e.getAttribute('data-reveal-polaroid'), m = window.__fbStore.revealPhotos[id];
    return { id, full: im.getAttribute('data-reveal-full'), thumb: im.src === m.src, isNew: !!m.full }; }));
  ok(ph.length >= 1 && ph.filter(x => x.isNew).length > 0 && ph.filter(x => x.isNew).every(x => x.full === '0' && x.thumb), 'telefonon a néző a bélyeget kapja (a lap kisebb a bélyegnél)', JSON.stringify(ph));
  // kontroll: egy nagy kijelzőn, egy lappal a néző is teljes képet kap (a lap nagyobb a bélyegnél)
  await p.evaluate(() => { window.__fbStore.config.revealProjector = { slots: 1 }; window.__rvSave(); });
  await p.setViewportSize({ width: 2400, height: 1350 });
  await go('&live=lk'); await p.waitForTimeout(800);
  const big = await p.evaluate(() => [...document.querySelectorAll('[data-reveal-polaroid]')].map(e => { const id = e.getAttribute('data-reveal-polaroid'); return { full: e.querySelector('img').getAttribute('data-reveal-full'), isNew: !!window.__fbStore.revealPhotos[id].full }; }));
  ok(big.filter(x => x.isNew).length > 0 && big.filter(x => x.isNew).every(x => x.full === '1'), 'kontroll: nagy kijelzőn a néző is teljes képet kap', JSON.stringify(big));

  console.log('\n===== 4. OPERÁTOR: NAGYÍTÁS =====');
  await p.setViewportSize({ width: 390, height: 844 });
  await go(); await login();
  await p.click('[data-reveal-role="operator"]'); await p.waitForTimeout(400);
  const slideFull = await p.evaluate(() => { const im = document.querySelector('[data-reveal-slideimg] img'); return im ? im.src.length : -1; });
  ok(slideFull > 0 && slideFull <= 150000, 'a lapozóban a bélyeg (nem tölt teljes képet listázáskor)', slideFull);
  await p.click('[data-reveal-slideimg]'); await p.waitForTimeout(500);
  const zm = await p.evaluate(() => { const im = document.querySelector('[data-reveal-oplightbox] img'); return im ? { full: im.getAttribute('data-reveal-full'), len: im.src.length } : null; });
  ok(zm && zm.full === '1' && zm.len > 150000, 'koppintásra a nagyítás a TELJES képet tölti be', JSON.stringify(zm));
  await p.click('[data-reveal-oplightbox]'); await p.waitForTimeout(200);

  console.log('\n===== 5. ZIP: TELJES KÉPEK =====');
  const zip = await p.evaluate(async () => {
    const items = Object.entries(window.__fbStore.revealPhotos).map(([id, v]) => Object.assign({ id }, v));
    const full = await revealWithFull(items);
    const r = revealBuildAlbum(full);
    const want = Object.values(window.__fbStore.revealFull).reduce((s, x) => s + x.src.length * 0.74, 0);
    return { files: r.count, size: r.blob.size, want: Math.round(want), allFull: full.filter(x => x.full).every(x => x.src === window.__fbStore.revealFull[x.id].src) };
  });
  ok(zip.allFull && zip.files === 2 && zip.size > zip.want * 0.95, 'a ZIP a teljes képeket viszi (2 kép, a méret a teljes képeké)', JSON.stringify(zip));

  console.log('\n===== 6. TÖRLÉS ÉS ÜRÍTÉS =====');
  const delId = ids[0];
  await p.evaluate(id => revealRemove(Object.assign({ id }, window.__fbStore.revealPhotos[id])), delId); await p.waitForTimeout(200);
  ok(await p.evaluate(id => !window.__fbStore.revealPhotos[id] && !(window.__fbStore.revealFull || {})[id], delId), 'törlés: a fő dokumentum ÉS a teljes kép is eltűnik');
  await p.evaluate(() => { const d = document.createElement('div'); d.id = '__a'; d.style.cssText = 'position:fixed;inset:0;z-index:7000;background:#fff;overflow:auto'; document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(RevealAlbumCard)); });
  await p.waitForTimeout(300);
  await p.click('#__a [data-reveal-p-clear]'); await p.waitForTimeout(100);
  await p.click('button:has-text("Mind törlése")'); await p.waitForTimeout(500);
  ok(await p.evaluate(() => Object.keys(window.__fbStore.revealPhotos || {}).length === 0 && Object.keys(window.__fbStore.revealFull || {}).length === 0), 'ürítés: a revealFull is kiürül');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMIND ZÖLD');
  process.exit(fail ? 1 : 0);
})();
