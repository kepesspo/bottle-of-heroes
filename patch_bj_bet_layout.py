#!/usr/bin/env python3
# v9.805: BJ betting layout — single chip display
import io

P = '/home/user/bottle-of-heroes/index.html'
c = io.open(P, encoding='utf-8').read()

# 1. Én sáv: hide Tét + chip stack during betting
OLD1 = """          {bj.phase !== 'joining' && (
            <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:8 }}>
              {inRound && <span style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.inkSoft }}>Tét: {myBet}</span>}
              <BJChipStack count={myChips} size={54} />
            </span>
          )}"""
NEW1 = """          {bj.phase !== 'joining' && bj.phase !== 'betting' && (
            <span style={{ marginLeft:'auto', display:'flex', alignItems:'center', gap:8 }}>
              {inRound && <span style={{ fontFamily:T.font, fontSize:13, fontWeight:T.weightTitle, color:T.inkSoft }}>Tét: {myBet}</span>}
              <BJChipStack count={myChips} size={54} />
            </span>
          )}"""
assert OLD1 in c and c.count(OLD1) == 1
c = c.replace(OLD1, NEW1)

# 2. Betting card: subtitle + labeled chip stack
OLD2 = """            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:12 }}>A tét a kortykészletedből megy — max {myChips} 🍺</div>
            <div style={{ display:'flex', justifyContent:'center', marginBottom:14 }}><BJChipStack count={myChips} size={44} /></div>"""
NEW2 = """            <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginBottom:12 }}>Ha veszítesz, ennyit iszol — ha nyersz, ennyivel nő a kupacod!</div>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'center', gap:8, marginBottom:14 }}><span style={{ fontFamily:T.font, fontSize:12, fontWeight:T.weightTitle, color:T.inkSoft }}>Készleted</span><BJChipStack count={myChips} size={44} /></div>"""
assert OLD2 in c and c.count(OLD2) == 1
c = c.replace(OLD2, NEW2)

# 3. Version bump
assert c.count('v9.804') >= 1, c.count('v9.804')
n = c.count('v9.804')
c = c.replace('v9.804', 'v9.805')
print('version occurrences bumped:', n)

io.open(P, 'w', encoding='utf-8').write(c)
print('patch OK')
