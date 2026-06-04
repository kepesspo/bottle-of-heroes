with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# Call onAdvance when card is chosen (reveal phase), remove Tovább button
old = "  const choose = (idx) => { setChosenIdx(idx); setPhase('reveal'); };"
new = "  const choose = (idx) => { setChosenIdx(idx); setPhase('reveal'); onAdvance && onAdvance({}); };"
assert old in html, "choose not found"
html = html.replace(old, new, 1)

# Remove Tovább button
old = """
          <button onClick={() => onAdvance && onAdvance({})} style={{ padding:'12px 28px', background:T.mint, color:'#fff', fontFamily:T.font, fontWeight:700, fontSize:15, borderRadius:14, border:'none', cursor:'pointer', boxShadow:T.shadow }}>
            Tovább →
          </button>"""
new = ""
assert old in html, "Tovabb button not found"
html = html.replace(old, new, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
