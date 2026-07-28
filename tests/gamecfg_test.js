// v10.175 — hat tovabbi jatek kapott sajat beallitast
//
// A lenyeg nem az, hogy a beallito lap megnyilik, hanem hogy a JATEK tenyleg
// maskepp fut tole. Egy lap, ami semmit nem valtoztat, rosszabb a semminel.
// Ezert minden jateknal a tenyleges hatast merjuk (kartyak szama, korok szama,
// racsmeret), nem a lap tartalmat.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const fresh = async (b) => {
  const p = await b.newPage({ viewport: { width: 390, height: 1000 } });
  p.__errs = []; p.on('pageerror', e => p.__errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`
    try { localStorage.setItem('boh_onboarded','1'); } catch(e) {}
    ['profiles','stats','game_stats','statEvents','gameStatEvents','seasons','usage','config']
      .forEach(k => window.__fbStore[k] = {});
  `);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);
  return p;
};

// Egy jatekot mountol adott gameMeta-val, es visszaadja a mert erteket.
const mountGame = (p, comp, meta, measure) => p.evaluate(([c, m, fn]) => {
  const r = document.getElementById('root'); if (r) r.remove();
  const root = document.createElement('div'); root.id = '__g';
  root.style.cssText = 'position:fixed;inset:0;z-index:1;background:#F5D89B;overflow:auto';
  document.body.appendChild(root);
  const PLAYERS = [
    { id:'a', name:'Anna', color:'#5BA0DB', points:0, drinks:0 },
    { id:'b', name:'Bela', color:'#E07A5F', points:0, drinks:0 },
    { id:'c', name:'Cili', color:'#A78BFA', points:0, drinks:0 },
  ];
  ReactDOM.createRoot(root).render(React.createElement(eval(c), {
    gameIdx: 0, players: PLAYERS, challenger: PLAYERS[0], opponent: PLAYERS[1],
    onAdvance: () => {}, onResult: () => {}, onSetHideFooter: () => {}, gameMeta: m,
  }));
  return null;
}, [comp, meta, null]);

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ─── 1) A jatekok tenyleg hasznaljak a beallitast ───
  console.log('\n===== A BEÁLLÍTÁS TÉNYLEG HAT =====');

  // Memoria: hany kartya van a paklin (par × 2)
  {
    const counts = [];
    for (const pairs of [4, 12]) {
      const p = await fresh(b);
      await mountGame(p, 'MemoriaGame', { memoriaConfig: { pairs } });
      await p.waitForTimeout(1200);
      counts.push(await p.evaluate(() => {
        const grid = [...document.querySelectorAll('#__g div')]
          .filter(d => d.children.length >= 8 && getComputedStyle(d).display === 'grid');
        return grid.length ? grid[0].children.length : -1;
      }));
      await p.close();
    }
    ok('Memória: a párok száma megváltoztatja a pakli méretét',
       counts[0] === 8 && counts[1] === 24, `4 pár → ${counts[0]} lap, 12 pár → ${counts[1]} lap`);
  }

  // Ritmus: racsmeret. A jatek indito kepernyovel kezd, at kell rajta lepni.
  {
    const cells = [];
    for (const grid of [9, 16]) {
      const p = await fresh(b);
      await mountGame(p, 'RitmusGame', { ritmusConfig: { grid, duration: 30 } });
      await p.waitForTimeout(1200);
      await p.evaluate(() => {
        const btn = [...document.querySelectorAll('#__g button')].find(x => /Start/i.test(x.innerText || ''));
        if (btn) btn.click();
      });
      await p.waitForTimeout(1200);
      cells.push(await p.evaluate(() => {
        const g = [...document.querySelectorAll('#__g div')]
          .filter(d => getComputedStyle(d).display === 'grid' && d.children.length >= 9);
        return g.length ? g[0].children.length : -1;
      }));
      await p.close();
    }
    ok('Ritmus: a rácsméret megváltoztatja a mezők számát',
       cells[0] === 9 && cells[1] === 16, `${cells[0]} / ${cells[1]} mező`);
  }

  // Utveszto: palyameret. Sugo-kepernyovel indul; a csapdaszam a palyabol jon,
  // kulonben 4x4-en tulzsufolt, 7x7-en elvesznek a csapdak.
  {
    const seen = [];
    for (const grid of [4, 7]) {
      const p = await fresh(b);
      await mountGame(p, 'UtvesztoGame', { utvesztoConfig: { grid } });
      await p.waitForTimeout(1200);
      const help = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
      await p.evaluate(() => {
        const btn = [...document.querySelectorAll('#__g button')].find(x => /Kezdés/i.test(x.innerText || ''));
        if (btn) btn.click();
      });
      await p.waitForTimeout(1200);
      const cells = await p.evaluate(() => {
        const g = [...document.querySelectorAll('#__g div')]
          .filter(d => getComputedStyle(d).display === 'grid' && d.children.length >= 16);
        return g.length ? g[0].children.length : -1;
      });
      const traps = (help.match(/Helyezz el (\d+) csapdát a saját (\d+)×/) || []).slice(1);
      seen.push({ cells, traps });
      await p.close();
    }
    ok('Útvesztő: a pálya mérete tényleg változik',
       seen[0].cells === 16 && seen[1].cells === 49,
       `4×4 → ${seen[0].cells}, 7×7 → ${seen[1].cells}`);
    ok('a súgó a beállított pályaméretet írja',
       seen[0].traps[1] === '4' && seen[1].traps[1] === '7',
       `${seen[0].traps.join('/')} · ${seen[1].traps.join('/')}`);
    ok('a csapdák száma követi a pályát (nem fix 5)',
       +seen[0].traps[0] === 3 && +seen[1].traps[0] === 10,
       `4×4 → ${seen[0].traps[0]} csapda, 7×7 → ${seen[1].traps[0]} csapda`);
  }

  // Meduza es Kartyacsata: a korszam a kepernyon is latszik ("1 / N")
  for (const [comp, key, label] of [['MeduzaGame', 'meduzaConfig', 'Medúza'],
                                    ['CardBattleGame', 'cardbattleConfig', 'Kártyacsata']]) {
    const seen = [];
    for (const rounds of [3, 7]) {
      const p = await fresh(b);
      await mountGame(p, comp, { [key]: { rounds } });
      await p.waitForTimeout(1400);
      const t = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
      const m = t.match(/\/\s*(\d+)/);
      seen.push(m ? +m[1] : (t.includes(String(rounds)) ? rounds : -1));
      await p.close();
    }
    ok(`${label}: a körök száma megjelenik a játékban`,
       seen[0] === 3 && seen[1] === 7, `${seen[0]} / ${seen[1]}`);
  }

  // ─── 2) A Kviz temakor-szures ───
  // Ezt a jatek MAR eddig is olvasta (gameMeta.quizConfig.cats), csak felulet
  // nem volt hozza — igy itt az a kerdes, hogy a lap a helyes kulcsokat irja.
  console.log('\n===== A KVÍZ TÉMAKÖRÖK =====');
  {
    const p = await fresh(b);
    await p.evaluate(() => {
      const r = document.getElementById('root'); if (r) r.remove();
      const root = document.createElement('div'); root.id = '__c';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;background:var(--app-bg)';
      document.body.appendChild(root);
      function H() { const [cfg, sc] = React.useState({}); window.__cfg = cfg;
        return React.createElement(QuizConfigSheet, { config: cfg, setConfig: sc, onClose: () => {} }); }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p.waitForTimeout(1000);
    ok('mind a négy témakör megjelenik',
       await p.evaluate(() => ['Általános','Sport','Zene','Film']
         .every(x => document.body.innerText.includes(x))));

    // egy kikapcsolasa
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('button')].find(x => /Sport/.test(x.innerText));
      if (btn) btn.click();
    });
    await p.waitForTimeout(500);
    const cats = await p.evaluate(() => window.__cfg.cats);
    ok('kikapcsolva kikerül a listából', Array.isArray(cats) && !cats.includes('sport'), JSON.stringify(cats));
    ok('a kulcsok egyeznek a játék adatbázisával',
       Array.isArray(cats) && cats.every(k => ['altalanos','sport','zene','film'].includes(k)), JSON.stringify(cats));

    // az utolsot nem lehet kikapcsolni — kerdes nelkul nincs jatek
    for (const name of ['Általános', 'Zene', 'Film']) {
      await p.evaluate(n => {
        const btn = [...document.querySelectorAll('button')].find(x => x.innerText.includes(n));
        if (btn && !btn.disabled) btn.click();
      }, name);
      await p.waitForTimeout(300);
    }
    const left = await p.evaluate(() => window.__cfg.cats);
    ok('az utolsó témakör nem kapcsolható ki', Array.isArray(left) && left.length >= 1, JSON.stringify(left));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 3) A nyilvantartas ───
  // Ha a jatek nincs a GAME_CONFIG_DEFS-ben, a ceruza-gomb es a Jatekmenet
  // oldal sem tud rola — a lap letezese onmagaban nem eleg.
  console.log('\n===== A NYILVÁNTARTÁS =====');
  {
    const src = fs.readFileSync('/home/user/bottle-of-heroes/app.src.html', 'utf8');
    const m = src.match(/const GAME_CONFIG_DEFS = \{([\s\S]*?)\n\};/);
    const ids = m ? [...m[1].matchAll(/^\s*([a-z]+):/gm)].map(x => x[1]) : [];
    const want = ['busz','beerpong','kisebb','collect','ovfj','zene','blackjack',
                  'memoria','ritmus','utveszto','meduza','cardbattle','quiz'];
    const missing = want.filter(k => !ids.includes(k));
    ok('mind a 13 beállítható játék szerepel', missing.length === 0,
       missing.length ? 'hiányzik: ' + missing.join(', ') : ids.length + ' játék');
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
