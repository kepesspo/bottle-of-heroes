#!/usr/bin/env python3
"""v9.342 — OnboardingOverlay: darken body so status bar zone also goes dark in PWA"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# In PWA black status bar mode, iOS reflects the body background behind status bar text.
# When overlay is visible, set body bg to dark so status bar zone matches overlay.
# Reset on done.
old_func = '''function OnboardingOverlay({ onDone }) {
  const [step, setStep] = React.useState(0);'''

new_func = '''function OnboardingOverlay({ onDone }) {
  const [step, setStep] = React.useState(0);
  React.useEffect(() => {
    const prev = document.body.style.background;
    document.body.style.background = 'rgb(14,14,24)';
    return () => { document.body.style.background = prev; };
  }, []);'''

assert old_func in html, "FAIL: OnboardingOverlay func"
html = html.replace(old_func, new_func, 1)

html = html.replace("const APP_VERSION = 'v9.341';", "const APP_VERSION = 'v9.342';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.342 — body bg darkened during onboarding, status bar zone matches overlay")
