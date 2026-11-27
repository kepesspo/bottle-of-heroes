# v10.477 (3. rész) — hosszú szavak elválasztása (magyar szótag-határ, puha kötőjel) + sor-ellenőrzés
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("""function bingoTextFont(t, s, cellW, font) {
  const cap = s === 4 ? 17 : 13.5;
  const room = Math.max(30, (cellW || (s === 4 ? 84 : 64)) - 10);
  const words = String(t || '').split(/\\s+/).filter(Boolean);
  const widest = Math.max(0.5, ...words.map(w => bingoWordW(w, font || 'sans-serif')));
  return Math.max(7, Math.min(cap, Math.floor(room / widest * 10) / 10));
}""",
"""// Magyar elválasztás egy helyen: mássalhangzó + magánhangzó ELŐTT (a kétjegyű betű — sz, cs, gy…
// — együtt marad). A legkiegyensúlyozottabb vágás nyer. Puha kötőjellel (U+00AD) tesszük be:
// a böngésző CSAK akkor tör ott, ha kell, és akkor kiírja a kötőjelet.
const BINGO_VOW = 'aáeéiíoóöőuúüűAÁEÉIÍOÓÖŐUÚÜŰ';
const BINGO_DIGRAPHS = ['sz', 'cs', 'gy', 'ny', 'ty', 'ly', 'zs', 'dz'];
function bingoHyphenCuts(w) {
  const out = [];
  for (let i = 2; i < w.length - 2; i++) {
    const c = w[i], n = w[i + 1];
    if (BINGO_VOW.indexOf(c) >= 0 || BINGO_VOW.indexOf(n) < 0 || !/[a-zA-ZÀ-ž]/.test(c)) continue;
    const cut = BINGO_DIGRAPHS.indexOf((w[i - 1] + c).toLowerCase()) >= 0 ? i - 1 : i;
    if (cut >= 2 && out.indexOf(cut) < 0) out.push(cut);
  }
  return out;
}
// → { size, text } — a szöveg a puha kötőjellel (ha az elválasztás nagyobb betűt ad)
function bingoFitText(t, s, cellW, font) {
  const f = font || 'sans-serif', cap = s === 4 ? 17 : 13.5;
  const room = Math.max(30, (cellW || (s === 4 ? 84 : 64)) - 10);
  const words = String(t || '').split(/\\s+/).filter(Boolean);
  const W = x => bingoWordW(x, f);
  // a sorok száma adott méretnél (mohó tördelés, a darabok a szavak/szótag-darabok)
  const lines = (pieces, size) => { let n = 1, cur = 0; const sp = W(' ');
    pieces.forEach(p => { const w = p.w * size, gap = cur ? sp * size : 0;
      if (cur && cur + gap + w > room) { n++; cur = w; } else cur += gap + w; });
    return n; };
  const fit = pieces => {
    const widest = Math.max(0.5, ...pieces.map(p => p.w));
    let size = Math.min(cap, room / widest);
    // a mező magassága is szab: n sor × 1,1 sorköz ≤ room
    for (let k = 0; k < 6 && lines(pieces, size) * size * 1.1 > room; k++) size *= 0.92;
    return Math.max(7, Math.floor(size * 10) / 10);
  };
  const plain = words.map(w => ({ w: W(w) }));
  let best = { size: fit(plain), text: words.join(' ') };
  if (best.size >= cap * 0.85) return best;
  // a leghosszabb szót elválasztjuk, ha attól nagyobb lesz a betű
  const li = plain.reduce((m, p, i) => p.w > plain[m].w ? i : m, 0), lw = words[li];
  bingoHyphenCuts(lw).forEach(cut => {
    const a = lw.slice(0, cut), b = lw.slice(cut);
    const pieces = plain.slice(0, li).concat([{ w: W(a + '-') }, { w: W(b) }], plain.slice(li + 1));
    const size = fit(pieces);
    if (size > best.size + 0.3) best = { size, text: words.slice(0, li).concat([a + '\\u00AD' + b], words.slice(li + 1)).join(' ') };
  });
  return best;
}
function bingoTextFont(t, s, cellW, font) { return bingoFitText(t, s, cellW, font).size; }""")

rep("""                    const k = free ? 0 : bingoK(item), txt = free ? bingoCenter.t : item.t;""",
    """                    const k = free ? 0 : bingoK(item), txt = free ? bingoCenter.t : item.t;
                    const fitT = bingoFitText(txt, grid.s, gridW ? (gridW - 6 * (grid.s - 1)) / grid.s : 0, T.font);""")
rep("""fontSize: bingoTextFont(txt, grid.s, gridW ? (gridW - 6 * (grid.s - 1)) / grid.s : 0, T.font), lineHeight:1.08, textAlign:'center', color: free ? '#1A2A4A' : T.ink, wordBreak:'break-word' }}>{txt}</span>""",
    """fontSize: fitT.size, lineHeight:1.08, textAlign:'center', color: free ? '#1A2A4A' : T.ink, hyphens:'manual', WebkitHyphens:'manual' }}>{fitT.text}</span>""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
