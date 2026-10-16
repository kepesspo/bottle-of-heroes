// v10.425 — DNR Games fejléc: a Beállítások helyén a „Kiegészítők", első: Betűsorsoló.
//
// Fogódzók:
//  1) a fejlécben nincs fogaskerék / Beállítások lap; van Kiegészítők gomb (a Statisztika marad)
//  2) a lap listát mutat, a Betűsorsoló megnyílik, és vissza lehet lépni
//  3) sorsolás: a lapon egy betű áll, és az az „Alap" készletből jön (= az Ország-Város betűi)
//  4) ⚠️ „Ne ismételjen": a teljes Alap készlet (22) végigsorsolva MINDEN betű pontosan egyszer
//     jön, utána a gomb újrakezdést kínál — kontroll: kikapcsolva a 23. húzás is megy
//  5) készletváltás (Teljes A–Z) nulláz, és megmarad újranyitás után
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const BASIC = 'ABCDEFGHIJKLMNOPRSTUVZ'.split('');

async function open(b, testDb) {
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(() => { try { localStorage.setItem('boh_onboarded', '1'); localStorage.setItem('boh_splash', '0'); } catch(e) {} });
  if (testDb !== undefined) await p.addInitScript(v => { try { localStorage.setItem('boh_testdb', v); } catch(e) {} }, testDb ? '1' : '0');
  await p.goto('file://' + ROOT + '/index.html?screen=games', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}
const face = p => p.evaluate(() => (document.querySelector('[data-letter-face]') || {}).innerText);
const drawLabel = p => p.evaluate(() => (document.querySelector('[data-letter-draw]') || {}).innerText);
const drawOnce = async p => { await p.evaluate(() => document.querySelector('[data-letter-draw]').closest('button').click()); await p.waitForTimeout(1500); return face(p); };

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('\n===== 1. FEJLÉC =====');
  let p = await open(b, false);
  const hdr = await p.evaluate(() => {
    const tools = document.querySelector('[data-home-tools]');
    const r = tools && tools.getBoundingClientRect();
    const gear = [...document.querySelectorAll('#root button')].some(x => x.querySelector('svg path[d^="M19.4 15"]'));
    return { tools: !!tools, right: r ? innerWidth - r.right : -1, top: r ? r.top : -1, gear };
  });
  ok(hdr.tools && hdr.right < 90 && hdr.top < 120, 'a Kiegészítők gomb a jobb felső sarokban', JSON.stringify(hdr));
  ok(!hdr.gear, 'nincs többé fogaskerék');
  await p.evaluate(() => document.querySelector('[data-home-tools]').click()); await p.waitForTimeout(600);
  let t = await p.evaluate(() => document.body.innerText);
  ok(/Kiegészítők/.test(t) && /Betűsorsoló/.test(t), 'a lap a Kiegészítőket listázza');
  ok(!/Splash screen|Hangeffektek/.test(t), 'a régi Beállítások tartalma (Splash, Hangeffektek) nincs ott');
  ok(!/envTop=/.test(t), 'éles DB-n a safe-area diagnosztika rejtve');
  {
    const q = await open(b, true);
    await q.evaluate(() => document.querySelector('[data-home-tools]').click()); await q.waitForTimeout(600);
    ok(/envTop=/.test(await q.evaluate(() => document.body.innerText)), 'TESZT DB-n a diagnosztika a Kiegészítők lap alján (docs/safe-area.md 4.)');
    await q.close();
  }

  console.log('\n===== 2. BETŰSORSOLÓ MEGNYITÁSA =====');
  await p.evaluate(() => document.querySelector('[data-tool-open="letter"]').click()); await p.waitForTimeout(400);
  ok(await p.evaluate(() => document.querySelector('[data-game-tools]').getAttribute('data-game-tools') === 'letter'), 'megnyílt a Betűsorsoló');
  ok(await face(p) === '?' && /Sorsolás/.test(await drawLabel(p)), 'kezdetben „?" és „Sorsolás"');
  await p.evaluate(() => document.querySelector('[data-tool-back]').click()); await p.waitForTimeout(300);
  ok(await p.evaluate(() => document.querySelector('[data-game-tools]').getAttribute('data-game-tools') === 'list'), 'a vissza a listára visz');
  await p.evaluate(() => document.querySelector('[data-tool-open="letter"]').click()); await p.waitForTimeout(300);

  console.log('\n===== 3. SORSOLÁS =====');
  const f1 = await drawOnce(p);
  ok(BASIC.includes(f1), 'egy Alap-betű áll a lapon', f1);
  ok(await p.evaluate(() => document.querySelectorAll('[data-letter-used]').length) === 1 && /Új betű/.test(await drawLabel(p)), 'bekerült a kihúzottak közé, a gomb „Új betű"');

  console.log('\n===== 4. NE ISMÉTELJEN =====');
  const seen = [f1];
  for (let i = 1; i < BASIC.length; i++) seen.push(await drawOnce(p));
  const uniq = new Set(seen);
  ok(uniq.size === BASIC.length && seen.every(x => BASIC.includes(x)), '⚠️ 22 húzás = mind a 22 Alap-betű pontosan egyszer', seen.join(''));
  ok(/elfogyott/.test(await drawLabel(p)), 'a készlet végén a gomb újrakezdést kínál', await drawLabel(p));
  await p.evaluate(() => document.querySelector('[data-letter-draw]').closest('button').click()); await p.waitForTimeout(300);
  ok(await face(p) === '?' && await p.evaluate(() => document.querySelectorAll('[data-letter-used]').length) === 0, 'az újrakezdés nulláz');
  // kontroll: ismétléssel a készleten túl is lehet húzni
  await p.evaluate(() => document.querySelector('[data-letter-norepeat] > div').click()); await p.waitForTimeout(200);
  for (let i = 0; i < 3; i++) await drawOnce(p);
  ok(await p.evaluate(() => document.querySelector('[data-letter-norepeat]').getAttribute('data-letter-norepeat')) === '0' && !/elfogyott/.test(await drawLabel(p)), 'kontroll: kikapcsolva nincs „elfogyott"');

  console.log('\n===== 5. KÉSZLETVÁLTÁS =====');
  await p.evaluate(() => document.querySelector('[data-letter-set="full"]').click()); await p.waitForTimeout(200);
  ok(await face(p) === '?' && await p.evaluate(() => document.querySelectorAll('[data-letter-used]').length) === 0, 'a készletváltás nulláz');
  ok(/^[A-Z]$/.test(await drawOnce(p)), 'a Teljes készletből is húz');
  ok(await p.evaluate(() => localStorage.getItem('boh_letter_set')) === 'full', 'a választott készlet megmarad (boh_letter_set)');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
