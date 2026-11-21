// Gender Reveal logó (v10.460) — „A · Lufipár": rózsaszín + kék lufi, közös masni,
// a DNR ikon-nyelvén (kék|narancs félkör, talajvonal, fekete kontúr, fehér matrica-sáv).
// Futtatás: node make_reveal_logo.js  → assets/dnr_reveal_logo_app.png (1024, fehér háttér)
//                                     + assets/dnr_reveal_logo_mark.png (512, átlátszó)
// ⚠️ Új tartalom = új fájlnév (CLAUDE.md v10.424) — a régi dnr_reveal_app/mark néven NE írd felül.
const fs = require('fs'), { chromium } = require('playwright');
const ROOT = __dirname;
const INK='#0A0C0E', BLUE='#86A7CA', ORANGE='#FDAA45', PINK='#F496B4', BABY='#96C8F0', CREAM='#FFF7E8', YEL='#FDCD65';
const LW=22, ST=LW+34;
const FONT='data:font/woff2;base64,'+fs.readFileSync(ROOT+'/assets/fonts/nunito-latin.woff2').toString('base64');
const bg = `
  <path d="M112,850 L112,650 A400,400 0 0 1 512,250 L512,850 Z" fill="${BLUE}"/>
  <path d="M912,850 L912,650 A400,400 0 0 0 512,250 L512,850 Z" fill="${ORANGE}"/>`;
const ground = `<rect x="120" y="842" width="784" height="20" rx="10" fill="${INK}"/>`;
// a tárgyat kétszer rajzoljuk: először vastag fehér „matricával", aztán rendesen
const sticker = obj => `<g style="--s:1">${obj.replace(/stroke-width="[\d.]+"/g, 'stroke-width="'+ST+'"').replace(/stroke="#0A0C0E"/g,'stroke="#fff"').replace(/fill="(?!none)[^"]+"/g,'fill="#fff"')}</g>${obj}`;
const conf = (x,y,c,r=0,w=26,h=12) => `<rect x="${x-w/2}" y="${y-h/2}" width="${w}" height="${h}" rx="4" fill="${c}" transform="rotate(${r} ${x} ${y})"/>`;
const dot = (x,y,c,r=11) => `<circle cx="${x}" cy="${y}" r="${r}" fill="${c}" stroke="${INK}" stroke-width="7"/>`;

// ── A: Lufipár masnival ──
const balloon = (cx,cy,rot,fill) => `<g transform="rotate(${rot} ${cx} ${cy})">
  <path d="M${cx-16},${cy+192} L${cx+16},${cy+192} L${cx+8},${cy+176} L${cx-8},${cy+176} Z" fill="${fill}" stroke="${INK}" stroke-width="${LW}" stroke-linejoin="round"/>
  <ellipse cx="${cx}" cy="${cy}" rx="148" ry="178" fill="${fill}" stroke="${INK}" stroke-width="${LW}"/>
  <path d="M${cx-92},${cy-58} Q${cx-78},${cy-128} ${cx-20},${cy-148}" fill="none" stroke="#fff" stroke-width="20" stroke-linecap="round" opacity=".9"/>
  <circle cx="${cx-100}" cy="${cy-12}" r="11" fill="#fff" opacity=".9"/></g>`;
const A_obj = `
  <path d="M424,640 C430,700 470,740 512,770" fill="none" stroke="${INK}" stroke-width="10" stroke-linecap="round"/>
  <path d="M600,612 C596,690 556,740 512,770" fill="none" stroke="${INK}" stroke-width="10" stroke-linecap="round"/>
  ${balloon(632,410,12,BABY)}
  ${balloon(392,440,-12,PINK)}
  <path d="M512,770 C470,730 430,745 440,780 C448,808 486,800 512,770 Z" fill="${PINK}" stroke="${INK}" stroke-width="16" stroke-linejoin="round"/>
  <path d="M512,770 C554,730 594,745 584,780 C576,808 538,800 512,770 Z" fill="${BABY}" stroke="${INK}" stroke-width="16" stroke-linejoin="round"/>
  <path d="M506,772 L486,822 M518,772 L540,822" stroke="${INK}" stroke-width="12" stroke-linecap="round"/>
  <circle cx="512" cy="772" r="15" fill="${YEL}" stroke="${INK}" stroke-width="12"/>`;
const A = bg + sticker(A_obj) + ground + conf(250,215,YEL,-20) + conf(785,190,PINK,25) + conf(840,330,YEL,10) + dot(512,150,BABY,12) + dot(200,330,PINK,9);


const svg = (inner, bgFill, px) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="${px}" height="${px}">
${bgFill ? `<rect width="1024" height="1024" fill="${bgFill}"/>` : ''}${inner}</svg>`;
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport:{ width:1024, height:1024 } });
  for (const [bgFill, px, name] of [['#fff', 1024, 'app'], ['', 512, 'mark']]) {
    await p.setViewportSize({ width:px, height:px });
    await p.setContent(`<html><body style="margin:0;background:transparent">${svg(A, bgFill, px)}</body></html>`);
    await p.waitForTimeout(200);
    await p.screenshot({ path: ROOT + '/assets/dnr_reveal_logo_' + name + '.png', clip:{ x:0, y:0, width:px, height:px }, omitBackground: !bgFill });
  }
  await b.close();
})();
