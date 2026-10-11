// v10.409 — DNR KÖZPONT: a nyitóképernyő, Rács / Kártyák nézettel
//
// Fogódzók:
//  1) az app a DNR központtal nyit (nem a DNR Games főoldallal), „DNR" felirattal
//  2) v10.411: csak a Kártya nézet van (nincs Rács, nincs váltó); a köszöntés
//     („Szia, csapat!" + nap · verzió) a központ fejléce alatt áll
//  3) a központból nyitott app „vissza"-ja a KÖZPONTBA visz (nem a Games főoldalra)
//  4) DNR Games → a régi főoldal, „‹ DNR" gombbal vissza a központba; a „További DNR"
//     sor és a Bingó-gomb már NINCS a Games főoldalon
//  5) Kártyák nézet: egy aktív kártya, lapozás nyíllal és pöttyel, NINCS alsó
//     kerek ikonsor; a nézet megmarad (boh_hub_view)
//  6) a kikapcsolt app (homeConfig.dnrApps.bar=false) nem jelenik meg a központban
//  7) önálló app-link (?screen=bingo) továbbra is egyenesen a saját appba nyit
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const hubView = p => p.evaluate(() => { const h = document.querySelector('[data-dnr-hub]'); return h ? h.getAttribute('data-dnr-hub') : null; });
const click = (p, sel) => p.evaluate(s => { const b = document.querySelector(s); if (!b) return false; b.click(); return true; }, sel);

