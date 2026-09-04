// v10.398 — Esemény RSVP: Egyedi (vendég) jelentkező
//
// Kérés: a DNR eseményre jelentkezésnél legyen „Egyedi" opció is, amivel egy nem
// mentett-profil név is jelentkezhet (default avatarral), és CSAK a lista mutatja.
//
// Döntések (a felhasználóval átbeszélve):
//  1) foglalt név (mentett profil VAGY már jelentkezett) TILTVA — „Ez a név már foglalt"
//  2) törlés/módosítás a jelentkező-LISTÁRÓL (koppintás = módosít, hosszú nyomás = töröl)
//  3) default avatar = szürke kör + kezdőbetű (a lista már így rajzol ismeretlen nevet)
//
// Fogódzók (1 esemény, 2 mentett profil: Sere, Kecsi):
//  1) a „Ki vagy?" rácsban ott az „Egyedi" csempe
//  2) foglalt névre („Sere") hibaüzenet, NEM lép tovább
//  3) szabad névre („Béla") a vendég beküld → rsvp.Béla='yes', a listán szürke+B avatar
//  4) a listáról koppintva módosítható (yes→no)
//  5) a listáról hosszú nyomással törölhető (eltűnik az rsvp-ből)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = 'evt1';
const rsvpOf = p => p.evaluate(c => ((window.__fbStore['events'] || {})[c] || {}).rsvp || {}, CODE);
// az első #__ev-beli gomb, aminek a szövege illeszkedik
const clickBtn = (p, reSrc, root) => p.evaluate(({ r, root }) => {
  const b = [...document.querySelectorAll((root || '#__ev') + ' button')].find(x => new RegExp(r).test(x.textContent || ''));
  if (b) { b.click(); return true; } return false;
}, { r: reSrc, root });
const clickDivText = (p, txt) => p.evaluate(t => {
  const el = [...document.querySelectorAll('#__ev *')].find(n => (n.textContent || '').includes(t) && getComputedStyle(n).cursor === 'pointer');
  if (el) { el.click(); return true; } return false;
}, txt);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1500 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ code }) => {
    const soon = new Date(Date.now() + 3 * 864e5).toISOString();
    window.__fbStore['events'] = { [code]: { title: 'Teszt Buli', date: soon, createdAt: new Date().toISOString(), emoji: '🎉', location: 'Kocsma', rsvp: {} } };
    // mentett profilok (a foglalt-név ellenőrzéshez): Sere, Kecsi
    window.getProfiles = () => Promise.resolve([
      { name: 'Sere', color: '#E07A5F' },
      { name: 'Kecsi', color: '#4FC2A0' },
    ]);
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const d = document.createElement('div'); d.id = '__ev';
    d.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:1500px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(d);
    ReactDOM.createRoot(d).render(React.createElement(EventLogScreen, { go: () => {}, goEdit: () => {}, deepLink: false }));
  }, { code: CODE });
  await p.waitForTimeout(1200);

  // ── Megnyitjuk az esemény részleteit ──
  console.log('\n===== 0. ESEMÉNY MEGNYITÁSA =====');
  ok(await clickDivText(p, 'Teszt Buli'), 'rákoppintunk az esemény kártyájára');
  await p.waitForTimeout(500);
  ok(await clickBtn(p, 'Visszaigazolás'), 'megnyílik a „Ki vagy?" lap (Visszaigazolás)');
  await p.waitForTimeout(400);

  // ── 1. Van „Egyedi" csempe ──
  console.log('\n===== 1. EGYEDI CSEMPE =====');
  const hasCustom = await p.evaluate(() => [...document.querySelectorAll('#__ev button')].some(b => /^Egyedi$|Egyedi/.test((b.textContent || '').trim()) && /＋|Egyedi/.test(b.textContent || '')));
  ok(hasCustom, '⚠️ a „Ki vagy?" rácsban ott az Egyedi csempe');
  ok(await clickBtn(p, 'Egyedi'), 'rákoppintunk az Egyedi csempére');
  await p.waitForTimeout(300);
  ok(await p.evaluate(() => !!document.querySelector('#__ev input')), 'megjelenik a név-beíró mező');

  // ── 2. Foglalt név TILTVA ──
  console.log('\n===== 2. FOGLALT NÉV TILTVA =====');
  await p.evaluate(() => { const i = document.querySelector('#__ev input'); const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; set.call(i, 'Sere'); i.dispatchEvent(new Event('input', { bubbles: true })); });
  await p.waitForTimeout(150);
  await clickBtn(p, 'Tovább');
  await p.waitForTimeout(300);
  ok(/Ez a név már foglalt/.test(await p.evaluate(() => document.getElementById('__ev').innerText || '')), '⚠️ foglalt névre („Sere") hibaüzenet');
  ok(await p.evaluate(() => !!document.querySelector('#__ev input')), 'még mindig a név-beíró lépésen vagyunk (nem lépett tovább)');
  ok(Object.keys(await rsvpOf(p)).length === 0, 'semmi nem került az rsvp-be', JSON.stringify(await rsvpOf(p)));

  // ── 3. Szabad névvel a vendég beküld ──
  console.log('\n===== 3. SZABAD NÉVVEL BEKÜLDÉS =====');
  await p.evaluate(() => { const i = document.querySelector('#__ev input'); const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; set.call(i, 'Béla'); i.dispatchEvent(new Event('input', { bubbles: true })); });
  await p.waitForTimeout(150);
  await clickBtn(p, 'Tovább');
  await p.waitForTimeout(300);
  ok(await clickBtn(p, 'Jövök'), 'a státusz-lépésen „Jövök"-öt választunk');
  await p.waitForTimeout(400);
  ok((await rsvpOf(p)).Béla === 'yes', '⚠️ a vendég bekerült az rsvp-be (Béla=yes)', JSON.stringify(await rsvpOf(p)));
  // a listán ott a Béla, szürke kör + „B" kezdőbetű (nincs mentett profil)
  const guestOnList = await p.evaluate(() => {
    const row = [...document.querySelectorAll('#__ev button')].find(b => /Béla/.test(b.textContent || '') && /Jövök/.test(b.textContent || ''));
    if (!row) return { found: false };
    const av = row.querySelector('div');
    const initial = (row.querySelector('span') || {}).textContent || '';
    return { found: true, bg: av ? getComputedStyle(av).backgroundColor : '', initial };
  });
  ok(guestOnList.found, 'a vendég ott van a jelentkező-listán');
  ok(guestOnList.initial === 'B', '⚠️ default avatar = kezdőbetű („B")', guestOnList.initial);

  // ── 4. Módosítás a listáról (yes → no) ──
  console.log('\n===== 4. MÓDOSÍTÁS A LISTÁRÓL =====');
  await p.evaluate(() => { const row = [...document.querySelectorAll('#__ev button')].find(b => /Béla/.test(b.textContent || '') && /Jövök/.test(b.textContent || '')); if (row) row.click(); });
  await p.waitForTimeout(400);
  ok(await clickBtn(p, 'Nem tudok menni'), 'a státusz-lapon „Nem tudok menni"-t választunk');
  await p.waitForTimeout(400);
  ok((await rsvpOf(p)).Béla === 'no', '⚠️ a vendég válasza módosult (Béla=no)', JSON.stringify(await rsvpOf(p)));

  // ── 5. Törlés a listáról (hosszú nyomás) ──
  console.log('\n===== 5. TÖRLÉS HOSSZÚ NYOMÁSSAL =====');
  await p.evaluate(() => { const row = [...document.querySelectorAll('#__ev button')].find(b => /Béla/.test(b.textContent || '')); if (row) row.dispatchEvent(new MouseEvent('mousedown', { bubbles: true })); });
  await p.waitForTimeout(750);   // > 600 ms → a hosszú-nyomás timer elsül (töröl)
  await p.evaluate(() => { const row = [...document.querySelectorAll('#__ev button')].find(b => /Béla/.test(b.textContent || '')); if (row) row.dispatchEvent(new MouseEvent('mouseup', { bubbles: true })); });
  await p.waitForTimeout(400);
  ok((await rsvpOf(p)).Béla === undefined, '⚠️ a vendég jelentkezése törlődött (hosszú nyomás)', JSON.stringify(await rsvpOf(p)));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
