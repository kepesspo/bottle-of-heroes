// v10.380 — Beer Pong 2.0: 1 CSOPORTOS 2 lépcsős opció (erősorrend)
//
// A 2 lépcsős tornáknál (Csoport → Kieséses / Csoport → Csoport) engedélyezve
// van az 1 csoport. 1 csoportnál a csoportkör egy KÖZÖS körmérkőzés = erősorrend,
// és MINDENKI továbbjut a főszakaszra, a végső állás szerint kiemelve (nem csak a
// top `groupAdvance`).
//
// Fogódzó: grp_rr_se, 1 csoport, groupAdvance:1 (!), 4 játékos → a csoport-RR után
// a kieséses főszakaszba MIND A 4 játékos bekerül (nem 1). A `groupAdvance:1` a
// lényeg: enélkül a régi logika 1 embert vinne tovább (degenerált).
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const CODE = '990044';
const bpState = p => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).bp2State || {}, CODE);

// Egy host meccs lezárása: a bal (p1) számláló 10, a jobb 0, majd megerősítés.
async function scoreLeftWins(p) {
  await p.evaluate(async () => {
    const rows = [...document.querySelectorAll('#__host div')].filter(d => {
      const k = [...d.children];
      return k.length === 3 && k[0].tagName === 'BUTTON' && k[2].tagName === 'BUTTON'
        && (k[0].textContent || '').trim() === '−' && (k[2].textContent || '').trim() === '+';
    });
    if (!rows[0]) return;
    const plus = [...rows[0].children][2];
    for (let i = 0; i < 10; i++) { plus.click(); await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); }
  });
  await p.waitForTimeout(120);
  await p.evaluate(() => { const b = [...document.querySelectorAll('#__host button')].find(x => /nyert — tovább|Döntetlen megerősítése/.test(x.textContent || '')); if (b) b.click(); });
  await p.waitForTimeout(380);
}

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1000 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ code }) => {
    const pl = [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
                { id:'p2', name:'Vivi', color:'#A78BFA', points:0, drinks:0 },
                { id:'p3', name:'Robi', color:'#5BA0DB', points:0, drinks:0 }];
    window.__fbStore['rooms'] = { [code]: { code, players: pl, gameIdx: 0, selectedGames: ['beerpong2'] } };
    window.__adv = null;
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const h = document.createElement('div'); h.id = '__host';
    h.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:960px;overflow:auto;z-index:9;background:#fff';
    document.body.appendChild(h);
    ReactDOM.createRoot(h).render(React.createElement(BeerPong2Game, {
      gameIdx: 0, players: pl, roomCode: code, initialBpState: null,
      // grp_rr_se, 1 csoport, groupAdvance:1 (a 1-csoport felulirja → mindenki tovabbjut)
      gameMeta: { beerpong2Config: { tournamentType:'grp_rr_se', mode:'egyeni', maxCups:10, finalCups:10, matchMinutes:0, numGroups:1, groupAdvance:1, thirdPlace:false } },
      onAdvance: (dm, pm) => { window.__adv = { dm, pm }; }, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
  }, { code: CODE });
  await p.waitForTimeout(1600);

  // ── 1. Csoport-fázis, EGY csoport ──
  console.log('\n===== 1. EGY CSOPORT (körmérkőzés) =====');
  const st0 = await bpState(p);
  ok(st0.phase === 'groups', 'a torna csoport-fázisban indul', st0.phase);
  const groups0 = st0.tsGroups ? (Array.isArray(st0.tsGroups) ? st0.tsGroups : Object.values(st0.tsGroups)) : [];
  ok(groups0.length === 1, '⚠️ PONTOSAN 1 csoport van (a régi min-2 feloldva)', groups0.length);
  const g0matches = groups0[0] ? (Array.isArray(groups0[0].matches) ? groups0[0].matches : Object.values(groups0[0].matches || {})) : [];
  ok(g0matches.length === 6, '4 fős körmérkőzés = 6 meccs', g0matches.length);

  // ── 2. Lejátsszuk a 6 csoport-meccset, majd a főszakasz indul ──
  console.log('\n===== 2. CSOPORT LEJÁTSZÁSA → FŐSZAKASZ =====');
  for (let i = 0; i < 10; i++) {
    const st = await bpState(p);
    if (st.phase === 'finals') break;
    await scoreLeftWins(p);
  }
  const st1 = await bpState(p);
  ok(st1.phase === 'finals', 'a csoport után a FŐSZAKASZ (finals) indul', st1.phase);

  // ── 3. A kieséses főszakaszba MIND A 4 játékos bekerült (nem 1) ──
  console.log('\n===== 3. MINDENKI TOVÁBBJUT (erősorrend szerint kiemelve) =====');
  const seR = st1.seRounds ? (Array.isArray(st1.seRounds) ? st1.seRounds : Object.values(st1.seRounds)) : [];
  const ids = new Set();
  seR.forEach(round => (Array.isArray(round) ? round : Object.values(round || {})).forEach(m => {
    if (m && m.p1) ids.add(m.p1.id); if (m && m.p2) ids.add(m.p2.id);
  }));
  ok(ids.size === 4, '⚠️ a kieséses bracketben MIND A 4 játékos ott van (groupAdvance:1 ellenére)', ids.size);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
