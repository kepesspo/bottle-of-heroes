with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

orig = html

# Fix "Tipped leadva" color — T.yellow is invisible on warm yellow bg
old = "              {canGuess ? '🚌 Tippelj!' : myPendingGuess ? '⏳ Tipped leadva' : myDone ? '✓ Teljesítve!' : '🚌 A te sorod!'}"
# The color line is just above — fix the color
old2 = "            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:canGuess?T.mint:myPendingGuess?T.yellow:T.inkSoft, letterSpacing:T.letterDisplay, textTransform:'uppercase', lineHeight:1.1 }}>"
new2 = "            <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:20, color:canGuess?T.mint:myPendingGuess?T.ink:T.inkSoft, letterSpacing:T.letterDisplay, textTransform:'uppercase', lineHeight:1.1 }}>"
assert old2 in html, "color line not found"
html = html.replace(old2, new2, 1)

# Also fix the "Tipped elküldve!" color in the waiting bubble
old3 = '              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.yellow }}>⏳ Tipped elküldve!</div>'
new3 = '              <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:T.ink }}>⏳ Tipped elküldve!</div>'
assert old3 in html, "elküldve not found"
html = html.replace(old3, new3, 1)

assert html != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("done")
