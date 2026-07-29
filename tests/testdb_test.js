// v10.180 — Teszt / eles adatbazis kapcsolo
//
// A sok tesztelestol a statisztika-kollekciok tele vannak szemettel. A valtas
// ugy tortent, hogy a MOSTANI (prefix nelkuli) kollekciok maradtak a teszt-
// adatnak, es az ELES megy uj, 'live_' prefixu kollekciokba — igy egyetlen
// dokumentumot sem kellett mozgatni, es az eles nullarol indul.
//
// v10.181 ota a kapcsolo GLOBALIS (config/dbMode) — eszkozonkent tarolva egy
// buli statisztikaja ketfele eshetett volna attol, hogy az egyik telefon teszt
// modban maradt.
//
// Negy dolog dolhet el csendben:
//   1) egy elfelejtett db.collection('stats') hivas, ami mindket modban
//      ugyanoda irna — a kapcsolo latszolag mukodne, az adat megis keveredne;
//   2) a coll() rossz iranyba prefixel (alapbol ELES kell legyen);
//   3) a kapcsolo tenyleg 3 koppintasra vall, nem 1-re vagy 2-re;
//   4) a valtas csak helyben tortenik meg, a tobbi keszulek nem tud rola.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';
const SRC = '/home/user/bottle-of-heroes/app.src.html';

// ezek a kollekciok leteznek ket peldanyban
const SPLIT = ['stats', 'statEvents', 'game_stats', 'gameStatEvents', 'usage',
               'bp_tournaments', 'profiles'];

