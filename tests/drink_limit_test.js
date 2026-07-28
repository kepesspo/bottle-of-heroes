// v10.144 — Korty-limit: kör végi popup + tartós 💧 a név mellett
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';

const seed = `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  // Anna limitje 3 korty, Belanak nincs limitje
  window.__fbStore['profiles'] = {
    p_a:{ name:'Anna', color:'#5BA0DB', drinkLimit:3 },
    p_b:{ name:'Bela', color:'#E07A5F' },
  };
  window.__fbStore['stats'] = {};
  window.__fbStore['game_stats'] = {};
  window.__fbStore['statEvents'] = {};
  window.__fbStore['gameStatEvents'] = {};
  window.__fbStore['seasons'] = {};
  window.__fbStore['config'] = {};
`;

// PlayScreen kozvetlen mountolasa — a bulit nem kell vegigkattintani
const mount = (drinksAnna) => `
  const root = document.createElement('div'); root.id='__ps';
  root.style.cssText='position:fixed;inset:0;background:#F5D89B;overflow:auto;z-index:99999';
  document.body.appendChild(root);
  window.__players = [
    { id:'a', name:'Anna', color:'#5BA0DB', points:2, drinks:${drinksAnna}, profileId:'p_a' },
    { id:'b', name:'Bela', color:'#E07A5F', points:1, drinks:9, profileId:'p_b' },
  ];
  function Harness() {
    const [players, setPlayers] = React.useState(window.__players);
    React.useEffect(() => { window.__setPlayers = setPlayers; window.__players = players; }, [players]);
    return React.createElement(window.PlayScreen, {
      players, setPlayers, selectedGames:['kopapir'], go:()=>{}, roomCode:null,
      gameMeta:{ modes:['points','drinks'] },
      setGameMeta:()=>{}, setLastGameRound:()=>{}, setScoreHistory:()=>{},
    });
  }
  ReactDOM.createRoot(root).render(React.createElement(Harness));
`;

