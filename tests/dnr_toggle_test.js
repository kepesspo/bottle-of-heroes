// v10.141 — Admin kapcsolo a "TOVÁBBI DNR" feliratra
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync('/home/user/bottle-of-heroes/tests/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const seedFor = (homeCfg) => `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = { p_a:{name:'Alfa',color:'#5BA0DB'} };
  window.__fbStore['stats'] = { p_a:{ totalPoints:100 } };
  window.__fbStore['game_stats'] = {};
  window.__fbStore['statEvents'] = {};
  window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['seasons'] = {};
  window.__fbStore['config'] = ${homeCfg === null ? '{}' : JSON.stringify({ homeConfig: homeCfg })};
`;

async function home(b, homeCfg) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seedFor(homeCfg));
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  p.__errs = errs;
  return p;
}
const hasRow = (p) => p.evaluate(() => /TOVÁBBI DNR/i.test(document.body.innerText));

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('===== FOOLDAL · ALAPERTELMEZES =====');
  let p = await home(b, null);
  ok('config nelkul BE van kapcsolva (visszafele kompatibilis)', await hasRow(p));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  console.log('\n===== FOOLDAL · KIKAPCSOLVA =====');
  p = await home(b, { dnrAppsEnabled: false });
  ok('dnrAppsEnabled:false -> NEM latszik', (await hasRow(p)) === false);
  // ⚠️ A feliratot a FORRASBOL kerdezzuk. Korabban bedrotozott „Quick Game" allt
  // itt, a gomb viszont regota „Villám Játék" — a sor emiatt tartosan piros volt,
  // holott a termek jol mukodott.
  const quickLabel = await p.evaluate(() => t('quickGame'));
  ok('a tobbi fooldal-elem megmaradt (Játék, ' + quickLabel + ')',
     await p.evaluate((q) => /Játék/.test(document.body.innerText) && document.body.innerText.includes(q), quickLabel),
     quickLabel);
  ok('a "Főképernyőre mentés" link megmaradt', await p.evaluate(() => /Főképernyőre mentés/.test(document.body.innerText)));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  console.log('\n===== FOOLDAL · EXPLICIT BEKAPCSOLVA =====');
  p = await home(b, { dnrAppsEnabled: true });
  ok('dnrAppsEnabled:true -> latszik', await hasRow(p));
  await p.close();

  console.log('\n===== ADMIN KAPCSOLO =====');
  p = await home(b, null);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__adm';
    root.style.cssText = 'width:390px;box-sizing:border-box';
    document.body.appendChild(root);
    ReactDOM.createRoot(root).render(React.createElement(window.AdminHomeToggles));
  });
  await p.waitForTimeout(900);
  const admTxt = await p.evaluate(() => document.getElementById('__adm').innerText);
  ok('van "Főoldal" kartya a kapcsoloval', /Főoldal/.test(admTxt) && /További DNR/.test(admTxt), admTxt.replace(/\n/g, ' | ').slice(0, 120));
  const toggleState = () => p.evaluate(() => {
    const t = document.querySelector('#__adm div[style*="border-radius: 16px"][style*="width: 52px"]') ||
      Array.from(document.querySelectorAll('#__adm div')).find(d => d.style.width === '52px' && d.style.height === '32px');
    return t ? getComputedStyle(t).backgroundColor : null;
  });
  const onColor = await toggleState();
  ok('a kapcsolo alapbol BE (menta)', onColor === 'rgb(79, 194, 160)', onColor);

  // kikapcsolas
  await p.evaluate(() => {
    const t = Array.from(document.querySelectorAll('#__adm div')).find(d => d.style.width === '52px' && d.style.height === '32px');
    if (t) t.click();
  });
  await p.waitForTimeout(700);
  const stored = await p.evaluate(() => (window.__fbStore['config'] || {}).homeConfig);
  ok('a kapcsolo a config/homeConfig-ba ir', stored && stored.dnrAppsEnabled === false, JSON.stringify(stored));
  const offColor = await toggleState();
  ok('a kapcsolo atvaltott KI-re', offColor !== 'rgb(79, 194, 160)', offColor);
  ok('figyelmezteto sor megjelent', /Kikapcsolva/.test(await p.evaluate(() => document.getElementById('__adm').innerText)));

  // vissza be
  await p.evaluate(() => {
    const t = Array.from(document.querySelectorAll('#__adm div')).find(d => d.style.width === '52px' && d.style.height === '32px');
    if (t) t.click();
  });
  await p.waitForTimeout(700);
  const stored2 = await p.evaluate(() => (window.__fbStore['config'] || {}).homeConfig);
  ok('visszakapcsolhato', stored2 && stored2.dnrAppsEnabled === true, JSON.stringify(stored2));
  ok('nincs JS hiba (admin)', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.screenshot({ path: __dirname + '/dnr_toggle_admin.png', fullPage: true });
  await p.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
