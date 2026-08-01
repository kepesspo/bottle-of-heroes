// v10.262 — Result Banner: világos kártya, állapotcsíkkal
//
// Amit ellenőriz:
//   1. a kártya MINDIG 300 px magas (1 fő / vegyes / csapat — mindegy)
//   2. a csík: zöld / piros / félig-félig / palaszürke (döntetlen)
//   3. 1 fő → név nagyban; 2+ fő → avatarok + a névsor a sor ALATT
//   4. a szám (pont/korty) mindkét formában UGYANABBAN a jobb oldali oszlopban
//   5. a jegyzet nem ismétli a metrikát („+1 pont" kikerül)
//   6. wildcard-jelvény a csíkon, középen
//   7. a kicsi sáv 56 px, ugyanolyan széles mint a kártya, és CSAK az ivó oldalt mutatja
//   8. a profilkép-elemek nem épülnek újra rerendernél (ez volt az „ugráló avatar")
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

const AV = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';
const P = n => ({ id:n.toLowerCase(), name:n, color:'#5BA0DB', img:AV, points:0, drinks:0 });

// A bannert a PlayScreen belsejebol nehez elerni; a jatek-eredmenyt viszont a
// PlayScreen sajat onResult-jan keresztul lehet kivaltani. Ezert a PlayScreen-t
// mountoljuk, es egy segedgombbal hivjuk meg az onResult-ot.
const show = (p, res) => p.evaluate(r => { window.__setRes(r); }, res);

const readCard = p => p.evaluate(() => {
  const root = document.getElementById('__pl');
  const card = [...root.querySelectorAll('div')].find(d =>
    d.style && d.style.height === '300px' && d.style.borderRadius === '22px');
  if (!card) return null;
  const r = card.getBoundingClientRect();
  const stripe = card.children[0];
  const seg = [...stripe.children].map(s => getComputedStyle(s).backgroundColor);
  const rows = [...card.querySelectorAll(':scope > div')][1];
  const rowEls = rows ? [...rows.children] : [];
  const metrics = [...card.querySelectorAll('div')].filter(d => d.style && d.style.minWidth === '52px');
  return {
    h: Math.round(r.height), w: Math.round(r.width),
    stripe: seg,
    rows: rowEls.length,
    rowText: rowEls.map(e => (e.innerText || '').replace(/\s+/g, ' ').trim()),
    metricRights: metrics.map(m => Math.round(r.right - m.getBoundingClientRect().right)),
    text: (card.innerText || '').replace(/\s+/g, ' ').trim(),
    imgs: card.querySelectorAll('img').length,
    // A CSS a "0"-t "0px"-re normalizalja, ezert a borderRadius-ra szurni
    // torekeny — a jelvenyt a pozicioja azonositja (a csik kozepen ul).
    wc: (() => { const b = [...card.querySelectorAll('div')].find(d => d.style &&
                   d.style.position === 'absolute' && d.style.top === '0px' && d.style.left === '50%');
                 return b ? { txt: (b.innerText||'').trim(), left: Math.round(b.getBoundingClientRect().left - r.left),
                              w: Math.round(b.getBoundingClientRect().width) } : null; })(),
  };
});