async function play(b, drinksAnna) {
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);
  await p.evaluate(mount(drinksAnna));
  await p.waitForTimeout(4200); // a kör-popup elhaladjon
  p.__errs = errs;
  return p;
}
const popup = (p) => p.evaluate(() => {
  const d = Array.from(document.querySelectorAll('div')).find(x => /VÍZSZÜNET/i.test(x.innerText || '') && x.style.borderRadius === '24px');
  return d ? d.innerText.replace(/\n/g, ' | ') : null;
});
const pillText = (p) => p.evaluate(() => {
  const el = document.querySelector('#__ps .play-footer-inner');
  return el ? el.innerText.replace(/\n/g, ' | ') : null;
});

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── Limit alatt: semmi ──
  console.log('===== LIMIT ALATT =====');
  let p = await play(b, 1);
  ok('nincs popup', (await popup(p)) === null);
  ok('nincs 💧 a pillben', !/💧/.test((await pillText(p)) || ''), await pillText(p));
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.close();

  // ── Limit elerve: NEM azonnal, hanem a kor vegen ──
  console.log('\n===== LIMIT ELERVE =====');
  p = await play(b, 3);
  ok('a popup NEM ugrik fel azonnal (jatek kozben)', (await popup(p)) === null, await popup(p));
  ok('viszont a 💧 mar ott van a pillben', /Anna 💧/.test((await pillText(p)) || ''), await pillText(p));

  // A kort a JATEK vegigjatszasa lepteti: kattintunk, amig a Kövi aktiv nem lesz
  const advanceRound = async () => {
    for (let i = 0; i < 14; i++) {
      const done = await p.evaluate(() => {
        const k = Array.from(document.querySelectorAll('#__ps button')).find(x => /Kövi/.test(x.innerText || ''));
        return !!(k && !k.disabled);
      });
      if (done) break;
      await p.evaluate(() => {
        const btns = Array.from(document.querySelectorAll('#__ps button'));
        const b2 = btns.find(x => /Senki sem iszik/.test(x.innerText || '') && !x.disabled);
        if (b2) b2.click();
      });
      await p.waitForTimeout(450);
    }
    await p.evaluate(() => {
      const k = Array.from(document.querySelectorAll('#__ps button')).find(x => /Kövi/.test(x.innerText || ''));
      if (k && !k.disabled) k.click();
    });
    // a "N. Kör" atvezeto ~2 mp-ig el — a vizszunet csak utana johet
    await p.waitForTimeout(3400);
  };
  await advanceRound();
  const pop = await popup(p);
  ok('a kor vegen FELUGRIK a vizszunet-popup', !!pop, pop);
  ok('a nevet es a limitet is kiirja', pop && /Anna/.test(pop) && /3 kortyos limitjét/.test(pop), pop);
  ok('jelzi, hogy a 💧 ott marad', pop && /ott marad a 💧/.test(pop), pop);
  const geo = await p.evaluate(() => {
    const d = Array.from(document.querySelectorAll('div')).find(x => /VÍZSZÜNET/i.test(x.innerText || '') && x.style.borderRadius === '24px');
    if (!d) return null;
    const r = d.getBoundingClientRect();
    return { w: Math.round(r.width), h: Math.round(r.height), centered: Math.abs((r.left + r.right) / 2 - 195) < 3 };
  });
  ok('kozepre igazitott, nem log ki', geo && geo.centered && geo.w <= 358, JSON.stringify(geo));

  // koppintasra bezarhato
  await p.evaluate(() => {
    const d = Array.from(document.querySelectorAll('div')).find(x => /VÍZSZÜNET/i.test(x.innerText || '') && x.style.zIndex === '9991');
    if (d) d.click();
  });
  await p.waitForTimeout(400);
  ok('koppintasra bezarhato', (await popup(p)) === null);
  ok('bezaras utan is ott a 💧', /Anna 💧/.test((await pillText(p)) || ''), await pillText(p));

  // ── Csak egyszer ugrik fel, de a 💧 marad ──
  await p.evaluate(() => {
    window.__setPlayers(ps => ps.map(x => x.id === 'a' ? { ...x, drinks: x.drinks + 5 } : x));
  });
  await p.waitForTimeout(600);
  await advanceRound();
  ok('tovabbi kortyoknel NEM ugrik fel ujra', (await popup(p)) === null, await popup(p));
  ok('de a 💧 tovabbra is ott van', /💧/.test((await pillText(p)) || ''), await pillText(p));

  // ── Az allas-listaban is ott a 💧, Belanal nincs ──
  await p.evaluate(() => {
    const b2 = Array.from(document.querySelectorAll('#__ps button')).find(x => /MENÜ/i.test(x.innerText || ''));
    if (b2) b2.click();
  });
  await p.waitForTimeout(900);
  const menu = await p.evaluate(() => document.body.innerText.replace(/\n/g, ' | '));
  ok('az allas-listaban Anna mellett ott a 💧', /Anna 💧/.test(menu), (menu.match(/Anna[^|]*/) || ['NINCS'])[0]);
  ok('Bela mellett NINCS (neki nincs limitje)', !/Bela 💧/.test(menu), (menu.match(/Bela[^|]*/) || ['NINCS'])[0]);
  ok('nincs JS hiba', p.__errs.filter(e => !/ServiceWorker/.test(e)).length === 0, p.__errs.join(' | '));
  await p.screenshot({ path: __dirname + '/drink_limit_menu.png', fullPage: true });
  await p.close();

  // ─── v10.166: a limit SZERKESZTESE az Admin > Tartalom > Profilok alatt ───
  // A limit a profilon el, ezert a Jatekmenet oldalrol kikerult (v10.165).
  // Egy helyen, egy gorgetessel kell tudni vegigmenni mindenkin — ha ez a
  // kartya eltunik, a limitet csak profilonkent kulon megnyitva lehetne allitani.
  console.log('\n===== TÖMEGES SZERKESZTŐ (Admin > Profilok) =====');
  {
    const p2 = await b.newPage({ viewport: { width: 390, height: 1000 } });
    const errs = []; p2.on('pageerror', e => errs.push(e.message));
    await p2.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p2.addInitScript(stub);
    await p2.addInitScript(seed);
    await p2.goto(BASE, { waitUntil: 'domcontentloaded' });
    await p2.waitForTimeout(3600);
    await p2.evaluate(() => {
      const r = document.getElementById('root'); if (r) r.style.display = 'none';
      const root = document.createElement('div'); root.id = '__ad';
      root.style.cssText = 'position:fixed;inset:0;display:flex;flex-direction:column;background:#EFC77A;overflow:auto';
      document.body.appendChild(root);
      ReactDOM.createRoot(root).render(React.createElement(window.AdminScreen,
        { go: () => {}, setTheme: () => {}, currentTheme: 'warm' }));
    });
    await p2.waitForTimeout(2200);
    const at = () => p2.evaluate(() => document.querySelector('#__ad').innerText.replace(/\s+/g, ' '));

    ok('a kártya ott van a Profilok panelen', /Kortyolási limitek/.test(await at()));
    ok('zárva is látszik, hány limit van', /1 beállítva/.test(await at()),
       ((await at()).match(/Kortyolási limitek.{0,120}/) || ['—'])[0].slice(-30));

    await p2.evaluate(() => {
      const b2 = [...document.querySelectorAll('#__ad button')].find(x => /Kortyolási limitek/.test(x.innerText));
      if (b2) b2.click();
    });
    await p2.waitForTimeout(700);
    const n = await p2.evaluate(() => document.querySelectorAll('#__ad input[type="number"]').length);
    ok('minden profil egy sorban, egy görgetéssel', n === 2, n + ' mező (2 profil)');
    ok('a meglévő limit betöltődik',
       await p2.evaluate(() => [...document.querySelectorAll('#__ad input[type="number"]')][0].value) === '3');

    // Belanak adunk limitet — a mezobol kilepeskor mentodik
    await p2.evaluate(() => {
      const i = [...document.querySelectorAll('#__ad input[type="number"]')][1];
      const set = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
      i.focus(); set.call(i, '5');
      i.dispatchEvent(new Event('input', { bubbles: true }));
      i.blur();
    });
    await p2.waitForTimeout(900);
    const saved = await p2.evaluate(() => window.__fbStore['profiles'].p_b);
    ok('a mezőből kilépve a profilba mentődik', saved && saved.drinkLimit === 5, JSON.stringify(saved));
    ok('a többi profilmező érintetlen', saved && saved.name === 'Bela' && !!saved.color, JSON.stringify(saved));
    ok('nincs JS hiba', errs.filter(e => !/ServiceWorker/.test(e)).length === 0, errs.join(' | '));
    await p2.close();
  }

  await b.close();
  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
