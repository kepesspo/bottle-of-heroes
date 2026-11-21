// v10.432 — Gender Reveal: leleplezés, vendégfeltöltés jóváhagyással, jókívánság-fal,
// Babaquiz, album.
//
// Fogódzók:
//  1) admin: az eredmény titkos dokumentumban (`revealSecret`), mentés után maszkolva;
//     a `revealState`-ben a leleplezésig NINCS eredmény
//  2) ⚠️ az operátor NEM tud leleplezni; a Leleplező külön kóddal (hibás kód → nem enged)
//  3) leleplezés: a vetítőn visszaszámlálás → robbanás a helyes felirattal → utána a
//     képfolyam a kiderült színben (`data-reveal-revealed`)
//  4) próba-leleplezés: lefut, de nem árul el semmit és nem színezi a vetítőt
//  5) ⚠️ később nyitott vetítő: animáció NÉLKÜL rögtön a kiderült szín
//  6) vendég (QR-link, jelszó nélkül): név → kép és üzenet `pending`-ként; a vetítő
//     nem mutatja; az operátor jóváhagyja → a vetítőn rögtön jön, ÚJ jelöléssel
//  7) Babakvíz (v10.433): a PDF 20 kérdése; papíron szavaznak — a vetítő/operátor csak
//     lapoz: kérdések → ugyanezek a helyes válasszal kiemelve → pontozás → vége
//  8) album: ZIP (Python zipfile-lal ellenőrizve) + a csak nézhető galéria-link
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs'), cp = require('child_process');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const PX = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 1400, height: 820 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.addInitScript(`(function(){ try { var s = JSON.parse(sessionStorage.getItem('__rv') || 'null'); if (s) Object.keys(s).forEach(function(k){ window.__fbStore[k] = s[k]; }); } catch(e) {}
    window.__rvSave = function(){ sessionStorage.setItem('__rv', JSON.stringify({ config: window.__fbStore.config || {}, revealPhotos: window.__fbStore.revealPhotos || {}, revealQuizAns: window.__fbStore.revealQuizAns || {} })); }; })();`);
  const go = async q => { await p.goto('file://' + ROOT + '/index.html?screen=reveal' + (q || ''), { waitUntil: 'domcontentloaded' }); await p.waitForTimeout(2600); };
  const has = sel => p.evaluate(s => !!document.querySelector(s), sel);
  const attr = (sel, a) => p.evaluate(({ s, a }) => { const e = document.querySelector(s); return e ? e.getAttribute(a) : null; }, { s: sel, a });
  const store = () => p.evaluate(() => JSON.parse(JSON.stringify({ c: window.__fbStore.config || {}, ph: window.__fbStore.revealPhotos || {}, qa: window.__fbStore.revealQuizAns || {} })));
  // egy második nézet a vetítő mellé (jobb oldalon, a vetítő portálja fölött)
  const mountSide = (comp, props) => p.evaluate(({ comp, props }) => {
    let d = document.getElementById('__side'); if (d) { d.__r.unmount(); d.remove(); }
    d = document.createElement('div'); d.id = '__side';
    d.style.cssText = 'position:fixed;right:0;top:0;width:420px;height:100vh;z-index:6500;background:#fff;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(d); d.__r = ReactDOM.createRoot(d); d.__r.render(React.createElement(window[comp] || eval(comp), Object.assign({ onBack: () => {} }, props || {})));
  }, { comp, props });
  // v10.450: a Jóváhagyás döntés-gombjai a lap ALJÁN, az ÉPP látható tételre — odalapozunk, aztán döntünk
  const decide = async (id, what) => {
    await p.evaluate(id => { const tr = document.querySelector('[data-reveal-reviewtrack]'), el = tr && tr.querySelector(`[data-reveal-pend="${id}"]`);
      if (el) { tr.scrollLeft = (+el.getAttribute('data-idx')) * tr.clientWidth; tr.dispatchEvent(new Event('scroll')); } }, id);
    await p.waitForTimeout(150);
    await p.evaluate(w => document.querySelector(`[data-reveal-review] [data-reveal-${w}]`).click(), what);
    await p.waitForTimeout(200);
  };
  const login = async () => { await p.waitForSelector('[data-reveal-key]', { timeout: 8000 }).catch(() => {}); await p.keyboard.type('1234'); await p.waitForTimeout(350); };

  // ── alapállapot: jelszó, címek, kulcsok az admin mentésével ──
  await go();
  await p.evaluate(() => { window.__revealSpeed = 0.06; });
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = '__adm'; d.style.cssText = 'position:fixed;inset:0;z-index:9000;background:#fff;overflow:auto';
    document.body.appendChild(d); d.__r = ReactDOM.createRoot(d); d.__r.render(React.createElement(AdminReveal));
  });
  await p.waitForTimeout(300);

  console.log('\n===== 1. ADMIN: CSAK A BELÉPŐ KÓD · A TITKOS RÉSZ A SZÜLŐKNÉL (v10.455) =====');
  const admGone = await p.evaluate(() => ['title', 'when', 'countdown', 'clear', 'zip', 'quiz', 'guesturl', 'albumurl', 'secret', 'result', 'code', 'video', 'secretsave', 'state'].filter(k => document.querySelector('[data-admin-reveal-' + k + ']')));
  ok(admGone.length === 0, 'v10.455: az adminban CSAK a belépő kód maradt (nincs eredmény, szülői kód, videó)', admGone.join(','));
  ok(await has('[data-admin-reveal-moved]') && await has('[data-admin-reveal-pw]'), 'az admin megmondja, hová került minden más');
  await p.fill('[data-admin-reveal-pw]', '1234');
  await p.click('[data-admin-reveal-save]'); await p.waitForTimeout(200);
  let st = await store();
  ok(st.c.revealConfig.guestKey && st.c.revealConfig.albumKey && st.c.revealConfig.guestKey !== st.c.revealConfig.albumKey, 'mentéskor vendég- és album-kulcs keletkezik', JSON.stringify(st.c.revealConfig));
  await p.evaluate(() => { const d = document.getElementById('__adm'); d.__r.unmount(); d.remove(); });
  // kód nélkül a Szülők maguk állítják be az elsőt
  await mountSide('RevealTrigger'); await p.waitForTimeout(250);
  ok(await has('#__side [data-reveal-nocode] [data-reveal-p-newcode]'), 'szülői kód nélkül: „Szülői kód beállítása" (nem az admin)');
  await p.fill('#__side [data-reveal-p-newcode]', '20'); await p.waitForTimeout(60);
  ok(await p.evaluate(() => [...document.querySelectorAll('#__side [data-reveal-nocode] button')].find(b => /Kód mentése/.test(b.textContent)).disabled), '4 jegynél rövidebb kód nem menthető');
  await p.fill('#__side [data-reveal-p-newcode]', '2026'); await p.waitForTimeout(60);
  await p.evaluate(() => [...document.querySelectorAll('#__side [data-reveal-nocode] button')].find(b => /Kód mentése/.test(b.textContent)).click()); await p.waitForTimeout(300);
  st = await store();
  ok(st.c.revealSecret && st.c.revealSecret.code === '2026' && await has('#__side [data-reveal-p-schedule]'), 'a kód a titkos dokumentumba megy, és beenged', JSON.stringify(st.c.revealSecret));
  ok(!(await has('#__side [data-reveal-p-secret]')), 'a titkos kártya alapból CSUKVA');
  await p.click('#__side [data-reveal-p-secretrow]'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-p-secret]') && await has('#__side [data-reveal-p-result="girl"]'), 'az „Eredmény és kód" sorra koppintva nyílik; eredmény nélkül a két gomb látszik');
  await p.click('#__side [data-reveal-p-result="girl"]'); await p.waitForTimeout(250);
  st = await store();
  ok(st.c.revealSecret.result === 'girl' && st.c.revealSecret.code === '2026', 'az eredmény koppintásra a TITKOS dokumentumba megy', JSON.stringify(st.c.revealSecret));
  ok(!st.c.revealState, '⚠️ a leleplezésig a revealState-ben nincs eredmény');
  ok(!(await has('#__side [data-reveal-p-videourl]')), 'v10.456: a titkos kártyán NINCS videó-link mező (a videót feltöltik)');
  await p.fill('#__side [data-reveal-p-code]', '20'); await p.waitForTimeout(60);
  ok(await p.evaluate(() => document.querySelector('#__side [data-reveal-p-codesave]').disabled), 'a kódcsere rövid kóddal tiltott');
  await p.fill('#__side [data-reveal-p-code]', '2026'); await p.waitForTimeout(60);
  // újranyitva: maszkolva
  await mountSide('RevealTrigger'); await p.waitForTimeout(200);
  await p.waitForSelector('#__side [data-reveal-key]'); await p.keyboard.type('2026'); await p.waitForTimeout(350);
  await p.click('#__side [data-reveal-p-secretrow]'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-p-masked]') && !(await has('#__side [data-reveal-p-result="girl"]')), 'újranyitva az eredmény maszkolva („●●● beállítva")');
  await p.click('#__side [data-reveal-p-peek]'); await p.waitForTimeout(80);
  ok(await p.getAttribute('#__side [data-reveal-p-result="girl"]', 'aria-pressed') === 'true', '👁 Mutat → látszik, a Kislány kijelölve');
  await p.evaluate(() => { const d = document.getElementById('__side'); d.__r.unmount(); d.remove(); });
  // v10.439: a cím, a linkek és az időpont a Szülőknél
  await mountSide('RevealTrigger'); await p.waitForTimeout(200);
  ok(!(await has('#__side [data-reveal-p-schedule]')), 'a Szülők beállításai a kód mögött vannak');
  await p.keyboard.type('2026'); await p.waitForTimeout(350);
  // v10.448: a fül-sáv PORTÁLBAN van (a body-ban, fixen alul) — a teszt oldalpanelje
  // (z-index 6500) eltakarja, ezért a fülváltás JS-kattintással megy.
  // v10.444: négy fül — Leleplezés · Vetítő · Kvíz · Esemény; egyszerre csak egy látszik
  const tabs = await p.evaluate(() => [...document.querySelectorAll('[data-reveal-ptab]')].map(b => b.getAttribute('data-reveal-ptab')).join(','));
  ok(tabs === 'reveal,proj,quiz,event' && await has('#__side [data-reveal-pstatus]'), 'v10.444: alul négy fül, felül az állapot-sáv', tabs);
  const onTab = async () => p.evaluate(() => ['schedule', 'video', 'links', 'album'].filter(k => document.querySelector('#__side [data-reveal-p-' + k + ']')).join(',')
    + (document.querySelector('#__side [data-reveal-parentctl]') ? '+ctl' : '') + (document.querySelector('#__side [data-reveal-quizctl]') ? '+quiz' : ''));
  ok((await onTab()) === 'schedule,video', 'Leleplezés fül: előkészületek + videó', await onTab());
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="proj"]').click()); await p.waitForTimeout(100);
  ok((await onTab()) === '+ctl', 'Vetítő fül: csak a vetítő beállításai', await onTab());
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="quiz"]').click()); await p.waitForTimeout(100);
  ok((await onTab()) === '+quiz' && await has('#__side [data-reveal-p-quizeditbtn]'), 'Kvíz fül: lapozó + kérdések szerkesztése', await onTab());
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="event"]').click()); await p.waitForTimeout(100);
  ok((await onTab()) === 'links,album', 'Esemény fül: cím, linkek, album', await onTab());
  ok(await has('#__side [data-reveal-p-guesturl]') && await has('#__side [data-reveal-p-albumurl]'), 'a két link a Szülőknél');
  ok(!(await has('#__side [data-reveal-p-titlesave]')) && !(await has('#__side [data-reveal-p-schedsave]')), 'nincs külön Mentés gomb');
  await p.fill('#__side [data-reveal-p-title]', 'Anna & Bence babája'); await p.waitForTimeout(700);   // azonnali mentés (450 ms késleltetés)
  ok((await p.textContent('#__side [data-reveal-p-linksmsg]')).includes('Mentve'), 'a cím azonnal ment („Mentve")');
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="reveal"]').click()); await p.waitForTimeout(100);
  ok(!(await has('#__side [data-reveal-p-when]')), 'az időpont-mező a sorra koppintva nyílik');
  await p.click('#__side [data-reveal-p-whenrow]'); await p.waitForTimeout(100);
  await p.fill('#__side [data-reveal-p-when]', '2030-06-01T18:30'); await p.waitForTimeout(200);
  ok(!(await has('#__side [data-reveal-p-countdown]')), 'v10.453: a Leleplezés fülön NINCS visszaszámláló-kapcsoló');
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="proj"]').click()); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-parentctl] [data-reveal-p-countdown]') && !(await has('#__side [data-reveal-p-countdownnote]')), 'a Vetítő fülön van (időponttal nincs figyelmeztetés)');
  ok((await attr('#__side [data-reveal-p-countdown]', 'aria-checked')) === 'true', 'a visszaszámláló alapból BE (kapcsoló)');
  await p.click('#__side [data-reveal-p-countdown]'); await p.waitForTimeout(200);   // BE → KI, azonnal ment
  st = await store();
  ok(st.c.revealConfig.title === 'Anna & Bence babája', 'a cím a Szülőktől mentődik', st.c.revealConfig.title);
  ok(st.c.revealConfig.revealAt === new Date(2030, 5, 1, 18, 30).getTime() && st.c.revealConfig.countdownOn === false, 'az időpont (helyi idő) és a visszaszámláló-kapcsoló a revealConfig-ba megy', JSON.stringify([st.c.revealConfig.revealAt, st.c.revealConfig.countdownOn]));
  ok(!st.c.revealSecret.revealAt, 'az időpont nem a titkos dokumentumba kerül');
  ok((await attr('#__side [data-reveal-p-countdown]', 'aria-checked')) === 'false', 'a kapcsoló követi a mentett állapotot');
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="reveal"]').click()); await p.waitForTimeout(100);
  ok(await has('#__side [data-reveal-when]'), 'a Leleplezés fülön az időpont-sor marad');
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="quiz"]').click()); await p.waitForTimeout(100);
  await p.click('#__side [data-reveal-p-quizeditbtn]'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-p-quizedit] [data-admin-reveal-quiz]'), 'a Babakvíz kérdései a Szülőknél szerkeszthetők (teljes képernyős lapon)');
  await p.evaluate(() => { const d = document.getElementById('__side'); d.__r.unmount(); d.remove(); });
  await p.evaluate(() => window.__rvSave());

  console.log('\n===== 2. KI LELEPLEZHET =====');
  await go(); await p.evaluate(() => { window.__revealSpeed = 0.06; });
  await login();
  ok(await has('[data-reveal-role="trigger"]') && (await p.textContent('[data-reveal-role="trigger"]')).includes('Szülők'), 'a szerepválasztón: Vetítő · Operátor · Szülők');
  await p.click('[data-reveal-role="operator"]'); await p.waitForTimeout(200);
  ok(!(await has('[data-reveal-fire]')) && !(await has('[data-reveal-test]')), '⚠️ az operátor nézetben NINCS leleplező gomb');
  await p.click('.appbar-shell button'); await p.waitForTimeout(150);
  await p.click('[data-reveal-role="projector"]'); await p.waitForTimeout(300);
  ok(await has('[data-reveal-projector]') && !(await attr('[data-reveal-projector]', 'data-reveal-revealed')), 'a vetítő nyitva, még nincs eredmény');
  await mountSide('RevealTrigger');
  await p.waitForTimeout(200);
  ok(await has('#__side [data-reveal-codegate]'), 'a Leleplező kódot kér');
  ok(await p.evaluate(() => document.querySelectorAll('#__side [data-reveal-codegate] [data-reveal-key]').length === 10 && !document.querySelector('#__side input[data-reveal-code]')), 'v10.452: a Szülői kód is számbillentyűzeten (nincs szövegmező)');
  await p.keyboard.type('1234'); await p.waitForTimeout(350);
  ok(await has('#__side [data-reveal-codebad]') && !(await has('[data-reveal-fire]')), 'a közös jelszó NEM jó leleplező kódnak');
  await p.keyboard.type('2026'); await p.waitForTimeout(350);
  ok(await has('[data-reveal-fire]'), 'a jó kóddal ott a LELEPLEZÉS gomb');
  ok(!/lány|fiú/i.test(await p.textContent('[data-reveal-firepanel]')), 'a leleplező sem látja az eredményt');

  console.log('\n===== 4. PRÓBA-LELEPLEZÉS =====');
  await p.click('[data-reveal-test]'); await p.waitForTimeout(150);
  ok((await attr('[data-reveal-show]', 'data-reveal-show')) === 'count', 'próba: a vetítőn indul a visszaszámlálás');
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') === 'boom'; }, null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-show]', 'data-reveal-boom')) === 'test' && (await p.textContent('[data-reveal-word]')).includes('PRÓBA'), 'próba: „PRÓBA" robbanás, nem az eredmény');
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 4000 }).catch(() => {});
  ok(!(await has('[data-reveal-show]')) && !(await attr('[data-reveal-projector]', 'data-reveal-revealed')), 'próba után a vetítő NEM színeződik');

  console.log('\n===== 3. A NAGY LELEPLEZÉS =====');
  await p.click('[data-reveal-fire]'); await p.waitForTimeout(100);
  await p.click('button:has-text("Indulhat!")'); await p.waitForTimeout(120);
  st = await store();
  ok(st.c.revealState.phase === 'reveal' && st.c.revealState.result === 'girl' && !st.c.revealState.test, 'a gomb a titkos eredményt a szobába másolja', JSON.stringify(st.c.revealState));
  const cd = await attr('[data-reveal-show]', 'data-reveal-countdown');
  ok((await attr('[data-reveal-show]', 'data-reveal-show')) === 'count' && +cd >= 1 && +cd <= 10, 'visszaszámlálás a vetítőn', cd);
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') === 'boom'; }, null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-show]', 'data-reveal-boom')) === 'girl' && (await p.textContent('[data-reveal-word]')).trim() === 'KISLÁNY!', 'robbanás: „KISLÁNY!”');
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-projector]', 'data-reveal-revealed')) === 'girl' && await has('[data-reveal-resultbadge]'), 'utána a képfolyam a kiderült színben, sarok-jelvénnyel');
  const bc = await p.evaluate(() => { const r = document.querySelector('[data-reveal-resultbadge]').getBoundingClientRect(); return Math.round(r.left + r.width / 2 - innerWidth / 2); });
  ok(Math.abs(bc) < 4, 'v10.438: a jelvény fent KÖZÉPEN', bc);
  ok(!(await has('[data-reveal-replay]')), 'v10.438: a vetítőn nincs „Leleplezés újra" (a Szülőknél van)');

  console.log('\n===== 3b. VIDEÓ: hibás link sem akasztja meg =====');
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealState').set({ phase: 'reveal', run: 'vid1', test: false, result: 'girl', videoUrl: 'file:///nincs/ilyen.mp4', at: Date.now() }));
  ok(await has('[data-reveal-show="count"]') && await p.evaluate(() => { const v = document.querySelector('video[data-reveal-video][preload="auto"]'); return !!v && /ilyen\.mp4$/.test(v.getAttribute('src') || '') && v.style.display === 'none'; }), 'a videó már a visszaszámlálás alatt betöltődik (rejtve, a vetítő állandó elemében)');
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') !== 'count'; }, null, { timeout: 4000 }).catch(() => {});
  const vs = await attr('[data-reveal-show]', 'data-reveal-show');
  ok(vs === 'video' || vs === 'boom', 'a visszaszámlálás után a videó-szakasz jön', vs);
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') === 'boom'; }, null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-show]', 'data-reveal-boom')) === 'girl', 'betölthetetlen videónál is a robbanás jön');
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 4000 }).catch(() => {});

  console.log('\n===== 3b2. VIDEÓ LEMENT → NINCS „KISLÁNY!" KÉPERNYŐ, A VETÍTŐ JÖN (v10.456) =====');
  const tinyVid = 'file://' + ROOT + '/tests/fixtures/tiny_reveal.webm';   // 1 mp-es webm (ffmpeg, rózsaszín kép)
  await p.evaluate(() => { window.__stages = []; const mo = new MutationObserver(() => { const e = document.querySelector('[data-reveal-show]'); const v = e ? e.getAttribute('data-reveal-show') : 'none'; if (window.__stages[window.__stages.length - 1] !== v) window.__stages.push(v); });
    mo.observe(document.body, { subtree: true, childList: true, attributes: true, attributeFilter: ['data-reveal-show'] }); window.__stMo = mo; });
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealProjector').set({ vol: 0.5 }, { merge: true }));
  await p.evaluate(() => { window.__vidState = null; window.__landEarly = false;
    window.__vsIv = setInterval(() => { const v = document.querySelector('video[data-reveal-video]'), e = document.querySelector('[data-reveal-show]');
      if (v && e && e.getAttribute('data-reveal-show') === 'video' && !v.paused && !window.__vidState) window.__vidState = { muted: v.muted, vol: v.volume };
      if (e && e.getAttribute('data-reveal-show') === 'outro' && document.querySelector('[data-reveal-projector]').getAttribute('data-reveal-revealed') === 'girl') window.__landEarly = true; }, 20); });
  await p.evaluate(u => firebase.firestore().collection('config').doc('revealState').set({ phase: 'reveal', run: 'vidok', test: false, result: 'girl', videoUrl: u, at: Date.now() }), tinyVid);
  await p.waitForFunction(() => window.__stages.includes('video'), null, { timeout: 6000 }).catch(() => {});
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 8000 }).catch(() => {});
  const stg = await p.evaluate(() => { window.__stMo.disconnect(); clearInterval(window.__vsIv); return window.__stages.join('>'); });
  ok(stg.includes('video') && !stg.includes('boom'), 'a videó lement, és utána NEM jött robbanás-képernyő', stg);
  ok(/video>outro/.test(stg), 'v10.458: a videó után lágy átmenet (outro) jön, nem éles vágás', stg);
  const vstate = await p.evaluate(() => window.__vidState || null);
  ok(vstate && vstate.muted === false && Math.abs(vstate.vol - 0.5) < 0.01, 'v10.458: a videó HANGGAL indul, a Szülők hangerejével (50%)', JSON.stringify(vstate));
  ok(await p.evaluate(() => window.__landEarly === true), 'v10.458: a kiderült szín már az átmenet alatt a fal mögött van');
  ok((await attr('[data-reveal-projector]', 'data-reveal-revealed')) === 'girl', 'a vetítő a kiderült színnel folytatja');
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealState').set({ phase: 'reveal', run: 'vidyt', test: false, result: 'girl', videoUrl: 'https://www.youtube.com/watch?v=abc', at: Date.now() }));
  await p.waitForTimeout(150);
  ok(await p.evaluate(() => !/youtube/.test((document.querySelector('video[data-reveal-video]') || {}).getAttribute?.('src') || '')), 'YouTube-linket a vetítő nem próbál lejátszani (nem kerül a <video>-ba)');
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') === 'boom'; }, null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-show]', 'data-reveal-boom')) === 'girl', '…ilyenkor a robbanás mondja ki az eredményt');
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 4000 }).catch(() => {});

  console.log('\n===== 3c. VIDEÓ A SZÜLŐKTŐL (darabolt feltöltés, v10.439) =====');
  ok(!(await has('[data-reveal-videobtn]')) && !(await has('[data-reveal-videoinput]')), 'a vetítőn nincs videó-gomb');
  const vf = '/tmp/claude-0/-home-user-bottle-of-heroes/41faa226-19f7-5bf9-9bc4-4d933d77bf20/scratchpad/fake_reveal.mp4';
  fs.mkdirSync(require('path').dirname(vf), { recursive: true }); fs.writeFileSync(vf, Buffer.alloc(1500000, 7));
  await mountSide('RevealTrigger'); await p.waitForTimeout(200);
  await p.keyboard.type('2026'); await p.waitForTimeout(350);
  await p.setInputFiles('#__side [data-reveal-p-videoinput]', vf);
  await p.waitForFunction(() => { const m = (window.__fbStore.config || {}).revealVideo; return m && m.vid; }, null, { timeout: 15000 }).catch(() => {});
  const vm = await p.evaluate(() => { const m = window.__fbStore.config.revealVideo || {}, ch = Object.values(window.__fbStore.revealVideo || {});
    return { n: m.n, size: m.size, chunks: ch.filter(c => c.vid === m.vid).length, maxLen: Math.max(0, ...ch.map(c => c.d.length)) }; });
  ok(vm.n === 3 && vm.chunks === 3 && vm.size === 1500000 && vm.maxLen < 1000000, 'a videó 3 darabban, darabonként 1 MB alatt kerül a szobába', JSON.stringify(vm));
  await p.waitForTimeout(200);
  ok((await p.textContent('#__side [data-reveal-p-videostatus]')).includes('1.4 MB'), 'a Szülőknél: feltöltve, mérettel', await p.textContent('#__side [data-reveal-p-videostatus]'));
  ok(!(await has('#__side video')), 'a Szülők nem játsszák le (előnézet nincs)');
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-videoready="1"]'), null, { timeout: 5000 }).catch(() => {});
  ok(await has('[data-reveal-videoready="1"]'), 'a vetítő betöltötte (a sávon „videó kész")');
  // v10.458: hangerő (nincs némítás) + saját zene a visszaszámlálásra
  ok(await has('#__side [data-reveal-p-volrow]'), 'v10.458: videóval a Szülőknél hangerő-sor van');
  const volOpts = await p.evaluate(() => [...document.querySelectorAll('#__side [data-reveal-p-vol]')].map(b => b.textContent.trim()));
  ok(volOpts.join(',') === '25%,50%,75%,100%', '…négy fokozat, némítás nélkül', volOpts.join(','));
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__side [data-reveal-p-vol]')].find(x => x.textContent.trim() === '75%'); b.click(); });
  await p.waitForTimeout(150);
  ok(await p.evaluate(() => (window.__fbStore.config.revealProjector || {}).vol === 0.75), '…a választás a közös vetítő-dokumentumba megy (0.75)');
  const wav = vf.replace('fake_reveal.mp4', 'count_music.wav');
  { const sr = 8000, n = sr, buf = Buffer.alloc(44 + n * 2); buf.write('RIFF', 0); buf.writeUInt32LE(36 + n * 2, 4); buf.write('WAVEfmt ', 8); buf.writeUInt32LE(16, 16);
    buf.writeUInt16LE(1, 20); buf.writeUInt16LE(1, 22); buf.writeUInt32LE(sr, 24); buf.writeUInt32LE(sr * 2, 28); buf.writeUInt16LE(2, 32); buf.writeUInt16LE(16, 34); buf.write('data', 36); buf.writeUInt32LE(n * 2, 40);
    for (let i = 0; i < n; i++) buf.writeInt16LE(Math.round(Math.sin(i / 8) * 3000), 44 + i * 2); fs.writeFileSync(wav, buf); }
  ok(await has('#__side [data-reveal-p-musicinput]'), 'v10.458: a Szülőknél van „Visszaszámlálás zenéje" feltöltő');
  await p.setInputFiles('#__side [data-reveal-p-musicinput]', wav);
  await p.waitForFunction(() => { const m = (window.__fbStore.config || {}).revealAudio; return m && m.vid; }, null, { timeout: 15000 }).catch(() => {});
  ok(await p.evaluate(() => { const m = window.__fbStore.config.revealAudio || {}; return m.n === 1 && Object.values(window.__fbStore.revealAudio || {}).length === 1; }), '…a zene a saját gyűjteményébe kerül (revealAudio), a videó mellé');
  ok(await p.evaluate(() => Object.values(window.__fbStore.revealVideo || {}).length === 3), '…és a videó darabjai érintetlenek');
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-musicready="1"]'), null, { timeout: 5000 }).catch(() => {});
  ok(await has('[data-reveal-musicready="1"]'), '…a vetítő előre betöltötte („zene kész")');
  await p.evaluate(() => { window.__plays = []; const orig = HTMLMediaElement.prototype.play; HTMLMediaElement.prototype.play = function () { window.__plays.push({ tag: this.tagName, blob: String(this.src).startsWith('blob:'), vol: this.volume }); return orig.apply(this, arguments); }; });
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealState').set({ phase: 'reveal', run: 'vid2', test: false, result: 'girl', videoUrl: '', at: Date.now() }));
  await p.waitForTimeout(150);
  const vsrc = await p.evaluate(() => { const v = document.querySelector('video[data-reveal-video]'); return v ? v.getAttribute('src') : null; });
  ok((await attr('[data-reveal-show]', 'data-reveal-music')) === '1', 'v10.458: a visszaszámlálás a feltöltött zenével megy');
  const mp = await p.evaluate(() => window.__plays.filter(x => x.tag === 'AUDIO'));
  ok(mp.length === 1 && mp[0].blob && Math.abs(mp[0].vol - 0.75) < 0.01, '…a zene a feltöltött fájlból szól, a beállított hangerővel', JSON.stringify(mp));
  ok(vsrc && vsrc.startsWith('blob:'), 'a leleplezés a feltöltött videót viszi', vsrc);
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 6000 }).catch(() => {});
  // v10.457: nagy (85 MB) videó — darabonként olvasva fel, és a vetítő be is tölti
  const vbig = vf.replace('fake_reveal.mp4', 'fake_reveal_big.mp4'); const BIG = 85 * 1048576;
  fs.writeFileSync(vbig, Buffer.alloc(BIG, 3));
  await p.setInputFiles('#__side [data-reveal-p-videoinput]', vbig);
  await p.waitForFunction(B => { const m = (window.__fbStore.config || {}).revealVideo; return m && m.vid && m.size === B; }, BIG, { timeout: 120000 }).catch(() => {});
  const vb = await p.evaluate(() => { const m = window.__fbStore.config.revealVideo || {}, ch = Object.values(window.__fbStore.revealVideo || {});
    return { n: m.n, size: m.size, chunks: ch.filter(c => c.vid === m.vid).length, stale: ch.filter(c => c.vid !== m.vid).length, maxLen: Math.max(0, ...ch.map(c => c.d.length)) }; });
  ok(vb.size === BIG && vb.n === Math.ceil(BIG / 690000) && vb.chunks === vb.n && vb.stale === 0 && vb.maxLen < 1000000, '85 MB-os videó: feltöltve, minden darab 1 MB alatt, a régi darabok törölve', JSON.stringify(vb));
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-videoready="1"]'), null, { timeout: 60000 }).catch(() => {});
  const vbsz = await p.evaluate(() => { const v = document.querySelector('[data-reveal-videoready="1"]'); return v ? 1 : 0; });
  ok(vbsz === 1, 'a vetítő a 85 MB-os videót is betöltötte („videó kész")');
  fs.unlinkSync(vbig);
  // v10.459: a hang a leleplezés ELŐTT élesedik — nincs nagy „Hang bekapcsolása" gomb
  console.log('\n===== 3d. HANG ELŐRE ÉLESÍTVE (v10.459) =====');
  await p.setInputFiles('#__side [data-reveal-p-videoinput]', ROOT + '/tests/fixtures/tiny_reveal.webm');
  await p.waitForFunction(() => { const m = (window.__fbStore.config || {}).revealVideo; return m && m.vid && m.size < 1000000; }, null, { timeout: 15000 }).catch(() => {});
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-videoready="1"]'), null, { timeout: 8000 }).catch(() => {});
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-sound]'); return e && e.getAttribute('data-reveal-sound') === 'ok'; }, null, { timeout: 4000 }).catch(() => {});
  if ((await attr('[data-reveal-sound]', 'data-reveal-sound')) !== 'ok') { await p.mouse.click(20, 400); await p.waitForTimeout(400); }
  ok((await attr('[data-reveal-sound]', 'data-reveal-sound')) === 'ok', 'a bal alsó csip jelzi: 🔊 hang kész (videó + zene)', await p.textContent('[data-reveal-tally]'));
  ok(await p.evaluate(() => { const v = document.querySelector('video[data-reveal-video]'); return v && v.paused && v.style.display === 'none'; }), '…a próba után a videó áll és rejtve van (nem szivárog ki a vetítőre)');
  await p.evaluate(() => { window.__vs2 = null; window.__vs2Iv = setInterval(() => { const v = document.querySelector('video[data-reveal-video]'), e = document.querySelector('[data-reveal-show]');
    if (v && e && e.getAttribute('data-reveal-show') === 'video' && !v.paused && !window.__vs2) window.__vs2 = { muted: v.muted, shown: v.style.display, big: [...document.querySelectorAll('[data-reveal-unmute]')].map(b => b.getBoundingClientRect().height) }; }, 20); });
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealState').set({ phase: 'reveal', run: 'vid3', test: false, result: 'girl', videoUrl: '', at: Date.now() }));
  await p.waitForFunction(() => !!window.__vs2, null, { timeout: 8000 }).catch(() => {});
  const vs2 = await p.evaluate(() => { clearInterval(window.__vs2Iv); return window.__vs2; });
  ok(vs2 && vs2.muted === false && vs2.shown === 'block', 'a leleplezésnél a videó HANGGAL, interakció nélkül indul', JSON.stringify(vs2));
  ok(vs2 && vs2.big.every(h => h < 40), 'nincs nagy „Hang bekapcsolása" gomb a videó közepén', JSON.stringify(vs2));
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 8000 }).catch(() => {});
  // újratöltött vetítő (még senki nem kattintott): a „Vetítő indítása" kapu kéri az EGY kattintást
  await p.evaluate(() => { Object.defineProperty(navigator, 'userActivation', { configurable: true, get: () => ({ hasBeenActive: false, isActive: false }) }); });
  await p.evaluate(() => document.querySelector('[data-reveal-exit]').click()); await p.waitForTimeout(300);
  await p.evaluate(() => document.querySelector('[data-reveal-role="projector"]').click());
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-startgate]'), null, { timeout: 8000 }).catch(() => {});
  ok(await has('[data-reveal-startgate]'), 'kattintás nélküli vetítőn megjelenik a „Vetítő indítása" kapu');
  await p.click('[data-reveal-startgate]'); await p.waitForTimeout(500);
  ok(!(await has('[data-reveal-startgate]')) && (await attr('[data-reveal-sound]', 'data-reveal-sound')) === 'ok', '…egy kattintás után eltűnik, és a hang élesítve');
  await p.click('#__side [data-reveal-p-videodel]'); await p.waitForTimeout(100);
  await p.locator('button:text-is("Törlés")').last().click(); await p.waitForTimeout(400);
  const vgone = await p.evaluate(() => ({ vid: (window.__fbStore.config.revealVideo || {}).vid, ch: Object.keys(window.__fbStore.revealVideo || {}).length }));
  ok(!vgone.vid && vgone.ch === 0, 'törlés: a meta és a darabok is eltűnnek', JSON.stringify(vgone));
  ok(!(await has('[data-reveal-videoready]')), 'a vetítő is elengedi');
  await p.click('#__side [data-reveal-p-musicdel]'); await p.waitForTimeout(100);
  await p.locator('button:text-is("Törlés")').last().click(); await p.waitForTimeout(400);
  ok(await p.evaluate(() => !(window.__fbStore.config.revealAudio || {}).vid && Object.keys(window.__fbStore.revealAudio || {}).length === 0), 'v10.458: a zene törölhető (meta + darab)');
  ok(!(await has('[data-reveal-musicready]')) && !(await has('#__side [data-reveal-p-volrow]')), '…a vetítő elengedi, és média nélkül nincs hangerő-sor');
  fs.unlinkSync(wav);
  await p.evaluate(() => { const d = document.getElementById('__side'); if (d) { d.__r.unmount(); d.remove(); } });
  await p.evaluate(() => window.__rvSave());

  console.log('\n===== 5. KÉSŐBB NYITOTT VETÍTŐ =====');
  await go(); await p.evaluate(() => { window.__revealSpeed = 0.06; });
  await login(); await p.click('[data-reveal-role="projector"]'); await p.waitForTimeout(400);
  ok(!(await has('[data-reveal-show]')) && (await attr('[data-reveal-projector]', 'data-reveal-revealed')) === 'girl', '⚠️ animáció nélkül, rögtön a kiderült szín');

  console.log('\n===== 5b. IDŐZÍTETT LELEPLEZÉS: időpont + a szülő engedélye =====');
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealState').set({ phase: 'idle', run: 'reset1' }));
  await p.evaluate(t => firebase.firestore().collection('config').doc('revealConfig').set({ revealAt: t, countdownOn: true }, { merge: true }), Date.now() + 1500);
  await p.waitForTimeout(250);
  ok(!(await attr('[data-reveal-projector]', 'data-reveal-revealed')), 'visszaállítás után a vetítő elengedi a színt');
  ok(await has('[data-reveal-corner]') && /\d\d:\d\d/.test(await p.textContent('[data-reveal-corner-time]')), 'visszaszámláló a vetítőn', await p.textContent('[data-reveal-corner-time]'));
  const cr = await p.evaluate(() => { const r = document.querySelector('[data-reveal-corner]').getBoundingClientRect(); return { dx: Math.round(r.left + r.width / 2 - innerWidth / 2), top: r.top, bottom: r.bottom }; });
  ok(Math.abs(cr.dx) < 4 && cr.top >= 64 && cr.top < 110, 'v10.438: fent KÖZÉPEN ül, a gombsor ALATT', JSON.stringify(cr));
  await p.evaluate(px => firebase.firestore().collection('revealPhotos').doc('top1').set({ src: px, w: 4, h: 3, at: 50, hidden: false }), PX);
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-board]'), null, { timeout: 3000 }).catch(() => {});
  const bTop = await p.evaluate(() => { const b = document.querySelector('[data-reveal-board]'); return b ? b.getBoundingClientRect().top : null; });
  ok(bTop !== null && bTop >= cr.bottom, 'a polaroid-fal a visszaszámláló ALATT kezdődik (nem takarják egymást)', bTop + ' vs ' + Math.round(cr.bottom));
  await p.evaluate(() => { delete window.__fbStore.revealPhotos.top1; return firebase.firestore().collection('revealPhotos').doc('top1').delete(); });
  const ctlB = await p.evaluate(() => document.querySelector('[data-reveal-controls]').getBoundingClientRect().bottom);
  ok(cr.top >= ctlB - 4, 'a sarok-óra nem csúszik a látható gombsor alá', cr.top + ' vs ' + ctlB.toFixed(0));
  await p.waitForTimeout(2000);
  st = await store();
  ok(!(await has('[data-reveal-show]')) && st.c.revealState.phase === 'idle', '⚠️ engedély NÉLKÜL az időpont elmúlik, és nem indul semmi');
  ok((await p.textContent('[data-reveal-corner]')).includes('MINDJÁRT'), 'a sarok „mindjárt kiderül"-t ír');
  await p.evaluate(t => firebase.firestore().collection('config').doc('revealConfig').set({ revealAt: t }, { merge: true }), Date.now() + 4000);
  await mountSide('RevealTrigger');
  await p.waitForTimeout(200);
  await p.keyboard.type('2026'); await p.waitForTimeout(350);
  ok(await has('#__side [data-reveal-when]') && await has('[data-reveal-arm]'), 'a szülőnél: az időpont és az „Engedélyezem" gomb');
  await p.click('[data-reveal-arm]'); await p.waitForTimeout(100);
  await p.click('button:text-is("Engedélyezem")'); await p.waitForTimeout(200);
  st = await store();
  ok(st.c.revealState.phase === 'armed' && !st.c.revealState.result, 'engedélyezve — és az eredmény MÉG nincs a szobában', JSON.stringify(st.c.revealState));
  ok(!(await has('[data-reveal-show]')), 'az időpont előtt még nem indul');
  await p.waitForFunction(() => !!document.querySelector('[data-reveal-show]'), null, { timeout: 6000 }).catch(() => {});
  st = await store();
  ok(await has('[data-reveal-show]') && st.c.revealState.phase === 'reveal' && st.c.revealState.result === 'girl' && /-go$/.test(st.c.revealState.run), 'az időpontra MAGÁTÓL indul (a vetítő írja be az eredményt)', JSON.stringify(st.c.revealState));
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 6000 }).catch(() => {});
  ok((await attr('[data-reveal-projector]', 'data-reveal-revealed')) === 'girl' && !(await has('[data-reveal-corner]')), 'utána a kiderült szín, a sarok-óra eltűnik');
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealState').set({ phase: 'idle', run: 'reset2' }));
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealConfig').set({ revealAt: Date.now() + 60000, countdownOn: false }, { merge: true }));
  await p.waitForTimeout(250);
  ok(!(await has('[data-reveal-corner]')), 'kikapcsolva (admin) nincs sarok-óra');
  await p.evaluate(() => { const d = document.getElementById('__side'); if (d) { d.__r.unmount(); d.remove(); } });

  console.log('\n===== 6. VENDÉG: KÉP + ÜZENET JÓVÁHAGYÁSSAL =====');
  await p.evaluate(px => { const db = firebase.firestore(); ['a', 'b'].forEach((id, i) => db.collection('revealPhotos').doc(id).set({ src: px, w: 1, h: 1, at: i + 1, hidden: false, pending: false })); }, PX);
  await p.waitForTimeout(150);
  await p.evaluate(() => { window.__revealSpeed = 100; });   // a vetítő ne lépjen magától
  const cfgV = (await store()).c.revealConfig;
  await mountSide('RevealGuest', { cfg: cfgV });
  await p.waitForTimeout(200);
  ok(await has('#__side [data-reveal-guest="name"]'), 'a vendég előbb a nevét adja meg');
  await p.fill('#__side [data-reveal-guestname]', 'Zsófi'); await p.keyboard.press('Enter'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-guest="main"]'), 'utána a feltöltő oldal');
  await p.setInputFiles('#__side [data-reveal-guestinput]', ROOT + '/assets/dnr_reveal_app.png');
  await p.waitForFunction(() => Object.values(window.__fbStore.revealPhotos).some(x => x.by === 'Zsófi' && x.src), null, { timeout: 8000 }).catch(() => {});
  ok(!(await has('#__side [data-reveal-wishinput]')), 'v10.443: alapból a Kép fül nyílik');
  await p.click('#__side [data-reveal-guesttab="wish"]'); await p.waitForTimeout(120);
  await p.fill('#__side [data-reveal-wishinput]', 'Isten hozott, kicsi!'); await p.waitForTimeout(80);
  ok((await p.textContent('#__side [data-reveal-wishpreview] [data-reveal-wishtext]')) === 'Isten hozott, kicsi!' && (await p.textContent('#__side [data-reveal-wishpreview]')).includes('— Zsófi'),
    'élő polaroid-előnézet: a szöveg és a név a lapon');
  await p.click('#__side [data-reveal-wishsend]'); await p.waitForTimeout(200);
  st = await store();
  const gPhoto = Object.entries(st.ph).find(([, v]) => v.by === 'Zsófi' && v.src), gWish = Object.entries(st.ph).find(([, v]) => v.kind === 'wish');
  ok(gPhoto && gPhoto[1].pending === true, 'a vendég képe jóváhagyásra vár (pending, a nevével)');
  ok(gWish && gWish[1].pending === true && gWish[1].text === 'Isten hozott, kicsi!' && gWish[1].by === 'Zsófi', 'az üzenet is jóváhagyásra vár');
  ok((await p.textContent('[data-reveal-count]')).trim() === '2 kép', '⚠️ a vetítő a jóváhagyás előtt NEM mutatja', await p.textContent('[data-reveal-count]'));
  ok((await p.evaluate(() => document.querySelectorAll('#__side [data-reveal-mineitem][data-pending="1"]').length)) === 2, 'a vendég „Beküldéseid" listáján mindkettő: jóváhagyásra vár');
  await mountSide('RevealOperator');
  await p.waitForTimeout(250);
  ok(!(await has('#__side [data-reveal-pend]')) && (await p.textContent('#__side [data-reveal-pendbtn]')).includes('2'), 'v10.446: a várakozók egy gomb mögött (a gombon a darabszám)');
  await p.click('#__side [data-reveal-pendbtn]'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-review]') && (await p.textContent('#__side [data-reveal-reviewpos]')).trim() === '1 / 2', 'megnyitva teljes képernyős lapozó: 1 / 2');
  ok(await has(`#__side [data-reveal-pend="${gPhoto[0]}"] img`) && await has(`#__side [data-reveal-pend="${gWish[0]}"] [data-reveal-wishpreview]`), 'a kép nagyban, az üzenet polaroidként');
  await p.click('#__side [data-reveal-reviewdot="1"]'); await p.waitForTimeout(500);
  ok((await p.textContent('#__side [data-reveal-reviewpos]')).trim() === '2 / 2', 'léptethető (2 / 2)');
  await decide(gWish[0], 'approve');
  await p.evaluate(() => revealCtlWrite({ next: revealToken() })); await p.waitForTimeout(200);   // a Szülők „Következő ›"-je
  ok((await attr('[data-reveal-projector]', 'data-reveal-current')) === gWish[0] && (await attr('[data-reveal-projector]', 'data-reveal-isnew')) === '1', 'jóváhagyás után az üzenet rögtön jön, ÚJ jelöléssel');
  ok(await has(`[data-reveal-wish="${gWish[0]}"]`) && (await p.textContent(`[data-reveal-wish="${gWish[0]}"]`)).includes('Zsófi'), 'jókívánság-kártya a küldő nevével');
  ok(await has(`[data-reveal-wish="${gWish[0]}"] [data-reveal-wishface]`) && (await p.textContent(`[data-reveal-wish="${gWish[0]}"] [data-reveal-wishtext]`)) === 'Isten hozott, kicsi!', 'v10.443: a vetítőn UGYANAZ az üzenet-arc, mint az előnézetben');
  await decide(gPhoto[0], 'approve');
  ok(!(await has('#__side [data-reveal-review]')) && !(await has('#__side [data-reveal-pendbtn]')), 'az utolsó döntés után a felület bezárul, a gomb eltűnik');
  ok((await p.textContent('[data-reveal-count]')).trim() === '3 kép', 'a jóváhagyott kép bekerül a vetítőre');
  await p.evaluate(() => { window.__fbStore.revealPhotos.junk = { src: 'data:image/png;base64,AAAA', pending: true, by: 'X', at: 99 }; return firebase.firestore().collection('revealPhotos').doc('junk2').set({ kind: 'wish', text: 'rossz', by: 'Y', pending: true, at: 100 }); });
  await p.waitForTimeout(150);
  ok(!(await has('#__side [data-reveal-review]')), 'új beküldés NEM nyitja fel magától a felületet');
  await p.click('#__side [data-reveal-pendbtn]'); await p.waitForTimeout(150);
  await decide('junk2', 'reject');
  ok(await p.evaluate(() => !window.__fbStore.revealPhotos.junk2), '„Eldob" → törlődik');
  await p.evaluate(() => { delete window.__fbStore.revealPhotos.junk; });

  console.log('\n===== 6b. VENDÉGENKÉNT 1 KÉP + 1 ÜZENET · VETÍTŐ-SAROKJELVÉNY · SZÜLŐI JÓVÁHAGYÁS (v10.449) =====');
  await mountSide('RevealGuest', { cfg: cfgV });
  await p.waitForTimeout(250);
  ok(await has('#__side [data-reveal-guestdone="photo"]') && !(await has('#__side [data-reveal-guestpick]')), 'a képét már elküldte: a Kép fülön a saját képe, nincs feltöltő gomb');
  ok(!(await p.evaluate(() => document.querySelector('#__side [data-reveal-guestinput]').multiple)), 'a vendég fájl-mezője egyetlen képet fogad');
  const zsofiN = () => p.evaluate(() => Object.values(window.__fbStore.revealPhotos).filter(x => x.by === 'Zsófi').length);
  const n0 = await zsofiN();
  await p.setInputFiles('#__side [data-reveal-guestinput]', ROOT + '/assets/dnr_reveal_app.png'); await p.waitForTimeout(600);
  ok((await zsofiN()) === n0, 'a rejtett mezőn át sem küldhet második képet', n0 + ' → ' + (await zsofiN()));
  await p.click('#__side [data-reveal-guesttab="wish"]'); await p.waitForTimeout(100);
  ok(await has('#__side [data-reveal-guestdone="wish"]') && !(await has('#__side [data-reveal-wishinput]')), 'az üzenetét is elküldte: nincs második üzenet');
  await p.click('#__side button:text-is("Nem te vagy?")'); await p.waitForTimeout(80);
  await p.fill('#__side [data-reveal-guestname]', 'Álnév'); await p.keyboard.press('Enter'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-guestdone]'), '⚠️ névcserével sem nyílik új keret (eszközönkénti azonosító)');
  const wishId = gWish[0];
  await p.evaluate(id => firebase.firestore().collection('revealPhotos').doc(id).delete(), wishId); await p.waitForTimeout(200);
  await p.click('#__side [data-reveal-guesttab="wish"]'); await p.waitForTimeout(100);
  ok(await has('#__side [data-reveal-wishinput]'), 'ha az üzenetét eldobták (törlődött), újra írhat');
  // v10.452: a vetítő szervezői csipje — bal ALUL, kicsiben (képszám + várakozók)
  ok(!(await has('[data-reveal-pendbadge]')), 'nincs várakozó → nincs „vár" jelzés');
  await p.evaluate(px => firebase.firestore().collection('revealPhotos').doc('pz1').set({ src: px, w: 1, h: 1, at: 200, by: 'Vendég', pending: true }), PX);
  await p.evaluate(() => firebase.firestore().collection('revealPhotos').doc('pz2').set({ kind: 'wish', text: 'Szia!', by: 'Vendég2', at: 201, pending: true }));
  await p.waitForTimeout(200);
  const corners = await p.evaluate(() => { const b = document.querySelector('[data-reveal-pendbadge]'), t = document.querySelector('[data-reveal-tally]'), bd = document.querySelector('[data-reveal-board]');
    const rt = t.getBoundingClientRect(), rd = bd && bd.getBoundingClientRect();
    return { n: b && b.getAttribute('data-reveal-pendbadge'), inTally: !!(b && t.contains(b)), left: Math.round(rt.left), bottomGap: Math.round(innerHeight - rt.bottom), h: Math.round(rt.height),
      fs: parseFloat(getComputedStyle(t).fontSize), boardBottom: rd && Math.round(rd.bottom), tTop: Math.round(rt.top), vw: innerWidth, vh: innerHeight,
      topEls: document.querySelectorAll('[data-reveal-topm]').length }; });
  ok(corners.n === '2' && corners.inTally, 'a várakozók száma (2) a bal alsó csipben', JSON.stringify(corners));
  ok(corners.left < corners.vw * 0.03 && corners.bottomGap < corners.vh * 0.03 && (await p.textContent('[data-reveal-count]')).trim() === '3 kép', 'bal ALUL a képek száma', JSON.stringify(corners));
  ok(corners.h <= 28 && corners.fs <= 14, 'kicsi és halk (≤ 28 px magas, ≤ 14 px betű) — csak a szervezőknek', JSON.stringify(corners));
  ok(corners.boardBottom <= corners.tTop && corners.topEls === 0, 'a polaroid-fal a csip FÖLÖTT végződik; felül nincs sarok-elem', JSON.stringify(corners));
  // szülői jóváhagyás
  await mountSide('RevealTrigger');
  await p.waitForTimeout(200);
  await p.keyboard.type('2026'); await p.waitForTimeout(350);
  ok(await has('#__side [data-reveal-ppendbtn]') && (await p.textContent('#__side [data-reveal-ppendcount]')).trim() === '2', 'a Szülők állapot-sorában: Jóváhagyás (2)');
  await p.evaluate(() => document.querySelector('#__side [data-reveal-ppendbtn]').click()); await p.waitForTimeout(200);
  ok(await has('#__side [data-reveal-review]') && !(await has('[data-reveal-pdock]')), 'megnyílik a közös lapozó, és a dokk eltűnik alatta');
  await decide('pz1', 'approve');
  await decide('pz2', 'reject');
  st = await store();
  ok(st.ph.pz1 && st.ph.pz1.pending === false && !st.ph.pz2, 'a Szülők jóváhagyták a képet, eldobták az üzenetet');
  ok(!(await has('#__side [data-reveal-review]')) && await has('[data-reveal-pdock]') && !(await has('#__side [data-reveal-ppendbtn]')), 'utána bezárul, a dokk visszajön, a gomb eltűnik');
  ok(!(await has('[data-reveal-pendbadge]')) && (await p.textContent('[data-reveal-count]')).trim() === '4 kép', 'a vetítőn: nincs „vár" jelzés, 4 kép');
  // a későbbi blokkok (album) az eredeti állapotra épülnek: az üzenet vissza, a plusz kép ki
  await p.evaluate(({ id, v }) => { const db = firebase.firestore(); db.collection('revealPhotos').doc('pz1').delete(); return db.collection('revealPhotos').doc(id).set(Object.assign({}, v, { pending: false })); }, { id: gWish[0], v: gWish[1] });
  await p.waitForTimeout(150);
  await p.evaluate(() => { const d = document.getElementById('__side'); if (d) { d.__r.unmount(); d.remove(); } });

  console.log('\n===== 7. BABAKVÍZ (papíron, csak lapozás) =====');
  const key = await p.evaluate(() => REVEAL_QUIZ_DEFAULT.map(q => 'ABC'[q.ok]).join(''));
  ok(await p.evaluate(() => REVEAL_QUIZ_DEFAULT.length === 20 && REVEAL_QUIZ_DEFAULT.every(q => q.opts.length === 3)), 'a PDF 20 kérdése, mind A/B/C');
  ok(key === 'BBABCABBAACBBCAABBAA', 'a megoldókulcs egyezik a játékmesteri lappal', key);
  await p.evaluate(() => firebase.firestore().collection('config').doc('revealQuiz').set({ questions: [
    { q: 'Első kérdés?', opts: ['A1', 'B1', 'C1'], ok: 1 }, { q: 'Második?', opts: ['A2', 'B2', 'C2'], ok: 0 } ] }));
  await p.waitForTimeout(150);
  const qz = () => attr('[data-reveal-quiz]', 'data-reveal-quiz'), qi = () => attr('[data-reveal-quiz]', 'data-reveal-quiz-idx');
  ok(!(await has('[data-reveal-quizbtn]')), 'v10.435: a vetítőről NEM indítható a Babakvíz (nincs gomb)');
  await mountSide('RevealOperator');
  await p.waitForTimeout(250);
  ok(!(await has('#__side [data-reveal-quizctl]')), 'v10.434: az operátornál NINCS kvíz-vezérlő');
  await mountSide('RevealTrigger');
  await p.waitForTimeout(200);
  ok(!(await has('#__side [data-reveal-quizctl]')), 'a Szülők kvíz-vezérlője is a kód mögött van');
  await p.keyboard.type('2026'); await p.waitForTimeout(350);
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="quiz"]').click()); await p.waitForTimeout(100);
  ok(await has('#__side [data-reveal-parentquiz] [data-reveal-quizctl]'), 'a kóddal a Szülők Kvíz fülén ott a Babakvíz-lapozó');
  // v10.438: a vetítő MINDEN beállítása a Szülőknél (v10.444: a Vetítő fülön)
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="proj"]').click()); await p.waitForTimeout(100);
  const pc = await p.evaluate(() => ({ secs: [...document.querySelectorAll('#__side [data-reveal-ctl-secs]')].map(b => b.getAttribute('data-reveal-ctl-secs')).join(','),
    slots: [...document.querySelectorAll('#__side [data-reveal-ctl-slots]')].map(b => b.getAttribute('data-reveal-ctl-slots')).join(','),
    pause: !!document.querySelector('#__side [data-reveal-ctl-pause]'), next: !!document.querySelector('#__side [data-reveal-ctl-next]'), qr: document.querySelectorAll('#__side [data-reveal-ctl-qr]').length }));
  ok(pc.secs === '3,5,8' && pc.slots === '1,2,3' && pc.pause && pc.next && pc.qr === 1, 'a Szülőknél: idő, polaroidok, szünet, következő, QR-kapcsoló', JSON.stringify(pc));
  await p.click('#__side [data-reveal-ctl-slots="2"]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => (window.__fbStore.config.revealProjector || {}).slots === 2), 'a Szülők a közös dokumentumba írnak (2 lap)');
  await p.click('#__side [data-reveal-ctl-qr]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => (window.__fbStore.config.revealProjector || {}).qr === false) && (await attr('#__side [data-reveal-ctl-qr]', 'aria-checked')) === 'false', 'a QR is innen kapcsolható');
  await p.click('#__side [data-reveal-ctl-qr]'); await p.waitForTimeout(100);
  await p.evaluate(() => document.querySelector('[data-reveal-ptab="quiz"]').click()); await p.waitForTimeout(100);
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(250);
  ok((await qz()) === 'cover' && (await p.textContent('[data-reveal-quiz-covertitle]')) === 'Babakvíz' && !(await has('[data-reveal-quiz-q]')), 'v10.442: az első oldal a BORÍTÓ, nem a kérdés');
  ok((await p.textContent('#__side [data-reveal-quiz-next]')).includes('Első kérdés'), 'a borító után „Első kérdés ›"');
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(200);
  ok((await qz()) === 'q' && (await p.textContent('[data-reveal-quiz]')).includes('Első kérdés?'), 'utána a vetítőn az 1. kérdés');
  ok(!(await has('[data-reveal-quiz] [data-reveal-qr]')), 'a kvízben nincs QR-kód (papíron szavaznak)');
  ok((await p.evaluate(() => document.querySelectorAll('[data-reveal-quiz-opt][data-correct="1"]').length)) === 0, 'kérdezéskor NINCS kiemelve a helyes válasz');
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(150);
  ok((await qz()) === 'q' && (await qi()) === '1', 'a Szülők lapoznak: 2. kérdés');
  await mountSide('RevealGuest', { cfg: cfgV });
  await p.waitForTimeout(200);
  ok(!(await has('#__side [data-reveal-guestquiz]')) && !(await has('#__side [data-reveal-guestopt]')), 'a vendég telefonján nincs kvíz-válasz');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(150);
  ok((await qz()) === 'solcover' && (await p.textContent('[data-reveal-quiz-covertitle]')) === 'Megoldások' && !(await has('[data-reveal-quiz-opt]')), 'v10.442: a megoldások előtt is BORÍTÓ jön');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(150);
  ok((await qz()) === 'sol' && (await qi()) === '0', 'a borító után a megoldások (1. kérdés újra)');
  ok((await attr('[data-reveal-quiz-opt="1"]', 'data-correct')) === '1' && (await p.textContent('[data-reveal-quiz]')).includes('Megoldások'), 'a megoldásnál a helyes válasz kiemelve');
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(120);
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(150);
  ok((await qz()) === 'q' && (await qi()) === '1', '‹ visszalép a borítón át az utolsó kérdésre');
  await mountSide('RevealQuizControl'); await p.waitForTimeout(150);   // a Szülők lapozója (a kód mögötti rész)
  ok(await has('#__side [data-reveal-quiz-jumps]'), 'v10.444: az ugró-rács mindig kint van');
  const jlist = () => p.evaluate(() => [...document.querySelectorAll('#__side [data-reveal-quiz-jump]')].map(b => b.getAttribute('data-reveal-quiz-jump') + ':' + b.textContent).join(','));
  const jl = await jlist();
  ok(jl === '0:Borító,1:1,2:2,6:Pontozás', 'Kérdések rész: borító + kérdések + pontozás', jl);
  ok((await attr('#__side [data-reveal-quiz-jump="2"]', 'aria-pressed')) === 'true', 'a rács jelöli, hol tartunk (2. kérdés)');
  await p.click('#__side [data-reveal-quiz-sec="sol"]'); await p.waitForTimeout(100);
  ok((await jlist()) === '3:Borító,4:1,5:2,6:Pontozás', 'Megoldások rész: borító + megoldások + pontozás', await jlist());
  await p.click('#__side [data-reveal-quiz-jump="5"]'); await p.waitForTimeout(150);
  ok((await qz()) === 'sol' && (await qi()) === '1' && (await attr('[data-reveal-quiz-opt="0"]', 'data-correct')) === '1', 'ugrás: rögtön a 2. megoldás (A)');
  ok((await p.textContent('#__side [data-reveal-quiz-next]')).includes('Pontozás'), 'az utolsó megoldás után „Pontozás ›"');
  ok(!(await has('[data-reveal-quiznav]')), 'v10.438: a vetítőn nincs kvíz-lapozó gombsor');
  await p.click('#__side [data-reveal-quiz-sec="q"]'); await p.waitForTimeout(80);
  await p.click('#__side [data-reveal-quiz-jump="0"]'); await p.waitForTimeout(150);
  ok((await qz()) === 'cover' && await p.evaluate(() => document.querySelector('#__side [data-reveal-quiz-prev]').disabled), 'ugrás vissza a borítóra (ott az „‹ Előző" tiltott)');
  await p.click('#__side [data-reveal-quiz-jump="6"]'); await p.waitForTimeout(200);
  ok((await qz()) === 'end' && (await p.evaluate(() => document.querySelectorAll('[data-reveal-quiz-band]').length)) === 4, 'ugrás a pontozásra: a négy pontsáv a lapról');
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(200);
  ok(!(await has('[data-reveal-quiz]')) && await has('[data-reveal-board]'), 'kvíz vége → vissza a polaroid-fal');
  await p.click('#__side [data-reveal-quiz-sec="sol"]'); await p.waitForTimeout(80);
  await p.click('#__side [data-reveal-quiz-jump="3"]'); await p.waitForTimeout(200);
  const qst = await p.evaluate(() => window.__fbStore.config.revealQuizState);
  ok((await qz()) === 'solcover' && qst.run && qst.qs && qst.qs.length === 2, 'nem futó kvíznél az ugrás el is indítja (rögtön a megoldásokhoz)', JSON.stringify({ ph: qst.phase, n: (qst.qs || []).length }));
  await p.click('#__side [data-reveal-quiz-end]'); await p.waitForTimeout(200);
  ok(!(await has('[data-reveal-quiz]')), 'megszakítva vissza a képfolyam');

  console.log('\n===== 8. ALBUM =====');
  const zipB64 = await p.evaluate(async () => {
    const items = Object.entries(window.__fbStore.revealPhotos).map(([id, v]) => Object.assign({ id }, v));
    items.push({ id: 'h', src: items.find(x => x.src).src, hidden: true });
    const r = revealBuildAlbum(items); const buf = new Uint8Array(await r.blob.arrayBuffer());
    let s = ''; for (let i = 0; i < buf.length; i++) s += String.fromCharCode(buf[i]); return btoa(s);
  });
  const zp = '/tmp/claude-0/-home-user-bottle-of-heroes/41faa226-19f7-5bf9-9bc4-4d933d77bf20/scratchpad/album_test.zip';
  fs.writeFileSync(zp, Buffer.from(zipB64, 'base64'));
  const py = cp.execFileSync('python3', ['-I', '-c', 'import zipfile,sys;z=zipfile.ZipFile(sys.argv[1]);print(z.testzip());print("|".join(z.namelist()));print(z.read("jokivansagok.txt").decode())', zp]).toString().split('\n');
  ok(py[0] === 'None', 'a ZIP ép (Python zipfile.testzip)', py[0]);
  const names = py[1].split('|');
  ok(names.filter(n => /^kep_\d{3}/.test(n)).length === 3 && names.includes('jokivansagok.txt'), '3 kép (a rejtett nem) + jokivansagok.txt', py[1]);
  ok(names.some(n => /Zsofi/.test(n)), 'a fájlnévben a feltöltő neve (ékezet nélkül)');
  ok(py.slice(2).join('\n').includes('Zsófi: Isten hozott, kicsi!'), 'a jókívánságok a szövegfájlban');
  await p.evaluate(() => window.__rvSave());
  await go('&album=' + cfgV.albumKey);
  ok(await has('[data-reveal-album]') && !(await has('[data-reveal-gate]')), 'galéria-link: jelszó nélkül nyílik');
  ok((await p.evaluate(() => document.querySelectorAll('[data-reveal-albumthumb]').length)) === 3, 'a galériában a 3 jóváhagyott kép');
  await p.click('[data-reveal-albumthumb]'); await p.waitForTimeout(150);
  ok(await has('[data-reveal-lightbox]'), 'koppintásra nagyban nyílik');
  ok(await has('[data-reveal-albumzip]'), 'van „Összes letöltése (ZIP)"');
  await go('&g=' + cfgV.guestKey);
  ok(await has('[data-reveal-guest]') && !(await has('[data-reveal-gate]')), 'vendég-link: jelszó nélkül nyílik');
  await go('&g=rossz');
  ok(await has('[data-reveal-badlink]'), 'rossz kulccsal: „Ez a link már nem érvényes"');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMIND ZÖLD');
  process.exit(fail ? 1 : 0);
})();
