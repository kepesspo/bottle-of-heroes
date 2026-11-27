# v10.477 (2. rész) — az ikon nélküli mező betűmérete MÉRT szóhosszból, a mező valódi szélességéhez.
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old)
    assert n == cnt, (n, old[:90])
    s = s.replace(old, new)

rep("""// Ikon nélküli mező betűmérete: a LEGHOSSZABB szó férjen ki egy sorba (a szótörés csúnya).
// A Nunito 800 átlagos betűszélessége ~0,56 em; a hasznos szélesség 5×5-ön ~58, 4×4-en ~78 px.
function bingoTextFont(t, s) {
  const w = Math.max(1, ...String(t || '').split(/\\s+/).map(x => x.length));
  const room = s === 4 ? 78 : 58, cap = s === 4 ? 17 : 13.5;
  return Math.max(7, Math.min(cap, Math.floor(room / (0.56 * w) * 10) / 10));
}""",
"""// Ikon nélküli mező betűmérete: a LEGHOSSZABB szó férjen ki egy sorba (a szótörés csúnya —
// „Csapatmunk|a"). A szót canvason MÉRJÜK (900-as súly), és a mező tényleges szélességéhez
// igazítjuk; becsült betűszélességgel a keskeny/széles betűk miatt hol tört, hol túl kicsi lett.
const _bingoMeasure = { ctx: null, cache: {} };
function bingoWordW(word, font) {
  const key = font + '|' + word;
  if (_bingoMeasure.cache[key] != null) return _bingoMeasure.cache[key];
  try {
    if (!_bingoMeasure.ctx) _bingoMeasure.ctx = document.createElement('canvas').getContext('2d');
    _bingoMeasure.ctx.font = '900 100px ' + font;
    return (_bingoMeasure.cache[key] = _bingoMeasure.ctx.measureText(word).width / 100);
  } catch (e) { return word.length * 0.6; }
}
function bingoTextFont(t, s, cellW, font) {
  const cap = s === 4 ? 17 : 13.5;
  const room = Math.max(30, (cellW || (s === 4 ? 84 : 64)) - 10);
  const words = String(t || '').split(/\\s+/).filter(Boolean);
  const widest = Math.max(0.5, ...words.map(w => bingoWordW(w, font || 'sans-serif')));
  return Math.max(7, Math.min(cap, Math.floor(room / widest * 10) / 10));
}""")

rep("""  const [profOpen, setProfOpen] = React.useState(false);""",
"""  const [profOpen, setProfOpen] = React.useState(false);
  // v10.477: a rács szélessége (a mező-betűméret ehhez igazodik) + újramérés a webfont betöltése után
  const [gridW, setGridW] = React.useState(0);
  const [, setFontTick] = React.useState(0);
  const gridRef = React.useCallback(el => {
    if (!el) return;
    const upd = () => setGridW(el.getBoundingClientRect().width);
    upd();
    if (typeof ResizeObserver !== 'undefined') new ResizeObserver(upd).observe(el);
  }, []);
  React.useEffect(() => {
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(() => { _bingoMeasure.cache = {}; setFontTick(t => t + 1); }).catch(() => {});
  }, []);""")

rep("""            <div data-bingo-grid={grid.s} style={{ display:'grid',""",
    """            <div ref={gridRef} data-bingo-grid={grid.s} style={{ display:'grid',""")
rep("""fontSize: bingoTextFont(txt, grid.s), lineHeight:1.08""",
    """fontSize: bingoTextFont(txt, grid.s, gridW ? (gridW - 6 * (grid.s - 1)) / grid.s : 0, T.font), lineHeight:1.08""")
open(P, 'w', encoding='utf-8').write(s)
print('OK')
