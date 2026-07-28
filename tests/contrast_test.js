// v10.158 — Szövegkontraszt témánként
//
// A hiba, ami ezt kiváltotta: a Statisztika „Összes" és „Mind" pirulái
// `background:T.ink` + `color:'#fff'` párost használtak. Világos témában az ink
// sötét, tehát jó — SÖTÉT témában viszont az ink majdnem fehér (#EDF1FB), és a
// fehér szöveg 1.13-as kontraszttal jelent meg. Gyakorlatilag láthatatlan volt,
// és semmilyen teszt nem fogta meg, mert funkcionálisan minden működött.
//
// Ez a teszt minden témára végigméri a látható szövegeket (WCAG-kontraszt), és
// KEMÉNY PADLÓT húz: ami ez alatt van, az olvashatatlan, nem stílus kérdése.
// A 4.5-ös WCAG-minimum alattiakat csak kiírja — azok között régi, minden
// témában meglévő esetek is vannak (pl. fehér szöveg a mentazöld fülön), azok
// külön dizájn-döntést igényelnek, nem csendes javítást.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const FLOOR = 2.5;   // ez alatt olvashatatlan — HIBA
const WCAG  = 4.5;   // ez alatt csak jelentjük

// Ismert, TUDATOSAN vallalt esetek. Nem elrejtes: felsorolva, indokkal — ami
// nincs a listan es a padlo ala esik, az bukik. Egyik sem tema-fuggo hiba:
// mindegyik minden temaban ugyanigy nez ki, tehat dizajn-dontes, nem regresszio.
const BASELINE = [
  // Erem-szinek: arany/ezust/bronz a helyezes-szamon. A jelentesuk maga a szin.
  { test: r => /^[123]$/.test(r.txt), why: 'érem-színek (arany/ezüst/bronz) a helyezésszámon' },
  // Az avatar-korong a jatekos sajat valasztott szine, benne a kezdobetu.
  { test: r => /^[A-ZÁÉÍÓÖŐÚÜŰ]$/.test(r.txt), why: 'avatar-korong a játékos saját profilszínével' },
  // A marka elsodleges szinen allo feher szoveg. Nem feliratra szol, hanem a
  // SZINPARRA: minden gombon, pirulan es fulon ez a lathato nyelv (2.1-2.2).
  // Paletta-szintu dontes; ha egyszer valtoztatunk rajta, azt egyben kell,
  // mind a 153 helyen.
  { test: (r, mint) => r.fg === 'rgb(255, 255, 255)' && r.bg === mint,
    why: 'márka: fehér szöveg a téma kiemelőszínén' },
  // A PrimaryButton hattere linear-gradient, ezert nincs backgroundColor-ja: a
  // mero atlep rajta a lap hatterere es hamis alacsony erteket szamol. A gomb
  // valojaban a kiemeloszinen ul, feher szoveggel — ugyanaz az eset, mint fent.
  { test: r => /^(Játék indítása|Tovább|Indítás|⏱)/i.test(r.txt) && r.fg === 'rgb(255, 255, 255)',
    why: 'indítógomb (gradiens háttér — a mérő átlép rajta)' },
];
// temank kiemeloszine rgb()-ben, a vallalt szinpar ellenorzesehez
const MINT = { warm:'rgb(79,194,160)', ice:'rgb(32,112,192)', jade:'rgb(32,160,96)',
               dark:'rgb(79,194,160)', slate:'rgb(64,200,160)' };
let CURRENT_MINT = MINT.warm;
const known = (r) => BASELINE.find(b => b.test(r, CURRENT_MINT));

