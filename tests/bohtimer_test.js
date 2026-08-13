// v10.329 — BohTimer: a KÖZÖS vízszintes visszaszámláló (három variáns)
//
// Amit őriz:
//   1. mindhárom variáns UGYANAZON a magasságon áll (BOH_TIMER_H = 30) — ez a
//      lényeg: a mai gyűrűk 148–200 px-et esznek a játék tartalma elől;
//   2. a három fokozat színe FIX, NEM témafüggő. Ez nem esztétika: a `T.mint`
//      a téma AKCENTUSA (barackban #E06030), a `T.coral` pedig #F08060 — vagyis
//      témából származtatva a VÉSZJELZÉS világosabb lenne, mint a nyugalmi
//      állapot. Ugyanaz a szabály, mint a Szűrés nehézség-kártyáinál.
//   3. a küszöbök: fél idő alatt borostyán, az utolsó negyedben (de legfeljebb
//      5 mp-nél) piros;
//   4. a kiírt szám 10 mp alatt tizedes, fölötte egész.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

async function open(b, theme) {
  const p = await b.newPage({ viewport: { width: 402, height: 900 } });
  p.__errs = [];
  p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_theme','${theme}');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  return p;
}

const mount = (p, items) => p.evaluate((its) => {
  const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
  let root = document.getElementById('__p');
  if (root) root.remove();
  root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:9;overflow:auto;padding:12px';
  document.body.appendChild(root);
  ReactDOM.createRoot(root).render(React.createElement('div', {},
    its.map((it, i) => React.createElement('div', { key:i, style:{ marginBottom:10 } },
      React.createElement(BohTimer, it)))));
}, items);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. küszöbök és felirat (böngésző nélkül is kiértékelhető függvények) ──
  console.log('\n===== 1. KUSZOBOK ES FELIRAT =====');
  let p = await open(b, 'peach');
  const logic = await p.evaluate(() => {
    const k = (t, l) => bohTimerTone(t, l).key;
    return {
      keys30: [k(30,30), k(30,20), k(30,15), k(30,6), k(30,4), k(30,0)],
      // 60 mp-es kornel a negyed 15 mp lenne — a plafon 5 mp
      warn60: [k(60,20), k(60,10), k(60,6), k(60,4)],
      labels: [bohTimerLabel(30), bohTimerLabel(10), bohTimerLabel(9.94), bohTimerLabel(0)],
      tones: BOH_TIMER_TONES, H: BOH_TIMER_H,
    };
  });
  ok(logic.keys30.join(',') === 'ok,ok,mid,mid,warn,done',
     '30 mp: felette ok → fél idő alatt mid → utolsó negyedben warn', logic.keys30.join(','));
  ok(logic.warn60.join(',') === 'mid,mid,mid,warn',
     '60 mp: a riasztás 5 mp-nél kapcsol, nem 15-nél', logic.warn60.join(','));
  ok(logic.labels.join(',') === '30,10,9.9,0.0',
     '10 mp alatt tizedes, fölötte egész', logic.labels.join(','));

  // ── 2. a fokozat-színek FIXEK, nem témafüggők ──
  console.log('\n===== 2. A SZINEK FIXEK =====');
  const peachT = await p.evaluate(() => ({ tones: BOH_TIMER_TONES, mint: T.mint, coral: T.coral }));
  await p.close();
  p = await open(b, 'ice');
  const iceT = await p.evaluate(() => ({ tones: BOH_TIMER_TONES, mint: T.mint, coral: T.coral }));
  ok(JSON.stringify(peachT.tones) === JSON.stringify(iceT.tones),
     'a három fokozat színe témától FÜGGETLEN', JSON.stringify(iceT.tones));
  ok(peachT.mint !== iceT.mint, 'a téma akcentusa viszont TÉNYLEG változik (kontroll)',
     peachT.mint + ' vs ' + iceT.mint);
  // a temabol szarmaztatva a veszjelzes vilagosabb lenne, mint a nyugalom —
  // ezt a csapdat rogziti ez a sor
  const lum = h => { const n = parseInt(h.slice(1), 16); return ((n>>16&255)*0.299 + (n>>8&255)*0.587 + (n&255)*0.114); };
  ok(lum(peachT.coral) > lum(peachT.mint),
     'kontroll: barack témában a T.coral VILÁGOSABB a T.mint-nél — ezért nem témából jön a szín',
     Math.round(lum(peachT.coral)) + ' > ' + Math.round(lum(peachT.mint)));
  ok(lum(iceT.tones.warn) < lum(iceT.tones.ok),
     'a vészjelzés SÖTÉTEBB/erősebb, mint a nyugalmi állapot',
     Math.round(lum(iceT.tones.warn)) + ' < ' + Math.round(lum(iceT.tones.ok)));

  // ── 3. mindhárom variáns EGY magasságon ──
  console.log('\n===== 3. HELYFOGLALAS =====');
  await mount(p, [
    { variant:'bar', total:30, left:17, label:'Kör' },
    { variant:'ticks', total:30, left:17 },
    { variant:'pill', total:30, left:17 },
  ]);
  await p.waitForTimeout(700);
  const geo = await p.evaluate(() => [...document.querySelectorAll('#__p [role="timer"]')]
    .map(x => ({ h: Math.round(x.getBoundingClientRect().height), w: Math.round(x.getBoundingClientRect().width),
                 aria: x.getAttribute('aria-label') })));
  ok(geo.length === 3, 'mindhárom variáns renderel', geo.length);
  ok(geo.every(g => g.h === logic.H), `mindhárom pontosan ${logic.H} px magas`, JSON.stringify(geo.map(g => g.h)));
  ok(geo[0].w > 300 && geo[1].w > 300, 'a sáv és a pöttyök teljes szélességet töltenek', geo[0].w + ' / ' + geo[1].w);
  ok(geo[2].w < 160, 'a pirula csak akkora, amekkora kell', geo[2].w);
  ok(geo.every(g => /Hátralévő idő/.test(g.aria || '')), 'mindhárom visz aria-label-t');

  // ── 4. a SÁV: a letelt ido no, es van „necces" zona a jobb vegen ──
  // A regi valtozat a HATRALEVO idot rajzolta, ami balra fogyott — oda nem
  // lehetett zonat tenni (a szam-csip alá esett volna).
  console.log('\n===== 4. A SAV: LETELT IDO + NECCES ZONA =====');
  await mount(p, [
    { variant:'bar', total:30, left:30 },   // induláskor: semmi nem telt el
    { variant:'bar', total:30, left:15 },   // félidő
    { variant:'bar', total:30, left:0 },    // lejárt: a sáv tele
  ]);
  await p.waitForTimeout(700);
  const bar = await p.evaluate(() => {
    const tracks = [...document.querySelectorAll('#__p [role="timer"]')];
    return tracks.map(tr => {
      const w = tr.getBoundingClientRect().width;
      const kids = [...tr.children];
      // a kitoltes az egyetlen gyerek, aminek TOMOR hattere van (a zona csikos)
      const fillEl = kids.find(k => /^rgb\(/.test(getComputedStyle(k).backgroundColor) && getComputedStyle(k).backgroundImage === 'none' && k.getAttribute('aria-hidden') === null);
      const zone = kids.find(k => getComputedStyle(k).backgroundImage.includes('gradient'));
      return { fill: fillEl ? Math.round(fillEl.getBoundingClientRect().width / w * 100) : null,
               zone: zone ? Math.round(zone.getBoundingClientRect().width / w * 100) : null,
               zoneRight: zone ? Math.round(tr.getBoundingClientRect().right - zone.getBoundingClientRect().right) : null };
    });
  });
  ok(bar[0].fill === 0, 'induláskor a sáv ÜRES (semmi nem telt el)', bar[0].fill + '%');
  ok(bar[1].fill === 50, 'félidőben félig telt', bar[1].fill + '%');
  ok(bar[2].fill === 100, 'lejártkor teljesen telt — beért a végére', bar[2].fill + '%');
  ok(bar.every(x => x.zone === 17), 'a „necces" zóna 30 mp-nél a sáv 1/6-a (5 mp)', bar.map(x => x.zone + '%').join(','));
  ok(bar.every(x => x.zoneRight === 0), 'a zóna a sáv JOBB végén van', JSON.stringify(bar.map(x => x.zoneRight)));

  // rovid kornel a zona nem viheti el az egesz savot
  await mount(p, [{ variant:'bar', total:10, left:10 }, { variant:'bar', total:60, left:60 }]);
  await p.waitForTimeout(600);
  const zones = await p.evaluate(() => [...document.querySelectorAll('#__p [role="timer"]')].map(tr => {
    const w = tr.getBoundingClientRect().width;
    const z = [...tr.children].find(k => getComputedStyle(k).backgroundImage.includes('gradient'));
    return z ? Math.round(z.getBoundingClientRect().width / w * 100) : null;
  }));
  // A zona szelessege = a piros kuszob: min(25%, 5/total).
  ok(zones[0] === 25, '20 mp-ig a zóna a sáv negyede (a küszöb ott a negyed)', zones[0] + '%');
  ok(zones[1] === 8, '60 mp-nél arányosan keskenyebb (5 mp = 1/12)', zones[1] + '%');
  // …es a zona PONTOSAN ott kezdodik, ahol a szam is pirosra valt
  const sync = await p.evaluate(() => {
    const at = t => { const w = Math.min(t * 0.25, 5); return { frac: w / t, warnAt: w }; };
    return [10, 30, 60].map(t => ({ t, ...at(t), key: bohTimerTone(t, at(t).warnAt).key }));
  });
  ok(sync.every(x => x.key === 'warn'),
     'a zóna kezdetén a szám MÁR piros — a két küszöb ugyanaz', JSON.stringify(sync.map(x => x.t + 'mp:' + x.key)));

  ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
  await p.close();

  // ── A BEKOTOTT JATEKOK (v10.358) ──
  // A `BohTimer` v10.329 ota kesz volt, de sokaig csak KET helyen ment. Ez a
  // blokk azt orzi, hogy a tobbi jatek se essen vissza sajat gyurure.
  // ⚠️ A PlayScreen fejlec-gyuruje NEM idozito, hanem a KOR-szamlalo — azt a
  // `#__p [role="timer"]` szelektor nem is talalja meg.
  console.log('\n===== A BEKOTOTT JATEKOK =====');
  for (const [gid, label] of [['csakegyszó','Csak Egy Szó'], ['ritmus','Ritmus'], ['tabu','Tabu']]) {
    const p = await b.newPage({ viewport: { width: 402, height: 900 } });
    const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3200);
    await p.evaluate((g) => {
      const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
      const root = document.createElement('div'); root.id = '__p';
      root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column;overflow:auto';
      document.body.appendChild(root);
      const PL = [{ id:'a', name:'Sere', color:'#E07A5F', points:0, drinks:0 },
                  { id:'b', name:'Luca', color:'#4FC2A0', points:0, drinks:0 },
                  { id:'c', name:'Vivi', color:'#A78BFA', points:0, drinks:0 }];
      function H(){ const [ps,setPs]=React.useState(PL);
        return React.createElement(PlayScreen, { go:()=>{}, players:ps, setPlayers:setPs,
          selectedGames:[g], roomCode:null, gameMeta:{modes:['points'],difficulty:'easy'},
          setGameMeta:()=>{}, setScoreHistory:()=>{}, setLastGameRound:()=>{} }); }
      ReactDOM.createRoot(root).render(React.createElement(H));
    }, gid);
    await p.waitForTimeout(2200);
    for (let i = 0; i < 4; i++) {
      if (await p.evaluate(() => !!document.querySelector('#__p [role="timer"]'))) break;
      await p.evaluate(() => {
        const b2 = [...document.querySelectorAll('#__p button')]
          .find(x => /Kezd|Indít|Start|Mehet|Felfed|Megvan|Tovább|Rajta/i.test(x.textContent||''));
        b2 && b2.click();
      });
      await p.waitForTimeout(1100);
    }
    const m = await p.evaluate(() => {
      const t = document.querySelector('#__p [role="timer"]');
      // a jatek TORZSEBEN nem maradhat gyuru-idozito (`stroke-dasharray`-es kor)
      const rings = [...document.querySelectorAll('#__p svg circle')]
        .filter(c => c.getAttribute('stroke-dasharray')).length;
      return { has: !!t, h: t ? Math.round(t.getBoundingClientRect().height) : null,
               w: t ? Math.round(t.getBoundingClientRect().width) : null, rings };
    });
    ok(m.has, label + ': a KÖZÖS BohTimer-t használja');
    ok(m.h === 30, label + ': 30 px magas (BOH_TIMER_H)', m.h + ' px');
    ok(m.w > 200, label + ': vízszintes, széles', m.w + ' px');
    ok(m.rings === 0, label + ': nem maradt saját gyűrű-időzítő', m.rings);
    ok(errs.length === 0, label + ': nincs JS hiba', errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