async function open(b, query, init) {
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}` + (init || ''));
  await p.goto('file://' + ROOT + '/index.html' + (query || ''), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  let p = await open(b, '');

  console.log('\n===== 1–2. NYITÓKÉPERNYŐ: DNR KÖZPONT, CSAK KÁRTYÁK =====');
  ok((await hubView(p)) === 'cards', '⚠️ az app a DNR központtal nyit, Kártya nézetben', await hubView(p));
  ok(await p.evaluate(() => !document.querySelector('[data-hub-view]')), '⚠️ nincs nézetváltó (a Rács kikerült)');
  const gr = await p.evaluate(() => { const g = document.querySelector('[data-hub-greet]'); return g ? g.innerText.replace(/\s+/g, ' ') : null; });
  ok(!!gr && /Szia, csapat!/.test(gr) && /· v\d+\.\d+/.test(gr), '⚠️ a köszöntés és a nap · verzió a központban', gr);
  ok(await p.evaluate(() => /^DNR$/.test((document.querySelector('[data-hub-wordmark]') || {}).textContent || '')), 'a fejlécben „DNR" felirat');
  const hd = await p.evaluate(() => { const h = document.querySelector('[data-hub-header]').getBoundingClientRect(); const hub = document.querySelector('[data-dnr-hub]'); const sc = [...hub.querySelectorAll('div')].filter(d => d.scrollHeight > d.clientHeight + 1 && /auto|scroll/.test(getComputedStyle(d).overflowY)); return { top: Math.round(h.top), admin: !!document.querySelector('[data-hub-header] [data-hub-admin]'), scroll: sc.length }; });
  ok(hd.top < 40 && hd.admin, '⚠️ a fejléc (DNR + váltó + admin) a képernyő tetején', JSON.stringify(hd));
  ok(hd.scroll === 0, 'a központ 390×844-en nem görget', JSON.stringify(hd));
  const tiles = await p.evaluate(() => [...document.querySelectorAll('[data-dnr-hub] [data-hub-open]')].map(x => x.getAttribute('data-hub-open')));
  ok(tiles.includes('home') && ['log','jukebox','bar','bingo','stats'].every(s => tiles.includes(s)), 'kiemelt DNR Games + mind az 5 DNR app', tiles.join(','));

  console.log('\n===== 3. APP A KÖZPONTBÓL → VISSZA A KÖZPONTBA =====');
  // a nem aktív kártya gombja előbb odalapoz, a második koppintás nyit
  await click(p, '[data-hub-open="bar"]'); await p.waitForTimeout(500);
  await click(p, '[data-hub-open="bar"]'); await p.waitForTimeout(900);
  ok((await hubView(p)) === null, 'megnyílt a Pub (a központ eltűnt)');
  ok(await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => { const r = x.getBoundingClientRect(); return r.top < 140 && r.left < 80 && r.width > 0 && x.querySelector('svg'); }); if (b) { b.click(); return true; } return false; }), 'a Pub vissza gombja');
  await p.waitForTimeout(800);
  ok((await hubView(p)) === 'cards', '⚠️ a vissza gomb a KÖZPONTBA vitt', await hubView(p));

  console.log('\n===== 4. DNR GAMES ↔ KÖZPONT =====');
  await click(p, '[data-hub-open="home"]'); await p.waitForTimeout(900);
  const home = await p.evaluate(() => ({ back: !!document.querySelector('[data-home-hub]'), txt: document.body.innerText }));
  ok(home.back && /DNR GAMES/i.test(home.txt), 'a DNR Games főoldal, „‹ DNR" gombbal', home.back);
  ok(!/Szia, csapat!/.test(home.txt), 'a köszöntés már NINCS a Games főoldalon (a központba költözött)');
  ok(!/További\s*DNR/i.test(home.txt), '⚠️ a „További DNR" sor már nincs a Games főoldalon');
  ok(await p.evaluate(() => ![...document.querySelectorAll('button')].some(x => /🏆/.test(x.textContent || ''))), 'a Bingó-gomb sincs a Games főoldalon');
  await click(p, '[data-home-hub]'); await p.waitForTimeout(800);
  ok((await hubView(p)) === 'cards', '„‹ DNR" → vissza a központba');

  console.log('\n===== 5. KÁRTYÁK NÉZET =====');
  const c1 = await p.evaluate(() => ({ active: (document.querySelector('[data-hub-card][data-active="1"]') || {}).getAttribute && document.querySelector('[data-hub-card][data-active="1"]').getAttribute('data-hub-card'), n: document.querySelectorAll('[data-hub-card]').length }));
  ok(c1.active === 'home' && c1.n === 6, 'az első aktív kártya a DNR Games, összesen 6 kártya', JSON.stringify(c1));
  const order = await p.evaluate(() => [...document.querySelectorAll('[data-hub-card]')].map(x => x.getAttribute('data-hub-card')));
  ok(order[2] === 'bingo', '⚠️ a Bingó / DNR a tortán a harmadik kártya (v10.413)', order.join(','));
  // ⚠️ v10.410: VALÓDI egérkattintás a nyíl közepére (hit-test). Az element.click()
  // átment akkor is, amikor a kártya-sáv rálógott a nyíl-sorra és elnyelte a koppintást.
  const hit = await p.evaluate(() => { const b = document.querySelector('[data-hub-next]'); const r = b.getBoundingClientRect(); const x = r.left + r.width / 2, y = r.top + r.height / 2; const top = document.elementFromPoint(x, y); return { x, y, own: !!top && (top === b || b.contains(top)) }; });
  ok(hit.own, '⚠️ a „Következő" nyíl közepén a nyíl áll (semmi nem takarja)', JSON.stringify(hit));
  await p.mouse.click(hit.x, hit.y); await p.waitForTimeout(500);
  ok(await p.evaluate(() => document.querySelector('[data-hub-card][data-active="1"]').getAttribute('data-hub-card') !== 'home'), '⚠️ a nyíl (valódi kattintással) a következő kártyára lapoz');
  const hp = await p.evaluate(() => { const b = document.querySelector('[data-hub-prev]'); const r = b.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; });
  await p.mouse.click(hp.x, hp.y); await p.waitForTimeout(500);
  ok(await p.evaluate(() => document.querySelector('[data-hub-card][data-active="1"]').getAttribute('data-hub-card') === 'home'), 'az „Előző" nyíl visszalapoz');
  for (const [w, h] of [[390, 844], [375, 667], [430, 932]]) {
    await p.setViewportSize({ width: w, height: h }); await p.waitForTimeout(400);
    const g = await p.evaluate(() => {
      const hub = document.querySelector('[data-dnr-hub]');
      const sc = [...hub.querySelectorAll('div')].filter(d => d.scrollHeight > d.clientHeight + 1 && /auto|scroll/.test(getComputedStyle(d).overflowY));
      const card = document.querySelector('[data-hub-card][data-active="1"]').getBoundingClientRect();
      const arr = document.querySelector('[data-hub-arrows]').getBoundingClientRect();
      const head = document.querySelector('[data-hub-header]').getBoundingClientRect();
      return { scroll: sc.length, docScroll: document.scrollingElement.scrollHeight > innerHeight + 1, headTop: Math.round(head.top), cardBottom: Math.round(card.bottom), arrTop: Math.round(arr.top), arrBottom: Math.round(arr.bottom), vh: innerHeight };
    });
    ok(g.scroll === 0 && !g.docScroll && g.cardBottom <= g.arrTop && g.arrBottom <= g.vh && g.headTop < 40, `${w}×${h}: nem görget, a kártya a nyilak fölött végződik, a fejléc felül`, JSON.stringify(g));
  }
  // ⚠️ v10.412: széles kijelzőn a fejléc a képernyő SZÉLEIN (nem egy 720-as oszlopban)
  await p.setViewportSize({ width: 2000, height: 1071 }); await p.waitForTimeout(400);
  const edge = await p.evaluate(() => { const w = document.querySelector('[data-hub-wordmark]').getBoundingClientRect(), a = document.querySelector('[data-hub-admin]').getBoundingClientRect(); return { left: Math.round(w.left), right: Math.round(innerWidth - a.right) }; });
  ok(edge.left <= 60 && edge.right <= 60, '⚠️ 2000 px-en a DNR balra, az admin jobbra a szélen', JSON.stringify(edge));
  await p.setViewportSize({ width: 390, height: 844 });
  await click(p, '[data-hub-next]'); await p.waitForTimeout(400);
  ok(await p.evaluate(() => !document.querySelector('nav[aria-label="Gyorsváltó"]') && document.querySelectorAll('[data-dnr-hub] img').length <= 7), '⚠️ nincs alsó kerek ikonsor (csak a kártyák ikonjai)');
  // a régi „Rács" beállítás (boh_hub_view=grid) sem hozza vissza a rácsot
  await p.evaluate(() => localStorage.setItem('boh_hub_view', 'grid'));
  await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(3200);
  ok((await hubView(p)) === 'cards', 'régi boh_hub_view=grid mellett is Kártyák');
  // ⚠️ v10.411: a Pub és az Events ikonja a KÖRÖN BELÜL (nem lóg ki, nem vágódik)
  const fit = await p.evaluate(() => ['log','bar','bingo','stats','jukebox'].map(sc => {
    const img = document.querySelector(`[data-hub-card="${sc}"] img`); const c = img.parentElement;
    const ri = img.getBoundingClientRect(), rc = c.getBoundingClientRect();
    return { sc, r: Math.round(ri.width / rc.width * 100) };
  }));
  ok(fit.filter(f => f.sc !== 'jukebox').every(f => f.r <= 72) && fit.find(f => f.sc === 'jukebox').r >= 95, '⚠️ a négyzetes ikonok (Events, Pub, Bingó, Liga) beférnek a körbe, a kerek BOX kitölti', JSON.stringify(fit));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 6. KIKAPCSOLT APP NEM JELENIK MEG =====');
  p = await open(b, '', `window.__fbStore=window.__fbStore||{};window.__fbStore.config=Object.assign(window.__fbStore.config||{},{homeConfig:{dnrAppsEnabled:true,dnrApps:{bar:false}}});`);
  const t2 = await p.evaluate(() => [...document.querySelectorAll('[data-dnr-hub] [data-hub-open]')].map(x => x.getAttribute('data-hub-open')));
  ok(!t2.includes('bar') && t2.includes('bingo') && t2.includes('home'), '⚠️ a kikapcsolt Pub nincs a központban, a többi ott van', t2.join(','));
  await p.close();

  console.log('\n===== 7. ÖNÁLLÓ APP-LINK =====');
  p = await open(b, '?screen=bingo');
  ok((await hubView(p)) === null && /Ki vagy|Bingó|tortán/i.test(await p.evaluate(() => document.body.innerText)), '?screen=bingo egyenesen a Bingóba nyit, nem a központba');
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
