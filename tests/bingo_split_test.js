// v10.419 — a Bingó, a Tippbajnokság és a DNR a tortán KÜLÖN app.
// Mögöttük ugyanaz a mechanika és ugyanaz a config/bingoConfig doksi, de saját
// képernyő (`bingo` / `tipp` / `torta`), deep link, admin-fül és „Ki vagy?".
//
// Fogódzók:
//  1) ?screen=torta a Tortánt nyitja akkor is, ha a régi `mode` 'bingo' — az app dönt, nem a mód
//  2) ?screen=tipp a Tippet nyitja (régi mode=torta mellett is)
//  3) ⚠️ RÉGI telepített ikon: ?screen=bingo + régi config (mode=torta, apps nélkül) → a Tortán nyílik
//     (különben a frissítés után a telefonon lévő „DNR a tortán" ikon csendben Bingót nyitna)
//  4) kontroll: ha a Bingó be van kapcsolva, a ?screen=bingo már a Bingó
//  5) a központból nyitott Tortán „vissza"-ja a központba visz
//  6) „Ki vagy?" apponként mentődik (boh_torta_who), a Bingóét nem írja felül
//  7) ⚠️ az Alaphelyzet CSAK a saját app adatait nullázza (a Bingó fülön nem törli a Tortán csapatait)
//  8) az Admin felületen a Bingó, a Tipp és a Tortán külön fül
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PROFILES = [{ id:'p0', name:'Sere', color:'#E07A5F' }, { id:'p1', name:'Kecsi', color:'#4FC2A0' },
                  { id:'p2', name:'Vivi', color:'#A78BFA' }, { id:'p3', name:'Robi', color:'#5BA0DB' }];
const TEAMS = [{ id:'tA', name:'A', members:['p0','p1'] }, { id:'tB', name:'B', members:['p2','p3'] }];

