// v10.337 — A „Játék indítása" gomb csak akkor él, ha a hálózat már kész
//
// A BEJELENTÉS: „ha túl gyorsan nyomom a játékmenet után a játék indítása
// gombot, akkor beragad a szoba létrehozása képernyő. Amit látok, hogy valaminek
// a letöltése/betöltése nem történt meg."
//
// KÉT OK, és a második magyarázza a beragadást:
//
// 1. A szobanyitás az ELSŐ Firestore-körforduló. Indulás után pár tizedig a
//    csatorna még épül, tehát a legelső írás a leglassabb.
//
// 2. ⚠️ A `config/dbMode` figyelő `location.reload()`-ot hív, ha az eszköz
//    gyorsítótárazott teszt/éles beállítása más, mint a szerveren lévő. Ez a
//    pillanatkép a betöltés UTÁN pár tizeddel érkezik — pont abba az ablakba,
//    amikor a gyors felhasználó már a „Töltjük a szobát" képernyőn áll. Az
//    újratöltés elvágja a folyamatban lévő szoba-írást.
//
// A 3. blokk EZT méri, és ez a lényeg: a `beforeunload` nem sülhet el, amíg a
// szoba készül. Ezt geometriával vagy szöveggel nem lehetne megfogni — a
// képernyő a hibás verzión is „rendben" néz ki, csak épp eltűnik alóla az oldal.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

// A gomb a BottomBar-ban ul; a feliratabol olvassuk ki az allapotat.
const startBtn = p => p.evaluate(() => {
  const x = [...document.querySelectorAll('#__p button, button')]
    .find(y => /Játék indítása|Betöltés…/.test(y.textContent || ''));
  return x ? { txt: (x.textContent || '').replace(/\s+/g, ' ').trim(), off: !!x.disabled } : null;
});

async function open(b, opts) {
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');
    ${opts && opts.seedTestDb ? "localStorage.setItem('boh_testdb','1');" : ''}}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  return p;
}

// A Jatekmenet kepernyot mountoljuk, adott keszenlettel.
const mountSetup = (p, netReady) => p.evaluate((netReady) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p'); if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
  document.body.appendChild(root);
  window.__went = null;
  ReactDOM.createRoot(root).render(React.createElement(SetupScreen, {
    go: (n) => { window.__went = n; },
    players: [{ id:'a', name:'Sere', color:'#E07A5F' }, { id:'b', name:'Kecsi', color:'#4FC2A0' }],
    selectedGames: ['erem', 'memoria'], gameMeta: { modes:['points'], difficulty:'mid' },
    setGameMeta: () => {}, netReady }));
}, netReady);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. a keszenlet-jelzo maga ──
  console.log('\n===== 1. A KESZENLET-JELZO =====');
  let p = await open(b);
  await p.waitForTimeout(3400);
  const api = await p.evaluate(() => ({
    hasFlag: typeof window.bohNetReady === 'boolean',
    hasSub: typeof window.onBohNetReady === 'function',
    ready: window.bohNetReady,
  }));
  ok(api.hasFlag && api.hasSub, 'van `bohNetReady` jelző és `onBohNetReady` feliratkozó', JSON.stringify(api));
  ok(api.ready === true, 'a szoba-figyelő első pillanatképe után KÉSZ', api.ready);
  // a keses-halo: kesobbi feliratkozo is azonnal megkapja
  const late = await p.evaluate(() => new Promise(res => {
    let fired = false;
    window.onBohNetReady(() => { fired = true; res('azonnal'); });
    setTimeout(() => { if (!fired) res('SOHA'); }, 500);
  }));
  ok(late === 'azonnal', 'a később feliratkozó is azonnal megkapja', late);

  // ── 2. a gomb: keszenlet elott LETILTVA, utana el ──
  console.log('\n===== 2. A GOMB =====');
  await mountSetup(p, false);
  await p.waitForTimeout(700);
  const off = await startBtn(p);
  ok(off && off.off === true, 'készenlét ELŐTT a gomb letiltott', JSON.stringify(off));
  ok(off && /Betöltés/.test(off.txt), 'és megmondja, mire vár', off && off.txt);
  await p.evaluate(() => {
    const x = [...document.querySelectorAll('#__p button')].find(y => /Betöltés/.test(y.textContent || ''));
    if (x) x.click();
  });
  await p.waitForTimeout(300);
  ok(await p.evaluate(() => window.__went) === null,
     'a letiltott gombra kattintva NEM indul szobanyitás', await p.evaluate(() => window.__went));

  await mountSetup(p, true);
  await p.waitForTimeout(700);
  const on = await startBtn(p);
  ok(on && on.off === false && /Játék indítása/.test(on.txt), 'készenlét UTÁN élő, rendes felirattal', JSON.stringify(on));
  await p.evaluate(() => {
    const x = [...document.querySelectorAll('#__p button')].find(y => /Játék indítása/.test(y.textContent || ''));
    if (x) x.click();
  });
  await p.waitForTimeout(300);
  ok(await p.evaluate(() => window.__went) === 'play', 'és tényleg elindítja a partit',
     await p.evaluate(() => window.__went));
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── 3. ⚠️ A LENYEG: a dbMode-valtas NEM tolthet ujra szobanyitas kozben ──
  // Az eszkoz TESZT modban all, a szerver ELESBEN — tehat a `config/dbMode`
  // pillanatkep `location.reload()`-ot kerne. Ha ez a szoba-iras kozben sul el,
  // a szoba nem jon letre: pontosan a bejelentett tunet.
  console.log('\n===== 3. AZ UJRATOLTES NEM VAGHATJA EL A SZOBANYITAST =====');
  p = await open(b, { seedTestDb: true });
  await p.waitForTimeout(3400);
  // ⚠️ NEM gunyoljuk a `location.reload`-ot — Chromiumban nem is lehet. A
  // fogodzo egy JELOLO az ablakon: ha az oldal ujratoltodik, a jelolo eltunik.
  // A kontroll-ag TENYLEG ujratolt, ami elpusztitja a vegrehajtasi kornyezetet —
  // ezert a varakozas a teszt oldalan van, nem az oldalon belul, es az olvasas
  // kulon `evaluate`, navigacio-turoen.
  const probe = async (busy) => {
    await p.evaluate((busy) => {
      window.__probe = 'alive';
      window.__bohBusy = busy;
      window.__bohPendingReload = false;
    }, busy);
    await p.evaluate(() => firebase.firestore().collection('config').doc('dbMode')
      .set({ test: !window.isTestDb(), ts: Date.now() })).catch(() => {});
    await p.waitForTimeout(900);
    return p.evaluate(() => ({ alive: window.__probe === 'alive', pend: !!window.__bohPendingReload }))
      .catch(() => ({ alive: false, pend: false }));
  };
  const cut = await probe(true);
  // KONTROLL: ugyanez foglaltsag NELKUL — ott TENYLEG ujra kell toltenie.
  const free = await probe(false);
  ok(cut.alive === true, 'szoba-létrehozás KÖZBEN nincs újratöltés — a szoba nem szakad félbe', cut.alive);
  ok(cut.pend === true, 'de az átállás nem vész el: függőben marad', cut.pend);
  ok(free.alive === false, 'kontroll: foglaltság NÉLKÜL viszont tényleg újratölt', free.alive);
  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
