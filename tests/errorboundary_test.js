// Hibahatár: egy játék render-hibája ne vigye el az egész bulit
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 390, height: 900 } });
  const errs = []; p.on('pageerror', e => { if(!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(() => { try { localStorage.setItem('boh_onboarded','1'); } catch(e){} });
  await p.goto('file:///home/user/bottle-of-heroes/index.html', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(3500);

  // PlayScreen két játékkal; az elsőt szándékosan elrontjuk
  await p.evaluate(() => {
    window.__players = [
      { id:'a', name:'Anna', color:'#5BA0DB', points:3, drinks:2, profileId:'p_a' },
      { id:'b', name:'Bela', color:'#E07A5F', points:1, drinks:5, profileId:'p_b' },
    ];
    // az eredeti GameContent-et becsomagoljuk: a 'rulett' render-hibát dob
    const orig = window.GameContent;
    window.GameContent = function Patched(props) {
      // a jatek-sorrend sorsolt, ezert az ELSOKENT betoltott jatekot rontjuk el
      if (window.__broken == null) window.__broken = props.gameId;
      if (props.gameId === window.__broken && !window.__healed) throw new Error("Cannot read properties of null (reading 'artist')");
      return React.createElement(orig, props);
    };
    const root = document.createElement('div'); root.id='__ps';
    root.style.cssText='position:fixed;inset:0;background:#F5D89B;overflow:auto;z-index:99999';
    document.body.appendChild(root);
    function Harness() {
      const [players, setPlayers] = React.useState(window.__players);
      const [screen, setScreen] = React.useState('play');
      React.useEffect(() => { window.__players = players; window.__screen = screen; }, [players, screen]);
      return React.createElement(window.PlayScreen, {
        players, setPlayers, selectedGames:['rulett','kopapir'], go:(s)=>setScreen(s), roomCode:null,
        gameMeta:{ modes:['points','drinks'] },
        setGameMeta:()=>{}, setLastGameRound:()=>{}, setScoreHistory:()=>{},
      });
    }
    ReactDOM.createRoot(root).render(React.createElement(Harness));
  });
  await p.waitForTimeout(4200);  // a kör-popup elhaladjon

  const txt = () => p.evaluate(() => document.getElementById('__ps').innerText);
  const t1 = await txt();
  console.log('1 nem fehér a képernyő (van tartalom):', t1.trim().length > 40);
  console.log('2 megjelent a hibadoboz:', /elakadt/i.test(t1));
  console.log('3 van "Újra" és "Kövi játék" gomb:', /Újra/.test(t1) && /Kövi játék/.test(t1));
  console.log('4 a hiba üzenete látszik:', /artist/.test(t1));
  console.log('5 a footer/állás megmaradt (Anna látszik):', /Anna/.test(t1));
  console.log('6 naplózva lett a client_errors-be:', await p.evaluate(() => Object.keys(window.__fbStore['client_errors']||{}).length));
  const logged = await p.evaluate(() => { const c = window.__fbStore['client_errors']||{}; const k = Object.keys(c)[0]; return k ? { where:c[k].where, msg:(c[k].message||'').slice(0,40), ver:c[k].version } : null; });
  console.log('   napló:', JSON.stringify(logged));
  const box = await p.evaluate(() => {
    const el = Array.from(document.querySelectorAll('#__ps div')).find(d => /elakadt/.test(d.innerText||'') && d.style.borderRadius);
    if (!el) return null;
    const r = el.getBoundingClientRect();
    const cs = getComputedStyle(el);
    return { top:Math.round(r.top), left:Math.round(r.left), w:Math.round(r.width), h:Math.round(r.height), vis:cs.visibility, disp:cs.display, op:cs.opacity };
  });
  console.log('   hibadoboz geometria:', JSON.stringify(box));
  await p.evaluate(() => { const el = Array.from(document.querySelectorAll('#__ps div')).find(d => /elakadt/.test(d.innerText||'') && d.style.borderRadius); if (el) el.scrollIntoView({block:'center'}); });
  await p.waitForTimeout(400);
  await p.screenshot({ path: __dirname + '/errorboundary.png' });

  // "Kövi játék" → lépjen a következőre, és az állás maradjon meg
  await p.evaluate(() => { window.__healed = true; const b2 = Array.from(document.querySelectorAll('#__ps button')).find(x=>/Kövi játék/.test(x.innerText)); if (b2) b2.click(); });
  await p.waitForTimeout(2000);
  const t2 = await txt();
  console.log('7 tovabblepett (nincs mar hibadoboz):', !/elakadt/i.test(t2));
  console.log('8 allas megmaradt:', JSON.stringify(await p.evaluate(()=>window.__players.map(x=>`${x.name}:${x.points}p/${x.drinks}k`))));
  console.log('9 kepernyo eleje:', t2.split('\n').slice(0,6).join(' | '));
  console.log('HIBAK (konzol):', errs.join(' | ') || 'nincs');
  await b.close();
})().catch(e=>{console.error('CRASH',e);process.exit(1);});