async function open(b, q, cfg, extraLs) {
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  p.__errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(({ cfg, profiles, extraLs }) => {
    try {
      localStorage.setItem('boh_onboarded', '1'); localStorage.setItem('boh_splash', '0');
      Object.keys(extraLs || {}).forEach(k => localStorage.setItem(k, extraLs[k]));
    } catch(e) {}
    window.__fbStore['config'] = Object.assign(window.__fbStore['config'] || {}, cfg ? { bingoConfig: cfg } : {});
    const ps = {}; profiles.forEach(x => { ps[x.id] = x; });
    window.__fbStore['profiles'] = Object.assign(window.__fbStore['profiles'] || {}, ps);
  }, { cfg, profiles: PROFILES, extraLs: extraLs || {} });
  await p.goto('file://' + ROOT + '/index.html' + q, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);
  return p;
}
const view = p => p.evaluate(() => {
  const t = (document.getElementById('root').innerText || '').replace(/\s+/g, ' ');
  return { torta: !!document.querySelector('[data-torta-logo]'), hub: !!document.querySelector('[data-dnr-hub]'),
           tipp: /Tippbajnokság 🎯/.test(t), bingo: /VB Bingó ⚽/.test(t), txt: t.slice(0, 80) };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  console.log('\n===== 1. ?screen=torta — AZ APP DÖNT, NEM A MÓD =====');
  let p = await open(b, '?screen=torta', { enabled: true, mode: 'bingo', apps: { bingo: true, tipp: true, torta: true }, tortaTeams: TEAMS });
  let v = await view(p);
  ok(v.torta && !v.bingo && !v.tipp, '⚠️ régi mode=bingo mellett is a Tortán nyílik', JSON.stringify(v));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  console.log('\n===== 2. ?screen=tipp =====');
  p = await open(b, '?screen=tipp', { enabled: true, mode: 'torta', tortaTeams: TEAMS });
  v = await view(p);
  ok(v.tipp && !v.torta, 'a Tipp nyílik (régi mode=torta mellett is)', JSON.stringify(v));
  await p.close();

  console.log('\n===== 3. RÉGI TELEPÍTETT IKON: ?screen=bingo + mode=torta =====');
  p = await open(b, '?screen=bingo', { enabled: true, mode: 'torta', tortaTeams: TEAMS });
  v = await view(p);
  ok(v.torta && !v.bingo, '⚠️ a régi Tortán-ikon (?screen=bingo) továbbra is a Tortánt nyitja', JSON.stringify(v));
  await p.close();

  console.log('\n===== 4. KONTROLL: BEKAPCSOLT BINGÓ =====');
  p = await open(b, '?screen=bingo', { enabled: true, mode: 'torta', apps: { bingo: true, tipp: false, torta: true }, tortaTeams: TEAMS });
  v = await view(p);
  ok(v.bingo && !v.torta, 'ha a Bingó be van kapcsolva, a ?screen=bingo a Bingó', JSON.stringify(v));
  await p.close();

  console.log('\n===== 5. KÖZPONT → TORTÁN → VISSZA =====');
  p = await open(b, '', { enabled: true, mode: 'bingo', apps: { bingo: true, tipp: true, torta: true }, tortaTeams: TEAMS });
  const keys = await p.evaluate(() => [...document.querySelectorAll('[data-hub-card]')].map(x => x.getAttribute('data-hub-card')));
  ok(keys[2] === 'torta' && keys[3] === 'tipp' && keys[4] === 'bingo', 'a központban: … Tortán (3.) · Tipp · Bingó', keys.join(','));
  for (let i = 0; i < 2; i++) {   // nem aktív kártyán az első koppintás odalapoz
    await p.evaluate(() => { const c = document.querySelector('[data-hub-card="torta"]'); const btn = [...c.querySelectorAll('button')].find(x => /Megnyitás/.test(x.textContent)); btn && btn.click(); });
    await p.waitForTimeout(700);
  }
  v = await view(p);
  ok(v.torta && !v.hub, 'a Tortán kártya a Tortán appot nyitja', JSON.stringify(v));
  await p.evaluate(() => { const bb = document.querySelector('.appbar-shell button'); bb && bb.click(); });
  await p.waitForTimeout(800);
  ok((await view(p)).hub, 'a „vissza" a KÖZPONTBA visz');
  await p.close();

  console.log('\n===== 6. „KI VAGY?" APPONKÉNT =====');
  p = await open(b, '?screen=torta', { enabled: true, mode: 'torta', tortaTeams: TEAMS }, { boh_bingo_who: 'p3' });
  v = await p.evaluate(() => ({ picker: document.querySelectorAll('[data-who-pick]').length, t: (document.getElementById('root').innerText || '').replace(/\s+/g, ' ') }));
  ok(v.picker === 0 && /Robi/.test(v.t), 'első nyitáskor átveszi a régi közös választást (boh_bingo_who → Robi)', v.picker);
  await p.evaluate(() => { const bt = [...document.querySelectorAll('.appbar-shell button')].find(x => /Váltás/.test(x.textContent)); bt && bt.click(); });
  await p.waitForTimeout(500);
  await p.evaluate(() => { const x = document.querySelector('[data-who-pick="p0"]'); x && x.click(); });
  await p.waitForTimeout(500);
  const ls = await p.evaluate(() => ({ t: localStorage.getItem('boh_torta_who'), b: localStorage.getItem('boh_bingo_who') }));
  ok(ls.t === 'p0' && ls.b === 'p3', '⚠️ a Tortán választása a saját kulcsába megy, a Bingóét nem írja felül', JSON.stringify(ls));
  await p.close();

  console.log('\n===== 7. ALAPHELYZET CSAK A SAJÁT APPOT =====');
  p = await open(b, '?screen=games', { enabled: true, mode: 'torta', title: 'Saját Bingó', tippTitle: 'VB Tipp', tortaTeams: TEAMS, tortaEvenings: [{ id:'e1', date:'', hostId:'tA', guestIds:['tB'], locked:false }] });
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = '__ab';
    d.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:2400px;overflow:auto;z-index:99;background:#fff';
    document.body.appendChild(d); ReactDOM.createRoot(d).render(React.createElement(AdminBingo, { app: 'bingo' }));
  });
  await p.waitForTimeout(900);
  for (let i = 0; i < 2; i++) {
    await p.evaluate(() => { const bt = [...document.querySelectorAll('#__ab button')].find(x => /Alaphelyzet/.test(x.textContent)); bt && bt.click(); });
    await p.waitForTimeout(400);
  }
  const c7 = await p.evaluate(() => window.__fbStore.config.bingoConfig);
  ok(c7.title === 'VB Bingó', 'a Bingó címe alaphelyzetbe állt', c7.title);
  ok((c7.tortaTeams || []).length === 2 && (c7.tortaEvenings || []).length === 1 && c7.tippTitle === 'VB Tipp', '⚠️ a Tortán csapatai/alkalmai és a Tipp címe érintetlen', JSON.stringify({ t: (c7.tortaTeams || []).length, e: (c7.tortaEvenings || []).length, tipp: c7.tippTitle }));
  await p.close();

  console.log('\n===== 8. ADMIN: HÁROM KÜLÖN FÜL =====');
  const src = fs.readFileSync(ROOT + '/app.src.html', 'utf8');
  ok(/\['bingo','Bingó'\],\['tipp','Tipp'\],\['torta','Tortán'\]/.test(src), 'az admin fülsorában külön Bingó / Tipp / Tortán');
  ok(/tab === 'tipp'\s+&& <AdminBingo key="tipp"\s+app="tipp"/.test(src) && /tab === 'torta' && <AdminBingo key="torta" app="torta"/.test(src), 'mindegyik fül a saját appjával mountolja a szerkesztőt');
  ok(!/data-bingo-mode=/.test(src), 'nincs többé mód-váltó gomb');

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