const seed = (theme) => `
  try { localStorage.setItem('boh_onboarded','1'); localStorage.setItem('boh_theme','${theme}'); } catch(e){}
  window.__fbStore['profiles'] = { p_a:{name:'Anna',color:'#5BA0DB'}, p_b:{name:'Bela',color:'#E07A5F'} };
  window.__fbStore['stats'] = {
    p_a:{ totalPoints:640, totalDrinks:320, totalSessions:28, totalRounds:1200, totalWins:12 },
    p_b:{ totalPoints:300, totalDrinks:150, totalSessions:12, totalRounds:400,  totalWins:4  } };
  window.__fbStore['game_stats'] = {}; window.__fbStore['statEvents'] = {};
  window.__fbStore['gameStatEvents'] = {}; window.__fbStore['seasons'] = {};
  window.__fbStore['config'] = {}; window.__fbStore['usage'] = {};
`;

// A mérés a böngészőben fut: a tényleges háttér a szülőkön felfelé haladva áll
// össze (áttetsző rétegeket összefésülve), különben a ratio hazudna.
const MEASURE = () => {
  const lum = (r, g, b) => { const f = c => { c /= 255; return c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); };
    return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b); };
  const parse = s => { const m = (s||'').match(/[\d.]+/g); return m ? { r:+m[0], g:+m[1], b:+m[2], a:m[3]!==undefined?+m[3]:1 } : null; };
  const blend = (fg, bg) => ({ r:fg.r*fg.a+bg.r*(1-fg.a), g:fg.g*fg.a+bg.g*(1-fg.a), b:fg.b*fg.a+bg.b*(1-fg.a), a:1 });
  const effBg = el => {
    let cur = el, acc = null;
    while (cur && cur !== document.documentElement) {
      const c = parse(getComputedStyle(cur).backgroundColor);
      if (c && c.a > 0) { acc = acc ? blend(acc, c) : c; if (acc.a >= 0.999) return acc; }
      cur = cur.parentElement;
    }
    return acc || { r:255, g:255, b:255, a:1 };
  };
  const out = [];
  const scope = document.querySelector('#__g') || document;
  scope.querySelectorAll('*').forEach(el => {
    // SVG-n belul a fill nem CSS hatter — a meres ott ertelmetlen
    if (el.closest && el.closest('svg')) return;
    const txt = [...el.childNodes].filter(n => n.nodeType === 3).map(n => n.textContent.trim()).join(' ').trim();
    if (!txt || txt.length > 40) return;
    const r = el.getBoundingClientRect();
    if (r.width < 4 || r.height < 4 || r.bottom < 0 || r.top > 2000) return;
    const cs = getComputedStyle(el);
    if (cs.visibility === 'hidden' || cs.opacity === '0') return;
    const fg = parse(cs.color); if (!fg) return;
    const bg = effBg(el);
    const f = fg.a < 1 ? blend(fg, bg) : fg;
    const L1 = lum(f.r, f.g, f.b), L2 = lum(bg.r, bg.g, bg.b);
    const ratio = (Math.max(L1, L2) + 0.05) / (Math.min(L1, L2) + 0.05);
    out.push({ txt, ratio: +ratio.toFixed(2), size: Math.round(parseFloat(cs.fontSize)),
               fg: cs.color, bg: `rgb(${Math.round(bg.r)},${Math.round(bg.g)},${Math.round(bg.b)})` });
  });
  return out.sort((a, b) => a.ratio - b.ratio);
};

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // a Beallitasokban valaszthato mind az ot tema
  for (const theme of ['warm', 'ice', 'jade', 'dark', 'slate']) {
    console.log(`\n===== ${theme.toUpperCase()} =====`);
    CURRENT_MINT = MINT[theme];
    const p = await b.newPage({ viewport: { width: 390, height: 900 } });
    const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(seed(theme));
    await p.goto(BASE + '?screen=liga', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(4200);

    const rows = await p.evaluate(MEASURE);
    const low  = rows.filter(x => x.ratio < FLOOR);
    const unreadable = low.filter(x => !known(x));
    const accepted   = low.filter(x =>  known(x));
    const weak = rows.filter(x => x.ratio >= FLOOR && x.ratio < WCAG);

    ok(`nincs olvashatatlan szöveg (kontraszt < ${FLOOR})`, unreadable.length === 0,
       unreadable.map(x => `"${x.txt}" ${x.ratio} (${x.fg} / ${x.bg})`).join(' | ') || 'egy sem');
    if (accepted.length) console.log(`         (vállalt: ${[...new Set(accepted.map(x => known(x).why))].join('; ')})`);
    if (weak.length) console.log(`         (${weak.length} db a WCAG 4.5 alatt, de olvasható: ${weak.slice(0,4).map(x => `"${x.txt}" ${x.ratio}`).join(', ')}…)`);
    ok('nincs JS hiba', errs.filter(e => !/ServiceWorker/.test(e)).length === 0, errs.join(' | '));
    await p.close();
  }

  // ── A Jatekmenet oldal: itt a tartalom a HATTEREN ul, nem feher kartyan ──
  // A v10.161-ben a doboz kivetele pont ezt torte el: ami feher lapon meg
  // olvashato volt (3.1), a homokszinen 1.93 lett. Az ilyen atrendezes barmikor
  // visszahozhatja, ezert kulon merjuk.
  console.log('\n===== JÁTÉKMENET OLDAL (tartalom a háttéren) =====');
  for (const theme of ['warm', 'jade', 'dark', 'slate']) {
    CURRENT_MINT = MINT[theme];
    const p3 = await b.newPage({ viewport: { width: 390, height: 1400 } });
    await p3.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p3.addInitScript(stub); await p3.addInitScript(seed(theme));
    await p3.goto(BASE, { waitUntil: 'domcontentloaded' });
    await p3.waitForTimeout(3600);
    await p3.evaluate(() => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__g';
      root.style.cssText = 'position:fixed;inset:0;z-index:99999;display:flex;flex-direction:column;background:var(--app-bg)';
      document.body.appendChild(root);
      function H() {
        const [m, sm] = React.useState({ modes:['points'], difficulty:'easy', observerAllowed:true });
        return React.createElement(SetupScreen, { go: () => {},
          players: [{ id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a' }],
          selectedGames: ['zene','erem'], gameMeta: m, setGameMeta: sm });
      }
      ReactDOM.createRoot(root).render(React.createElement(H));
    });
    await p3.waitForTimeout(1600);
    const rows3 = (await p3.evaluate(MEASURE)).filter(x => x.ratio < FLOOR && !known(x));
    ok(`${theme}: nincs olvashatatlan szöveg`, rows3.length === 0,
       rows3.map(x => `"${x.txt}" ${x.ratio} (${x.fg} / ${x.bg})`).join(' | ') || 'egy sem');
    await p3.close();
  }

  // ── A konkret hiba, ami ezt kivaltotta: T.ink hatteren SOHA ne legyen
  //    hardcode-olt feher szoveg — az onInk() a temahoz igazodik.
  console.log('\n===== A KIVALTO MINTA =====');
  const src = fs.readFileSync('/home/user/bottle-of-heroes/app.src.html', 'utf8');
  const offenders = src.split('\n')
    .map((l, i) => ({ l, i: i + 1 }))
    .filter(({ l }) => /background:\s*[^;]*\bT\.ink\b/.test(l) && /color:\s*(?:[^,;]*\?\s*)?'#fff'/.test(l));
  ok("nincs `background:T.ink` + hardcode `color:'#fff'` páros", offenders.length === 0,
     offenders.map(o => ':' + o.i).join(' ') || 'egy sem');

  const p2 = await b.newPage();
  await p2.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p2.addInitScript(stub); await p2.addInitScript(seed('dark'));
  await p2.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p2.waitForTimeout(3600);
  const oi = await p2.evaluate(() => {
    const before = window.T && window.T.ink;
    return { helper: typeof onInk === 'function', dark: typeof onInk === 'function' ? onInk() : null, ink: before };
  }).catch(() => ({ helper: false }));
  ok('az onInk() létezik', oi.helper === true, JSON.stringify(oi));
  ok('sötét témában NEM fehéret ad', oi.dark !== '#fff' && oi.dark != null, `onInk()=${oi.dark} (T.ink=${oi.ink})`);
  await p2.close();

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
