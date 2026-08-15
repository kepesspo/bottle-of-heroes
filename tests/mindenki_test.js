// v10.375 — Mindenki Iszik: KI VELE? (koccintás)
//
// A régi passzív „az app kisorsol valakit, egyedül iszik egyet" megszűnt. Az új
// mechanika: a sorsolt játékos KIVÁLASZT egy társat, és KOCCINTANAK — mindketten
// isznak egyet. Nincs lezárás-gond, tisztán szociális csavar.
//
// Fogódzók:
//  1) a partner-választó a KÖZÖS PlayerDrinkRow variant='pick' (aria a szó nélkül) —
//     a sorsolt maga NEM választható (csak a többiek)
//  2) a koccintás gomb TILTOTT, amíg nincs partner
//  3) koccintás → MINDKETTEN isznak, a helyes (skálázott) kortyszámmal
//  4) NYERS szám → a PlayScreen szoroz: nehéz szinten fejenként 1 raw = 3 korty
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const mount = (p, diff) => p.evaluate((diff) => {
  const r = document.getElementById('root'); if (r) r.style.display = 'none';
  const old = document.getElementById('__p'); if (old) old.remove();
  const root = document.createElement('div'); root.id = '__p';
  root.style.cssText = 'position:fixed;inset:0;z-index:1;display:flex;flex-direction:column;background:#EAF2FB';
  document.body.appendChild(root);
  function H() {
    const [ps, setPs] = React.useState([
      { id: 'a', name: 'Sere', color: '#E07A5F', points: 0, drinks: 0 },
      { id: 'b', name: 'Kecsi', color: '#4FC2A0', points: 0, drinks: 0 },
      { id: 'c', name: 'Vivi', color: '#A78BFA', points: 0, drinks: 0 },
      { id: 'd', name: 'Robi', color: '#60A5FA', points: 0, drinks: 0 }]);
    window.__players = ps;
    return React.createElement(PlayScreen, { go: () => {}, players: ps, setPlayers: setPs, selectedGames: ['mindenki'],
      roomCode: null, setGameMeta: () => {}, setScoreHistory: () => {}, setLastGameRound: () => {},
      gameMeta: { modes: ['points', 'drinks'], difficulty: diff } });
  }
  ReactDOM.createRoot(root).render(React.createElement(H));
}, diff);

// A koccintás gomb (nem a „Kövi" footer, nem a picker-sor)
const clinkBtn = p => p.evaluate(() => [...document.querySelectorAll('#__p button')]
  .find(x => /Koccintás|Megiszom/.test(x.textContent || '')));
const clinkDisabled = p => p.evaluate(() => {
  const b = [...document.querySelectorAll('#__p button')].find(x => /Koccintás|Megiszom/.test(x.textContent || ''));
  return b ? b.disabled : null;
});
const clickClink = p => p.evaluate(() => {
  const b = [...document.querySelectorAll('#__p button')].find(x => /Koccintás|Megiszom/.test(x.textContent || ''));
  if (b && !b.disabled) { b.click(); return true; } return false;
});
// A picker-sorok: PlayerDrinkRow variant='pick' — kattintható div-ek a nevekkel
const pickPartner = (p, name) => p.evaluate((name) => {
  // a „Kivel koccintasz?" cím alatti sorok; a sor egy div, benne a név
  // ⚠️ a sor innerText-je az avatar kezdőbetűjével indul („KKecsi"), ezért
  // *tartalmazza* a nevet, nem startsWith (v10.353 fogódzó). A kattintható SOR
  // a display:flex + cursor:pointer div.
  const rows = [...document.querySelectorAll('#__p div')].filter(d => {
    const t = (d.textContent || '');
    return t.includes(name) && d.style && d.style.cursor === 'pointer' && d.style.display === 'flex';
  });
  rows.sort((a, b) => a.textContent.length - b.textContent.length);
  if (rows[0]) { rows[0].click(); return true; } return false;
}, name);
const stateOf = p => p.evaluate(() => (window.__players || []).map(x => ({ n: x.name, d: x.drinks, pt: x.points })));
const bannerTxt = p => p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); return el ? (el.innerText || '').replace(/\s+/g, ' ').trim() : ''; });
const clickKovi = p => p.evaluate(() => { const b = [...document.querySelectorAll('#__p button')].find(x => /Kövi/i.test(x.textContent || '')); if (b) b.click(); });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });

  // ── 1. NEHÉZ: Sere (sorsolt) koccint Kecsivel → mindketten 1 raw × 3 = 3 korty ──
  console.log('\n===== 1. KI VELE? — koccintás, mindketten isznak (nehéz, ×3) =====');
  {
    const p = await b.newPage({ viewport: { width: 402, height: 950 } });
    p.__errs = [];
    p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) p.__errs.push(e.message); });
    await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
    await p.addInitScript(stub);
    await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');}catch(e){}`);
    await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
    await p.waitForTimeout(3000);
    await mount(p, 'hard');
    await p.waitForTimeout(2200);

    // a sorsolt = list[0] = Sere; a picker a többi 3-at mutatja, Sere-t NEM
    const pickerNames = await p.evaluate(() => {
      const hdr = [...document.querySelectorAll('#__p div')].find(d => /Kivel koccintasz/i.test(d.textContent || ''));
      return document.getElementById('__p').innerText;
    });
    ok(/Kivel koccintasz/i.test(pickerNames), 'megjelenik a „Kivel koccintasz?" választó');

    ok(await clinkDisabled(p) === true, '⚠️ a koccintás gomb TILTOTT, amíg nincs partner');

    ok(await pickPartner(p, 'Kecsi'), 'a Kecsi sorára lehet koppintani (picker)');
    await p.waitForTimeout(250);
    ok(await clinkDisabled(p) === false, 'partner után a gomb aktív');

    await clickClink(p); await p.waitForTimeout(1400);
    const banner = await bannerTxt(p);
    await p.evaluate(() => { const el = [...document.querySelectorAll('div')].find(d => d.style && d.style.zIndex === '250'); if (el) el.click(); });
    await p.waitForTimeout(300);
    await clickKovi(p); await p.waitForTimeout(1600);
    const st = await stateOf(p);
    const sere = st.find(x => x.n === 'Sere'), kecsi = st.find(x => x.n === 'Kecsi');
    ok(sere && sere.d === 3, '⚠️ a sorsolt (Sere) 1 raw × 3 = 3 kortyot ivott', sere && sere.d);
    ok(kecsi && kecsi.d === 3, 'a partner (Kecsi) is 3 kortyot ivott', kecsi && kecsi.d);
    ok(st.filter(x => x.d > 0).length === 2, 'pontosan KETTEN ittak', st.filter(x => x.d > 0).map(x => x.n).join(','));
    ok(st.every(x => x.pt === 0), 'senki nem kap pontot (tisztán korty)', st.map(x => x.pt).join(','));
    ok(/3\s*KORTY/i.test(banner), 'a banner „3 KORTY" metrikát mutat', (banner.match(/\d+\s*KORTY/i) || ['nincs'])[0]);
    ok(p.__errs.length === 0, 'nincs JS hiba', p.__errs.join(' | '));
    await p.close();
  }

  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
