// v10.297 — a gameMeta Firestore-ba MENTETT config, nem callback-csatorna
//
// A TÜNET (éles eszközön): "NEM SIKERÜLT A SZOBA LÉTREHOZÁSA — invalid-argument
// … Unsupported field value: a function (found in field gameMeta.onBetUpdate)".
//
// AZ OK: a Lóverseny tét-visszajelzője (jobb felső korong) a callbackjét a
// gameMeta-ba tette (setGameMeta(m => ({...m, onBetUpdate: fn}))). A gameMeta
// viszont lemegy a createRoom-ba. Amint EGYSZER elindult egy játék, a gameMeta
// örökre "mérgezett" lett, és a KÖVETKEZŐ szobanyitás halt bele — ezért nézett
// ki véletlenszerűnek.
//
// Amit ellenőriz:
//   1. a sanitizeForFirestore kiszedi a függvényt, a többi mezőt meghagyja
//   2. egy végigjátszott meccs UTÁN is nyitható új szoba (ez a valódi repró)
//   3. a Lóverseny tét-korongja a prop-csatornán továbbra is működik
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

// Titkos 5-koppintas a "Minimum 2 fo" feliraton: betolti az elso 6 profilt.
// FONTOS, hogy a koppintasok KOZOTT legyen ujrarajzolas — a szamlalo a
// closure-bol olvas, ot egyidejuleg kiadott klikk mind 0-t latna.
const loadPlayers = async (p) => {
  for (let i = 0; i < 5; i++) {
    await p.evaluate(() => {
      const lbl = [...document.querySelectorAll('*')]
        .find(e => /(Minimum 2 fő|\d\/5…)/.test(e.textContent || '') && e.children.length === 0);
      if (lbl && lbl.parentElement && lbl.parentElement.parentElement) lbl.parentElement.parentElement.click();
    });
    await p.waitForTimeout(160);
  }
  await p.waitForTimeout(1200);
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

  console.log('\n===== 1. A SANITIZER KISZEDI A FÜGGVÉNYT =====');
  // A valodi kodutat hasznaljuk: window.createRoom -> sanitizeForFirestore -> stub set()
  const san = await p.evaluate(async () => {
    try {
      await window.createRoom('900001', [{ id: 'a', name: 'A' }], ['loverseny'], {
        difficulty: 'mid',
        onBetUpdate: function () { return 42; },
        nested: { keep: 7, cb: () => {} },
        arr: [1, function () {}, 3],
      });
      const d = window.__fbStore['rooms']['900001'];
      return {
        threw: null,
        hasFn: 'onBetUpdate' in d.gameMeta,
        difficulty: d.gameMeta.difficulty,
        nestedKeep: d.gameMeta.nested.keep,
        nestedCb: 'cb' in d.gameMeta.nested,
        arr: JSON.stringify(d.gameMeta.arr),
      };
    } catch (e) { return { threw: String(e.message || e) }; }
  });
  ok(san.threw === null, 'a szoba-írás nem dob hibát függvényes gameMeta-ra', san.threw || 'lefutott');
  ok(san.hasFn === false, 'a függvény-mező eltűnt (nem null lett, hanem nincs)');
  ok(san.difficulty === 'mid', 'a szomszédos mező megmaradt', san.difficulty);
  ok(san.nestedKeep === 7 && san.nestedCb === false, 'mélyen ágyazva is tisztít, a többit hagyja');
  ok(san.arr === '[1,null,3]', 'tömbben null megy a helyére (az index számít)', san.arr);

  console.log('\n===== 2. JÁTÉK UTÁN IS NYITHATÓ ÚJ SZOBA (a valódi repró) =====');
  // A createRoom-ot elfogjuk, es a NYERS meta-t vizsgaljuk — a sanitizer elott.
  // Igy akkor is bukik a teszt, ha valaki megint callbacket tesz a gameMeta-ba:
  // a vedohalo elrejtene a hibat, a gyoker-ok viszont ettol meg ott lenne.
  await p.evaluate(() => {
    const orig = window.createRoom;
    window.__metaCalls = [];
    const fnPaths = (o, path, out, seen) => {
      if (typeof o === 'function') { out.push(path || 'root'); return out; }
      if (!o || typeof o !== 'object' || seen.has(o)) return out;
      seen.add(o);
      Object.keys(o).forEach(k => fnPaths(o[k], (path ? path + '.' : '') + k, out, seen));
      return out;
    };
    window.createRoom = function (code, players, games, meta) {
      window.__metaCalls.push({ code, fns: fnPaths(meta, '', [], new Set()) });
      return orig.apply(this, arguments);
    };
  });

  ok(await tap(p, '^Játék$', 1100) !== null, 'a főoldalról indulunk');
  await loadPlayers(p);
  ok(/Sere|Kecsi|Luca/.test(await txt(p)), 'betöltöttek a játékosok');
  ok(await tap(p, 'Tovább') !== null, 'tovább a játékokhoz');

  // Kifejezetten a Loversenyt valasztjuk — ez tette a callbacket a gameMeta-ba
  const picked = await p.evaluate(() => {
    const el = [...document.querySelectorAll('*')]
      .find(e => /Lóverseny/.test(e.textContent || '') && e.children.length === 0);
    let n = el;
    for (let i = 0; i < 6 && n; i++) { n = n.parentElement; if (n && (n.onclick || n.tagName === 'BUTTON')) { n.click(); return true; } }
    if (el && el.parentElement) { el.parentElement.click(); return true; }
    return false;
  });
  await p.waitForTimeout(700);
  ok(picked, 'kiválasztottuk a Lóversenyt');

  await tap(p, 'Játék indítása|Indítás', 2600);
  const inGame = await txt(p);
  ok(/MENÜ|Kövi/.test(inGame), 'elindult a játék', inGame.slice(0, 70));

  // A tet-korong a prop-csatornan el-e: a "+" a fejlec korongjat is emelje.
  // (Ez a tet-beallito leptetoje, nem a kozos PlayerDrinkRow — sima −/+ gombok.)
  const circleOf = () => p.evaluate(() => {
    const m = document.body.innerText.replace(/\s+/g, ' ').match(/(\d+)\s*KORTY/);
    return m ? m[1] : null;
  });
  const before = await circleOf();
  const bumped = await p.evaluate(() => {
    const btn = [...document.querySelectorAll('button')].find(x => (x.innerText || '').trim() === '+');
    if (!btn) return false;
    btn.click(); return true;
  });
  await p.waitForTimeout(700);
  const after = await circleOf();
  ok(bumped, 'a Lóverseny tét-léptetője elérhető');
  ok(before === '1' && after === '2',
     'a "+" a jobb felső korongot is emeli (prop-csatorna él)', before + ' → ' + after);

  // Vissza a fooldalra, es UJ szoba — ez halt meg elesben
  await p.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(x => /MENÜ/.test(x.innerText || ''));
    if (b) b.click();
  });
  await p.waitForTimeout(900);
  await tap(p, '^Kilépés$', 1200);
  await p.evaluate(() => {
    const b = [...document.querySelectorAll('button')].find(x => /Igen|Biztos|Kilépés|Vége/.test(x.innerText || ''));
    if (b) b.click();
  });
  await p.waitForTimeout(1800);
  // a kilepes a "Jatek vege!" osszegzore visz — onnan a Fomenu vezet haza
  await tap(p, '^Főmenü$', 1600);

  // Masodik parti: ugyanaz az ut, most mar a "hasznalt" gameMeta-val.
  // A Fomenu uriti a jatekoslistat, ezert ujra be kell tolteni oket.
  await tap(p, '^Játék$', 1200);
  await loadPlayers(p);
  await tap(p, 'Tovább', 900);
  await tap(p, '^Véletlen$', 900);
  await tap(p, 'Játék indítása|Indítás', 2600);
  const calls = await p.evaluate(() => window.__metaCalls);
  ok(calls.length >= 2, 'tényleg kétszer nyitottunk szobát', 'createRoom hívások: ' + calls.length);
  const dirty = calls.filter(c => c.fns.length);
  ok(dirty.length === 0,
     'a gameMeta EGYIK szobanyitásnál sem tartalmaz függvényt',
     dirty.length ? dirty.map(c => c.code + ': ' + c.fns.join(',')).join(' | ') : 'mind tiszta');
  const t2 = await txt(p);
  ok(!/NEM SIKERÜLT A SZOBA/i.test(t2), 'nincs "nem sikerült a szoba létrehozása" hibaképernyő', t2.slice(0, 80));

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
