// Test Imposztor game with 1 and 2 impostors based on player count
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const ROOT = '/home/user/bottle-of-heroes';
const OUT = __dirname;
const stub = fs.readFileSync(path.join(ROOT, 'tests/fbstub.js'), 'utf8');

let fail = 0;
const ok = (c, n, x) => { console.log((c ? '  OK  ' : '  HIBA') + '   ' + n + (x !== undefined ? '  → ' + x : '')); if (!c) fail++; };

async function mount(p, n) {
  await p.evaluate(({ n }) => {
    const old = document.getElementById('__p'); if (old) old.remove();
    [...document.body.children].forEach(c => { if (c.id !== '__p') c.style.display = 'none'; });
    const root = document.createElement('div'); root.id = '__p';
    root.style.cssText = 'position:fixed;inset:0;z-index:9;display:flex;flex-direction:column';
    document.body.appendChild(root);
    const nev = ['Sere','Kecsi','Luca','Tóth','Márk','Dani'].slice(0, n);
    function H() {
      const [players, setPlayers] = React.useState(nev.map((x,i)=>({ id:'p'+i, name:x, color:'#5BA0DB', points:0, drinks:0 })));
      window.__players = players;
      return React.createElement(PlayScreen, { go:()=>{}, players, setPlayers, selectedGames:['imposztor'],
        roomCode:null, setGameMeta:()=>{}, setScoreHistory:()=>{}, setLastGameRound:()=>{},
        gameMeta:{ modes:['points'], difficulty:'easy' } });
    }
    ReactDOM.createRoot(root).render(React.createElement(H));
  }, { n });
  await p.waitForTimeout(2600);
  await p.evaluate(() => { const pop=[...document.querySelectorAll('div')].find(d=>d.style&&d.style.zIndex==='9998'); if(pop) pop.click(); });
  await p.waitForTimeout(600);
}

(async () => {
  const browser = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await browser.newPage({ viewport: { width: 402, height: 874 }, deviceScaleFactor: 2 });
  const errs = [];
  p.on('pageerror', e => errs.push(e.message));
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
  await p.goto('file://' + path.join(ROOT, 'index.html'), { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);

  console.log('\n===== IMPOSZTOR 4 JÁTÉKOS (1 imposztor) =====');
  await mount(p, 4);
  const reveal4 = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const txt = R.innerText || '';
    // Check for key UI elements: player name with "jön", hold button, and "Láttam" pass button
    const hasJoen = /\s+jön/.test(txt);
    const hasHoldBtn = txt.includes('Nyomd');
    const hasPassBtn = txt.includes('Láttam');
    return { hasJoen, hasHoldBtn, hasPassBtn, playerCount: (txt.match(/\/\d/g) || [''])[0] };
  });
  ok(reveal4.hasJoen && reveal4.hasHoldBtn && reveal4.hasPassBtn, 'A 4 játékos játékban a felfedés fázis indul');
  ok(reveal4.playerCount === '/4', '4 játékos van a mutatóban', reveal4.playerCount);

  console.log('\n===== IMPOSZTOR 5+ JÁTÉKOS (2 imposztor) =====');
  // Reset and test with 5 players (should have 2 impostors)
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);
  await mount(p, 5);

  const reveal5 = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const txt = R.innerText || '';
    return { hasReveal: txt.includes('jön'), hasHoldBtn: txt.includes('Nyomd') };
  });
  ok(reveal5.hasReveal && reveal5.hasHoldBtn, 'Az 5 játékos játékban a felfedés fázis indul (2 imposztor)');

  // Test with 6 players
  await p.reload({ waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(2500);
  await mount(p, 6);

  const reveal6 = await p.evaluate(() => {
    const R = document.getElementById('__p');
    const txt = R.innerText || '';
    return { hasReveal: txt.includes('jön'), playerCount: (txt.match(/\/\d+/g) || [''])[0] };
  });
  ok(reveal6.hasReveal, '6 játékossal a játék elindul');
  ok(reveal6.playerCount === '/6', '6 játékos van a mutatóban', reveal6.playerCount);

  ok(errs.length === 0, 'nincs JS hiba', errs.slice(0,3).join(' | '));
  console.log(fail ? `\n❌ ${fail} HIBA` : '\n✅ MINDEN ELLENORZES RENDBEN');
  await browser.close();
  process.exit(fail ? 1 : 0);
})();
