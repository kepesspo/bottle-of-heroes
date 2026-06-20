#!/usr/bin/env python3
"""v9.340 — Fix OnboardingOverlay: move outside overflow:hidden screen container"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# OnboardingOverlay is position:fixed but rendered inside overflow:hidden screen container.
# On iOS Safari this causes clipping. Move it BEFORE the screen container (sibling level).
old = '''      <BubbleBackground />
      <div key={screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>
        {showOnboarding && <OnboardingOverlay onDone={() => setShowOnboarding(false)} />}'''

new = '''      <BubbleBackground />
      {showOnboarding && <OnboardingOverlay onDone={() => setShowOnboarding(false)} />}
      <div key={screen} style={{ height:'100dvh', width:'100%', display:'flex', flexDirection:'column', overflow:'hidden', boxSizing:'border-box', animation:`slide${dir>0?'In':'Back'} .35s cubic-bezier(.2,.85,.3,1.05)` }}>'''

assert old in html, "FAIL: OnboardingOverlay position"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.339';", "const APP_VERSION = 'v9.340';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.340 — OnboardingOverlay moved outside overflow:hidden container")
