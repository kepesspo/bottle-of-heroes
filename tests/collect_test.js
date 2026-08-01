// v10.278 — Collect & Boom: a táblán pontosan annyi korty fekszik, amennyi a max
//
// A BEJELENTETT HIBA
//   6×6-os rács, „Max korty: 12". A játékos +2,+2,+3,+1,+1,+1,+3,+2 = 15
//   kortyot fordított fel, a számláló mégis 12/12-n állt meg. A többlet némán
//   elveszett — és minél nagyobb a rács, annál nagyobb volt a szakadék
//   (6×6-on 32 korty feküdt a táblán, a plafon 12).
//
// Amit ellenőriz:
//   1. a számláló maximuma = COLLECT_MAX_POT az adott rácsméretre
//   2. FELFORDÍTVA a teljes táblát, a látható „+N" értékek ÖSSZEGE soha nem
//      több a maximumnál — ez a bejelentett hiba közvetlen ellenőrzése
//   3. a számláló pontosan a felfordított értékek összegét mutatja (nem vág)
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

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);

  const CAPS = await p.evaluate(() => COLLECT_MAX_POT);
  console.log('\n===== 1. A SZÁMLÁLÓ MAXIMUMA A RÁCSMÉRETBŐL JÖN =====');
  for (const grid of [4, 5, 6]) {
    await p.evaluate((grid) => {
      const old = document.getElementById('__c'); if (old) old.remove();
      [...document.body.children].forEach(c => { if (c.id !== '__c') c.style.display = 'none'; });
      const root = document.createElement('div'); root.id = '__c';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;background:#fff;padding:8px';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(CollectBoomGame, {
        gameIdx: 1,
        players: [{ id: 'a', name: 'A', color: '#4FC2A0' }, { id: 'b', name: 'B', color: '#5BA0DB' }],
        onAdvance: () => {}, onResult: () => {},
        gameMeta: { collectConfig: { gridSize: grid, bombCount: 2 } },
      }));
    }, grid);
    await p.waitForTimeout(800);
    const max = await p.evaluate(() => {
      const t = (document.getElementById('__c').innerText || '').replace(/\s+/g, ' ');
      const m = t.match(/\/ *(\d+)/);
      return m ? +m[1] : null;
    });
    ok(max === CAPS[grid], `${grid}×${grid}: a számláló maximuma ${CAPS[grid]}`, String(max));
  }

  console.log('\n===== 2. A TÁBLÁN NINCS TÖBB KORTY, MINT A MAXIMUM =====');
  // Vegigkattintjuk az EGESZ tablat. Az elso bomba utan a tobbi koppintas
  // hatastalan (`if (revealed[i] || bombPid) return`), ezert tobb gameIdx-et
  // nezunk: a seedelt RNG miatt mindegyik mas tablat ad, es van kozottuk olyan,
  // ahol a bomba kesore esik — ott szinte a teljes tabla felfordul.
  for (const grid of [4, 5, 6]) {
    let legtobb = 0, esetek = 0;
    for (let gi = 1; gi <= 8; gi++) {
      await p.evaluate(({ grid, gi }) => {
        const old = document.getElementById('__c'); if (old) old.remove();
        const root = document.createElement('div'); root.id = '__c';
        root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;background:#fff;padding:8px';
        document.body.appendChild(root);
        ReactDOM.createRoot(root).render(React.createElement(CollectBoomGame, {
          gameIdx: gi,
          players: [{ id: 'a', name: 'A', color: '#4FC2A0' }, { id: 'b', name: 'B', color: '#5BA0DB' }],
          onAdvance: () => {}, onResult: () => {},
          gameMeta: { collectConfig: { gridSize: grid, bombCount: 1 } },
        }));
      }, { grid, gi });
      await p.waitForTimeout(450);
      // A maximumot MEG A KATTINTAS ELOTT olvassuk ki: amint a bomba felfordul,
      // a jatek eredmeny-allapotba megy, es a "GYUJTVE n / MAX" kijelzo eltunik.
      const maxElotte = await p.evaluate(() => {
        const t = (document.getElementById('__c').innerText || '').replace(/\s+/g, ' ');
        const m = t.match(/\/ *(\d+)/);
        return m ? +m[1] : null;
      });
      // minden cellara rakoppintunk
      await p.evaluate(() => {
        const root = document.getElementById('__c');
        const g = [...root.querySelectorAll('div')].find(d => d.style && d.style.gridTemplateColumns);
        if (g) [...g.children].forEach(c => c.click());
      });
      await p.waitForTimeout(450);
      const r = await p.evaluate(() => {
        const root = document.getElementById('__c');
        const txt = (root.innerText || '').replace(/\s+/g, ' ');
        const g = [...root.querySelectorAll('div')].find(d => d.style && d.style.gridTemplateColumns);
        const plusok = g ? [...g.children]
          .map(c => (c.textContent || '').trim())
          .filter(t => /^\+\d+$/.test(t)).map(t => +t.slice(1)) : [];
        const m = txt.match(/(\d+) *\/ *(\d+)/);
        return { osszeg: plusok.reduce((a, x) => a + x, 0), db: plusok.length,
                 szamlalo: m ? +m[1] : null };
      });
      r.max = maxElotte;
      if (r.max == null) continue;
      esetek++;
      legtobb = Math.max(legtobb, r.osszeg);
      if (r.osszeg > r.max) {
        ok(false, `${grid}×${grid} (gameIdx ${gi}): a felfordított korty TÖBB a maximumnál`,
           `${r.osszeg} > ${r.max}`);
      }
      // a szamlalo a bomba utan eltunik — csak akkor vetjuk ossze, ha meg latszik
      if (r.szamlalo !== null && r.szamlalo !== r.osszeg) {
        ok(false, `${grid}×${grid} (gameIdx ${gi}): a számláló nem a felfordított összeget mutatja`,
           `számláló ${r.szamlalo}, felfordítva ${r.osszeg}`);
      }
    }
    ok(esetek > 0, `${grid}×${grid}: lefutott ${esetek} tábla`);
    ok(legtobb <= CAPS[grid],
       `${grid}×${grid}: a legtöbb felfordított korty ${legtobb} ≤ max ${CAPS[grid]}`,
       `${legtobb} / ${CAPS[grid]}`);
    // Ha a plafon SOSEM erheto el, az is hiba lenne (ures tabla). A bomba
    // helyetol fugg, hogy melyik seednel mennyi jon ossze, de valamelyiknel
    // el kell erni a maximumot.
    ok(legtobb === CAPS[grid],
       `${grid}×${grid}: és van olyan tábla, ahol a teljes ${CAPS[grid]} felfordul`,
       String(legtobb));
  }

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
