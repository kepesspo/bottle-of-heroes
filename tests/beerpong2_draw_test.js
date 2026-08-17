// v10.396 — Beer Pong 2.0: observer-oldali DÖNTETLEN beküldés
//
// Bejelentés: „Observer képernyőről Döntetlen-t nem lehet megadni. Legyen ugy hogy
// az időzitő inditása után lesz aktiv a gomb hogy utánna döntetlent meg lehessen adni."
//
// Fogódzók:
//  RR (körmérkőzés, matchMinutes:5):
//   1) elindítás ELŐTT egy döntetlen (egyenlő pohár) NEM küldhető be (gomb tiltva,
//      „⏱ Indítsd el az órát a döntetlenhez")
//   2) az óra elindítása UTÁN a döntetlen gomb AKTÍV („Döntetlen beküldése")
//   3) beküldve a bp2Submit p1===p2, a host jóváhagyó gombja „Döntetlen rögzítése",
//      elfogadva a meccs draw:true-val zárul
//  SE (kontroll): elindítás után is TILTOTT a döntetlen (SE-ben nincs döntetlen)
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
const RR = '990396', SE = '990397';

// Az RR 0. meccsének mk-kulcsa mindig rr#0. Segédek a store-hoz.
const rrMatch0 = (p, code) => p.evaluate(c => {
  const bp = (window.__fbStore['rooms'][c] || {}).bp2State || {};
  const ms = bp.rrMatches ? (Array.isArray(bp.rrMatches) ? bp.rrMatches : Object.values(bp.rrMatches)) : [];
  const m = ms[0];
  return m ? { winner: m.winner ? m.winner.id : null, draw: !!m.draw, score: m.score || null } : null;
}, code);
const sub = (p, code) => p.evaluate(c => (window.__fbStore['rooms'][c] || {}).bp2Submit || {}, code);
const live = (p, code, k) => p.evaluate(({ c, k }) => (((window.__fbStore['rooms'][c] || {}).bp2Live) || {})[k] || null, { c: code, k });

