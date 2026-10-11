// v10.409 — DNR KÖZPONT: a nyitóképernyő, Rács / Kártyák nézettel
//
// Fogódzók:
//  1) az app a DNR központtal nyit (nem a DNR Games főoldallal), „DNR" felirattal
//  2) Rács nézet (alap): kiemelt DNR Games + a többi engedélyezett app csempeként
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

  console.log('\n===== 1–2. NYITÓKÉPERNYŐ: DNR KÖZPONT, RÁCS =====');
  ok((await hubView(p)) === 'grid', '⚠️ az app a DNR központtal nyit, Rács nézetben', await hubView(p));
  ok(await p.evaluate(() => /^DNR$/.test((document.querySelector('[data-hub-wordmark]') || {}).textContent || '')), 'a fejlécben „DNR" felirat');
  const tiles = await p.evaluate(() => [...document.querySelectorAll('[data-dnr-hub] [data-hub-open]')].map(x => x.getAttribute('data-hub-open')));
  ok(tiles.includes('home') && ['log','jukebox','bar','bingo','stats'].every(s => tiles.includes(s)), 'kiemelt DNR Games + mind az 5 DNR app', tiles.join(','));

  console.log('\n===== 3. APP A KÖZPONTBÓL → VISSZA A KÖZPONTBA =====');
  await click(p, '[data-hub-open="bar"]'); await p.waitForTimeout(900);
  ok((await hubView(p)) === null, 'megnyílt a Pub (a központ eltűnt)');
  ok(await p.evaluate(() => { const b = [...document.querySelectorAll('button')].find(x => { const r = x.getBoundingClientRect(); return r.top < 140 && r.left < 80 && r.width > 0 && x.querySelector('svg'); }); if (b) { b.click(); return true; } return false; }), 'a Pub vissza gombja');
  await p.waitForTimeout(800);
  ok((await hubView(p)) === 'grid', '⚠️ a vissza gomb a KÖZPONTBA vitt', await hubView(p));

  console.log('\n===== 4. DNR GAMES ↔ KÖZPONT =====');
  await click(p, '[data-hub-open="home"]'); await p.waitForTimeout(900);
  const home = await p.evaluate(() => ({ back: !!document.querySelector('[data-home-hub]'), txt: document.body.innerText }));
  ok(home.back && /DNR GAMES/i.test(home.txt), 'a DNR Games főoldal, „‹ DNR" gombbal', home.back);
  ok(!/További\s*DNR/i.test(home.txt), '⚠️ a „További DNR" sor már nincs a Games főoldalon');
  ok(await p.evaluate(() => ![...document.querySelectorAll('button')].some(x => /🏆/.test(x.textContent || ''))), 'a Bingó-gomb sincs a Games főoldalon');
  await click(p, '[data-home-hub]'); await p.waitForTimeout(800);
  ok((await hubView(p)) === 'grid', '„‹ DNR" → vissza a központba');

  console.log('\n===== 5. KÁRTYÁK NÉZET =====');
  await click(p, '[data-hub-view="cards"]'); await p.waitForTimeout(500);
  ok((await hubView(p)) === 'cards', 'átvált Kártyák nézetre');
  const c1 = await p.evaluate(() => ({ active: (document.querySelector('[data-hub-card][data-active="1"]') || {}).getAttribute && document.querySelector('[data-hub-card][data-active="1"]').getAttribute('data-hub-card'), n: document.querySelectorAll('[data-hub-card]').length }));
  ok(c1.active === 'home' && c1.n === 6, 'az első aktív kártya a DNR Games, összesen 6 kártya', JSON.stringify(c1));
  await click(p, '[data-hub-next]'); await p.waitForTimeout(500);
  ok(await p.evaluate(() => document.querySelector('[data-hub-card][data-active="1"]').getAttribute('data-hub-card') !== 'home'), 'a nyíl a következő kártyára lapoz');
  ok(await p.evaluate(() => !document.querySelector('nav[aria-label="Gyorsváltó"]') && document.querySelectorAll('[data-dnr-hub] img').length <= 7), '⚠️ nincs alsó kerek ikonsor (csak a kártyák ikonjai)');
  await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(3200);
  ok((await hubView(p)) === 'cards', 'újratöltés után is Kártyák (megjegyezve)');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 6. KIKAPCSOLT APP NEM JELENIK MEG =====');
  p = await open(b, '', `window.__fbStore=window.__fbStore||{};window.__fbStore.config=Object.assign(window.__fbStore.config||{},{homeConfig:{dnrAppsEnabled:true,dnrApps:{bar:false}}});try{localStorage.setItem('boh_hub_view','grid');}catch(e){}`);
  const t2 = await p.evaluate(() => [...document.querySelectorAll('[data-dnr-hub] [data-hub-open]')].map(x => x.getAttribute('data-hub-open')));
  ok(!t2.includes('bar') && t2.includes('bingo'), '⚠️ a kikapcsolt Pub nincs a központban, a többi ott van', t2.join(','));
  await p.close();

  console.log('\n===== 7. ÖNÁLLÓ APP-LINK =====');
  p = await open(b, '?screen=bingo');
  ok((await hubView(p)) === null && /Ki vagy|Bingó|tortán/i.test(await p.evaluate(() => document.body.innerText)), '?screen=bingo egyenesen a Bingóba nyit, nem a központba');
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
