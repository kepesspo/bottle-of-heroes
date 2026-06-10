#!/usr/bin/env python3
"""v8.63: BP manuális sorsolásszerkesztő — online módban is elérhető"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """              {mode !== 'Online' && (
                <button onClick={() => {
                  const ep = (MODE === 'csapat' && teamsReady && teamPlayersRef.current) ? teamPlayersRef.current : players;
                  setManualEdit(ep);
                }} title="Manuális sorsolás" style={{ width:28, height:28, borderRadius:8, border:'none', cursor:'pointer', background:'rgba(20,30,50,0.07)', display:'grid', placeItems:'center', fontSize:14 }}>✏️</button>
              )}"""

NEW = """              <button onClick={() => {
                  const ep = (MODE === 'csapat' && teamsReady && teamPlayersRef.current) ? teamPlayersRef.current : players;
                  setManualEdit(ep);
                }} title="Manuális sorsolás" style={{ width:28, height:28, borderRadius:8, border:'none', cursor:'pointer', background:'rgba(20,30,50,0.07)', display:'grid', placeItems:'center', fontSize:14 }}>✏️</button>"""

assert OLD in content, "mode check not found"
content = content.replace(OLD, NEW, 1)
print("✓ Online mód korlát eltávolítva")

OLD_VER = "const APP_VERSION = 'v8.62';"
NEW_VER = "const APP_VERSION = 'v8.63';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.63 saved")