const readMini = p => p.evaluate(() => {
  const root = document.getElementById('__pl');
  const bar = [...root.querySelectorAll('div')].find(d =>
    d.style && d.style.position === 'fixed' && /translateX\(-50%\)/.test(d.style.transform || '') && d.style.zIndex === '45');
  if (!bar) return null;
  const inner = bar.firstElementChild;
  const r = inner.getBoundingClientRect();
  return { h: Math.round(r.height), w: Math.round(r.width),
           text: (inner.innerText || '').replace(/\s+/g, ' ').trim(),
           imgs: inner.querySelectorAll('img').length };
});

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 874 } });
  const errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // A bannert a PlayScreen sajat onResult-jan keresztul valtjuk ki: a
  // GameContent helyere egy stub megy, ami kivezeti az onResult-ot.
  const mount = async (players, res) => {
    await p.evaluate(({ pl, r }) => {
      // A REGI FAT LE KELL SZERELNI: ha csak a DOM-csomopontot vesszuk ki, a regi
      // PlayScreen tovabb el (idozitoi ujrarajzoljak), es a stub effektje
      // visszairja a SAJAT onResult-jat a window.__fire-be — a kesobbi
      // eredmenyek igy egy lecsatolt fara mennenek, es semmi nem latszana.
      if (window.__root) { try { window.__root.unmount(); } catch (e) {} }
      const old = document.getElementById('__pl'); if (old) old.remove();
      const root = document.createElement('div');
      root.id = '__pl';
      root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;z-index:9;background:' + T.bg;
      document.body.appendChild(root);
      window.__root = ReactDOM.createRoot(root);
      function Harness() {
        const [n, setN] = React.useState(0);
        window.__rerender = () => setN(x => x + 1);
        return React.createElement(PlayScreen, {
          players: pl, setPlayers: () => {}, selectedGames: ['reakcio'], go: () => {}, roomCode: null,
          gameMeta: { modes:['points'], difficulty:'easy', observerAllowed:true },
          setGameMeta: () => {}, setLastGameRound: () => {}, setScoreHistory: () => {},
          __forceResult: r,
        });
      }
      window.__root.render(React.createElement(Harness));
    }, { pl: players, r: res });
    await p.waitForTimeout(700);
  };

  // A PlayScreen nem fogad __forceResult propot — helyette a jatekbol jovo
  // onResult-ot utanozzuk: a PlayScreen-en belul a GameContent hivja meg.
  // Ezert a GameContent-et csereljuk le egy stubra, ami mountkor tuzel.
  await p.evaluate(() => {
    window.__realGameContent = GameContent;
    window.GameContent = function StubGame(props) {
      React.useEffect(() => { window.__fire = props.onResult; }, [props.onResult]);
      return null;
    };
  });

  const fire = async (players, res) => {
    await mount(players, null);
    await p.evaluate(r => window.__fire(r), res);
    await p.waitForTimeout(600);
  };

  const A = P('Sere'), Bp = P('Luca'), C = P('Kecsi'), D = P('Tóth'), E = P('Anna'), F = P('Peti');

  console.log('\n===== 1. FIX MAGASSÁG =====');
  const cases = [
    ['vegyes 1↔1', [A, Bp], { winners:[A], losers:[Bp], drinks:2, winNote:'+1 pont · 347 ms', loseNote:'381 ms' }],
    ['csak nyertes', [A, Bp], { winners:[A], drinks:0, winNote:'+1 pont' }],
    ['csak iszik', [A, Bp], { losers:[Bp], drinks:1, loseNote:'A kerék őt választotta' }],
    ['csapat 3↔3', [A, Bp, C, D, E, F], { winners:[A, C, E], losers:[Bp, D, F], drinks:3, winNote:'+1 pont', loseNote:'Lebuktak' }],
  ];
  const seen = [];
  for (const [name, pls, res] of cases) {
    await fire(pls, res);
    const c = await readCard(p);
    ok(c && c.h === 300, `${name}: a kártya 300 px magas`, c && c.h + ' px');
    if (c) seen.push(c.h);
  }
  ok(new Set(seen).size === 1, 'mind a négy eset PONTOSAN ugyanakkora', JSON.stringify(seen));

  console.log('\n===== 2. AZ ÁLLAPOTCSÍK =====');
  await fire([A, Bp], { winners:[A], losers:[Bp], drinks:2 });
  let c = await readCard(p);
  ok(c.stripe.length === 2, 'vegyes körnél a csík KÉT szegmens', JSON.stringify(c.stripe));
  ok(/46, 154, 112/.test(c.stripe[0]) && /208, 87, 76/.test(c.stripe[1]),
     'bal fele zöld, jobb fele piros', c.stripe.join(' | '));
  await fire([A], { winners:[A], drinks:0 });
  c = await readCard(p);
  ok(c.stripe.length === 1 && /46, 154, 112/.test(c.stripe[0]), 'csak nyertes → egy zöld csík', c.stripe[0]);
  await fire([A, Bp], { losers:[A, Bp], drinks:1, draw:true });
  c = await readCard(p);
  ok(c.stripe.length === 1 && /110, 124, 147/.test(c.stripe[0]), 'döntetlen → palaszürke csík', c.stripe[0]);
  ok(/DÖNTETLEN/i.test(c.text), 'és a felirat is „Döntetlen"');

  console.log('\n===== 3. EGY FŐ vs. TÖBB FŐ =====');
  await fire([A, Bp], { winners:[A], losers:[Bp], drinks:2 });
  c = await readCard(p);
  ok(/NYERTES Sere/i.test(c.rowText[0]), '1 főnél a név a soron belül, nagyban', c.rowText[0]);
  await fire([A, Bp, C, D], { winners:[A, C], losers:[Bp, D], drinks:2 });
  c = await readCard(p);
  ok(/NYERTESEK/i.test(c.rowText[0]) && /Sere · Kecsi/.test(c.rowText[0]),
     '2+ főnél a névsor a felirat ALATT, ponttal elválasztva', c.rowText[0]);
  ok(c.imgs === 4, 'minden résztvevő avatarja ott van', c.imgs + ' kép');

  console.log('\n===== 4. A SZÁM MINDIG UGYANOTT =====');
  await fire([A, Bp, C, D], { winners:[A], losers:[Bp, C, D], drinks:3 });
  c = await readCard(p);
  ok(/NYERTES Sere/i.test(c.rowText[0]) && /ISZNAK/i.test(c.rowText[1]),
     'vegyes: a felső sor egyszerű, az alsó több fős', JSON.stringify(c.rowText));
  ok(c.metricRights.length === 2 && c.metricRights[0] === c.metricRights[1],
     'a két szám AZONOS távolságra van a jobb széltől', JSON.stringify(c.metricRights));

  console.log('\n===== 5. A JEGYZET NEM ISMÉTEL =====');
  await fire([A, Bp], { winners:[A], losers:[Bp], drinks:2, winNote:'+1 pont · 347 ms', loseNote:'381 ms' });
  c = await readCard(p);
  ok(/347 ms · 381 ms/.test(c.text), 'a jegyzetben ott az új információ', c.text.slice(-40));
  ok((c.text.match(/\+1 pont/g) || []).length === 0, 'de a „+1 pont" nem ismétlődik a jegyzetben');
  ok(/\+1 PONT/.test(c.text), 'a metrikában viszont ott van');

  console.log('\n===== 6. WILDCARD-JELVÉNY =====');
  // A PlayScreen onResult-ja a SAJAT aktiv wildcardjat irja a gameResult.effect-be,
  // tehat kivulrol nem lehet befecskendezni — valodi wildcardot kell inditani.
  // A konfigbol nem lehet 1 percnel rovidebbre venni, ezert az egy darab
  // 60 000 ms-os idozitot rovidre zarjuk (mas idozito nem hasznal pont ennyit).
  await p.evaluate(() => {
    window.__WC = WILDCARDS.slice();
    WILDCARDS.length = 0;
    WILDCARDS.push(window.__WC.find(w => w.effect === 'double'));
    const orig = window.setTimeout;
    window.__origTimeout = orig;
    window.setTimeout = (fn, ms) => orig(fn, ms === 60000 ? 100 : ms);
  });
  await p.evaluate(({ pl }) => {
    if (window.__root) { try { window.__root.unmount(); } catch (e) {} }
    const old = document.getElementById('__pl'); if (old) old.remove();
    const root = document.createElement('div');
    root.id = '__pl';
    root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;z-index:9;background:' + T.bg;
    document.body.appendChild(root);
    window.__root = ReactDOM.createRoot(root);
    window.__root.render(React.createElement(PlayScreen, {
      players: pl, setPlayers: () => {}, selectedGames: ['reakcio'], go: () => {}, roomCode: null,
      gameMeta: { modes:['points','wildcard'], difficulty:'easy', wildcardMin:1, wildcardMax:1, observerAllowed:true },
      setGameMeta: () => {}, setLastGameRound: () => {}, setScoreHistory: () => {},
    }));
  }, { pl: [A, Bp] });
  await p.waitForTimeout(1500);
  await p.evaluate(r => window.__fire(r), { winners:[A], losers:[Bp], drinks:2 });
  await p.waitForTimeout(600);
  c = await readCard(p);
  ok(c.wc !== null, 'megjelenik a wildcard-jelvény', c.wc && c.wc.txt);
  const mid = c.wc ? Math.abs((c.wc.left + c.wc.w / 2) - c.w / 2) : 99;
  ok(mid <= 1, 'és pontosan középen áll a csíkon', 'eltérés a középtől: ' + mid + ' px');

  await p.evaluate(() => { WILDCARDS.length = 0; window.__WC.forEach(w => WILDCARDS.push(w));
                           window.setTimeout = window.__origTimeout; });

  console.log('\n===== 7. A KICSI SÁV =====');
  await fire([A, Bp, C, D], { winners:[A], losers:[Bp, C, D], drinks:3, winNote:'+1 pont' });
  const cardW = (await readCard(p)).w;
  await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const banner = [...root.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250');
    banner.click();
  });
  await p.waitForTimeout(1200);
  const m = await readMini(p);
  ok(m !== null, 'lekicsinyítve megjelenik a sáv');
  ok(m.h === 56, 'a sáv 56 px magas', m.h + ' px');
  ok(m.w === cardW, 'és ugyanolyan széles, mint a kártya', m.w + ' vs ' + cardW + ' px');
  ok(/3 fő/.test(m.text) && /3 KORTY/.test(m.text), 'csak az ivó oldal + a korty látszik', m.text);
  ok(!/Sere/.test(m.text), 'a győztes NEM szerepel rajta', m.text);
  ok(m.imgs === 2, 'két avatar látszik a sávon', m.imgs + ' kép');

  console.log('\n===== 8. NEM UGRÁL A PROFILKÉP =====');
  await fire([A, Bp], { winners:[A], losers:[Bp], drinks:2 });
  const before = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    window.__imgs = [...root.querySelectorAll('img')];
    return window.__imgs.length;
  });
  await p.evaluate(() => window.__rerender && window.__rerender());
  await p.waitForTimeout(400);
  const same = await p.evaluate(() => {
    const root = document.getElementById('__pl');
    const now = [...root.querySelectorAll('img')];
    return now.length === window.__imgs.length && now.every((el, i) => el === window.__imgs[i]);
  });
  ok(before > 0, 'vannak profilképek a bannerben', before + ' kép');
  ok(same, 'újrarajzoláskor UGYANAZOK az <img> elemek maradnak (nincs remount)');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
