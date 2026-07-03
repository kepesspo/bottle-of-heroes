import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add touched state for title validation
OLD1 = "  function submit() {\n    if (!title.trim() || saving) return;\n    setSaving(true);"
NEW1 = "  const [titleTouched, setTitleTouched] = React.useState(false);\n  const titleErr = titleTouched && !title.trim();\n\n  function submit() {\n    if (!title.trim() || saving) { setTitleTouched(true); return; }\n    setSaving(true);"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# Update the title field to show error state
OLD2 = """      {/* Név */}
      <div style={card}>
        {label('Esemény neve')}
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="pl. Pénteki parti" style={inpStyle} />
      </div>"""
NEW2 = """      {/* Név */}
      <div style={{ ...card, border: titleErr ? '1.5px solid #ef4444' : '1.5px solid transparent' }}>
        <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:8 }}>
          {label('Esemény neve')}
          {titleErr && <div style={{ fontFamily:T.font, fontSize:11, color:'#ef4444', fontWeight:700 }}>Kötelező mező</div>}
        </div>
        <input value={title} onChange={e => { setTitle(e.target.value); setTitleTouched(true); }} onBlur={() => setTitleTouched(true)} placeholder="pl. Pénteki parti" style={{ ...inpStyle, outline: titleErr ? '1.5px solid #ef4444' : 'none' }} />
      </div>"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

content = re.sub(r'v9\.719', 'v9.720', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.720")
