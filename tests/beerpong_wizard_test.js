// v10.382 — Beer Pong beállító WIZARD = a Játékmenet lépés MAGA (nincs köztes képernyő)
//
// Beer pongnál (Torna ÉS 2.0) a Játékmenet lépés egyből a lépésenkénti WIZARD:
// Mód → Formátum → Részletek → Név → Indítás. Nincs üres köztes képernyő, nincs
// „Beer Pong beállítása" gomb. A lépés-1 „Vissza" a Játékokhoz visz, a záró
// „Torna indítása" indítja a partit. A generikus szekciók (Nehézség, sorrend,
// max kör, módok) nincsenek.
//
// Fogódzók:
//  1) beer pongnál a Játékmenet EGYBŐL a wizard (Mód lépés), nincs gomb/szekció
//  2) a lépés-1 „Vissza" a Játékokhoz visz (go('games'))
//  3) a flow végigmegy (formátum→config, név→config), a „Torna indítása" → go('play')
//  4) a régi Beer Pong Torna is a wizardot kapja, a beerpongConfig-ba ír, 2.0-mező nélkül
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
const clickBack = p => p.evaluate(() => { const b = [...document.querySelectorAll('#__g button')].find(x => (x.textContent || '').trim() === '‹'); if (b) { b.click(); return true; } return false; });

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

  // ── 1. Egyből a wizard, nincs köztes képernyő/gomb/szekció ──
  console.log('\n===== 1. EGYBŐL A WIZARD (nincs köztes képernyő) =====');
  const t1 = await txt(p);
  ok(/Ki játszik\?/.test(t1), 'a Játékmenet EGYBŐL a „Mód" lépéssel nyit', /Ki játszik/.test(t1));
  ok(/1\/4/.test(t1), 'a haladásjelző 1/4-en áll', (t1.match(/\d\/4/) || ['?'])[0]);
  ok(!/Beer Pong beállítása/.test(t1), 'NINCS köztes „Beer Pong beállítása" gomb', !/Beer Pong beállítása/.test(t1));
  ok(!/Nehézségi szint/.test(t1) && !/Játéksorrend/.test(t1), 'NINCS Nehézség / Játéksorrend szekció');

  // ── 2. A lépés-1 „Vissza" a Játékokhoz visz ──
  console.log('\n===== 2. LÉPÉS-1 VISSZA → JÁTÉKOK =====');
  await clickBack(p); await p.waitForTimeout(300);
  ok(await p.evaluate(() => window.__went) === 'games', 'a ‹ (lépés 1) a Játékokhoz visz (go(games))', await p.evaluate(() => window.__went));
  // vissza a wizardba a következő lépésekhez
  await p.evaluate(() => { window.__went = null; });

  // ── 3. Végigmegyünk a flow-n, formátumot választunk, majd indítás ──
  console.log('\n===== 3. FLOW VÉGIG → INDÍTÁS =====');
  await clickG(p, /Tovább/); await p.waitForTimeout(300);   // Mód → Formátum
  ok(/Milyen formátum/.test(await txt(p)), 'a 2. lépés a Formátum');
  await clickG(p, /Körmérkőzés/); await p.waitForTimeout(250);
  await clickG(p, /Tovább/); await p.waitForTimeout(300);   // Formátum → Részletek
  ok(/Részletek/.test(await txt(p)), 'a 3. lépés a Részletek');
  await clickG(p, /Tovább/); await p.waitForTimeout(300);   // Részletek → Név
  ok(/Majdnem kész/.test(await txt(p)), 'a 4. lépés a Név + összefoglaló');
  await p.evaluate(() => { const inp = document.querySelector('#__g input'); if (inp) { const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set; setter.call(inp, 'Teszt Kupa'); inp.dispatchEvent(new Event('input', { bubbles:true })); } });
  await p.waitForTimeout(250);
  const meta1 = await p.evaluate(() => window.__meta);
  ok(meta1.beerpong2Config && meta1.beerpong2Config.tournamentType === 'rr', 'a formátum-választás a configba került (rr)', meta1.beerpong2Config && meta1.beerpong2Config.tournamentType);
  ok(meta1.beerpong2Config && meta1.beerpong2Config.tournamentName === 'Teszt Kupa', 'a bajnokság neve a configba került', meta1.beerpong2Config && meta1.beerpong2Config.tournamentName);
  await clickG(p, /Torna indítása/); await p.waitForTimeout(400);
  ok(await p.evaluate(() => window.__went) === 'play', 'a „Torna indítása" elindítja a partit (go(play))', await p.evaluate(() => window.__went));

  // ── 4. A régi Beer Pong Torna is a wizardot kapja, beerpongConfig-ba ír ──
  console.log('\n===== 4. RÉGI BEER PONG TORNA — beerpongConfig, nincs 2.0-mező =====');
  await p.evaluate(() => { const g = document.getElementById('__g'); if (g) g.remove(); });
  await p.evaluate(MOUNT(['beerpong']));
  await p.waitForTimeout(800);
  ok(/Ki játszik\?/.test(await txt(p)), 'a régi Beer Pong Torna is EGYBŐL a wizardot mutatja');
  await clickG(p, /Tovább/); await p.waitForTimeout(250);   // Mód → Formátum
  await clickG(p, /Kieséses/); await p.waitForTimeout(250); // formátum (→ beerpongConfig íródik)
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