// Sajat kontextus kell: file:// alatt minden lap ugyanazt a localStorage-t
// latja, tehat a kapcsolo allasa atszivarogna az egyik esetbol a masikba.
const open = async (b, testMode) => {
  const ctx = await b.newContext({ viewport: { width: 390, height: 1000 } });
  const p = await ctx.newPage();
  p.__ctx = ctx;
  p.__errs = []; p.on('pageerror', e => p.__errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`
    try {
      localStorage.setItem('boh_onboarded','1');
      // A stub alapbol teszt modba all — itt mindket iranyt kimondjuk, de CSAK
      // az elso betolteskor: ujratoltes utan epp azt vizsgaljuk, mire allt at.
      if (!localStorage.getItem('boh_seeded')) {
        localStorage.setItem('boh_seeded','1');
        localStorage.setItem('boh_testdb', ${testMode ? "'1'" : "'0'"});
      }
    } catch(e) {}
    window.__fbStore['profiles'] = { p_a:{ name:'Anna', color:'#5BA0DB' } };
    ['stats','game_stats','statEvents','gameStatEvents','seasons','usage','config']
      .forEach(k => window.__fbStore[k] = {});
  `);
  await p.goto(BASE, { waitUntil: 'domcontentloaded', timeout: 90000 });
  await p.waitForTimeout(3600);
  return p;
};

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const src = fs.readFileSync(SRC, 'utf8');

  // ─── 1) EGYETLEN ut vezet a statisztika-kollekciokhoz ───
  // Ez a legfontosabb ellenorzes: egy kihagyott hivashely ket modban ugyanoda
  // irna, es ezt semmilyen felulet nem mutatna meg.
  console.log('\n===== EGY ÚT VEZET ODA =====');
  {
    // A v10.180 verzioja csak a "db.collection('x')" alakot kereste, ezert nem
    // vette eszre a profil-osszevono db2.collection('stats') hivasait — azok
    // mindket modban a teszt statisztikaba irtak. Most barmilyen valtozon
    // elkapjuk; az egyetlen kivetel a coll() sajat definicioja, es az egyszeri
    // atemelo, ami szandekosan mindket kollekciot NEVEN nevezi.
    const bypass = [];
    src.split('\n').forEach((line, i) => {
      if (/return db\.collection\(split/.test(line)) return;
      if (/fdb\.collection\(/.test(line)) return;
      SPLIT.forEach(n => {
        if (new RegExp("\\.collection\\('" + n + "'\\)").test(line))
          bypass.push(n + ' @' + (i + 1));
      });
    });
    ok('egyetlen hívás sem kerüli meg a coll()-t', bypass.length === 0,
       bypass.length ? 'kimaradt: ' + bypass.join(', ') : SPLIT.length + ' kollekció');
    const n = (src.match(/[^.\w]coll\('/g) || []).length;
    ok('a coll() tényleg használatban van', n >= 15, n + ' hívás');
  }

  // ─── 2) A coll() iranya ───
  console.log('\n===== MELYIK ADATBÁZIS =====');
  {
    const p = await open(b, false);
    const r = await p.evaluate((names) => {
      const out = { def: window.isTestDb(), live: {}, test: {} };
      names.forEach(n => { out.live[n] = window.bohColl(n).__name || window.bohColl(n).path || window.bohColl(n).id; });
      window.setTestDb(true);
      out.after = window.isTestDb();
      names.forEach(n => { out.test[n] = window.bohColl(n).__name || window.bohColl(n).path || window.bohColl(n).id; });
      window.setTestDb(false);
      return out;
    }, SPLIT);
    ok('alapból ÉLES (nem kell semmit nyomni hozzá)', r.def === false, String(r.def));
    const liveBad = SPLIT.filter(n => r.live[n] !== 'live_' + n);
    ok('éles módban minden a live_ kollekciókba megy', liveBad.length === 0,
       liveBad.length ? liveBad.map(n => n + '→' + r.live[n]).join(', ') : Object.values(r.live).join(', '));
    const testBad = SPLIT.filter(n => r.test[n] !== n);
    ok('teszt módban a mostani (prefix nélküli) kollekciók — nem kellett adatot mozgatni',
       testBad.length === 0,
       testBad.length ? testBad.map(n => n + '→' + r.test[n]).join(', ') : Object.values(r.test).join(', '));

    // Amit szandekosan NEM valasztunk ketté: ezek nem az eredmenyekrol szolnak,
    // es a szezonok is csak datumokat tarolnak — az allas mindig az epp aktiv
    // statisztikabol szamolodik.
    const shared = await p.evaluate((names) => {
      const out = {};
      names.forEach(n => {
        window.setTestDb(true);  const a = window.bohColl(n).path;
        window.setTestDb(false); const b = window.bohColl(n).path;
        out[n] = a === b ? a : (a + '/' + b);
      });
      return out;
    }, ['config', 'rooms', 'barDrinks', 'tasks', 'party_templates', 'seasons']);
    const split = Object.keys(shared).filter(k => shared[k] !== k);
    ok('a nem eredmény-jellegű kollekciók közösek maradnak', split.length === 0,
       split.length ? split.map(k => k + '→' + shared[k]).join(', ') : Object.keys(shared).join(', '));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.__ctx.close();
  }

  // ─── 3) A rejtett kapcsolo ───
  // Rejtett, mert nem napi funkcio — de pont ezert kell, hogy 1-2 veletlen
  // koppintas NE valtsa at.
  console.log('\n===== A HÁROM KOPPINTÁS =====');
  {
    const p = await open(b, false);
    // a LEGSZUKEBB elem, ami meg tartalmazza a verziot — a tagabb wrapperekre
    // kattintva az esemeny felfele buborekol, nem le a kezelohoz
    const ver = await p.evaluate(() => {
      const all = [...document.querySelectorAll('div')].filter(x => /v\d+\.\d+/.test(x.textContent));
      if (!all.length) return null;
      all.sort((a, b) => a.textContent.length - b.textContent.length);
      window.__ver = all[0];
      return all[0].textContent.trim();
    });
    ok('a verziószám megvan a kezdőképernyőn', ver !== null, ver);

    const tap = (n) => p.evaluate(k => { for (let i = 0; i < k; i++) window.__ver.click(); }, n);
    const state = () => p.evaluate(() => localStorage.getItem('boh_testdb'));

    await tap(2); await p.waitForTimeout(200);
    ok('két koppintás még nem vált', (await state()) !== '1', await state());

    await p.waitForTimeout(1800);   // a szamlalo lejar
    await tap(2); await p.waitForTimeout(200);
    ok('a számláló lejár — 2+2 koppintás sem vált', (await state()) !== '1', await state());

    await p.waitForTimeout(1800);
    await tap(3); await p.waitForTimeout(300);
    ok('három koppintásra teszt módba vált', (await state()) === '1', await state());

    const toast = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    ok('a váltásról üzenet szól', /Teszt adatbázis — mostantól MINDEN eszközön/.test(toast),
       (toast.match(/Teszt adatbázis.{0,60}/) || ['NINCS ÜZENET'])[0]);
    await p.__ctx.close();
  }

  // ─── 4) Teszt modban latszik is, hogy teszt modban vagyunk ───
  // Enelkul konnyu ott felejtodni: az app ugyanugy nez ki, csak az adat megy
  // mashova.
  console.log('\n===== LÁTSZIK, HOGY TESZT MÓD =====');
  {
    const p = await open(b, true);
    const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    ok('a kezdőképernyőn ott a jelzés', /TESZT DB/.test(t), (t.match(/.{0,30}TESZT DB/) || ['NINCS JELZÉS'])[0]);

    // es vissza is lehet kapcsolni
    await p.evaluate(() => {
      const all = [...document.querySelectorAll('div')].filter(x => /v\d+\.\d+/.test(x.textContent));
      all.sort((a, b) => a.textContent.length - b.textContent.length);
      for (let i = 0; i < 3; i++) all[0].click();
    });
    await p.waitForTimeout(300);
    ok('vissza is lehet kapcsolni élesre',
       (await p.evaluate(() => localStorage.getItem('boh_testdb'))) === '0',
       await p.evaluate(() => localStorage.getItem('boh_testdb')));
    const t2 = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    ok('erről is szól üzenet', /Éles adatbázis — mostantól MINDEN eszközön/.test(t2),
       (t2.match(/Éles adatbázis.{0,50}/) || ['NINCS ÜZENET'])[0]);
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.__ctx.close();
  }

  // ─── 5) Az iras tenyleg a helyere kerul ───
  // A ket elozo pont kulon-kulon jo lehet ugy is, hogy a tenyleges statisztika-
  // iras megis rossz helyre megy — ezert egy valodi irast is megnezunk.
  console.log('\n===== AZ ÍRÁS HELYE =====');
  {
    for (const [mode, want, other] of [[false, 'live_stats', 'stats'], [true, 'stats', 'live_stats']]) {
      const p = await open(b, mode);
      await p.evaluate(() => { window.__fbStore['stats'] = {}; window.__fbStore['live_stats'] = {}; });
      await p.evaluate(() => incrementStats('p_a', { games: 1, wins: 1 }));
      await p.waitForTimeout(700);
      const seen = await p.evaluate(() => ({
        stats: Object.keys(window.__fbStore['stats'] || {}),
        live: Object.keys(window.__fbStore['live_stats'] || {}),
      }));
      const hit = mode ? seen.stats : seen.live;
      const miss = mode ? seen.live : seen.stats;
      ok(`${mode ? 'teszt' : 'éles'} módban a(z) ${want} kapja az adatot`,
         hit.includes('p_a') && !miss.includes('p_a'),
         `${want}: [${hit.join(',')}] · ${other}: [${miss.join(',')}]`);
      await p.__ctx.close();
    }
  }

  // ─── 6) A valtas GLOBALIS ───
  // Ez a v10.181 lenyege. Eszkozonkent tarolva egy buli statisztikaja ketfele
  // eshetett: az egyik telefon a teszt-, a masik az eles kollekciokba irt volna,
  // es semmi nem jelezte volna.
  console.log('\n===== MINDENKINÉL VÁLT =====');
  {
    // a) a koppintas kiirja a kozos dokumentumot — enelkul a tobbi keszulek
    //    sosem ertesulne rola
    const p = await open(b, false);
    await p.evaluate(() => {
      const all = [...document.querySelectorAll('div')].filter(x => /v\d+\.\d+/.test(x.textContent));
      all.sort((a, b) => a.textContent.length - b.textContent.length);
      for (let i = 0; i < 3; i++) all[0].click();
    });
    await p.waitForTimeout(400);
    const doc = await p.evaluate(() => (window.__fbStore['config'] || {}).dbMode);
    ok('a koppintás a közös config/dbMode dokumentumba ír', !!doc && doc.test === true,
       JSON.stringify(doc));
    await p.__ctx.close();
  }
  {
    // b) ha valaki MASHOL kapcsol, ez a keszulek is atall — es ujratolt,
    //    kulonben a kepernyon a masik adatbazis adata maradna
    const p = await open(b, false);
    // A location.reload nem irhato felul (a Location [LegacyUnforgeable]), ezert
    // egy jelzot teszunk le: az ujratoltes uj window-t hoz, tehat ha a jelzo
    // eltunt, a lap tenyleg ujratoltott.
    await p.evaluate(() => { window.__alive = 1; });
    await p.evaluate(() => firebase.firestore().collection('config').doc('dbMode')
      .set({ test: true, ts: Date.now() }));
    await p.waitForTimeout(4500);   // ujratoltes + ujboli indulas
    ok('a másik készüléken indított váltást ez is átveszi',
       (await p.evaluate(() => localStorage.getItem('boh_testdb'))) === '1',
       await p.evaluate(() => localStorage.getItem('boh_testdb')));
    ok('és újratölt, hogy ne a másik adatbázis adata maradjon a képernyőn',
       (await p.evaluate(() => window.__alive)) === undefined);

    // ugyanaz az ertek ujra — NEM szabad ujra ujratolteni, kulonben egy
    // ismetlodo snapshot vegtelen ujratoltes-hurkot csinalna
    await p.evaluate(() => { window.__alive = 1; });
    await p.evaluate(() => firebase.firestore().collection('config').doc('dbMode')
      .set({ test: true, ts: Date.now() + 1 }));
    await p.waitForTimeout(1500);
    ok('változatlan érték nem tölt újra (nincs újratöltés-hurok)',
       (await p.evaluate(() => window.__alive)) === 1);
    await p.__ctx.close();
  }
  {
    // c) hianyzo dokumentum = nincs jelzes. Ha ezt "eles"-nek vennenk, egy
    //    elakadt olvasas menet kozben kikapcsolna a teszt modot mindenkinel.
    const p = await open(b, true);
    await p.evaluate(() => { window.__alive = 1; });
    await p.waitForTimeout(1200);
    const r = await p.evaluate(() => ({
      cache: localStorage.getItem('boh_testdb'), alive: window.__alive === 1 }));
    ok('hiányzó dokumentum nem kapcsol át senkit menet közben',
       r.cache === '1' && r.alive === true, JSON.stringify(r));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.__ctx.close();
  }

  // ─── 7) A profilok atemelese ───
  // Az eles profil-lista uresen indul, ezert egy egyszeri atemeles hozza at a
  // SZEMELYES adatokat. Harom dolog szamit: az azonositok maradjanak, eredmeny
  // NE jojjon at, es a mar elesben levo, HIANYOS profil is toltodjon fel.
  //
  // Ez utobbi valos hiba volt: a Jatekosok kepernyo indulaskor beirja a 12 elore
  // beallitott profilt az EPP AKTIV adatbazisba. Aki eles modban ranyitott,
  // annal letrejottek a hardkodolt alapertekekkel, es a regi atemeles ezeket
  // "mar megvolt"-kent kihagyta — a becenev, avatar, korty limit sosem jott at.
  console.log('\n===== A PROFILOK ÁTEMELÉSE =====');
  {
    const p = await open(b, true);
    await p.evaluate(() => {
      window.__fbStore['profiles'] = {
        p_a: { name:'Anna', color:'#5BA0DB', nickname:'Ani', phone:'+3612', email:'a@x.hu',
               birthday:'1990-05-05', img:'assets/avatars/char_1.png', avatarId:'c1', drinkLimit:12,
               // eredmeny-jellegu mezok: ezeknek NEM szabad atmenniuk
               games:99, wins:42, bp_h2h:{ p_b:{ w:3 } }, badges:['x'] },
        // ezt a Jatekosok kepernyo mar letrehozta elesben, alapertekekkel
        preset_x: { name:'Tóth Bence', color:'#10B981', nickname:'Tóth', drinkLimit:8, phone:'+3620' },
        p_b: { name:'Béla', color:'#E07A5F' },
        p_junk: { color:'#000' },          // nev nelkuli szemet — kimarad
      };
      window.__fbStore['live_profiles'] = {
        p_b: { name:'Béla (élesben javítva)', color:'#111' },
        preset_x: { name:'Tóth Bence', color:'#10B981' },   // becenev, limit, telefon hianyzik
      };
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__cp';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);padding:16px';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(AdminProfileCopy, { onDone: () => {} }));
    });
    await p.waitForTimeout(1400);

    // a) MEG A GOMB ELOTT megmondja, mi hianyzik
    const before = await p.evaluate(() => document.querySelector('#__cp').innerText.replace(/\s+/g, ' '));
    ok('gombnyomás nélkül kiírja a két oldal darabszámát',
       /teszt 4/i.test(before) && /éles 2/i.test(before),
       (before.match(/TESZT \d+ ÉLES \d+/i) || ['—'])[0]);
    ok('névszerint megmondja, ki nincs meg élesben',
       /Élesben még nincs meg \(1\): Anna/.test(before),
       (before.match(/Élesben még nincs meg[^E]*/) || ['NEM ÍRJA KI'])[0]);
    ok('azt is, ki van fent hiányos adattal',
       /Hiányos adattal van fenn \(1\): Tóth Bence/.test(before),
       (before.match(/Hiányos adattal[^A-ZÉ]*[^ ]*/) || ['NEM ÍRJA KI'])[0]);

    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__cp button')].find(x => /Átemelés/.test(x.innerText));
      if (btn) btn.click();
    });
    await p.waitForTimeout(1400);

    const live = await p.evaluate(() => window.__fbStore['live_profiles']);
    // b) a hianyzo profil teljes egeszeben atjon
    const a = live.p_a || {};
    ok('a hiányzó profil ugyanazzal az azonosítóval kerül át', !!live.p_a, Object.keys(live).join(', '));
    const wantPersonal = ['name','color','nickname','phone','email','birthday','img','avatarId','drinkLimit'];
    const missing = wantPersonal.filter(k => a[k] === undefined);
    ok('a személyes adatok mind átmennek', missing.length === 0,
       missing.length ? 'hiányzik: ' + missing.join(', ') : wantPersonal.join(', '));
    const leaked = ['games','wins','bp_h2h','badges'].filter(k => a[k] !== undefined);
    ok('az eredmények NEM mennek át', leaked.length === 0,
       leaked.length ? 'átszivárgott: ' + leaked.join(', ') : 'egy sem');

    // c) EZ A JAVITAS: a mar fent levo, hianyos profil feltoltodik
    const px = live.preset_x || {};
    ok('a hiányos éles profil megkapja a hiányzó mezőket',
       px.nickname === 'Tóth' && px.drinkLimit === 8 && px.phone === '+3620',
       JSON.stringify(px));
    // d) de amit elesben mar kitoltottek, ahhoz nem nyulunk
    ok('a már kitöltött éles érték marad', (live.p_b || {}).name === 'Béla (élesben javítva)',
       (live.p_b || {}).name);
    ok('a név nélküli szemét kimarad', live.p_junk === undefined, JSON.stringify(live.p_junk));

    const msg = await p.evaluate(() => document.querySelector('#__cp').innerText.replace(/\s+/g, ' '));
    ok('megmondja, mi történt',
       /1 új profil/.test(msg) && /1 kiegészítve/.test(msg) && /1 névtelen kihagyva/.test(msg),
       (msg.match(/\d+ új profil[^.]*/) || ['NINCS VISSZAJELZÉS'])[0]);
    ok('utána már nincs eltérés', /Minden teszt profil fent van élesben/.test(msg),
       (msg.match(/Minden teszt profil[^.]*/) || ['MÉG VAN ELTÉRÉS'])[0]);

    // e) masodszorra nincs mit tenni
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__cp button')].find(x => /Átemelés/.test(x.innerText));
      if (btn) btn.click();
    });
    await p.waitForTimeout(1200);
    const msg2 = await p.evaluate(() => document.querySelector('#__cp').innerText.replace(/\s+/g, ' '));
    ok('másodszorra nem másol újra', /0 új profil/.test(msg2),
       (msg2.match(/\d+ új profil[^.]*/) || ['—'])[0]);
    ok('a teszt profilok érintetlenül maradnak',
       (await p.evaluate(() => Object.keys(window.__fbStore['profiles']).length)) === 4);
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.__ctx.close();
  }

  // ─── 8) Sok profil: a koteg 500-nal elhasad ───
  // A Firestore egy kotegben 500 irast enged. Egyetlen kotegben a 600. profil
  // csendben nem jonne at — es a visszajelzes megis sikert mondana.
  console.log('\n===== SOK PROFIL =====');
  {
    const p = await open(b, true);
    await p.evaluate(() => {
      const src = {};
      for (let i = 0; i < 600; i++) src['p' + i] = { name: 'J' + i, color: '#111' };
      window.__fbStore['profiles'] = src;
      window.__fbStore['live_profiles'] = {};
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__cp';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg);padding:16px';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(AdminProfileCopy, { onDone: () => {} }));
    });
    await p.waitForTimeout(1400);
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__cp button')].find(x => /Átemelés/.test(x.innerText));
      if (btn) btn.click();
    });
    await p.waitForTimeout(2500);
    const n = await p.evaluate(() => Object.keys(window.__fbStore['live_profiles'] || {}).length);
    ok('600 profil is hiánytalanul átmegy (több kötegben)', n === 600, n + ' profil');
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.__ctx.close();
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
