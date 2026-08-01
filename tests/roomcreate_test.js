// v10.248 — a szoba-létrehozás nem ragadhat be némán
//
// A TÜNET: a Játékmenet képernyőn még nem töltöttek be a képek (= rossz háló),
// a felhasználó megnyomja a "Játék indítása" gombot, és a szoba létrehozásánál
// megáll.
//
// AZ OK: createRoom = doc.set(...), és a Firestore-on be van kapcsolva az
// offline perzisztencia. Ilyenkor az írás HELYBEN azonnal érvényesül, de a
// visszaadott ígéret CSAK a SZERVER NYUGTÁJÁRA oldódik fel — rossz hálón tehát
// függőben marad. Ezt hamisítja ez a teszt: a createRoom soha nem oldódik fel.
//
// Amit ellenőriz:
//   1. 4 mp után a töltőképernyő megmondja, hogy lassú a kapcsolat
//   2. és ott helyben felkínál egy kiutat (offline indítás)
//   3. a kiúttal tényleg be lehet lépni a játékba
//   4. amíg fut egy létrehozás, a második gombnyomás NEM indít újabb írást
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = path.join(__dirname, '..');
const stub = fs.readFileSync(path.join(__dirname, 'fbstub.js'), 'utf8');

let fail = 0;
const ok = (cond, name, extra) => {
  console.log((cond ? '  OK  ' : '  HIBA') + '   ' + name + (extra !== undefined ? '  → ' + extra : ''));
  if (!cond) fail++;
};

const txt = p => p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
const tap = async (p, re, wait) => {
  const r = await p.evaluate(rx => {
    const b = [...document.querySelectorAll('button')]
      .find(x => new RegExp(rx).test((x.innerText || '').replace(/\s+/g, ' ')) && !x.disabled);
    if (b) { b.click(); return (b.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 30); }
    return null;
  }, re);
  await p.waitForTimeout(wait || 800);
  return r;
};

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);

  // A szoba-iras SOSEM nyugtazodik — pont mint rossz halon.
  await p.evaluate(() => {
    window.__createCalls = 0;
    window.createRoom = function () { window.__createCalls++; return new Promise(function () {}); };
  });

  console.log('\n===== ELJUTUNK A JÁTÉKMENETIG =====');
  ok(await tap(p, '^Játék$', 1100) !== null, 'a főoldalról indulunk');
  // Titkos 5-koppintas: betolti az elso 6 profilt. FONTOS, hogy a koppintasok
  // KOZOTT legyen ujrarajzolas — a szamlalo a closure-bol olvas, ot egyidejuleg
  // kiadott klikk mind 0-t latna.
  for (let i = 0; i < 5; i++) {
    await p.evaluate(() => {
      const lbl = [...document.querySelectorAll('*')]
        .find(e => /(Minimum 2 fő|\d\/5…)/.test(e.textContent || '') && e.children.length === 0);
      if (lbl && lbl.parentElement && lbl.parentElement.parentElement) lbl.parentElement.parentElement.click();
    });
    await p.waitForTimeout(160);
  }
  await p.waitForTimeout(1200);
  const hasPlayers = /Sere|Kecsi|Luca/.test(await txt(p));
  ok(hasPlayers, 'betöltöttek a játékosok', (await txt(p)).slice(0, 70));

  ok(await tap(p, 'Tovább') !== null, 'tovább a játékokhoz');
  // a "Véletlen" gomb kivalaszt par jatekot — megbizhatobb, mint racsbol talalgatni
  await tap(p, '^Véletlen$', 900);
  const cta = await p.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(x => /Játék indítása/.test(x.innerText || ''));
    return b ? b.innerText.replace(/\s+/g, ' ').trim() : null;
  });
  ok(cta && !/\(0\)/.test(cta), 'kiválasztottunk játékokat', cta);

  console.log('\n===== INDÍTÁS ROSSZ HÁLÓN =====');
  const started = await tap(p, 'Játék indítása|Indítás', 900);
  ok(started !== null, 'a "Játék indítása" gomb megnyomható', started);
  ok(/Töltjük a szobát/i.test(await txt(p)), 'a töltőképernyő jön');

  // 4 mp elott meg nincs kiut, es nem is kell
  await p.waitForTimeout(1600);
  const early = await txt(p);
  ok(!/Lassú a kapcsolat/.test(early), '2,5 mp-nél még nem panaszkodik');

  // masodik gombnyomas ne inditson ujabb irast
  await tap(p, 'Játék indítása|Indítás', 300);
  ok(await p.evaluate(() => window.__createCalls) === 1,
     'a második indítás NEM kezd új szoba-írást',
     'createRoom hívások: ' + await p.evaluate(() => window.__createCalls));

  console.log('\n===== 4 MP UTÁN VAN KIÚT =====');
  await p.waitForTimeout(3200);
  const late = await txt(p);
  ok(/Lassú a kapcsolat/.test(late), 'megmondja, hogy lassú a kapcsolat', late.slice(0, 90));
  const escape = await p.evaluate(() =>
    [...document.querySelectorAll('button')].some(x => /Indítás offline/.test(x.innerText || '')));
  ok(escape, 'és ott helyben felkínálja az offline indítást');

  await tap(p, 'Indítás offline', 1400);
  const after = await txt(p);
  ok(!/Töltjük a szobát/i.test(after), 'a töltőképernyő eltűnt');
  ok(/MENÜ|Kövi/.test(after), 'a játék elindult', after.slice(0, 90));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
