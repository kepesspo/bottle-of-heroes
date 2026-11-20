// v10.436 — Gender Reveal: tippek a kép alatt (személy / pár) + számláló a vetítőn.
//
// Fogódzók:
//  1) a számolás (`revealVoteTally`): személy 1 tipp, pár 2; rejtett, jóváhagyásra váró
//     és üzenet NEM számít; ⚠️ személyre visszaváltva a bennmaradt 2. tipp sem
//  2) operátor: a kép ALATT a választó; személy → 1 sor, pár → 2 sor; a koppintás a
//     store-ba ír, ugyanarra koppintva törlődik
//  3) vetítő: a számláló élőben követi (tipp, törlés, elrejtés, pár → személy);
//     tipp nélkül nincs számláló; kvíz alatt sincs; a polaroidon látszik a tipp
//  4) a leleplezés után a nyertes oldal kiemelve
//  5) távirányító és operátor is kiírja az állást
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
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
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_reveal_slots','3');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html?screen=reveal', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2600);
  const has = sel => p.evaluate(s => !!document.querySelector(s), sel);
  const attr = (sel, a) => p.evaluate(({ s, a }) => { const e = document.querySelector(s); return e ? e.getAttribute(a) : null; }, { s: sel, a });
  const doc = id => p.evaluate(i => JSON.parse(JSON.stringify((window.__fbStore.revealPhotos || {})[i] || null)), id);
  const meter = () => p.evaluate(() => { const m = document.querySelector('[data-reveal-votes]'); return m ? { boy: +m.getAttribute('data-boy'), girl: +m.getAttribute('data-girl') } : null; });
  const mountSide = (comp, props) => p.evaluate(({ comp, props }) => {
    let d = document.getElementById('__side'); if (d) { d.__r.unmount(); d.remove(); }
    d = document.createElement('div'); d.id = '__side';
    d.style.cssText = 'position:fixed;right:0;top:0;width:420px;height:100vh;z-index:6500;background:#fff;display:flex;flex-direction:column;overflow:auto';
    document.body.appendChild(d); d.__r = ReactDOM.createRoot(d); d.__r.render(React.createElement(eval(comp), Object.assign({ onBack: () => {}, onExit: () => {} }, props || {})));
  }, { comp, props });
  // v10.450: a lapozó helyzete a bélyegkép-csíkból (aktív elem / elemszám)
  const slidePos = () => p.evaluate(() => { const all = document.querySelectorAll('#__side [data-reveal-strip]'), cur = document.querySelector('#__side [data-reveal-strip][aria-current="true"]');
    return cur ? (+cur.getAttribute('data-reveal-strip') + 1) + ' / ' + all.length : null; });
  const clickSide = sel => p.evaluate(s => { const e = document.querySelector('#__side ' + s); if (e) e.click(); return !!e; }, sel);

  console.log('\n===== 1. A SZÁMOLÁS =====');
  const t1 = await p.evaluate(() => revealVoteTally([
    { id:'a', src:'x', votes:['boy'] },
    { id:'b', src:'x', pair:true, votes:['boy', 'girl'] },
    { id:'c', src:'x', votes:['girl', 'boy'] },              // személy: a 2. tipp NEM számít
    { id:'d', src:'x', hidden:true, votes:['girl'] },
    { id:'e', src:'x', pending:true, votes:['girl'] },
    { id:'w', kind:'wish', text:'x', votes:['girl'] },
    { id:'f', src:'x', pair:true, votes:['boy', null] },
  ]));
  ok(t1.boy === 3 && t1.girl === 2, 'személy 1, pár 2 tipp; rejtett / váró / üzenet / üres nem számít', JSON.stringify(t1));

  // alapállapot: jelszó + három kép
  await p.evaluate(async px => { const db = firebase.firestore();
    await db.collection('config').doc('revealConfig').set({ password: '1234', title: 'Fiú vagy lány?' });
    for (const [id, at] of [['a', 1], ['b', 2], ['c', 3]]) await db.collection('revealPhotos').doc(id).set({ src: px, w: 1, h: 1, at, hidden: false, by: 'Vendég ' + id });
  }, PX);
  await p.keyboard.type('1234'); await p.waitForTimeout(350);
  await p.click('[data-reveal-role="projector"]'); await p.waitForTimeout(600);
  ok(await has('[data-reveal-projector]') && !(await has('[data-reveal-votes]')), 'tipp nélkül nincs számláló a vetítőn');

  console.log('\n===== 2. OPERÁTOR: a kép ALATT =====');
  await mountSide('RevealOperator'); await p.waitForTimeout(300);
  const lay = await p.evaluate(() => {
    const t = document.querySelector('#__side [data-reveal-thumb="a"]'), v = t && t.querySelector('[data-reveal-votepick]');
    const img = t && t.querySelector('img');
    return { has: !!v, below: !!(v && img && v.getBoundingClientRect().top >= img.getBoundingClientRect().bottom - 1),
      rows: v ? v.querySelectorAll('[data-reveal-vote="boy"]').length : 0 };
  });
  ok(lay.has && lay.below && lay.rows === 1, 'minden kép alatt ott a választó; személynél egy sor', JSON.stringify(lay));
  await clickSide('[data-reveal-votepick="a"] [data-reveal-vote="boy"]'); await p.waitForTimeout(150);
  let d = await doc('a');
  ok(d.pair === false && d.votes[0] === 'boy', 'személy → 💙 a store-ba megy', JSON.stringify(d));
  await clickSide('[data-reveal-votepick="b"] [data-reveal-votekind="pair"]'); await p.waitForTimeout(150);
  ok((await attr('#__side [data-reveal-votepick="b"]', 'data-pair')) === '1'
    && (await p.evaluate(() => document.querySelectorAll('#__side [data-reveal-votepick="b"] [data-reveal-vote="boy"]').length)) === 2, 'pár → két tipp-sor');
  await clickSide('[data-reveal-votepick="b"] [data-reveal-vote="boy"][data-vote-idx="0"]'); await p.waitForTimeout(120);
  await clickSide('[data-reveal-votepick="b"] [data-reveal-vote="girl"][data-vote-idx="1"]'); await p.waitForTimeout(150);
  d = await doc('b');
  ok(d.pair === true && d.votes[0] === 'boy' && d.votes[1] === 'girl', 'pár: két különböző tipp is leadható', JSON.stringify(d));
  await clickSide('[data-reveal-votepick="c"] [data-reveal-vote="girl"]'); await p.waitForTimeout(200);
  ok(JSON.stringify(await meter()) === '{"boy":2,"girl":2}', 'vetítő: élőben 2 – 2', JSON.stringify(await meter()));
  ok(await has('[data-reveal-board] [data-reveal-cardvotes]'), 'a polaroidon is látszik a tipp');
  ok((await p.textContent('#__side [data-reveal-optally]')).includes('2') , 'az operátor is látja az állást', await p.textContent('#__side [data-reveal-optally]'));

  console.log('\n===== 3. VÁLTOZÁSOK ÉLŐBEN =====');
  await clickSide('[data-reveal-votepick="a"] [data-reveal-vote="boy"]'); await p.waitForTimeout(200);
  ok((await doc('a')).votes[0] === null && JSON.stringify(await meter()) === '{"boy":1,"girl":2}', 'ugyanarra koppintva törlődik → 1 – 2', JSON.stringify(await meter()));
  await clickSide('[data-reveal-votepick="b"] [data-reveal-votekind="single"]'); await p.waitForTimeout(200);
  ok(JSON.stringify(await meter()) === '{"boy":1,"girl":1}', '⚠️ pár → személy: a 2. tipp kiesik a számolásból', JSON.stringify(await meter()));
  await clickSide('[data-reveal-thumb="c"] [data-reveal-hide]'); await p.waitForTimeout(200);
  ok(JSON.stringify(await meter()) === '{"boy":1,"girl":0}', 'elrejtett kép tippje nem számít', JSON.stringify(await meter()));
  await clickSide('[data-reveal-thumb="c"] [data-reveal-hide]'); await p.waitForTimeout(200);
  await p.evaluate(() => revealQuizWrite(revealQuizStep({ phase:'idle' }, 1, REVEAL_QUIZ_DEFAULT))); await p.waitForTimeout(250);
  ok(!(await has('[data-reveal-votes]')), 'Babakvíz alatt nincs számláló');
  await p.evaluate(() => revealQuizWrite({ phase:'idle' })); await p.waitForTimeout(250);
  ok(JSON.stringify(await meter()) === '{"boy":1,"girl":1}', 'a kvíz után visszajön', JSON.stringify(await meter()));
  const geo = await p.evaluate(() => { const r = document.querySelector('[data-reveal-votes]').getBoundingClientRect(); return { cx: Math.round(r.left + r.width / 2), bottom: Math.round(r.bottom) }; });
  ok(Math.abs(geo.cx - 700) < 4 && geo.bottom <= 820 && geo.bottom > 760, 'a számláló alul, középen', JSON.stringify(geo));

  console.log('\n===== 4. LELEPLEZÉS UTÁN =====');
  await mountSide('RevealVoteMeter', { tally: { boy: 4, girl: 7 }, revealed: 'girl' }); await p.waitForTimeout(150);
  ok((await attr('#__side [data-reveal-votes-side="girl"]', 'data-win')) === '1' && (await attr('#__side [data-reveal-votes-side="boy"]', 'data-win')) === '0',
    'a kiderült oldal kiemelve, a másik nem');
  ok((await p.textContent('#__side [data-reveal-votes]')).includes('🎯'), '„🎯" jelzi, kik találták el');

  console.log('\n===== 5. SZÜLŐK: VETÍTŐ-PANEL =====');
  await mountSide('RevealProjectorPanel'); await p.waitForTimeout(300);
  const rt = await p.evaluate(() => { const e = document.querySelector('#__side [data-reveal-ctl-tally]'); return e ? e.textContent : null; });
  ok(rt && /1.*·.*1/.test(rt), 'a Szülők vetítő-panelje is kiírja az állást', rt);

  console.log('\n===== 6. OPERÁTOR: LAPOZÓ (v10.440) =====');
  await mountSide('RevealOperator'); await p.waitForTimeout(300);
  const sl = await p.evaluate(() => {
    const first = document.querySelector('#__side [data-reveal-thumb][data-idx="0"]');
    const head = first.querySelector('[data-reveal-slidehead]'), img = first.querySelector('img');
    const hide = head.querySelector('[data-reveal-hide]'), del = head.querySelector('[data-reveal-del]');
    const vbtn = first.querySelector('[data-reveal-vote="boy"]');
    const tr = document.querySelector('#__side [data-reveal-track]');
    return { id: first.getAttribute('data-reveal-thumb'), num: first.querySelector('[data-reveal-slidenum]').textContent, newest: head.textContent.includes('LEGÚJABB'),
      ctlAbove: !!(hide && del) && del.getBoundingClientRect().bottom <= img.getBoundingClientRect().top + 1,
      onImg: !!img.parentElement.querySelector('[data-reveal-hide], [data-reveal-del]'),
      vh: Math.round(vbtn.getBoundingClientRect().height), snap: getComputedStyle(tr).scrollSnapType,
      pos: (() => { const all = document.querySelectorAll('#__side [data-reveal-strip]'), cur = document.querySelector('#__side [data-reveal-strip][aria-current="true"]'); return cur ? (+cur.getAttribute('data-reveal-strip') + 1) + ' / ' + all.length : null; })() };
  });
  ok(sl.id === 'c' && sl.num === '1. kép' && sl.newest, 'a legújabb elöl, felül „1. kép" + LEGÚJABB', JSON.stringify(sl));
  ok(sl.ctlAbove && !sl.onImg, 'az Elrejt és a 🗑 a lap fejlécében, nem a képen');
  ok(sl.vh >= 36 && sl.vh <= 44, 'v10.445: a Kisfiú / Kislány gomb kompakt (36–44 px)', sl.vh);
  const pk = await p.evaluate(() => { const v = document.querySelector('#__side [data-reveal-thumb][data-idx="0"] [data-reveal-votepick]'); return Math.round(v.getBoundingClientRect().height); });
  ok(pk <= 64, 'v10.445: személynél az egész választó egy sor (≤ 64 px)', pk);
  await clickSide('[data-reveal-thumb][data-idx="0"] [data-reveal-slideimg]'); await p.waitForTimeout(150);
  ok(await has('#__side [data-reveal-oplightbox] img'), 'a képre koppintva teljes képernyős nézet');
  await clickSide('[data-reveal-oplightbox]'); await p.waitForTimeout(120);
  ok(!(await has('#__side [data-reveal-oplightbox]')), 'koppintásra bezárul');
  ok(/x/.test(sl.snap) && sl.pos === '1 / 3', 'vízszintes lapozó (scroll-snap), a bélyegkép-csíkon az 1. aktív (1 / 3)', sl.snap + ' ' + sl.pos);
  await clickSide('[data-reveal-strip="1"]'); await p.waitForTimeout(700);
  const s2 = Object.assign({ pos: await slidePos() }, await p.evaluate(() => { const tr = document.querySelector('#__side [data-reveal-track]'); return { x: Math.round(tr.scrollLeft / tr.clientWidth * 100) / 100 }; }));
  ok(s2.pos === '2 / 3' && s2.x === 1, 'v10.450: a csík 2. bélyegképére koppintva a 2. képre lép', JSON.stringify(s2));
  await p.evaluate(() => { const tr = document.querySelector('#__side [data-reveal-track]'); tr.scrollLeft = tr.clientWidth * 2; tr.dispatchEvent(new Event('scroll')); }); await p.waitForTimeout(200);
  ok((await slidePos()) === '3 / 3', 'oldalra húzva is lép (3 / 3), és a csík követi');
  await p.evaluate(px => firebase.firestore().collection('revealPhotos').doc('d').set({ src: px, w: 1, h: 1, at: 10, hidden: false, by: 'Vendég d' }), PX);
  await p.waitForTimeout(800);
  const s3 = Object.assign({ pos: await slidePos() }, await p.evaluate(() => { const tr = document.querySelector('#__side [data-reveal-track]'); return { first: document.querySelector('#__side [data-reveal-thumb][data-idx="0"]').getAttribute('data-reveal-thumb'), x: tr.scrollLeft }; }));
  ok(s3.first === 'd' && s3.pos === '1 / 4' && s3.x < 5, 'új kép → az elejére ugrik, az új kép az első', JSON.stringify(s3));

  console.log('\n===== 7. OPERÁTOR: EGY KÉPERNYŐRE FÉR (v10.441) =====');
  await p.evaluate(() => { const d = document.getElementById('__side'); if (d) { d.__r.unmount(); d.remove(); } });
  await p.evaluate(() => revealVoteWrite({ id: 'd' }, true, ['boy', null]));   // pár → a legtöbb gomb
  const fit = async (w, h) => {
    await p.setViewportSize({ width: w, height: h });
    await p.evaluate(() => { let d = document.getElementById('__full'); if (d) { d.__r.unmount(); d.remove(); }
      d = document.createElement('div'); d.id = '__full'; d.style.cssText = 'position:fixed;inset:0;z-index:6500;display:flex;flex-direction:column;background:#fff';
      document.body.appendChild(d); d.__r = ReactDOM.createRoot(d); d.__r.render(React.createElement(RevealOperator, { onBack: () => {} })); });
    await p.waitForTimeout(400);
    return p.evaluate(() => { const r = document.getElementById('__full'), sc = r.querySelector('[data-reveal-opscroll]'), nav = r.querySelector('[data-reveal-slidenav]'),
      img = r.querySelector('[data-reveal-thumb][data-idx="0"] [data-reveal-slideimg]'), vp = r.querySelector('[data-reveal-thumb][data-idx="0"] [data-reveal-votepick]');
      const dk = document.querySelector('[data-reveal-opdock]');
      return { over: sc.scrollHeight - sc.clientHeight, navB: Math.round(nav.getBoundingClientRect().bottom), dockT: dk ? Math.round(dk.getBoundingClientRect().top) : -1, imgH: Math.round(img.getBoundingClientRect().height), pair: vp.getAttribute('data-pair'), vh: innerHeight }; });
  };
  const f1 = await fit(390, 844);
  ok(f1.over <= 1 && f1.navB <= f1.dockT && f1.pair === '1', '390×844 (pár-móddal): nincs görgetés, a bélyegkép-csík a fix feltöltő-dokk FÖLÖTT', JSON.stringify(f1));
  ok(f1.imgH >= 400, 'v10.445: a kép jól látható — páros módban is ≥ 400 px', f1.imgH);
  const f2 = await fit(375, 667);
  ok(f2.over <= 1 && f2.navB <= f2.dockT && f2.imgH >= 120, '375×667 (iPhone SE): itt is kifér', JSON.stringify(f2));
  await p.evaluate(() => { const d = document.getElementById('__full'); if (d) { d.__r.unmount(); d.remove(); } });
  await p.setViewportSize({ width: 1400, height: 820 });

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? `\n${fail} HIBA` : '\nMIND ZÖLD');
  process.exit(fail ? 1 : 0);
})();
