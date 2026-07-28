// v10.172 — A wildcard percalapu lett, nem korszamolos
//
// Miert valtozott: a korkadencia nem huzhato ra a magukban futo jatekokra. A
// Busz osszesen ~6 korlepest csinal, tehat 5-os gyakorisagnal pontosan EGY
// wildcardot kapott volna az egesz jatek alatt; a Power Hour meg a sajat 60
// perces oraja szerint fut. Az ido minden jatekra ugyanaz.
//
// Az idot a Playwright ora-API-javal tekerjuk elore — valos varakozassal ez a
// teszt percekig futna.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';
const SRC = '/home/user/bottle-of-heroes/app.src.html';

// minden wildcard felismerheto reszlete (az alapertelmezett listabol)
const WC_MARKERS = ['Bal kézzel', 'Csend kör', 'mutasson valakire', 'Fordított', 'Bumm',
  'szavak nélkül', 'Karakterkör', 'Dupla kör', 'Pókerpofa', 'Vád kör', 'Hangos kör',
  'Visszapörgetős', 'Szerencsekör', 'mutogatással'];
const foundWc = (txt) => WC_MARKERS.filter(w => txt.includes(w));

const seed = `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = { p_a:{name:'Anna',color:'#5BA0DB'} };
  ['stats','game_stats','statEvents','gameStatEvents','seasons','usage'].forEach(k => window.__fbStore[k] = {});
  window.__fbStore['config'] = { homeConfig: { setupFlowEnabled: true } };
`;

const newPage = async (b, withClock) => {
  const p = await b.newPage({ viewport: { width: 390, height: 1000 } });
  p.__errs = []; p.on('pageerror', e => p.__errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  if (withClock) await p.clock.install();
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  if (withClock) { await p.clock.runFor(4000); await p.waitForTimeout(1500); }
  else await p.waitForTimeout(3600);
  return p;
};

// PlayScreen kozvetlenul, adott wildcard-beallitassal
const mountPlay = (meta) => `
  (() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__ps';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#F5D89B;overflow:auto';
    document.body.appendChild(root);
    function H() {
      const [players, setPlayers] = React.useState([
        { id:'a', name:'Anna', color:'#5BA0DB', points:0, drinks:0 },
        { id:'b', name:'Bela', color:'#E07A5F', points:0, drinks:0 },
      ]);
      return React.createElement(PlayScreen, { go: () => {}, players, setPlayers,
        selectedGames: ['busz'], roomCode: null, gameMeta: ${JSON.stringify(meta)},
        setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {} });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  })();
`;

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const src = fs.readFileSync(SRC, 'utf8');

  // ─── 1) A korszamolo kadencia eltunt ───
  console.log('\n===== A KÖRSZÁMOLÓ KADENCIA =====');
  ok('nincs több wildcardFreq a forrásban', !src.includes('wildcardFreq'),
     (src.match(/.{0,40}wildcardFreq.{0,40}/) || ['—'])[0]);
  ok('nincs "Hányadik körönként?" felirat', !src.includes('Hányadik körönként'));
  const rm = src.match(/const WILDCARD_RANGES = \[([\s\S]*?)\];/);
  const ranges = rm ? [...rm[1].matchAll(/lo:\s*(\d+),\s*hi:\s*(\d+)/g)].map(x => x[1] + '–' + x[2]) : [];
  ok('percalapú tartományok vannak', ranges.length >= 3, ranges.join(', '));

  // ─── 2) A szovegek mar nem egyetlen korre hivatkoznak ───
  // A wildcard mar eddig sem egy korre szolt (a kovetkezoig ervenyben maradt),
  // percalapon pedig vegkepp idoszak. A "kör" NEVEK maradnak — azok a lap nevei.
  console.log('\n===== A SZÖVEGEK =====');
  const defBlock = src.slice(src.indexOf('const WILDCARDS_DEFAULT'), src.indexOf('let WILDCARDS'));
  ok('egyik alapértelmezett szöveg sem mond "ezen a körön"-t', !defBlock.includes('ezen a körön'),
     (defBlock.match(/.{0,50}ezen a körön.{0,20}/) || ['—'])[0]);

  // ─── 3) A beallito felulet ───
  console.log('\n===== A BEÁLLÍTÓ FELÜLET =====');
  {
    const p = await newPage(b, false);
    await p.evaluate(() => {
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__g';
      root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:var(--app-bg)';
      document.body.appendChild(root);
      function H() {
        const [m, sm] = React.useState({ modes:['points','wildcard'], difficulty:'mid' });
        window.__meta = m;
        return React.createElement(SetupScreen, { go: () => {},
          players: [{ id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a' }],
          selectedGames: ['busz'], gameMeta: m, setGameMeta: sm });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p.waitForTimeout(1500);
    const t = await p.evaluate(() => document.querySelector('#__g').innerText.replace(/\s+/g, ' '));
    ok('a felirat "Milyen gyakran?"', /Milyen gyakran/.test(t));
    ok('a tartományok percben jelennek meg', /\d+–\d+/.test(t), (t.match(/\d+–\d+/g) || []).join(' '));
    await p.evaluate(() => {
      const btn = [...document.querySelectorAll('#__g button')].find(x => x.innerText.trim() === '15–25');
      if (btn) btn.click();
    });
    await p.waitForTimeout(500);
    const meta = await p.evaluate(() => ({ min: window.__meta.wildcardMin, max: window.__meta.wildcardMax }));
    ok('a választás percekben mentődik', meta.min === 15 && meta.max === 25, JSON.stringify(meta));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 4) Az idozito tenylegesen kivalt ───
  console.log('\n===== AZ IDŐZÍTŐ =====');
  {
    const p = await newPage(b, true);
    await p.evaluate(mountPlay({ modes:['points','wildcard'], difficulty:'mid', wildcardMin:1, wildcardMax:1 }));
    await p.clock.runFor(2000); await p.waitForTimeout(600);

    const start = await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' '));
    ok('indításkor még nincs wildcard', foundWc(start).length === 0, foundWc(start).join(', ') || 'egy sem');

    await p.clock.runFor(70000); await p.waitForTimeout(800);
    const first = foundWc(await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')));
    ok('1 perc után megjelenik egy wildcard', first.length > 0, first.join(', ') || 'NEM JELENT MEG');

    // a kovetkezo nem lehet ugyanaz — a kod kiszuri az eppen aktivat
    await p.clock.runFor(70000); await p.waitForTimeout(800);
    const second = foundWc(await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')));
    ok('a következő másik lapot hoz', second.length > 0 && second.join() !== first.join(),
       `${first.join(',')} → ${second.join(',')}`);
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 5) Kikapcsolt wildcard eseten SEMMI nem tortenik ───
  // Enelkul egy elrontott feltetel eszrevetlenul mindenkinel bekapcsolna.
  console.log('\n===== KIKAPCSOLT WILDCARD =====');
  {
    const p = await newPage(b, true);
    await p.evaluate(mountPlay({ modes:['points'], difficulty:'mid', wildcardMin:1, wildcardMax:1 }));
    await p.clock.runFor(2000); await p.waitForTimeout(600);
    await p.clock.runFor(300000); await p.waitForTimeout(800);   // 5 perc
    const t = foundWc(await p.evaluate(() => document.body.innerText.replace(/\s+/g, ' ')));
    ok('5 perc alatt sem jön wildcard', t.length === 0, t.join(', ') || 'egy sem');
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
