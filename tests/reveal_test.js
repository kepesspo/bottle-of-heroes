// v10.430 — Gender Reveal: élő képvetítő (jelszó → Vetítő / Operátor, admin)
//
// Fogódzók:
//  1) jelszó nélkül nem lehet belépni; hibás jelszó → hiba; jó jelszó → szerepválasztó;
//     ⚠️ a jelszót NEM menti (v10.431): újratöltés után újra kéri; jelszócserénél kidob
//  2) ⚠️ a vetítő körbe jár, és a MENET KÖZBEN feltöltött kép a mostani UTÁN rögtön
//     jön („ÚJ KÉP"), majd a kör ott folytatódik, ahol abbamaradt
//  3) az épp vetített kép elrejtése → azonnal továbblép; minden kép eltűnik → üres állapot
//  4) mind a négy megjelenítési mód rajzol, és a választás megmarad
//  5) a tömörítés 1920 px-re kicsinyít, és 1 MB alatt marad (Firestore-korlát)
//  6) operátor: fájl-feltöltés a store-ba, elrejtés, törlés megerősítéssel
//  7) admin: jelszó mentése, a képfolyam ürítése
//  8) a DNR központban ott a csempe
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const PX = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
const wait = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const ctx = await b.newContext({ viewport: { width: 1280, height: 760 } });
  const p = await ctx.newPage();
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  // a store az oldal-újratöltést is túléli (sessionStorage), hogy az emlékezést mérni lehessen
  await p.addInitScript(`(function(){ try { var s = JSON.parse(sessionStorage.getItem('__rv') || 'null'); if (s) Object.keys(s).forEach(function(k){ window.__fbStore[k] = s[k]; }); } catch(e) {}
    window.__rvSave = function(){ sessionStorage.setItem('__rv', JSON.stringify({ config: window.__fbStore.config || {}, revealPhotos: window.__fbStore.revealPhotos || {} })); }; })();`);
  const open = async () => { await p.goto('file://' + ROOT + '/index.html?screen=reveal', { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(2600); };
  const has = sel => p.evaluate(s => !!document.querySelector(s), sel);
  const setCfg = data => p.evaluate(d => firebase.firestore().collection('config').doc('revealConfig').set(d, { merge: true }), data);
  const addPhoto = (id, at, extra) => p.evaluate(({ id, at, src, extra }) => firebase.firestore().collection('revealPhotos').doc(id).set(Object.assign({ src, at, w: 1, h: 1, hidden: false }, extra || {})), { id, at, src: PX, extra });
  const cur = () => p.evaluate(() => { const e = document.querySelector('[data-reveal-projector]'); return e ? { id: e.getAttribute('data-reveal-current'), isNew: e.getAttribute('data-reveal-isnew') } : null; });

  console.log('\n===== 1. JELSZÓ =====');
  await open();
  ok(await has('[data-reveal-nopw]'), 'jelszó nélkül: „Még nincs jelszó beállítva"');
  await setCfg({ password: 'baba', title: 'Fiú vagy lány?' });
  await p.waitForTimeout(200);
  ok(await has('[data-reveal-gate]'), 'jelszó beállítva → belépő lap');
  await p.fill('[data-reveal-pw]', 'rossz'); await p.keyboard.press('Enter'); await p.waitForTimeout(150);
  ok(await has('[data-reveal-bad]') && !(await has('[data-reveal-roles]')), 'hibás jelszó → „Hibás jelszó", nem enged be');
  await p.fill('[data-reveal-pw]', 'baba'); await p.keyboard.press('Enter'); await p.waitForTimeout(200);
  ok(await has('[data-reveal-roles]'), 'jó jelszó → szerepválasztó (Vetítő / Operátor)');
  ok(await p.evaluate(() => localStorage.getItem('boh_reveal_pw')) === null, 'a jelszó NINCS elmentve az eszközön (v10.431)');
  await p.evaluate(() => window.__rvSave());
  await open();
  ok(await has('[data-reveal-gate]') && !(await has('[data-reveal-roles]')), '⚠️ újratöltés után ÚJRA kéri a jelszót (v10.431)');
  await p.fill('[data-reveal-pw]', 'baba'); await p.keyboard.press('Enter'); await p.waitForTimeout(200);
  ok(await has('[data-reveal-roles]'), 'újra beírva beenged');
  await setCfg({ password: 'uj-jelszo' }); await p.waitForTimeout(200);
  ok(await has('[data-reveal-gate]'), 'jelszócsere után újra kéri');
  await p.fill('[data-reveal-pw]', 'uj-jelszo'); await p.keyboard.press('Enter'); await p.waitForTimeout(200);

  console.log('\n===== 2. VETÍTŐ: KÖR + ÉLŐ ÚJ KÉP =====');
  await addPhoto('a', 1); await addPhoto('b', 2); await addPhoto('c', 3);
  await p.evaluate(() => { window.__revealSpeed = 0.1; localStorage.setItem('boh_reveal_secs', '5'); });   // 5 mp → 0,5 mp
  await p.setViewportSize({ width: 420, height: 760 });   // álló vászon = 1 lap: a gyors feltöltés nem lapoz közbe
  await p.click('[data-reveal-role="projector"]'); await p.waitForTimeout(200);
  ok(await has('[data-reveal-projector]'), 'a vetítő megnyílt (teljes képernyős réteg)');
  ok((await cur()).id === 'a', 'az első kép a legrégebbi', JSON.stringify(await cur()));
  const empty0 = await p.evaluate(() => document.querySelector('[data-reveal-title]') ? 1 : 0);
  await p.waitForTimeout(560);
  ok((await cur()).id === 'b', 'egy ütem után a következő', JSON.stringify(await cur()));
  await addPhoto('n', 4);                                   // menet közben érkezik
  await p.waitForTimeout(120);
  ok((await cur()).id === 'b', 'az új kép NEM szakítja félbe a mostanit');
  await p.waitForTimeout(500);
  const cn = await cur();
  ok(cn.id === 'n' && cn.isNew === '1', '⚠️ a mostani után RÖGTÖN az új kép jön, ÚJ jelöléssel', JSON.stringify(cn));
  ok(await has('[data-reveal-newbadge]'), '„✨ ÚJ KÉP" jelvény látszik');
  await p.waitForTimeout(500);
  ok((await cur()).id === 'c', 'utána a kör ott folytatódik, ahol abbamaradt (b → c)', JSON.stringify(await cur()));
  await p.waitForTimeout(500);
  ok((await cur()).id === 'n' && (await cur()).isNew === '0', 'a kör végén az új kép már rendes tagja a körnek', JSON.stringify(await cur()));
  ok((await p.textContent('[data-reveal-count]')).trim() === '4 kép', 'a számláló 4 képet mutat', await p.textContent('[data-reveal-count]'));

  console.log('\n===== 3. ELREJTÉS / ÜRES =====');
  await p.evaluate(() => { window.__revealSpeed = 100; });   // ne lépjen magától
  await p.click('[data-reveal-next]'); await p.waitForTimeout(100);
  const before = (await cur()).id;
  await p.evaluate(id => firebase.firestore().collection('revealPhotos').doc(id).set({ hidden: true }, { merge: true }), before);
  await p.waitForTimeout(150);
  const after = (await cur()).id;
  ok(after && after !== before, 'a vetített kép elrejtése → azonnal továbblép', before + ' → ' + after);
  await p.evaluate(() => { const s = window.__fbStore.revealPhotos; Object.keys(s).forEach(k => s[k].hidden = true); return firebase.firestore().collection('revealPhotos').doc('a').set({ hidden: true }, { merge: true }); });
  await p.waitForTimeout(150);
  ok(await has('[data-reveal-empty]'), 'minden kép rejtve → üres állapot (cím + várakozás)');
  ok((await p.textContent('[data-reveal-empty]')).includes('Fiú vagy lány?'), 'az üres állapot az admin címét mutatja');
  await p.evaluate(() => { const s = window.__fbStore.revealPhotos; Object.keys(s).forEach(k => s[k].hidden = false); return firebase.firestore().collection('revealPhotos').doc('a').set({ hidden: false }, { merge: true }); });
  await p.waitForTimeout(150);
  ok(!(await has('[data-reveal-empty]')) && (await cur()).id, 'a képek visszajönnek → újra vetít');

  console.log('\n===== 4. POLAROID-FAL (széles vásznon több kép) =====');
  ok(!(await has('[data-reveal-modebtn]')), 'nincs módváltó — csak a Polaroid maradt (v10.433)');
  await p.setViewportSize({ width: 1280, height: 720 });
  await p.evaluate(() => { window.__revealSpeed = 0.1; });
  await p.waitForFunction(() => document.querySelectorAll('[data-reveal-board] [data-reveal-polaroid]').length >= 4, null, { timeout: 5000 }).catch(() => {});
  await p.evaluate(() => { window.__revealSpeed = 100; }); await p.waitForTimeout(1300);   // az ejtés-animáció (1,25× nagyítás) végét megvárjuk
  const wall = await p.evaluate(() => {
    const b = document.querySelector('[data-reveal-board]');
    const cards = [...document.querySelectorAll('[data-reveal-board] [data-reveal-polaroid]')];
    const ids = cards.map(c => c.getAttribute('data-reveal-polaroid'));
    const rs = cards.map(c => c.getBoundingClientRect());
    return { slots: +b.getAttribute('data-slots'), n: cards.length, uniq: new Set(ids).size, minL: Math.min(...rs.map(r => r.left)), maxR: Math.max(...rs.map(r => r.right)),
      overlap: rs.some((r, i) => rs.some((q, j) => i !== j && r.left < q.right && q.left < r.right)) };
  });
  ok(wall.slots === 4 && wall.n === 4, '16:9-en 4 polaroid látszik egyszerre (4 képnél)', JSON.stringify(wall));
  ok(wall.uniq === wall.n, 'nincs ismétlődő kép a falon');
  ok(wall.minL >= 0 && wall.maxR <= 1280, 'a szélső lapok sem lógnak ki a vászonról', wall.minL.toFixed(0) + '…' + wall.maxR.toFixed(0));
  ok(wall.overlap, 'a lapok kicsit átfedik egymást');
  await p.setViewportSize({ width: 390, height: 844 });
  await p.waitForTimeout(300);
  const ph = await p.evaluate(() => ({ slots: +document.querySelector('[data-reveal-board]').getAttribute('data-slots'), sw: document.documentElement.scrollWidth,
    ctl: (() => { const c = document.querySelector('[data-reveal-controls]'); return { h: c.getBoundingClientRect().height, wrap: getComputedStyle(c).flexWrap }; })() }));
  ok(ph.slots === 1 && ph.sw <= 390, 'telefonon (álló) 1 lap, és nincs vízszintes kicsúszás', JSON.stringify(ph));
  ok(ph.ctl.wrap === 'nowrap' && ph.ctl.h < 70, 'telefonon a vezérlősáv egy sorban marad (görgethető)', JSON.stringify(ph.ctl));
  await p.setViewportSize({ width: 1280, height: 760 });
  await p.evaluate(() => { window.__revealSpeed = 100; });
  await p.click('[data-reveal-secs="12"]');
  ok(await p.evaluate(() => localStorage.getItem('boh_reveal_secs')) === '12', 'az idő is megmarad (12 mp)');
  await p.waitForTimeout(3800);
  ok(await p.evaluate(() => getComputedStyle(document.querySelector('[data-reveal-controls]')).opacity) === '0', 'a vezérlők 3 mp tétlenség után eltűnnek');
  await p.click('[data-reveal-projector]', { position: { x: 5, y: 700 } }).catch(() => {});
  await p.mouse.move(420, 320); await p.waitForTimeout(450);
  await p.click('[data-reveal-exit]'); await p.waitForTimeout(150);
  ok(await has('[data-reveal-roles]') && !(await has('[data-reveal-projector]')), '„‹ Vissza" a szerepválasztóra visz');

  console.log('\n===== 5. TÖMÖRÍTÉS =====');
  const cmp = await p.evaluate(async () => {
    const c = document.createElement('canvas'); c.width = 4000; c.height = 3000;
    const x = c.getContext('2d'), id = x.createImageData(4000, 3000);
    for (let i = 0; i < id.data.length; i += 4) { id.data[i] = Math.random() * 255; id.data[i + 1] = Math.random() * 255; id.data[i + 2] = (i / 4) % 255; id.data[i + 3] = 255; }
    x.putImageData(id, 0, 0);
    const blob = await new Promise(r => c.toBlob(r, 'image/png'));
    const r = await revealCompress(new File([blob], 'zaj.png', { type: 'image/png' }));
    return { w: r.w, h: r.h, len: r.src.length, head: r.src.slice(0, 15) };
  });
  ok(Math.max(cmp.w, cmp.h) <= 1920 && Math.abs(cmp.w / cmp.h - 4 / 3) < 0.01, '4000×3000 → legfeljebb 1920 px, arányosan', cmp.w + '×' + cmp.h);
  ok(cmp.len <= 900000, '⚠️ zajos képnél is 1 MB alatt (Firestore-korlát)', cmp.len);
  ok(/^data:image\/(webp|jpeg)/.test(cmp.head), 'tömörített formátum', cmp.head);

  console.log('\n===== 6. OPERÁTOR =====');
  await p.click('[data-reveal-role="operator"]'); await p.waitForTimeout(200);
  ok(await has('[data-reveal-operator]'), 'operátor nézet');
  const n0 = await p.evaluate(() => Object.keys(window.__fbStore.revealPhotos).length);
  await p.setInputFiles('[data-reveal-input]', [ROOT + '/assets/dnr_reveal_app.png', ROOT + '/assets/dnr_tipp_app.png']);
  await p.waitForFunction(n => Object.keys(window.__fbStore.revealPhotos).length >= n + 2, n0, { timeout: 8000 }).catch(() => {});
  const up = await p.evaluate(() => Object.values(window.__fbStore.revealPhotos).filter(x => x.w === 1024));
  ok(up.length === 2 && up.every(x => /^data:image/.test(x.src) && x.at > 1000 && x.hidden === false), 'két fájl feltöltve a store-ba (tömörítve, időbélyeggel)', up.length);
  ok(await has('[data-reveal-progress]'), 'haladásjelző látszik');
  await p.waitForTimeout(200);
  const thumbs = await p.evaluate(() => [...document.querySelectorAll('[data-reveal-thumb]')].map(e => e.getAttribute('data-reveal-thumb')));
  ok(thumbs.length === 6 && thumbs[thumbs.length - 1] === 'a', 'a lista a legfrissebbel kezd (6 kép)', thumbs.join(','));
  await p.click('[data-reveal-thumb="b"] [data-reveal-hide]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => window.__fbStore.revealPhotos.b.hidden === true), 'Elrejt → hidden:true a store-ban');
  ok((await p.textContent('[data-reveal-opcount]')).includes('1 rejtve'), 'a számláló a rejtettet is jelzi', await p.textContent('[data-reveal-opcount]'));
  await p.click('[data-reveal-thumb="c"] [data-reveal-del]'); await p.waitForTimeout(150);
  ok(await has('[data-reveal-delpreview]'), 'a törlés megerősítést kér (előnézettel)');
  await p.click('button:has-text("Törlés")'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => !window.__fbStore.revealPhotos.c), 'megerősítés után a kép törlődik');

  console.log('\n===== 7. ADMIN =====');
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = '__a'; d.style.cssText = 'position:fixed;inset:0;z-index:7000;background:#fff;overflow:auto';
    document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(AdminReveal));
  });
  await p.waitForTimeout(300);
  ok((await p.inputValue('[data-admin-reveal-pw]')) === 'uj-jelszo', 'az admin a mentett jelszót mutatja');
  await p.fill('[data-admin-reveal-pw]', 'kisbaba'); await p.click('[data-admin-reveal-save]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => window.__fbStore.config.revealConfig.password === 'kisbaba'), 'jelszó mentve');
  ok((await p.textContent('[data-admin-reveal-msg]')).includes('Mentve'), '„Mentve ✓"');
  await p.click('[data-admin-reveal-clear]'); await p.waitForTimeout(100);
  await p.click('button:has-text("Mind törlése")'); await p.waitForTimeout(400);
  ok(await p.evaluate(() => Object.keys(window.__fbStore.revealPhotos).length === 0), 'ürítés → minden kép törölve');
  ok((await p.textContent('[data-admin-reveal-msg]')).includes('törölve'), 'visszajelzés a törölt darabszámmal', await p.textContent('[data-admin-reveal-msg]'));
  await p.evaluate(() => document.getElementById('__a').remove());

  console.log('\n===== 8. DNR KÖZPONT =====');
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(2600);
  ok(await has('[data-hub-card="reveal"]'), 'a központban ott a Gender Reveal kártya');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMIND ZÖLD');
  process.exit(fail ? 1 : 0);
})();