// A megadott konténerben az elso "beküldő" gomb (Döntetlen/Beküldés/Állítsd/Indítsd)
const submitBtn = (p, sel) => p.evaluate(s => {
  const b = [...document.querySelectorAll(s + ' button')].find(x => /Döntetlen beküldése|Beküldés a hostnak|Állítsd be az eredményt|Indítsd el az órát|Módosítás beküldése/.test(x.textContent || ''));
  return b ? { label: (b.textContent || '').trim(), disabled: b.disabled } : null;
}, sel);
const clickIn = (p, sel, reSrc) => p.evaluate(({ s, r }) => { const b = [...document.querySelectorAll(s + ' button')].find(x => new RegExp(r).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, { s: sel, r: reSrc });
const clickPlus = (p, sel, n) => p.evaluate(({ s, n }) => { const bs = [...document.querySelectorAll(s + ' button')].filter(x => (x.textContent || '').trim() === '+'); if (bs[n]) bs[n].click(); }, { s: sel, n });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1900 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  await p.evaluate(({ rr, se }) => {
    const mk = (code, extra) => { window.__fbStore['rooms'] = window.__fbStore['rooms'] || {}; };
    const players = () => [{ id:'p0', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                           { id:'p1', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
                           { id:'p2', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];
    window.__fbStore['rooms'] = {
      [rr]: { code: rr, players: players(), gameIdx: 0, selectedGames: ['beerpong2'] },
      [se]: { code: se, players: players(), gameIdx: 0, selectedGames: ['beerpong2'] },
    };
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const mount = (id, top, code, cfg, isObs) => {
      const d = document.createElement('div'); d.id = id;
      d.style.cssText = `position:absolute;left:${isObs?410:0}px;top:${top}px;width:402px;height:900px;overflow:auto;z-index:9;background:#fff`;
      document.body.appendChild(d);
      if (isObs) {
        function W() {
          const [room, setRoom] = React.useState(() => window.__fbStore['rooms'][code]);
          React.useEffect(() => firebase.firestore().collection('rooms').doc(code).onSnapshot(s => setRoom(s.data() || null)), []);
          if (!room) return null;
          return React.createElement(BeerPong2ObserverView, { room, code, observerName: 'Néző', onLeave: () => {} });
        }
        ReactDOM.createRoot(d).render(React.createElement(W));
      } else {
        ReactDOM.createRoot(d).render(React.createElement(BeerPong2Game, {
          gameIdx: 0, players: window.__fbStore['rooms'][code].players, roomCode: code, initialBpState: null,
          gameMeta: { beerpong2Config: cfg },
          onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, onSetBpEnded: () => {} }));
      }
    };
    const rrCfg = { tournamentType:'rr', mode:'egyeni', maxCups:10, finalCups:10, matchMinutes:5, thirdPlace:false };
    const seCfg = { tournamentType:'se', mode:'egyeni', maxCups:10, finalCups:10, visszavago:false, matchMinutes:5, thirdPlace:false };
    mount('__hostRR', 0, rr, rrCfg, false);
    mount('__obsRR', 0, rr, rrCfg, true);
    mount('__hostSE', 950, se, seCfg, false);
    mount('__obsSE', 950, se, seCfg, true);
  }, { rr: RR, se: SE });
  await p.waitForTimeout(2000);

  // ── 1. RR: elindítás ELŐTT a döntetlen NEM küldhető ──
  console.log('\n===== 1. RR — INDÍTÁS ELŐTT: DÖNTETLEN TILTVA =====');
  let sb = await submitBtn(p, '#__obsRR');
  ok(!!sb, 'megvan a beküldő gomb az RR observeren', JSON.stringify(sb));
  ok(sb && sb.disabled === true, '⚠️ 0–0 döntetlen indítás előtt TILTOTT', JSON.stringify(sb));
  ok(sb && /Állítsd be az eredményt/.test(sb.label), 'a felirat „Állítsd be az eredményt" (indítás előtt)', sb && sb.label);

  // ── 2. RR: óra indítása → döntetlen gomb AKTÍV ──
  console.log('\n===== 2. RR — INDÍTÁS UTÁN: DÖNTETLEN AKTÍV =====');
  await clickIn(p, '#__obsRR', 'Indítás');
  await p.waitForTimeout(500);
  ok(!!(await live(p, RR, 'rr#0')), 'az RR 0. meccs elindult (bp2Live rr#0)', JSON.stringify(await live(p, RR, 'rr#0')));
  // állítsunk egyenlő, NEM nulla eredményt: p1 +2, p2 +2
  await clickPlus(p, '#__obsRR', 0); await p.waitForTimeout(120); await clickPlus(p, '#__obsRR', 0); await p.waitForTimeout(120);
  await clickPlus(p, '#__obsRR', 1); await p.waitForTimeout(120); await clickPlus(p, '#__obsRR', 1); await p.waitForTimeout(200);
  sb = await submitBtn(p, '#__obsRR');
  ok(sb && sb.disabled === false, '⚠️ elindítás után a döntetlen gomb AKTÍV', JSON.stringify(sb));
  ok(sb && /Döntetlen beküldése/.test(sb.label), 'a felirat „Döntetlen beküldése"', sb && sb.label);

  // ── 3. RR: beküldés → host „Döntetlen rögzítése" → draw:true ──
  console.log('\n===== 3. RR — BEKÜLDÉS + HOST ELFOGADÁS =====');
  await clickIn(p, '#__obsRR', 'Döntetlen beküldése');
  await p.waitForTimeout(600);
  const s = await sub(p, RR);
  const sk = Object.keys(s)[0];
  ok(sk === 'rr#0', 'a beküldés kulcsa rr#0', sk);
  ok(sk && s[sk].p1 === s[sk].p2 && s[sk].p1 === 2, '⚠️ a beküldött eredmény döntetlen (2–2)', sk && (s[sk].p1 + '–' + s[sk].p2));
  // host jóváhagyó gomb
  const acc = await p.evaluate(() => { const b = [...document.querySelectorAll('#__hostRR button')].find(x => /Döntetlen rögzítése|Döntetlen — nem rögzíthető/.test(x.textContent || '')); return b ? { label:(b.textContent||'').trim(), disabled:b.disabled } : null; });
  ok(acc && /Döntetlen rögzítése/.test(acc.label) && acc.disabled === false, '⚠️ a host jóváhagyó gombja „Döntetlen rögzítése" (AKTÍV)', JSON.stringify(acc));
  await clickIn(p, '#__hostRR', 'Döntetlen rögzítése');
  await p.waitForTimeout(700);
  const m0 = await rrMatch0(p, RR);
  ok(m0 && m0.draw === true, '⚠️ az RR 0. meccs DÖNTETLENként rögzült (draw:true)', JSON.stringify(m0));
  ok(Object.keys(await sub(p, RR)).length === 0, 'a beküldés eltűnt az elfogadás után');

  // ── 4. SE kontroll: elindítás után is TILTOTT a döntetlen ──
  console.log('\n===== 4. SE KONTROLL — DÖNTETLEN NEM ENGEDÉLYEZETT =====');
  // az SE observeren elindítjuk az első meccset, majd 0–0-ra nézzük
  await clickIn(p, '#__obsSE', 'Indítás');
  await p.waitForTimeout(500);
  const sbSE = await submitBtn(p, '#__obsSE');
  ok(sbSE && sbSE.disabled === true, '⚠️ SE: elindítás után is TILTOTT a 0–0', JSON.stringify(sbSE));
  ok(sbSE && /Állítsd be az eredményt/.test(sbSE.label), 'SE: a felirat „Állítsd be az eredményt" (nem óra-hint)', sbSE && sbSE.label);

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
