// v10.151 — Betöltés: méret, külső kérések, hangok
//
// Ez a teszt nem funkciót őriz, hanem a BULI-BETÖLTÉST. Két dolog rontja el:
//  - a fájlméret (minden verzióbump teljes újratöltés a service worker miatt),
//  - a blokkoló, harmadik feles CDN-kérés (nincs a SW cache-ében, rossz
//    mobilneten megállítja az indulást).
// Mindkettőre felső korlát van, hogy ne csússzon vissza észrevétlenül.
const { chromium } = require('/opt/node22/lib/node_modules/playwright');
const fs = require('fs');
const path = require('path');
const stub = fs.readFileSync(__dirname + '/fbstub.js', 'utf8');
const ROOT = '/home/user/bottle-of-heroes';
const BASE = 'file://' + ROOT + '/index.html';

// Amit az app JOGGAL tölt le indulaskor. Minden mas harmadik feles keres hiba.
const ALLOWED = [/^https:\/\/www\.gstatic\.com\/firebasejs\//];  // a betutipus mar helyben van

const MAX_MB = 2.20;          // jelenleg 2.05 MB — a fejter ne kusszon vissza
const MAX_AUDIO_KB = 80;      // a ket nagy hang MP3-ban ~53 KB base64 (WAV-ban 471 KB volt)

const seed = `
  try { localStorage.setItem('boh_onboarded','1'); } catch(e){}
  window.__fbStore['profiles'] = {}; window.__fbStore['stats'] = {};
  window.__fbStore['game_stats'] = {}; window.__fbStore['statEvents'] = {};
  window.__fbStore['gameStatEvents'] = {}; window.__fbStore['seasons'] = {};
  window.__fbStore['config'] = {}; window.__fbStore['usage'] = {};
`;

(async () => {
  let fail = 0;
  const ok = (l, c, e) => { console.log((c ? '  OK   ' : '  HIBA ') + l + (e !== undefined ? '  → ' + e : '')); if (!c) fail++; };

  // ── Fajlmeret es a beagyazott hang ─────────────────────────────────────
  console.log('===== MERET =====');
  const html = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8');
  const bytes = Buffer.byteLength(html);
  ok(`index.html <= ${MAX_MB} MB`, bytes / 1048576 <= MAX_MB, `${(bytes / 1048576).toFixed(2)} MB`);

  const blobs = html.match(/[A-Za-z0-9+/]{4000,}={0,2}/g) || [];
  const audioKb = blobs.reduce((a, b) => a + b.length, 0) / 1024;
  ok(`a beagyazott hang <= ${MAX_AUDIO_KB} KB (tomoritett, nem nyers WAV)`, audioKb <= MAX_AUDIO_KB, `${audioKb.toFixed(0)} KB, ${blobs.length} blob`);
  ok('nincs tobb nyers WAV data URI a fajlban', !/data:audio\/wav;base64,[A-Za-z0-9+/]{20000,}/.test(html));

  // ── Blokkolo kulso script tagek ────────────────────────────────────────
  const tags = (html.match(/<script src="https:\/\/[^"]*"/g) || []).map(x => x.replace(/^<script src="|"$/g, ''));
  const unexpected = tags.filter(u => !ALLOWED.some(rx => rx.test(u)));
  ok('csak a Firebase toltodik blokkolva', unexpected.length === 0, unexpected.join(' | ') || `${tags.length} tag, mind engedelyezett`);

  // ── Valos betoltes: mit ker le tenylegesen ─────────────────────────────
  console.log('\n===== BETOLTES =====');
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium-1194/chrome-linux/chrome' });
  const p = await b.newPage({ viewport: { width: 390, height: 844 } });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const requested = [];
  p.on('request', r => { const u = r.url(); if (!u.startsWith('file://') && !u.startsWith('data:') && !u.startsWith('blob:')) requested.push(u); });
  await p.route('**://**', r => r.request().url().startsWith('file://') ? r.continue() : r.abort());
  await p.addInitScript(stub);
  await p.addInitScript(seed);
  await p.goto(BASE, { waitUntil: 'domcontentloaded' });
  await p.waitForFunction(() => { const r = document.getElementById('root'); return r && r.children.length > 0; }, { timeout: 30000 });
  await p.waitForTimeout(3000);

  const third = requested.filter(u => !ALLOWED.some(rx => rx.test(u)));
  ok('indulaskor NEM ker le Spotify SDK-t', !third.some(u => /scdn\.co|open\.spotify\.com/.test(u)), third.filter(u => /spotify/.test(u)).join(' | ') || 'nincs');
  ok('indulaskor NEM ker le html2canvas-t', !third.some(u => /html2canvas/.test(u)), third.filter(u => /html2canvas/.test(u)).join(' | ') || 'nincs');
  ok('indulaskor NEM ker le qrcode konyvtarat', !third.some(u => /qrcode/.test(u)), third.filter(u => /qrcode/.test(u)).join(' | ') || 'nincs');
  ok('semmilyen egyeb harmadik feles keres', third.length === 0, third.slice(0, 4).join(' | ') || 'nincs');

  // ── A betutipus helyben van, es a magyar ekezetek is megvannak ─────────
  console.log('\n===== BETUTIPUS =====');
  const font = await p.evaluate(async () => {
    const faces = Array.from(document.fonts).map(f => ({ family: f.family, weight: f.weight, status: f.status }));
    await document.fonts.ready;
    const loaded = Array.from(document.fonts).filter(f => f.status === 'loaded').map(f => f.family);
    // szelesseg-osszehasonlitas: ha a Nunito tenyleg betoltott, mas a szoveg
    // szelessege, mint a tartalek sans-serifnel
    const meas = (fam) => {
      const c = document.createElement('canvas').getContext('2d');
      c.font = '700 32px ' + fam;
      return Math.round(c.measureText('Kőbányai sörözőben űzött 5 pont').width);
    };
    return { faces, loaded, nunito: meas("Nunito, sans-serif"), fallback: meas("sans-serif"),
             acc: meas("Nunito, sans-serif") > 0 };
  });
  ok('a Nunito @font-face deklaralva van (2 subset)', font.faces.filter(f => /Nunito/.test(f.family)).length === 2, JSON.stringify(font.faces));
  ok('a Nunito betoltott (helyi fajlbol)', font.loaded.some(f => /Nunito/.test(f)), JSON.stringify(font.loaded));
  ok('a magyar ekezetes szoveg a Nunitoval rendezodik (nem tartalek)', font.nunito !== font.fallback && font.nunito > 0, `nunito=${font.nunito}px fallback=${font.fallback}px`);

  // ── A hangok ervenyes, lejatszhato MP3-ak ──────────────────────────────
  console.log('\n===== HANGOK =====');
  const snd = await p.evaluate(async () => {
    const out = {};
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const grab = (re) => {
      const m = document.documentElement.innerHTML.match(re);
      return m ? m[1] : null;
    };
    const b64s = (document.documentElement.innerHTML.match(/[A-Za-z0-9+/]{4000,}={0,2}/g) || []);
    out.n = b64s.length;
    out.decoded = [];
    for (const b of b64s.slice(0, 4)) {
      try {
        const bin = atob(b); const arr = new Uint8Array(bin.length);
        for (let i = 0; i < bin.length; i++) arr[i] = bin.charCodeAt(i);
        const buf = await ctx.decodeAudioData(arr.buffer);
        out.decoded.push({ kb: Math.round(b.length / 1024), sec: +buf.duration.toFixed(2), ch: buf.numberOfChannels });
      } catch (e) { out.decoded.push({ kb: Math.round(b.length / 1024), err: String(e).slice(0, 50) }); }
    }
    return out;
  });
  ok('mindkét nagy hang dekódolható (érvényes MP3)', snd.decoded.length >= 2 && snd.decoded.every(d => !d.err), JSON.stringify(snd.decoded));
  ok('a hosszuk valtozatlan maradt (~2,5 mp és ~3,2 mp)',
     snd.decoded.some(d => d.sec > 2.3 && d.sec < 2.7) && snd.decoded.some(d => d.sec > 3.0 && d.sec < 3.4),
     JSON.stringify(snd.decoded.map(d => d.sec)));
  ok('nincs JS hiba', errs.filter(e => !/ServiceWorker/.test(e)).length === 0, errs.join(' | '));
  await p.close();
  await b.close();

  console.log('\n' + (fail === 0 ? '✅ MINDEN ELLENORZES RENDBEN' : '❌ ' + fail + ' ELLENORZES BUKOTT'));
  process.exit(fail === 0 ? 0 : 1);
})().catch(e => { console.error('CRASH', e); process.exit(1); });
