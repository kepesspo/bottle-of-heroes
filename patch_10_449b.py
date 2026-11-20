# v10.449 (2) — a dokk a fölé nyíló lapok (jóváhagyás, kérdés-szerkesztő) alatt ELTŰNIK
# (v10.322 Pub-minta: a lap állapota kapcsolja ki, nem a rétegsorrend).
P = 'app.src.html'
s = open(P, encoding='utf-8').read()
def rep(old, new, cnt=1):
    global s
    n = s.count(old); assert n == cnt, (n, old[:140]); s = s.replace(old, new)
rep("""function RevealQuizControl() {
  const quiz = useRevealDoc('revealQuiz');""", """function RevealQuizControl({ onSheet }) {
  const quiz = useRevealDoc('revealQuiz');""")
rep("""  const [editOpen, setEditOpen] = React.useState(false);""", """  const [editOpen, setEditOpen] = React.useState(false);
  React.useEffect(() => { if (onSheet) onSheet(editOpen); return () => { if (onSheet && editOpen) onSheet(false); }; }, [editOpen]);""")
rep("""  const [review, setReview] = React.useState(false);
  React.useEffect(() => { if (!pendingItems.length && review) setReview(false); }, [pendingItems.length]);""", """  const [review, setReview] = React.useState(false);
  const [sheet, setSheet] = React.useState(false);
  React.useEffect(() => { if (!pendingItems.length && review) setReview(false); }, [pendingItems.length]);""")
rep("""<RevealQuizControl /></div>}""", """<RevealQuizControl onSheet={setSheet} /></div>}""")
rep("""      <RevealParentTabs tab={tab} onTab={setTab} dockRef={setDock} />
      {review &&""", """      {/* ⚠️ a dokk a body-ban ül: egy fölé nyíló lap alatt nem rétegsorrenddel, hanem eltüntetéssel tűnik el */}
      {!review && !sheet && <RevealParentTabs tab={tab} onTab={setTab} dockRef={setDock} />}
      {review &&""")
open(P, 'w', encoding='utf-8').write(s); print('ok')
