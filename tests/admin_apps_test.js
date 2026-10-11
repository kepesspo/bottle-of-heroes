// v10.420 — Az admin APPOK szerint kategorizált, és a Hirdetmény a DNR központba költözött.
//
// Fogódzók:
//  1) web: az oldalsáv sorrendje Általános · Games · Events · Tortán · Tipp · Bingó · BOX · Pub · Liga;
//     az egy-fülű appoknál maga az app sora a gomb (nincs „DNR Bingó" fejléc + „Bingó" al-elem)
//  2) a mindent érintő dolgok az Általánosban: Profilok, Hirdetmény, DNR központ, Rendszer…
//     — és az app-specifikus dolgok NINCSENEK ott (a Pub/BOX/Events témája, a Játékmenet-kapcsoló,
//     a Szezonzáró ablak a saját appjuknál)
//  3) telefon: görgethető app-sáv, al-fülek csak több fülnél
//  4) ⚠️ a Hirdetmény a KÖZPONTBAN látszik, a DNR Games főoldalán NEM
//  5) a hirdetmény bezárható; egy ÚJ hirdetmény megint előjön (a bezárás a tartalomra szól)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const ANN = { title: 'Hétvégi terv kész?', body: 'Nézd meg az eseményeket!', active: true };

async function open(b, q, w, h, cfg) {
  const p = await b.newPage({ viewport: { width: w, height: h } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(cfg => { try { localStorage.setItem('boh_onboarded', '1'); localStorage.setItem('boh_splash', '0'); } catch(e) {}
    window.__fbStore.config = Object.assign(window.__fbStore.config || {}, cfg || {}); }, cfg || {});
  await p.goto('file://' + ROOT + '/index.html' + q, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}
const mountAdmin = p => p.evaluate(() => {
  const r = document.getElementById('root'); if (r) r.style.display = 'none';
  const d = document.createElement('div'); d.id = '__a'; d.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column';
  document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(window.AdminScreen, { go:()=>{}, setTheme:()=>{}, currentTheme:'warm' }));
});
const bodyTxt = p => p.evaluate(() => (document.querySelector('#__a [data-admin-body]') || {}).innerText || '');
const clickTab = (p, k) => p.evaluate(k => { const b = document.querySelector(`#__a [data-admin-nav] [data-admin-tab="${k}"]`); b && b.click(); return !!b; }, k);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('\n===== 1. WEB: APPOK SZERINT =====');
  let p = await open(b, '?screen=games', 2000, 1100);
  await mountAdmin(p); await p.waitForTimeout(1200);
  const nav = await p.evaluate(() => [...document.querySelectorAll('#__a [data-admin-nav] > [data-admin-cat]')].map(x => ({ cat: x.getAttribute('data-admin-cat'), btn: x.tagName === 'BUTTON', subs: x.tagName === 'BUTTON' ? 0 : x.querySelectorAll('[data-admin-tab]').length })));
  ok(nav.map(x => x.cat).join() === 'general,games,events,torta,tipp,bingo,box,pub,liga', 'a sorrend: Általános, majd az appok a központ sorrendjében', nav.map(x => x.cat).join());
  ok(['torta','tipp','bingo','box','pub'].every(k => (nav.find(x => x.cat === k) || {}).btn), 'az egy-fülű appoknál maga az app sora a gomb', JSON.stringify(nav.filter(x => x.btn).map(x => x.cat)));
  ok(nav.find(x => x.cat === 'liga').subs === 3 && nav.find(x => x.cat === 'games').subs === 6, 'a Liga 3, a Games 6 fület visz');
  const title = await p.evaluate(() => (document.querySelector('#__a [data-admin-title]') || {}).innerText);
  ok(/Általános/.test(title) && /Profilok/.test(title), 'a lap fejléce: „Általános · Profilok"', title);

  console.log('\n===== 2. MI HOVA KERÜLT =====');
  await clickTab(p, 'settings'); await p.waitForTimeout(500);
  let t = await bodyTxt(p);
  ok(/Admin PIN/.test(t) && /Kényszerített frissítés/.test(t), 'Általános → Rendszer: admin PIN + kényszerített frissítés');
  ok(!/Pub témája|BOX témája|Events témája|Játékmenet oldal|Szezonzáró/.test(t), '⚠️ az app-specifikus beállítások NINCSENEK az Általánosban', t.slice(0, 120));
  await clickTab(p, 'hub'); await p.waitForTimeout(500);
  t = await bodyTxt(p);
  ok(/DNR appok a központban/.test(t) && /Melyik app látszódjon/i.test(t) && !/Játékmenet oldal/.test(t), 'Általános → DNR központ: csak a központ kapcsolói');
  await clickTab(p, 'message'); await p.waitForTimeout(500);
  ok(/Hirdetmény a DNR központban/.test(await bodyTxt(p)), 'Általános → Hirdetmény');
  await clickTab(p, 'pubTheme'); await p.waitForTimeout(500);
  ok(/Pub témája/.test(await bodyTxt(p)), 'DNR Pub → a Pub témája');
  await clickTab(p, 'gamesSettings'); await p.waitForTimeout(500);
  t = await bodyTxt(p);
  ok(/Játékmenet oldal/.test(t) && !/Szezonzáró/.test(t), 'DNR Games → Beállítások: a Játékmenet-kapcsoló');
  await clickTab(p, 'seasons'); await p.waitForTimeout(500);
  ok(/Szezonzáró ablak/.test(await bodyTxt(p)), 'DNR Liga → Szezonok: a Szezonzáró ablak');
  await clickTab(p, 'torta'); await p.waitForTimeout(700);
  ok(/DNR a tortán/.test(await p.evaluate(() => document.querySelector('#__a [data-admin-title]').innerText)) && await p.evaluate(() => !!document.querySelector('#__a [data-bingo-admin-app="torta"]')), 'DNR a tortán → a Tortán szerkesztő');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 3. TELEFON =====');
  p = await open(b, '?screen=games', 390, 844);
  await mountAdmin(p); await p.waitForTimeout(1200);
  const ph = await p.evaluate(() => { const bar = document.querySelector('#__a [data-admin-catbar]'); return { n: bar.querySelectorAll('[data-admin-cat]').length, scroll: bar.scrollWidth > bar.clientWidth, subs: !!document.querySelector('#__a [data-admin-subtabs]') }; });
  ok(ph.n === 9 && ph.scroll, 'kilenc app egy görgethető sávban', JSON.stringify(ph));
  ok(ph.subs, 'az Általánosnál vannak al-fülek');
  await p.evaluate(() => document.querySelector('#__a [data-admin-catbar] [data-admin-cat="bingo"]').click()); await p.waitForTimeout(600);
  ok(await p.evaluate(() => !document.querySelector('#__a [data-admin-subtabs]') && !!document.querySelector('#__a [data-bingo-admin-app="bingo"]')), 'egy-fülű appnál (Bingó) nincs al-fül sor, rögtön a szerkesztő');
  await p.close();

  console.log('\n===== 4. HIRDETMÉNY A KÖZPONTBAN =====');
  p = await open(b, '', 390, 844, { announcement: ANN });
  let a = await p.evaluate(() => { const x = document.querySelector('[data-hub-announcement]'); return x ? x.innerText : null; });
  ok(a && /Hétvégi terv kész\?/.test(a) && /eseményeket/.test(a), '⚠️ a hirdetmény a DNR központban áll', a);
  const scrolls = await p.evaluate(() => [...document.querySelectorAll('[data-dnr-hub] *')].some(el => el.scrollHeight > el.clientHeight + 2 && /(auto|scroll)/.test(getComputedStyle(el).overflowY)));
  ok(!scrolls, 'a központ hirdetménnyel sem görget');
  await p.close();
  p = await open(b, '?screen=games', 390, 844, { announcement: ANN });
  const g = await p.evaluate(() => document.getElementById('root').innerText);
  ok(/DNR Games/i.test(g) && !/Hétvégi terv kész/.test(g), '⚠️ a DNR Games főoldalán NINCS hirdetmény', g.slice(0, 80).replace(/\n/g, ' | '));
  await p.close();

  console.log('\n===== 5. BEZÁRÁS =====');
  p = await open(b, '', 390, 844, { announcement: ANN });
  await p.evaluate(() => document.querySelector('[data-hub-announcement-close]').click()); await p.waitForTimeout(300);
  ok(await p.evaluate(() => !document.querySelector('[data-hub-announcement]')), 'a × bezárja');
  await p.reload({ waitUntil: 'domcontentloaded' }); await p.waitForTimeout(3200);
  ok(await p.evaluate(() => !document.querySelector('[data-hub-announcement]')), 'újratöltés után is zárva marad (ugyanaz a tartalom)');
  await p.evaluate(() => firebase.firestore().collection('config').doc('announcement').set({ title: 'Új buli!', body: 'Szombaton.', active: true }));
  await p.waitForTimeout(500);
  a = await p.evaluate(() => { const x = document.querySelector('[data-hub-announcement]'); return x ? x.innerText : null; });
  ok(a && /Új buli!/.test(a), '⚠️ egy ÚJ hirdetmény megint előjön', a);
  await p.evaluate(() => firebase.firestore().collection('config').doc('announcement').set({ title: 'Régi', body: '', active: false }));
  await p.waitForTimeout(500);
  ok(await p.evaluate(() => !document.querySelector('[data-hub-announcement]')), 'inaktív hirdetmény nem látszik');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
