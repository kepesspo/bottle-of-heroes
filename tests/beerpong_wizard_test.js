// v10.381 — Beer Pong beállító WIZARD + a generikus szekciók elrejtése
//
// Beer pongnál (Torna ÉS 2.0) a Játékmenet generikus szekciói (Nehézség,
// Játéksorrend, Max körök, Módok, Egyéb) NEM kellenek — a beer pong nyers
// pohár-különbséget oszt. Helyettük egy „Beer Pong beállítása" gomb egy
// lépésenkénti WIZARD-ot nyit: Mód → Formátum → Részletek → Név → Indítás.
//
// Fogódzók:
//  1) beer pongnál a generikus szekciók eltűnnek, a „Beer Pong beállítása" gomb ott van
//  2) a gomb megnyitja a wizardot (Mód lépés)
//  3) a flow végigmegy (Mód → Formátum → Részletek → Név), a formátum-választás
//     lemegy a configba, és a „Torna indítása" elindítja a partit (go('play'))
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const BASE = 'file:///home/user/bottle-of-heroes/index.html';
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const MOUNT = (sel) => `
  (() => {
    const root = document.createElement('div'); root.id = '__g';
    root.style.cssText = 'position:fixed;inset:0;z-index:99999;background:#fff;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const PLAYERS = [
      { id:'a', name:'Anna', color:'#5BA0DB', profileId:'p_a' },
      { id:'b', name:'Béla', color:'#E07A5F', profileId:'p_b' },
      { id:'c', name:'Cili', color:'#4FC2A0', profileId:'p_c' },
      { id:'d', name:'Dani', color:'#A78BFA', profileId:'p_d' },
    ];
    function H() {
      const [sel] = React.useState(${JSON.stringify(sel)});
      const [meta, setMeta] = React.useState({});
      window.__meta = meta; window.__went = null;
      React.useEffect(() => { window.__meta = meta; }, [meta]);
      return React.createElement(SetupScreen, {
        go: (n) => { window.__went = n; },
        players: PLAYERS, selectedGames: sel, setSelectedGames: () => {},
        gameMeta: meta, setGameMeta: setMeta, netReady: true,
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  })();
`;

