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
  const login = async () => { await p.fill('[data-reveal-pw]', 'baba'); await p.keyboard.press('Enter'); await p.waitForTimeout(200); };

  // ── alapállapot: jelszó, címek, kulcsok az admin mentésével ──
  await go();
  await p.evaluate(() => { window.__revealSpeed = 0.06; });
  await p.evaluate(() => {
    const d = document.createElement('div'); d.id = '__adm'; d.style.cssText = 'position:fixed;inset:0;z-index:9000;background:#fff;overflow:auto';
    document.body.appendChild(d); d.__r = ReactDOM.createRoot(d); d.__r.render(React.createElement(AdminReveal));
  });
  await p.waitForTimeout(300);

  console.log('\n===== 1. ADMIN: TITKOS EREDMÉNY =====');
  await p.fill('[data-admin-reveal-pw]', 'baba'); await p.fill('[data-admin-reveal-title]', 'Anna & Bence babája');
  await p.click('[data-admin-reveal-save]'); await p.waitForTimeout(200);
  let st = await store();
  ok(st.c.revealConfig.guestKey && st.c.revealConfig.albumKey && st.c.revealConfig.guestKey !== st.c.revealConfig.albumKey, 'mentéskor vendég- és album-kulcs keletkezik', JSON.stringify(st.c.revealConfig));
  ok(await has('[data-admin-reveal-guesturl]') && await has('[data-admin-reveal-albumurl]'), 'a két link kint van az adminban');
  await p.click('[data-admin-reveal-result="girl"]');
  await p.fill('[data-admin-reveal-code]', '2026');
  await p.fill('[data-admin-reveal-when]', '2030-06-01T18:30');
  await p.click('[data-admin-reveal-countdown]');   // alapból BE → KI
  await p.click('[data-admin-reveal-secretsave]'); await p.waitForTimeout(200);
  st = await store();
  ok(st.c.revealSecret && st.c.revealSecret.result === 'girl' && st.c.revealSecret.code === '2026', 'az eredmény és a kód a TITKOS dokumentumba megy', JSON.stringify(st.c.revealSecret));
  ok(!st.c.revealState, '⚠️ a leleplezésig a revealState-ben nincs eredmény');
  ok(st.c.revealConfig.revealAt === new Date(2030, 5, 1, 18, 30).getTime() && st.c.revealConfig.countdownOn === false, 'az időpont (helyi idő) és a sarok-kapcsoló a revealConfig-ba megy', JSON.stringify([st.c.revealConfig.revealAt, st.c.revealConfig.countdownOn]));
  ok(!st.c.revealSecret.revealAt, 'az időpont nem a titkos dokumentumba kerül');
  await p.evaluate(() => { const d = document.getElementById('__adm'); d.__r.unmount(); d.remove(); });
  await p.evaluate(() => { const d = document.createElement('div'); d.id = '__adm'; d.style.cssText = 'position:fixed;inset:0;z-index:9000;background:#fff;overflow:auto'; document.body.appendChild(d); d.__r = ReactDOM.createRoot(d); d.__r.render(React.createElement(AdminReveal)); });
  await p.waitForTimeout(300);
  ok(await has('[data-admin-reveal-masked]') && !(await has('[data-admin-reveal-result="girl"]')), 'újranyitva az eredmény maszkolva („●●● beállítva")');
  await p.click('[data-admin-reveal-peek]'); await p.waitForTimeout(80);
  ok(await has('[data-admin-reveal-result="girl"]'), '👁 Mutat → látszik');
  await p.evaluate(() => { const d = document.getElementById('__adm'); d.__r.unmount(); d.remove(); });
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
  await p.fill('#__side [data-reveal-code]', 'baba'); await p.keyboard.press('Enter'); await p.waitForTimeout(100);
  ok(await has('#__side [data-reveal-codebad]') && !(await has('#__side [data-reveal-fire]')), 'a közös jelszó NEM jó leleplező kódnak');
  await p.fill('#__side [data-reveal-code]', '2026'); await p.keyboard.press('Enter'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-fire]'), 'a jó kóddal ott a LELEPLEZÉS gomb');
  ok(!/lány|fiú/i.test(await p.textContent('#__side [data-reveal-firepanel]')), 'a leleplező sem látja az eredményt');

  console.log('\n===== 4. PRÓBA-LELEPLEZÉS =====');
  await p.click('#__side [data-reveal-test]'); await p.waitForTimeout(150);
  ok((await attr('[data-reveal-show]', 'data-reveal-show')) === 'count', 'próba: a vetítőn indul a visszaszámlálás');
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') === 'boom'; }, null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-show]', 'data-reveal-boom')) === 'test' && (await p.textContent('[data-reveal-word]')).includes('PRÓBA'), 'próba: „PRÓBA" robbanás, nem az eredmény');
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 4000 }).catch(() => {});
  ok(!(await has('[data-reveal-show]')) && !(await attr('[data-reveal-projector]', 'data-reveal-revealed')), 'próba után a vetítő NEM színeződik');

  console.log('\n===== 3. A NAGY LELEPLEZÉS =====');
  await p.click('#__side [data-reveal-fire]'); await p.waitForTimeout(100);
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
  ok(await has('[data-reveal-show="count"] video[data-reveal-video][preload="auto"]'), 'a videó már a visszaszámlálás alatt betöltődik (rejtve)');
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') !== 'count'; }, null, { timeout: 4000 }).catch(() => {});
  const vs = await attr('[data-reveal-show]', 'data-reveal-show');
  ok(vs === 'video' || vs === 'boom', 'a visszaszámlálás után a videó-szakasz jön', vs);
  await p.waitForFunction(() => { const e = document.querySelector('[data-reveal-show]'); return e && e.getAttribute('data-reveal-show') === 'boom'; }, null, { timeout: 4000 }).catch(() => {});
  ok((await attr('[data-reveal-show]', 'data-reveal-boom')) === 'girl', 'betölthetetlen videónál is a robbanás jön');
  await p.waitForFunction(() => !document.querySelector('[data-reveal-show]'), null, { timeout: 4000 }).catch(() => {});
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
  await p.fill('#__side [data-reveal-code]', '2026'); await p.keyboard.press('Enter'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-when]') && await has('#__side [data-reveal-arm]'), 'a szülőnél: az időpont és az „Engedélyezem" gomb');
  await p.click('#__side [data-reveal-arm]'); await p.waitForTimeout(100);
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
  await p.fill('#__side [data-reveal-wishinput]', 'Isten hozott, kicsi!'); await p.click('#__side [data-reveal-wishsend]'); await p.waitForTimeout(200);
  st = await store();
  const gPhoto = Object.entries(st.ph).find(([, v]) => v.by === 'Zsófi' && v.src), gWish = Object.entries(st.ph).find(([, v]) => v.kind === 'wish');
  ok(gPhoto && gPhoto[1].pending === true, 'a vendég képe jóváhagyásra vár (pending, a nevével)');
  ok(gWish && gWish[1].pending === true && gWish[1].text === 'Isten hozott, kicsi!' && gWish[1].by === 'Zsófi', 'az üzenet is jóváhagyásra vár');
  ok((await p.textContent('[data-reveal-count]')).trim() === '2 kép', '⚠️ a vetítő a jóváhagyás előtt NEM mutatja', await p.textContent('[data-reveal-count]'));
  await mountSide('RevealOperator');
  await p.waitForTimeout(250);
  ok(await has(`#__side [data-reveal-pend="${gPhoto[0]}"]`) && await has(`#__side [data-reveal-pend="${gWish[0]}"]`), 'az operátornál a „Jóváhagyásra vár" sorban');
  await p.click(`#__side [data-reveal-pend="${gWish[0]}"] [data-reveal-approve]`); await p.waitForTimeout(150);
  await p.evaluate(() => revealCtlWrite({ next: revealToken() })); await p.waitForTimeout(200);   // a Szülők „Következő ›"-je
  ok((await attr('[data-reveal-projector]', 'data-reveal-current')) === gWish[0] && (await attr('[data-reveal-projector]', 'data-reveal-isnew')) === '1', 'jóváhagyás után az üzenet rögtön jön, ÚJ jelöléssel');
  ok(await has(`[data-reveal-wish="${gWish[0]}"]`) && (await p.textContent(`[data-reveal-wish="${gWish[0]}"]`)).includes('Zsófi'), 'jókívánság-kártya a küldő nevével');
  await p.click(`#__side [data-reveal-pend="${gPhoto[0]}"] [data-reveal-approve]`); await p.waitForTimeout(150);
  ok((await p.textContent('[data-reveal-count]')).trim() === '3 kép', 'a jóváhagyott kép bekerül a vetítőre');
  await p.evaluate(() => { window.__fbStore.revealPhotos.junk = { src: 'data:image/png;base64,AAAA', pending: true, by: 'X', at: 99 }; return firebase.firestore().collection('revealPhotos').doc('junk2').set({ kind: 'wish', text: 'rossz', by: 'Y', pending: true, at: 100 }); });
  await p.waitForTimeout(150);
  await p.click('#__side [data-reveal-pend="junk2"] [data-reveal-reject]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => !window.__fbStore.revealPhotos.junk2), '„Eldob" → törlődik');
  await p.evaluate(() => { delete window.__fbStore.revealPhotos.junk; });

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
  await p.fill('#__side [data-reveal-code]', '2026'); await p.keyboard.press('Enter'); await p.waitForTimeout(200);
  ok(await has('#__side [data-reveal-parentquiz] [data-reveal-quizctl]'), 'a kóddal a Szülők nézetben ott a Babakvíz-lapozó');
  // v10.438: a vetítő MINDEN beállítása a Szülőknél
  const pc = await p.evaluate(() => ({ secs: [...document.querySelectorAll('#__side [data-reveal-ctl-secs]')].map(b => b.getAttribute('data-reveal-ctl-secs')).join(','),
    slots: [...document.querySelectorAll('#__side [data-reveal-ctl-slots]')].map(b => b.getAttribute('data-reveal-ctl-slots')).join(','),
    pause: !!document.querySelector('#__side [data-reveal-ctl-pause]'), next: !!document.querySelector('#__side [data-reveal-ctl-next]'), qr: document.querySelectorAll('#__side [data-reveal-ctl-qr]').length }));
  ok(pc.secs === '3,5,8' && pc.slots === '1,2,3' && pc.pause && pc.next && pc.qr === 2, 'a Szülőknél: idő, polaroidok, szünet, következő, QR', JSON.stringify(pc));
  await p.click('#__side [data-reveal-ctl-slots="2"]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => (window.__fbStore.config.revealProjector || {}).slots === 2), 'a Szülők a közös dokumentumba írnak (2 lap)');
  await p.click('#__side [data-reveal-ctl-qr="0"]'); await p.waitForTimeout(150);
  ok(await p.evaluate(() => (window.__fbStore.config.revealProjector || {}).qr === false), 'a QR is innen kapcsolható');
  await p.click('#__side [data-reveal-ctl-qr="1"]'); await p.waitForTimeout(100);
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(250);
  ok((await qz()) === 'q' && (await p.textContent('[data-reveal-quiz]')).includes('Első kérdés?'), 'a Szülők indítják: a vetítőn az 1. kérdés');
  ok(!(await has('[data-reveal-quiz] [data-reveal-qr]')), 'a kvízben nincs QR-kód (papíron szavaznak)');
  ok((await p.evaluate(() => document.querySelectorAll('[data-reveal-quiz-opt][data-correct="1"]').length)) === 0, 'kérdezéskor NINCS kiemelve a helyes válasz');
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(150);
  ok((await qz()) === 'q' && (await qi()) === '1', 'a Szülők lapoznak: 2. kérdés');
  await mountSide('RevealGuest', { cfg: cfgV });
  await p.waitForTimeout(200);
  ok(!(await has('#__side [data-reveal-guestquiz]')) && !(await has('#__side [data-reveal-guestopt]')), 'a vendég telefonján nincs kvíz-válasz');
  await p.keyboard.press('ArrowRight'); await p.waitForTimeout(150);
  ok((await qz()) === 'sol' && (await qi()) === '0', 'a kérdések után a megoldások jönnek (1. kérdés újra)');
  ok((await attr('[data-reveal-quiz-opt="1"]', 'data-correct')) === '1' && (await p.textContent('[data-reveal-quiz]')).includes('Megoldások'), 'a megoldásnál a helyes válasz kiemelve');
  await p.keyboard.press('ArrowLeft'); await p.waitForTimeout(150);
  ok((await qz()) === 'q' && (await qi()) === '1', '‹ visszalép az utolsó kérdésre');
  await mountSide('RevealQuizControl'); await p.waitForTimeout(150);   // a Szülők lapozója (a kód mögötti rész)
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(120);
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(120);
  ok((await qz()) === 'sol' && (await qi()) === '1' && (await attr('[data-reveal-quiz-opt="0"]', 'data-correct')) === '1', '2. megoldás: A');
  ok((await p.textContent('#__side [data-reveal-quiz-next]')).includes('Pontozás'), 'az utolsó megoldás után „Pontozás ›"');
  ok(!(await has('[data-reveal-quiznav]')), 'v10.438: a vetítőn nincs kvíz-lapozó gombsor');
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(200);
  ok((await qz()) === 'end' && (await p.evaluate(() => document.querySelectorAll('[data-reveal-quiz-band]').length)) === 4, 'pontozás: a négy pontsáv a lapról');
  await p.click('#__side [data-reveal-quiz-next]'); await p.waitForTimeout(200);
  ok(!(await has('[data-reveal-quiz]')) && await has('[data-reveal-board]'), 'kvíz vége → vissza a polaroid-fal');

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
