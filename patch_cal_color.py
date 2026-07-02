import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Change EV_COLOR to mint green
OLD1 = "  const EV_COLOR = '#E8631A';"
NEW1 = "  const EV_COLOR = '#25b572';"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Rewrite the cell bar rendering: same solid bar for all, stripe overlay for multi-day
OLD2 = '''                {entries.slice(0,2).map(({ev,role},ri) => {
                  const col = EV_COLOR;
                  const isSingle = role==='single';
                  const isStart = role==='start';
                  const isEnd = role==='end';
                  const isMid = role==='mid';
                  return (
                    <div key={ri} style={{
                      width: isSingle ? '70%' : '100%',
                      height:4, marginBottom:1,
                      background: isTod ? 'rgba(255,255,255,0.7)' : col,
                      borderRadius: isSingle ? 3 : isStart ? '3px 0 0 3px' : isEnd ? '0 3px 3px 0' : 0,
                      marginLeft: isEnd||isMid ? 0 : undefined,
                      marginRight: isStart||isMid ? 0 : undefined,
                    }} />
                  );
                })}'''

NEW2 = '''                {entries.slice(0,2).map(({ev,role},ri) => {
                  const isSingle = role==='single';
                  const isStart = role==='start';
                  const isEnd = role==='end';
                  const isMid = role==='mid';
                  const isMultiDay = !isSingle;
                  const barColor = isTod ? 'rgba(255,255,255,0.7)' : EV_COLOR;
                  return (
                    <div key={ri} style={{
                      position:'relative', overflow:'hidden',
                      width: isSingle ? '70%' : '100%',
                      height:5, marginBottom:1,
                      background: barColor,
                      borderRadius: isSingle ? 3 : isStart ? '3px 0 0 3px' : isEnd ? '0 3px 3px 0' : 0,
                      marginLeft: isEnd||isMid ? 0 : undefined,
                      marginRight: isStart||isMid ? 0 : undefined,
                    }}>
                      {isMultiDay && <div style={{ position:'absolute', top:0, left:0, right:0, bottom:0, background:'repeating-linear-gradient(90deg, transparent 0px, transparent 5px, rgba(255,255,255,0.45) 5px, rgba(255,255,255,0.45) 7px)' }} />}
                    </div>
                  );
                })}'''

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. List items below calendar: color stripe + badge also green
# Already uses `col` variable which is EV_COLOR — already updated to green above
# Also update the today cell background: keep orange for today
# (already uses '#E8631A' for isTod bg — keep that, only EV_COLOR changes)

# version bump
content = re.sub(r'v9\.688', 'v9.689', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.689")