const txt = p => p.evaluate(() => (document.getElementById('__g').innerText || '').replace(/\s+/g, ' '));
const clickG = (p, re) => p.evaluate(reSrc => { const b = [...document.querySelectorAll('#__g button')].find(x => new RegExp(reSrc).test(x.textContent || '')); if (b) { b.click(); return true; } return false; }, re.source);

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1100 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3400);
  await p.evaluate(MOUNT(['beerpong2']));
  await p.waitForTimeout(1000);

  // ── 1. A generikus szekciók eltűntek, a beer pong gomb ott van ──
  console.log('\n===== 1. GENERIKUS SZEKCIÓK ELREJTVE =====');
  const t1 = await txt(p);
  ok(/Beer Pong beállítása/.test(t1), 'ott a „Beer Pong beállítása" gomb', /Beer Pong beállítása/.test(t1));
  ok(!/Nehézségi szint/.test(t1), 'NINCS Nehézség szekció', !/Nehézségi szint/.test(t1));
  ok(!/Játéksorrend/.test(t1), 'NINCS Játéksorrend', !/Játéksorrend/.test(t1));
  ok(!/Max körök/i.test(t1), 'NINCS Max körök', !/Max körök/i.test(t1));

  // ── 2. A gomb megnyitja a wizardot ──
  console.log('\n===== 2. WIZARD MEGNYITÁSA =====');
  await clickG(p, /Beer Pong beállítása/); await p.waitForTimeout(400);
  const t2 = await txt(p);
  ok(/Ki játszik\?/.test(t2), 'a wizard a „Mód" lépéssel nyit', /Ki játszik/.test(t2));
  ok(/1\/4/.test(t2), 'a haladásjelző 1/4-en áll', (t2.match(/\d\/4/) || ['?'])[0]);

  // ── 3. Végigmegyünk a flow-n, formátumot választunk, majd indítás ──
  console.log('\n===== 3. FLOW VÉGIG → INDÍTÁS =====');
  await clickG(p, /Tovább/); await p.waitForTimeout(300);   // Mód → Formátum
  ok(/Milyen formátum/.test(await txt(p)), 'a 2. lépés a Formátum');
  await clickG(p, /Körmérkőzés/); await p.waitForTimeout(250);   // rr formátum
  await clickG(p, /Tovább/); await p.waitForTimeout(300);   // Formátum → Részletek
  ok(/Részletek/.test(await txt(p)), 'a 3. lépés a Részletek');
  await clickG(p, /Tovább/); await p.waitForTimeout(300);   // Részletek → Név
  ok(/Majdnem kész/.test(await txt(p)), 'a 4. lépés a Név + összefoglaló');
  // név beírása
  await p.evaluate(() => { const inp = document.querySelector('#__g input'); if (inp) { const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; setter.call(inp, 'Teszt Kupa'); inp.dispatchEvent(new Event('input', { bubbles:true })); } });
  await p.waitForTimeout(250);
  const metaBefore = await p.evaluate(() => window.__meta);
  ok(metaBefore.beerpong2Config && metaBefore.beerpong2Config.tournamentType === 'rr', 'a formátum-választás a configba került (rr)', metaBefore.beerpong2Config && metaBefore.beerpong2Config.tournamentType);
  ok(metaBefore.beerpong2Config && metaBefore.beerpong2Config.tournamentName === 'Teszt Kupa', 'a bajnokság neve a configba került', metaBefore.beerpong2Config && metaBefore.beerpong2Config.tournamentName);
  await clickG(p, /Torna indítása/); await p.waitForTimeout(400);
  ok(await p.evaluate(() => window.__went) === 'play', 'a „Torna indítása" elindítja a partit (go(play))', await p.evaluate(() => window.__went));

  // ── 4. A régi Beer Pong Torna is a wizardot kapja, de a beerpongConfig-ba ír ──
  console.log('\n===== 4. RÉGI BEER PONG TORNA — beerpongConfig, nincs 2.0-mező =====');
  await p.evaluate(() => { const g = document.getElementById('__g'); if (g) g.remove(); });
  await p.evaluate(MOUNT(['beerpong']));
  await p.waitForTimeout(800);
  ok(/Beer Pong beállítása/.test(await txt(p)), 'a régi Beer Pong Torna is a „Beer Pong beállítása" gombot mutatja');
  await clickG(p, /Beer Pong beállítása/); await p.waitForTimeout(400);
  await clickG(p, /Tovább/); await p.waitForTimeout(250);   // Mód → Formátum
  await clickG(p, /Kieséses/); await p.waitForTimeout(250); // formátum: kieséses (→ beerpongConfig íródik)
  await clickG(p, /Tovább/); await p.waitForTimeout(250);   // Formátum → Részletek
  const t4 = await txt(p);
  ok(!/Asztalok száma/.test(t4), 'a régi Beer Pongnál NINCS „Asztalok száma" (2.0 funkció)');
  ok(!/3\. helyért/.test(t4), 'a régi Beer Pongnál NINCS „3. helyért meccs" (2.0 funkció)');
  await clickG(p, /Tovább/); await p.waitForTimeout(250);   // Részletek → Név
  await clickG(p, /Torna indítása/); await p.waitForTimeout(350);
  const m2 = await p.evaluate(() => window.__meta);
  ok(m2.beerpongConfig && !m2.beerpong2Config, 'a régi Beer Pong a beerpongConfig-ba ír (nem beerpong2Config)', JSON.stringify(Object.keys(m2)));
  ok(await p.evaluate(() => window.__went) === 'play', 'és elindítja a partit');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
