// v10.472 — három tulajdonosi kérés
//  A) a DNR központ NEM ugrik át magától a Games-re, ha csak az látszik (különben az admin
//     elérhetetlen, és a Games „‹ DNR" gombja azonnal visszadobott a Games-re)
//  B) a DNR Games is kikapcsolható (homeConfig.dnrApps.home); ha semmi nem látszik, üres
//     állapot jön — az admin gomb ott is megvan
//  C) DNR Bingó „Ki vagy?": lenyitható Profilok + Vendég (név, vagy üresen „Vendég N");
//     a vendég a config/bingo `_guests` térképébe kerül, és az Állásban is látszik
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const PROFILES = [{ id:'p0', name:'Sere', color:'#E07A5F' }, { id:'p1', name:'Kecsi', color:'#4FC2A0' }];

async function open(b, q, config, extraLs, vp) {
  const p = await b.newPage({ viewport: vp || { width: 402, height: 900 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(({ config, profiles, extraLs }) => {
    try {
      localStorage.setItem('boh_onboarded', '1'); localStorage.setItem('boh_splash', '0');
      Object.keys(extraLs || {}).forEach(k => localStorage.setItem(k, extraLs[k]));
    } catch(e) {}
    window.__fbStore['config'] = Object.assign(window.__fbStore['config'] || {}, config || {});
    const ps = {}; profiles.forEach(x => { ps[x.id] = x; });
    window.__fbStore['profiles'] = Object.assign(window.__fbStore['profiles'] || {}, ps);
  }, { config, profiles: PROFILES, extraLs: extraLs || {} });
  await p.goto('file://' + ROOT + '/index.html' + q, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);
  return p;
}
const has = (p, s) => p.evaluate(sel => !!document.querySelector(sel), s);
const cards = p => p.evaluate(() => [...document.querySelectorAll('[data-hub-card]')].map(c => c.getAttribute('data-hub-card')));

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('\n===== A. CSAK A GAMES LÁTSZIK → A KÖZPONT MARAD =====');
  let p = await open(b, '', { homeConfig: { dnrAppsEnabled: false } });
  ok(await has(p, '[data-dnr-hub]') && JSON.stringify(await cards(p)) === '["home"]', '⚠️ a központ nem ugrik át a Games-re, egyetlen kártya: Games', JSON.stringify(await cards(p)));
  ok(await has(p, '[data-hub-admin]'), 'az admin gomb elérhető');
  await p.evaluate(() => document.querySelector('[data-hub-open="home"]').click()); await p.waitForTimeout(900);
  ok(await has(p, '[data-home-hub]'), 'a Megnyitás a Games főoldalát nyitja');
  await p.evaluate(() => document.querySelector('[data-home-hub]').click()); await p.waitForTimeout(1500);
  ok(await has(p, '[data-dnr-hub]') && !(await has(p, '[data-home-hub]')), '⚠️ a „‹ DNR" a központban marad (nem dob vissza a Games-re)');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== B. A DNR GAMES KIKAPCSOLHATÓ =====');
  p = await open(b, '', { homeConfig: { dnrApps: { home: false } } });
  let cs = await cards(p);
  ok(!cs.includes('home') && cs.length > 0, 'dnrApps.home:false → nincs Games kártya, a többi app marad', JSON.stringify(cs));
  await p.close();
  p = await open(b, '', { homeConfig: { dnrAppsEnabled: false, dnrApps: { home: false } } });
  ok(await has(p, '[data-hub-empty]') && (await cards(p)).length === 0 && await has(p, '[data-hub-admin]'), 'semmi nem látszik → üres állapot, az admin gomb megvan');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();
  // admin kapcsoló
  p = await open(b, '', {});
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__adm'; document.body.appendChild(d);
    ReactDOM.createRoot(d).render(React.createElement(AdminHomeToggles, { only: 'hub' }));
  });
  await p.waitForTimeout(600);
  ok(await has(p, '#__adm [data-admin-games-row]'), 'az adminban van DNR Games sor');
  await p.evaluate(() => document.querySelector('#__adm [data-admin-games-row] > div:last-child').click()); await p.waitForTimeout(300);
  const hc = await p.evaluate(() => (window.__fbStore.config.homeConfig || {}).dnrApps || {});
  ok(hc.home === false, 'a kapcsoló a homeConfig.dnrApps.home-ot írja (false)', JSON.stringify(hc));
  await p.close();

  console.log('\n===== C. BINGÓ „KI VAGY?" — PROFILOK + VENDÉG =====');
  const BCFG = { bingoConfig: { enabled: true, mode: 'bingo', apps: { bingo: true } } };
  p = await open(b, '?screen=bingo', BCFG);
  ok(await has(p, '[data-who-split]') && await has(p, '[data-who-profiles]') && await has(p, '[data-who-guestbox]'), 'két rész: Profilok és Vendég');
  ok(!(await has(p, '[data-who-pick]')), 'a Profilok alapból csukva');
  await p.click('[data-who-profiles]'); await p.waitForTimeout(200);
  ok((await p.evaluate(() => document.querySelectorAll('[data-who-pick]').length)) === 2, 'lenyitva a két profil látszik');
  // üres név → „Vendég 1"
  await p.click('[data-who-guest]'); await p.waitForTimeout(500);
  let st = await p.evaluate(() => ({ g: (window.__fbStore.config.bingo || {})._guests || {}, who: localStorage.getItem('boh_bingo_who'), gid: localStorage.getItem('boh_bingo_guest'), t: document.getElementById('root').innerText }));
  const gids = Object.keys(st.g);
  ok(gids.length === 1 && st.g[gids[0]].name === 'Vendég 1' && st.who === gids[0] && st.gid === gids[0], 'üres névvel „Vendég 1" lesz, és ő a kiválasztott', JSON.stringify(st.g));
  ok(/Vendég 1 kártyája/.test(st.t), 'a saját kártya a vendég nevével');
  await p.evaluate(() => document.querySelector('[data-bingo="0"]').click()); await p.waitForTimeout(300);
  ok(/Vendég 1 · vendég \(te\)/.test(await p.evaluate(() => document.getElementById('root').innerText)), 'az Állásban „· vendég" jelöléssel');
  // másik eszköz: névvel
  const p2 = await open(b, '?screen=bingo', { bingoConfig: BCFG.bingoConfig, bingo: await p.evaluate(() => window.__fbStore.config.bingo) });
  await p2.fill('[data-who-guestname]', 'Béla'); await p2.keyboard.press('Enter'); await p2.waitForTimeout(500);
  const g2 = await p2.evaluate(() => (window.__fbStore.config.bingo || {})._guests || {});
  ok(Object.values(g2).some(x => x.name === 'Béla') && Object.keys(g2).length === 2, 'névvel beírt vendég, külön azonosítóval', JSON.stringify(Object.values(g2).map(x => x.name)));
  ok(await p2.evaluate(() => /Béla kártyája/.test(document.getElementById('root').innerText)), 'Béla kártyája');
  await p2.close();
  // ugyanaz az eszköz újra belép → ugyanaz a vendég (a kártya megmarad)
  await p.evaluate(() => { const bt = [...document.querySelectorAll('.appbar-shell button')].find(x => /Váltás/.test(x.textContent)); bt && bt.click(); });
  await p.waitForTimeout(400);
  await p.click('[data-who-guest]'); await p.waitForTimeout(400);
  st = await p.evaluate(() => ({ who: localStorage.getItem('boh_bingo_who'), n: Object.keys((window.__fbStore.config.bingo || {})._guests || {}).length }));
  ok(st.who === gids[0], 'ugyanaz az eszköz újra belépve ugyanazt a vendéget kapja (a kártya és a jelölések megmaradnak)', JSON.stringify(st));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== C2. KONTROLL: A TIPPBEN NINCS VENDÉG =====');
  p = await open(b, '?screen=tipp', { bingoConfig: { enabled: true, mode: 'tipp', apps: { tipp: true } } });
  ok(!(await has(p, '[data-who-guestbox]')) && (await p.evaluate(() => document.querySelectorAll('[data-who-pick]').length)) === 2, 'a Tipp választója változatlan (profilok, vendég nélkül)');
  await p.close();

  console.log('\n===== D. AZ ADMIN DÖNTI EL, KI LÉPHET BE (v10.475) =====');
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, BCFG.bingoConfig, { bingoWho: 'guest' }) });
  ok(await has(p, '[data-who-guestbox]') && !(await has(p, '[data-who-profiles]')) && !(await has(p, '[data-who-pick]')), '„Csak vendég" → vendég-belépés, profil-lista nincs');
  await p.close();
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, BCFG.bingoConfig, { bingoWho: 'profile' }) });
  ok(!(await has(p, '[data-who-guestbox]')) && !(await has(p, '[data-who-split]')) && (await p.evaluate(() => document.querySelectorAll('[data-who-pick]').length)) === 2, '„Csak profil" → a profilok rögtön látszanak, vendég-belépés nincs');
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();
  // elmentett vendég „Csak profil" mellett → vissza a választóra; kontroll: „both" mellett marad
  const GB = { _guests: { g_x1: { name:'Ottó', color:'#888', at:1 } } };
  p = await open(b, '?screen=bingo', { bingoConfig: Object.assign({}, BCFG.bingoConfig, { bingoWho: 'profile' }), bingo: GB }, { boh_bingo_who: 'g_x1' });
  ok(await has(p, '[data-who-pick]') && !(await p.evaluate(() => /Ottó kártyája/.test(document.getElementById('root').innerText))), 'elmentett vendég „Csak profil" mellett a választóra kerül');
  await p.close();
  p = await open(b, '?screen=bingo', { bingoConfig: BCFG.bingoConfig, bingo: GB }, { boh_bingo_who: 'g_x1' });
  ok(await p.evaluate(() => /Ottó kártyája/.test(document.getElementById('root').innerText)), 'kontroll: alapból a vendég bent marad');
  await p.close();
  // admin: a választó azonnal ment, és egy teljes Mentés is megtartja
  p = await open(b, '', { bingoConfig: BCFG.bingoConfig });
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const d = document.createElement('div'); d.id = '__adm'; document.body.appendChild(d);
    ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' }));
  });
  await p.waitForTimeout(800);
  ok((await p.evaluate(() => document.querySelectorAll('#__adm [data-bingo-who]').length)) === 3 && await p.evaluate(() => document.querySelector('#__adm [data-bingo-who="both"]').getAttribute('aria-pressed') === 'true'), 'az adminban háromállású választó, alapból „Profil + vendég"');
  await p.evaluate(() => document.querySelector('#__adm [data-bingo-who="guest"]').click()); await p.waitForTimeout(400);
  ok(await p.evaluate(() => (window.__fbStore.config.bingoConfig || {}).bingoWho) === 'guest', 'a választó azonnal a bingoConfig.bingoWho-t írja');
  // a Mentés csak módosítás után él — egy cím-átírással kényszerítjük a TELJES (merge nélküli) írást
  await p.fill('#__adm [data-bingo-titleemoji]', '🎤'); await p.waitForTimeout(150);
  await p.evaluate(() => { const bt = [...document.querySelectorAll('#__adm button')].find(x => x.textContent.trim() === 'Mentés'); bt && bt.click(); }); await p.waitForTimeout(700);
  const full = await p.evaluate(() => window.__fbStore.config.bingoConfig || {});
  ok(Array.isArray(full.items) && full.titleEmoji === '🎤', 'a teljes Mentés tényleg lefutott (items + új emoji a store-ban)', JSON.stringify(Object.keys(full)));
  ok(full.bingoWho === 'guest', '⚠️ a teljes Mentés (set, merge nélkül) is megtartja a bingoWho-t', full.bingoWho);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMINDEN OK');
  process.exit(fail ? 1 : 0);
})();
