// v10.404 — DNR a tortán: SORSOLÁS (zsákutca-mentes húzás + animált show)
//
// Szabályok: egy szezon = egy kör; minden csapat PONTOSAN egyszer házigazda, estéként
// 2 vendégpáros (soha nem 1), és egy csapat legfeljebb 2-szer megy vendégségbe.
//
// Fogódzók:
//  1) LOGIKA — 3…8 csapattal sok ezer teljes szezont végigsorsol: soha nincs hiba,
//     mindenki 1× házigazda, mindenki PONTOSAN 2× vendég, mindig 2 vendég, nem önmaga
//  1b) KONTROLL — a vak (ellenőrzés nélküli) húzás 5 csapatnál TÉNYLEG zsákutcába fut
//     néha; enélkül az 1) akkor is zöld lenne, ha a feladat eleve nem tudna elakadni
//  1c) egy kézzel elrontott állás (az utolsó házigazdához csak a saját jegye maradt)
//     → a sorsolás „Zsákutca" hibát ad, nem húz 1 vendéget
//  2) FELÜLET — a Sorsolás gomb admin PIN-t kér (hibás PIN → nem enged)
//  3) Próba húzás: lefut az animáció (tárcsa → házigazda → 2 vendég felfordul), és
//     SEMMI nem kerül a store-ba
//  4) Éles sorsolás: config/tortaDraw pending, az „Elfogadom" új alkalmat ír a
//     tortaEvenings-be (a húzott házigazdával és 2 vendéggel), a draw → accepted
//  5) aki később nyit rá egy függő húzásra, animáció nélkül, rögtön az eredményt látja
//  6) zsákutcás állásnál a panel kiírja a hibát, a gombok tiltva
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const ROOT = '/home/user/bottle-of-heroes';
const stub = fs.readFileSync(ROOT + '/tests/fbstub.js', 'utf8');
let fail = 0;
const ok = (c, l, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

const PROFILES = Array.from({ length: 10 }, (_, i) => ({ id: 'p' + i, name: ['Sere','Kecsi','Vivi','Robi','Luca','Béla','Anna','Gergő','Dóri','Máté'][i], color: '#5BA0DB' }));
const TEAMS = [0, 1, 2, 3, 4].map(i => ({ id: 't' + 'ABCDE'[i], name: 'Csapat ' + 'ABCDE'[i], members: ['p' + (2 * i), 'p' + (2 * i + 1)] }));
const CFG = { enabled: true, mode: 'torta', tortaTitle: 'DNR a tortán', tippRequireCode: false, tortaTeams: TEAMS, tortaEvenings: [] };
const store = (p, doc) => p.evaluate(d => JSON.parse(JSON.stringify(((window.__fbStore['config'] || {})[d]) || null)), doc);
const click = (p, sel) => p.evaluate(s => { const b = document.querySelector(s); if (!b) return false; b.click(); return true; }, sel);
const setInput = (p, sel, v) => p.evaluate(({ s, v }) => { const i = document.querySelector(s); const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set; set.call(i, v); i.dispatchEvent(new Event('input', { bubbles: true })); }, { s: sel, v });
const waitPhase = async (p, ph, ms) => { const t0 = Date.now(); while (Date.now() - t0 < ms) { if ((await p.evaluate(() => { const d = document.querySelector('[data-torta-draw]'); return d ? d.getAttribute('data-torta-phase') : null; })) === ph) return true; await p.waitForTimeout(150); } return false; };
const mount = (p) => p.evaluate(() => { window.__bRoot.render(React.createElement(BingoScreen, { key: 'k' + Math.random(), go: () => {}, deepLink: true })); });

(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 402, height: 1400 } });
  const errs = []; p.on('pageerror', e => { if (!/ServiceWorker/.test(e.message)) errs.push(e.message); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(`try{localStorage.setItem('boh_onboarded','1');localStorage.setItem('boh_splash','0');localStorage.setItem('boh_bingo_who','p0');localStorage.setItem('boh_admin_ok','1234');}catch(e){}`);
  await p.goto('file://' + ROOT + '/index.html', { waitUntil: 'domcontentloaded' });
  await p.waitForTimeout(3200);

  // ── 1. LOGIKA ──
  console.log('\n===== 1. LOGIKA — TELJES SZEZONOK =====');
  const sim = await p.evaluate(() => {
    const out = {};
    for (let n = 3; n <= 8; n++) {
      const teams = Array.from({ length: n }, (_, i) => ({ id: 'T' + i, members: [] }));
      let bad = 0, runs = 0;
      for (let k = 0; k < 400; k++) {
        runs++;
        const evs = [];
        for (let e = 0; e < n; e++) {
          const r = tortaDrawPick(teams, evs);
          if (r.error || r.guestIds.length !== 2 || r.guestIds.includes(r.hostId) || r.guestIds[0] === r.guestIds[1]) { bad++; break; }
          evs.push({ id: 'e' + e, hostId: r.hostId, guestIds: r.guestIds });
        }
        const hostCnt = {}, gCnt = {};
        evs.forEach(ev => { hostCnt[ev.hostId] = (hostCnt[ev.hostId] || 0) + 1; ev.guestIds.forEach(g => gCnt[g] = (gCnt[g] || 0) + 1); });
        if (evs.length !== n || teams.some(t => hostCnt[t.id] !== 1 || gCnt[t.id] !== 2)) bad++;
        if (!tortaDrawPick(teams, evs).error) bad++;   // a szezon végén nincs több húzás
      }
      out[n] = { runs, bad };
    }
    return out;
  });
  Object.keys(sim).forEach(n => ok(sim[n].bad === 0, `⚠️ ${n} csapat: ${sim[n].runs} szezon, mind szabályos (1× házigazda, pontosan 2× vendég, mindig 2 vendég)`, JSON.stringify(sim[n])));

  console.log('\n===== 1b. KONTROLL — VAK HÚZÁS ELAKAD =====');
  const naive = await p.evaluate(() => {
    let stuck = 0; const N = 2000, ids = ['A','B','C','D','E'];
    for (let k = 0; k < N; k++) {
      const hosts = ids.slice().sort(() => Math.random() - 0.5); const cap = { A:2, B:2, C:2, D:2, E:2 };
      for (const h of hosts) {
        const pool = ids.filter(g => g !== h && cap[g] > 0).sort(() => Math.random() - 0.5);
        if (pool.length < 2) { stuck++; break; }
        cap[pool[0]]--; cap[pool[1]]--;
      }
    }
    return { stuck, N };
  });
  ok(naive.stuck > 0, 'a vak húzás 5 csapatnál TÉNYLEG elakad néha (a probléma valós)', `${naive.stuck}/${naive.N} szezon`);

  console.log('\n===== 1c. ZSÁKUTCÁS ÁLLÁS =====');
  const dead = await p.evaluate(teams => {
    // A–D már házigazda volt, és A–D mind 2× vendég → E-hez csak E jegye maradna
    const evs = [
      { hostId:'tA', guestIds:['tB','tC'] }, { hostId:'tB', guestIds:['tC','tD'] },
      { hostId:'tC', guestIds:['tD','tA'] }, { hostId:'tD', guestIds:['tA','tB'] },
    ];
    return tortaDrawPick(teams, evs);
  }, TEAMS);
  ok(dead.error && /Zsákutca/.test(dead.error), '⚠️ elrontott állásnál „Zsákutca" hiba, NEM 1 vendég', JSON.stringify(dead).slice(0, 90));

  // ── FELÜLET ──
  await p.evaluate(({ profiles, cfg }) => {
    window.__fbStore['config'] = Object.assign(window.__fbStore['config'] || {}, { bingoConfig: JSON.parse(JSON.stringify(cfg)) });
    window.getProfiles = () => Promise.resolve(profiles);
    window.getAdminPin = () => Promise.resolve('1234');
    const r0 = document.getElementById('root'); if (r0) r0.style.display = 'none';
    const d = document.createElement('div'); d.id = '__b';
    d.style.cssText = 'position:absolute;left:0;top:0;width:402px;height:1400px;overflow:auto;z-index:9;background:#fff;display:flex;flex-direction:column';
    document.body.appendChild(d);
    window.__bRoot = ReactDOM.createRoot(d);
  }, { profiles: PROFILES, cfg: CFG });
  await mount(p); await p.waitForTimeout(900);

  console.log('\n===== 2. ADMIN PIN =====');
  ok(await click(p, '[data-torta-drawbtn]'), 'a Sorsolás gomb ott van a Tortán képernyőn');
  await p.waitForTimeout(400);
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-pin]')), '⚠️ PIN-t kér — akkor is, ha az Admin felület ezen a telefonon már fel volt oldva (boh_admin_ok)');
  await setInput(p, '[data-torta-pin]', '0000'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(200);
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-pin]') && !document.querySelector('[data-torta-livebtn]')), 'hibás PIN-nel NEM enged tovább');
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => document.querySelectorAll('[data-torta-drawstate]').length === 5), 'helyes PIN → a panel mind az 5 csapat állását mutatja');

  console.log('\n===== 3. PRÓBA HÚZÁS =====');
  await click(p, '[data-torta-practicebtn]');
  await p.waitForTimeout(300);
  ok(await p.evaluate(() => { const d = document.querySelector('[data-torta-draw]'); return d && d.getAttribute('data-torta-draw') === 'practice' && !!document.querySelector('[data-torta-practice]'); }), 'a próba-show elindul, PRÓBA címkével');
  ok(await waitPhase(p, 'reel', 1500), 'pörög a házigazda-tárcsa');
  const t0 = Date.now();
  ok(await waitPhase(p, 'host', 12000), 'a tárcsa megáll a házigazdán');
  const tHost = Date.now() - t0;
  ok(tHost > 7000, '⚠️ LASSÚ: a tárcsa legalább 7 mp-ig pörög', tHost + ' ms');
  ok(await waitPhase(p, 'done', 20000), 'a vendégek is kijönnek (done)');
  ok(Date.now() - t0 > 18000, '⚠️ LASSÚ: a teljes sorsolás 18 mp fölött', (Date.now() - t0) + ' ms');
  const pr = await p.evaluate(() => ({ host: (document.querySelector('[data-torta-host]') || {}).getAttribute && document.querySelector('[data-torta-host]').getAttribute('data-torta-host'), open: [...document.querySelectorAll('[data-torta-gcard][data-open="1"]')].map(x => x.getAttribute('data-torta-gcard')), hostTxt: (document.querySelector('[data-torta-host]') || {}).innerText || '' }));
  ok(pr.open.length === 2 && !pr.open.includes(pr.host), '⚠️ pontosan 2 vendégkártya fordult fel, és nem a házigazda', JSON.stringify(pr.open) + ' / ' + pr.host);
  ok(!/Csapat [A-E]/.test(pr.hostTxt) && /&/.test(pr.hostTxt), 'a házigazda-kártyán NINCS csapatnév, csak a két tag neve', pr.hostTxt.replace(/\s+/g, ' '));
  ok((await store(p, 'tortaDraw')) === null && ((await store(p, 'bingoConfig')).tortaEvenings || []).length === 0, '⚠️ a próba SEMMIT nem mentett');
  await p.evaluate(() => { const b = [...document.querySelectorAll('[data-torta-draw] button')].find(x => x.textContent.trim() === 'Bezárás'); b && b.click(); });
  await p.waitForTimeout(300);
  ok(await p.evaluate(() => !document.querySelector('[data-torta-draw]')), 'a próba bezárható');

  console.log('\n===== 4. ÉLES SORSOLÁS + ELFOGADÁS =====');
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-pin]')), '⚠️ újranyitáskor ÚJRA kéri a PIN-t');
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  await click(p, '[data-torta-livebtn]'); await p.waitForTimeout(400);
  const d1 = await store(p, 'tortaDraw');
  ok(d1 && d1.status === 'pending' && d1.guestIds.length === 2, '⚠️ a húzás a config/tortaDraw-ba került (pending, 2 vendég)', JSON.stringify(d1 && { h: d1.hostId, g: d1.guestIds, s: d1.status }));
  ok(await p.evaluate(() => (document.querySelector('[data-torta-draw]') || {}).getAttribute && document.querySelector('[data-torta-draw]').getAttribute('data-torta-draw') === 'live'), 'az éles show elindul');
  ok(await waitPhase(p, 'done', 30000), 'az éles show végigfut');
  const shown = await p.evaluate(() => ({ host: document.querySelector('[data-torta-host]').getAttribute('data-torta-host'), open: [...document.querySelectorAll('[data-torta-gcard][data-open="1"]')].map(x => x.getAttribute('data-torta-gcard')).sort() }));
  ok(shown.host === d1.hostId && shown.open.join() === d1.guestIds.slice().sort().join(), '⚠️ az animáció PONTOSAN a mentett húzást mutatja', JSON.stringify(shown));
  ok(await click(p, '[data-torta-accept]'), 'az admin „Elfogadom"-ot nyom');
  await p.waitForTimeout(500);
  const cfg1 = await store(p, 'bingoConfig'); const d2 = await store(p, 'tortaDraw');
  const ev = (cfg1.tortaEvenings || [])[0] || {};
  ok(cfg1.tortaEvenings.length === 1 && ev.hostId === d1.hostId && JSON.stringify(ev.guestIds) === JSON.stringify(d1.guestIds), '⚠️ új alkalom a tortaEvenings-ben a húzott felállással', JSON.stringify(ev));
  ok(d2.status === 'accepted', 'a húzás „accepted" lett', d2.status);
  // v10.407: elfogadás után NEM zárul be — „Következő sorsolás" ugyanitt
  const after = await p.evaluate(() => ({ open: !!document.querySelector('[data-torta-draw]'), next: !!document.querySelector('[data-torta-next]'), tag: [...document.querySelectorAll('[data-torta-histtag]')].map(x => x.getAttribute('data-torta-histtag')) }));
  ok(after.open && after.next, '⚠️ elfogadás után a show NYITVA marad „Következő sorsolás" gombbal', JSON.stringify(after));
  ok(after.tag.includes('ELFOGADVA'), 'az oldalsávon az elfogadott este „ELFOGADVA" jelöléssel', JSON.stringify(after.tag));
  await p.evaluate(() => { window.__tortaDrawSpeed = 0.08; });
  await click(p, '[data-torta-next]'); await p.waitForTimeout(300);
  const dNext = await store(p, 'tortaDraw');
  ok(dNext.id !== d1.id && dNext.status === 'pending' && dNext.hostId !== d1.hostId, '⚠️ a „Következő" új húzást indít kilépés nélkül (másik házigazda)', JSON.stringify({ h: dNext.hostId, s: dNext.status }));
  ok(await waitPhase(p, 'done', 6000), 'a következő húzás is végigfut');
  // véletlen éles húzás → Elvetés: nem lesz belőle este
  ok(await click(p, '[data-torta-discard]'), 'Elvetés gomb a függő húzáson');
  await p.waitForTimeout(400);
  ok((await store(p, 'tortaDraw')).status === 'discarded' && ((await store(p, 'bingoConfig')).tortaEvenings || []).length === 1, '⚠️ az elvetett húzásból NEM lett este (marad 1)', (await store(p, 'tortaDraw')).status);
  ok(await p.evaluate(() => !document.querySelector('[data-torta-draw]')), 'elvetés után a show bezárul');

  console.log('\n===== 5. KÉSŐBB NYITÓ TELEFON — NINCS ANIMÁCIÓ =====');
  await p.evaluate(() => { try { localStorage.removeItem('boh_torta_draw_seen'); } catch(e) {}
    window.__fbStore['config'].tortaDraw = { id: 'dLATE', hostId: 'tB', guestIds: ['tC', 'tD'], hostPool: ['tB','tC','tD','tE'], guestPool: ['tA','tC','tD','tE'], startedAt: Date.now() - 60000, status: 'pending' }; });
  await mount(p); await p.waitForTimeout(800);
  const late = await p.evaluate(() => { const d = document.querySelector('[data-torta-draw]'); return d ? { ph: d.getAttribute('data-torta-phase'), open: document.querySelectorAll('[data-torta-gcard][data-open="1"]').length } : null; });
  ok(late && late.ph === 'done' && late.open === 2, '⚠️ a függő húzás rögtön eredményként jön fel (nincs újrajátszott sorsolás)', JSON.stringify(late));
  ok(await p.evaluate(() => !document.querySelector('[data-torta-accept]')), 'újratöltés után PIN nélkül NINCS Elfogadom gomb');
  await p.evaluate(() => { const b = [...document.querySelectorAll('[data-torta-draw] button')].find(x => x.textContent.trim() === 'Bezárás'); b && b.click(); });
  await p.waitForTimeout(300);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-pendingpanel]')), 'PIN után a panel mutatja a függő sorsolást');
  await p.evaluate(() => { const b = [...document.querySelectorAll('[data-torta-pendingpanel] button')].find(x => /Megnézem/.test(x.textContent)); b && b.click(); });
  await p.waitForTimeout(400);
  await p.evaluate(() => { const b = [...document.querySelectorAll('[data-torta-draw] button')].find(x => /Újrasorsolás/.test(x.textContent)); b && b.click(); });
  await p.waitForTimeout(400);
  const d3 = await store(p, 'tortaDraw');
  ok(d3.id !== 'dLATE' && d3.status === 'pending', 'Újrasorsolás → új húzás (új azonosító)', d3.id);
  ok(await p.evaluate(() => { const d = document.querySelector('[data-torta-draw]'); return d && d.getAttribute('data-torta-phase') !== 'done'; }), 'az újrasorsolás újra animál');

  console.log('\n===== 6. ZSÁKUTCA A FELÜLETEN =====');
  await p.evaluate(() => { window.__fbStore['config'].tortaDraw = null;
    window.__fbStore['config'].bingoConfig.tortaEvenings = [
      { id:'x1', hostId:'tA', guestIds:['tB','tC'] }, { id:'x2', hostId:'tB', guestIds:['tC','tD'] },
      { id:'x3', hostId:'tC', guestIds:['tD','tA'] }, { id:'x4', hostId:'tD', guestIds:['tA','tB'] } ]; });
  await mount(p); await p.waitForTimeout(800);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  const blk = await p.evaluate(() => ({ err: (document.querySelector('[data-torta-drawerr]') || {}).innerText || '', dis: document.querySelector('[data-torta-livebtn]').disabled && document.querySelector('[data-torta-practicebtn]').disabled }));
  ok(/Zsákutca/.test(blk.err) && blk.dis, '⚠️ a panel kiírja a zsákutcát, mindkét gomb tiltva', blk.err.slice(0, 60));

  console.log('\n===== 7. NINCS ADMIN PIN → NEM SORSOLHAT =====');
  await p.evaluate(() => { window.getAdminPin = () => Promise.resolve(''); });
  await p.evaluate(() => { const b = document.querySelector('[data-torta-drawpanel]'); if (b) { const x = [...document.querySelectorAll('button')].find(y => y.getAttribute('aria-label') === 'Bezárás'); x && x.click(); } });
  await mount(p); await p.waitForTimeout(700);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-nopin]') && !document.querySelector('[data-torta-livebtn]')), '⚠️ beállított PIN nélkül nem enged sorsolni');

  console.log('\n===== 8. WEB: 2/3 SORSOLÁS · 1/3 KISORSOLT ESTÉK =====');
  await p.setViewportSize({ width: 1440, height: 900 });
  await p.evaluate(() => { window.getAdminPin = () => Promise.resolve('1234'); window.__tortaDrawSpeed = 1;
    window.__fbStore['config'].bingoConfig.tortaEvenings = [{ id:'h1', hostId:'tA', guestIds:['tB','tC'] }, { id:'h2', hostId:'tB', guestIds:['tC','tD'] }];
    window.__fbStore['config'].tortaDraw = null; });
  await mount(p); await p.waitForTimeout(700);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  await click(p, '[data-torta-practicebtn]'); await p.waitForTimeout(800);
  const lay = await p.evaluate(() => {
    const d = document.querySelector('[data-torta-draw]'), st = document.querySelector('[data-torta-stage]'), h = document.querySelector('[data-torta-history]');
    const reel = [...d.querySelectorAll('div')].find(x => x.style.overflow === 'hidden' && x.style.height);
    return { wide: d.getAttribute('data-torta-wide'), stage: st.getBoundingClientRect().width, hist: h.getBoundingClientRect().width, histLeft: h.getBoundingClientRect().left, rows: h.querySelectorAll('[data-torta-hist]').length, reelW: reel ? reel.getBoundingClientRect().width : 0,
      guestBottom: Math.max(0, ...[...d.querySelectorAll('[data-torta-gcard]')].map(x => x.getBoundingClientRect().bottom)),
      guestRight: Math.max(0, ...[...d.querySelectorAll('[data-torta-gcard]')].map(x => x.getBoundingClientRect().right)) };
  });
  ok(lay.wide === '1', 'széles képernyőn a 2/3–1/3 elrendezés él');
  ok(Math.abs(lay.stage / (lay.stage + lay.hist) - 2 / 3) < 0.03, '⚠️ a sorsolás a szélesség 2/3-a, a lista 1/3', `${Math.round(lay.stage)} : ${Math.round(lay.hist)}`);
  ok(lay.histLeft > lay.stage - 2, 'a kisorsolt esték JOBBRA állnak');
  ok(lay.rows === 2, '⚠️ az oldalsávon a 2 már kisorsolt este', lay.rows);
  ok(lay.reelW > 300, '⚠️ weben NAGYOBB a sorsolás (tárcsa > 300 px; mobilon 230)', Math.round(lay.reelW));
  ok(lay.guestBottom <= 900 && lay.guestRight <= lay.stage + 1, '⚠️ a vendég-blokk kifér (nem lóg le, nem lóg a listára)', `alja ${Math.round(lay.guestBottom)}, jobb ${Math.round(lay.guestRight)}`);

  console.log('\n===== 9. PRÓBASZEZON EGYMÁS UTÁN, KILÉPÉS NÉLKÜL =====');
  await p.setViewportSize({ width: 402, height: 1400 });
  await p.evaluate(() => { window.__tortaDrawSpeed = 0.06; window.__fbStore['config'].bingoConfig.tortaEvenings = []; window.__fbStore['config'].tortaDraw = null; });
  await mount(p); await p.waitForTimeout(700);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  await click(p, '[data-torta-practicebtn]');
  const hosts = []; let guard = 0;
  for (;;) {
    if (!(await waitPhase(p, 'done', 5000))) break;
    hosts.push(await p.evaluate(() => document.querySelector('[data-torta-host]').getAttribute('data-torta-host')));
    if (await p.evaluate(() => !!document.querySelector('[data-torta-seasondone]')) || ++guard > 8) break;
    await click(p, '[data-torta-next]'); await p.waitForTimeout(250);
  }
  ok(hosts.length === 5 && new Set(hosts).size === 5, '⚠️ 5 próba-húzás egymás után, mindegyik más házigazdával', hosts.join(','));
  const ph = await p.evaluate(() => ({ tags: [...document.querySelectorAll('[data-torta-histtag]')].map(x => x.getAttribute('data-torta-histtag')), done: !!document.querySelector('[data-torta-seasondone]'), next: !!document.querySelector('[data-torta-next]') }));
  ok(ph.done && !ph.next, 'a végén „próbaszezon kész", nincs több Következő', JSON.stringify(ph));
  ok(ph.tags.filter(t => t === 'PRÓBA').length === 5, 'az oldalsávon mind az 5 próba-este PRÓBA jelöléssel', JSON.stringify(ph.tags));
  ok((await store(p, 'tortaDraw')) === null && (await store(p, 'bingoConfig')).tortaEvenings.length === 0, '⚠️ a próbaszezonból SEMMI nem mentődött');

  console.log('\n===== 10. VISSZAVONÁS (VÉLETLEN ELFOGADÁS) =====');
  await p.evaluate(() => { const x = [...document.querySelectorAll('[data-torta-draw] button')].find(y => y.textContent.trim() === 'Bezárás'); x && x.click(); });
  await p.evaluate(() => {
    window.__fbStore['config'].bingoConfig.tortaEvenings = [{ id:'eX', date:'', hostId:'tA', guestIds:['tB','tC'], locked:false }];
    window.__fbStore['config'].tortaDraw = { id:'dX', hostId:'tA', guestIds:['tB','tC'], status:'accepted', eveningId:'eX', startedAt: 1 };
    window.__fbStore['config'].tortaScores = {};
  });
  await mount(p); await p.waitForTimeout(700);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  ok(await click(p, '[data-torta-undo]'), 'a panelen „Visszavonás" az utolsó elfogadott sorsolásra');
  await p.waitForTimeout(400);
  ok((await store(p, 'bingoConfig')).tortaEvenings.length === 0 && (await store(p, 'tortaDraw')).status === 'undone', '⚠️ visszavonva: az este törlődött, a húzás „undone"');
  // ha már pontoztak rá, NEM vonható vissza
  await p.evaluate(() => {
    window.__fbStore['config'].bingoConfig.tortaEvenings = [{ id:'eY', date:'', hostId:'tA', guestIds:['tB','tC'], locked:false }];
    window.__fbStore['config'].tortaDraw = { id:'dY', hostId:'tA', guestIds:['tB','tC'], status:'accepted', eveningId:'eY', startedAt: 1 };
    window.__fbStore['config'].tortaScores = { eY: { p2: { etel: 5 } } };
  });
  await mount(p); await p.waitForTimeout(700);
  await click(p, '[data-torta-drawbtn]'); await p.waitForTimeout(400);
  await setInput(p, '[data-torta-pin]', '1234'); await click(p, '[data-torta-pinok]'); await p.waitForTimeout(300);
  ok(await p.evaluate(() => !!document.querySelector('[data-torta-undopanel]') && !document.querySelector('[data-torta-undo]')), 'pontozott estére nincs visszavonás gomb (az Adminban törölhető)');

  ok(errs.length === 0, 'nincs JS hiba', errs.join(' | '));
  await b.close();
  console.log(fail ? '\n❌ ' + fail + ' HIBA' : '\n✅ MINDEN ELLENORZES RENDBEN');
  process.exit(fail ? 1 : 0);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
