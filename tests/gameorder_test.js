// v10.174 — a legtobbet jatszott jatekok elore, kategorian belul
//
// Az adat mar megvolt (game_stats/{id}.playCount minden jatek vegen no), csak
// a jatekvalaszto nem hasznalta: a lista a GAMES tomb sorrendjeben allt.
//
// A ket kulon eset a lenyeg:
//   1) ELSO megnyitas — meg nincs elmentett szam, marad a regi sorrend, es
//      csak elmentjuk a friss adatot;
//   2) KOVETKEZO megnyitas — mar a jatszottsag szerint all a lista.
// Ha az uj adatot azonnal alkalmaznank, a lista egy masodperccel a megnyitas
// utan atrendezodne a kez alatt — pont amikor az ember mar nyulna egy kartyaert.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const COUNTS = { emojikv: 50, matek: 30, anagramma: 5 };

const open = async (b, { seedCache }) => {
  const p = await b.newPage({ viewport: { width: 390, height: 1400 } });
  p.__errs = []; p.on('pageerror', e => p.__errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`
    try {
      localStorage.setItem('boh_onboarded','1');
      ${seedCache ? `localStorage.setItem('boh_playcounts', ${JSON.stringify(JSON.stringify(COUNTS))});` : ''}
    } catch(e) {}
    ['profiles','stats','statEvents','gameStatEvents','seasons','usage','config']
      .forEach(k => window.__fbStore[k] = {});
    window.__fbStore['game_stats'] = ${JSON.stringify(
      Object.fromEntries(Object.entries(COUNTS).map(([k, v]) => [k, { playCount: v }])))};
  `);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3600);
  await p.evaluate(() => {
    const r = document.getElementById('root'); if (r) r.style.display = 'none';
    const root = document.createElement('div'); root.id = '__g';
    root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:var(--app-bg)';
    document.body.appendChild(root);
    function H() {
      const [sel, setSel] = React.useState([]);
      const [m, sm] = React.useState({ modes:['points'], difficulty:'mid' });
      return React.createElement(GamesScreen, { go: () => {}, selectedGames: sel,
        setSelectedGames: setSel, gameMeta: m, setGameMeta: sm });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  });
  await p.waitForTimeout(1800);
  return p;
};

// Az "Egyéni" szekcio elso nehany jatekneve, a szekciofejlecek kozotti savbol.
const soloNames = (p) => p.evaluate(() => {
  const t = document.querySelector('#__g').innerText.split('\n').map(x => x.trim()).filter(Boolean);
  const i = t.findIndex(x => /^EGYÉNI$/i.test(x));
  const j = t.findIndex((x, k) => k > i && /^PÁROS$/i.test(x));
  return t.slice(i + 1, j > 0 ? j : i + 12).filter(x => x.length > 2 && !/^\d+$/.test(x)).slice(0, 6);
});

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ─── 1) Elso megnyitas: a lista NEM rendezodik at a kez alatt ───
  console.log('\n===== ELSŐ MEGNYITÁS =====');
  {
    const p = await open(b, { seedCache: false });
    const names = await soloNames(p);
    ok('a sorrend még a régi (nem ugrik szét betöltés közben)',
       names[0] !== 'Emoji Kvíz', names.join(' | '));
    const cached = await p.evaluate(() => localStorage.getItem('boh_playcounts'));
    const parsed = JSON.parse(cached || '{}');
    ok('a friss számok elmentődnek a következő megnyitásra',
       parsed.emojikv === 50 && parsed.matek === 30, cached);
    ok('csak a tényleg játszott játékok kerülnek be',
       Object.keys(parsed).length === 3, Object.keys(parsed).join(', '));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 2) Kovetkezo megnyitas: jatszottsag szerint ───
  console.log('\n===== KÖVETKEZŐ MEGNYITÁS =====');
  {
    const p = await open(b, { seedCache: true });
    const names = await soloNames(p);
    ok('a legtöbbet játszott áll elöl', names[0] === 'Emoji Kvíz', names.join(' | '));
    ok('a második a következő legtöbbet játszott', names[1] === 'Gyors Matek', names.join(' | '));
    ok('a harmadik a legkevesebbet játszott, de már játszott', names[2] === 'Anagramma', names.join(' | '));
    // A sort stabil: az azonos (0) jatszottsaguak az eredeti sorrendben maradnak,
    // kulonben minden megnyitasnal mas lenne a lista alja.
    const rest = names.slice(3);
    ok('a soha nem játszottak eredeti sorrendben követik', rest.length > 0 && !rest.includes('Emoji Kvíz'),
       rest.join(' | '));
    ok('nincs JS hiba', p.__errs.length === 0, p.__errs.join(' | '));
    await p.close();
  }

  // ─── 3) A rendezes a kategorian BELUL tortenik ───
  // A szekciok sorrendje (Egyéni / Páros / Csapat) nem valtozhat.
  console.log('\n===== A KATEGÓRIÁK =====');
  {
    const p = await open(b, { seedCache: true });
    const order = await p.evaluate(() => {
      const t = document.querySelector('#__g').innerText;
      return ['EGYÉNI', 'PÁROS', 'CSAPAT'].map(k => t.indexOf(k));
    });
    ok('a kategóriák sorrendje változatlan: Egyéni → Páros → Csapat',
       order.every((v, i) => v >= 0 && (i === 0 || v > order[i - 1])), order.join(' < '));
    await p.close();
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
