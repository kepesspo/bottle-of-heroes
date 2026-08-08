// v10.327 — Csoportos ivászat: számlálódik, és a PARTI nehézségét követi
//
// Két állítás, és mindkettő a felhasználó kérdéséből jött:
//   1. „Csoportos ivászat számlálódik?" — IGEN: a „Megiszom!" gomb MINDEN
//      játékos `drinks` mezőjét növeli, és a parti végén ez megy fel a
//      statisztikába (`totalDrinks += p.drinks`).
//   2. A mennyiség eddig a JÁTÉK-kártya statikus címkéjéből jött
//      (könnyű/közepes/nehéz → 1/2/3), tehát extrém szinten ugyanannyit adott,
//      mint könnyűn. Innentől a partira beállított szint szorzója (1/2/3/5).
//
// Az esemény 5–10 percenként sül el, ezért a `window.__groupDrinkTestDelay`
// felülírja az első tüzelés idejét — ugyanaz a fogódzó, mint a szélviharnál.
// A popup NEM játék közben jön: az ütemező csak „esedékesre" állít, és a
// következő kör/játék kezdete után jelenik meg, ~1,8 mp-cel.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PL = [{ id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
            { id:'b', name:'Kecsi', color:'#4FC2A0', points:0, drinks:0 },
            { id:'c', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // `erem` a hordozo jatek: a kartyajan „könnyű" cimke all, tehat a REGI
  // keplet mindharom szinten 1-et adott volna. Igy a teszt tenyleg a parti
  // szintjet meri, nem a jatek cimkejet.
  for (const [diff, mult] of [['easy', 1], ['mid', 2], ['hard', 3], ['extreme', 5]]) {
    console.log('\n===== ' + diff.toUpperCase() + ' =====');
    const p = await b.newPage({ viewport: { width: 402, height: 900 } });
    const errs = [];
    p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}
      window.__groupDrinkTestDelay = 250;`);
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3200);
    await p.evaluate(({ pl, diff }) => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
      document.body.appendChild(root);
      function H() {
        const [ps, setPs] = React.useState(pl);
        window.__players = ps;
        return React.createElement(PlayScreen, {
          go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['erem'],
          // 'group' kapcsolja be a csoportos ivaszatot, 'points' pedig a
          // konyvelest (`trackScores`) — egy valodi parti mindkettot viszi.
          roomCode: null, gameMeta: { modes: ['group', 'points'], difficulty: diff }, setGameMeta: () => {},
          setScoreHistory: () => {}, setLastGameRound: () => {},
        });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    }, { pl: PL, diff });
    // Az utemezo csak „esedekesre" ALLIT — a popup a KOVETKEZO kor/jatek
    // kezdete utan ~1,8 mp-cel jon (hogy ne szakitsa felbe a jatekot).
    // Ezert le kell jatszani egy kort: FEJ → eredmeny → Kövi.
    await p.waitForTimeout(1200);
    await p.evaluate(() => {
      const x = [...document.querySelectorAll('#__p button')].find(y => /FEJ/.test(y.innerText || ''));
      if (x) x.click();
    });
    await p.waitForTimeout(4200);
    await p.evaluate(() => {
      const x = [...document.querySelectorAll('button')].find(y => /Kövi/.test(y.innerText || ''));
      if (x) x.click();
    });
    await p.waitForTimeout(3200);

    const shown = await p.evaluate(() => {
      const t = document.body.innerText;
      const m = t.match(/Mindenki iszik\s*\n\s*(\d+)\s*\n\s*kortyt/);
      return { open: /Csoportos Ivászat/i.test(t), n: m ? Number(m[1]) : null };
    });
    ok(shown.open, 'felugrott a Csoportos Ivászat');
    ok(shown.n === mult, `a mennyiség a PARTI szintjét követi (${diff} → ${mult})`, shown.n);

    const before = await p.evaluate(() => (window.__players || []).map(x => ({ n:x.name, d:x.drinks })));
    await p.evaluate(() => {
      const x = [...document.querySelectorAll('button')].find(y => /Megiszom/.test(y.innerText || ''));
      if (x) x.click();
    });
    await p.waitForTimeout(800);
    // A kor eredmenye NINCS commitalva (nem nyomtunk Kövi-t), tehat amennyivel
    // itt no a szam, az PONTOSAN a csoportos ivaszat.
    const after = await p.evaluate(() => (window.__players || []).map(x => ({ n:x.name, d:x.drinks })));
    ok(after.length === 3 && after.every(x => x.d - (before.find(y => y.n === x.n) || {}).d === mult),
       'MINDENKI kortyához hozzáadódik — tehát számlálódik',
       JSON.stringify(before) + ' → ' + JSON.stringify(after));
    ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
