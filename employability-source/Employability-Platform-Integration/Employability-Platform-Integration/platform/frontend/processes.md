# Process notes — EmployaAI frontend

What actually happened while building this, including the mistakes, so there's a record
beyond just the final code.

## Reading the design pack first

Before writing anything, I read the full 25-page v2 design pack you uploaded
(`Version 2 Summary (Key Changes & Improvements).pdf`) — the design system, component
library, responsive rules, and all eleven screens. That's what everything below is built
against; there was no separate image mock-up needed since the pack already has full
desktop screens.

## Bugs hit while building, and how they were found

**1. The app crashed on first run — wrong file path.**
`app.py` opened `assets/styles.css` using a path relative to wherever Streamlit happened
to be launched from, not relative to the app file itself. First run threw
`FileNotFoundError`. Fixed by building the path off `os.path.dirname(__file__)` instead of
assuming the working directory.

**2. Tablet-width sidebar bug, found by actually resizing the browser.**
The plan was: sidebar narrows to an icon rail at tablet width, and the text labels get
hidden with CSS. That doesn't work, because Streamlit's `st.button` renders plain text —
there's no `<span>` around the label to hide, so the CSS rule targeting it did nothing,
and the text wrapped one letter per line down the sidebar instead. This only showed up
once I actually resized the preview to 768px and looked — it wasn't visible at desktop
width. Fixed by dropping the icon-rail idea in favour of a narrower sidebar (200px) with
`text-overflow: ellipsis`, which doesn't need a wrapper element to work.

**3. Mobile bottom nav rendered as a tall stack instead of a row, also found by resizing.**
The bottom navigation bar (Home / Score / Gaps / Learn / More) is built from five
`st.columns()`. At phone width, it wasn't a row — it was five full-width buttons stacked
on top of each other, taking up most of the screen. I inspected the actual computed CSS in
the browser (via dev-tools-style JS, since it wasn't obvious from the screenshot alone) and
found the cause: Streamlit has its own responsive CSS that forces columns to
`min-width: calc(100% - 24px)` below its own breakpoint, so my "make it a row" CSS was
losing to Streamlit's own mobile styles. Fixed by adding a more specific override scoped
just to that one container, so it doesn't affect columns anywhere else in the app.

**4. Deprecation warnings in the server log.**
Streamlit 1.55 warns that `use_container_width=True` is being replaced by `width="stretch"`
across every widget that takes it (buttons, charts, etc.). Not a functional bug, but left
alone it would print a warning on every single widget on every page. Cleaned up across all
files in one pass rather than leaving it half-fixed in some files and not others.

**5. The browser-automation tool used for testing got flaky at the phone viewport size**
(coordinate clicks kept timing out on the "Sign in" button specifically at 375px width).
Worked around it by triggering the same click via a JS `element.click()` call instead, to
confirm the app itself was behaving correctly rather than fighting the test tool. Once
confirmed, testing continued normally.

**6. Scope correction, mid-build.**
While building, I initially wrote all eleven screens in one sitting after being told not
to leave placeholder pages in the nav. That overshot what was actually wanted — the ask
was to keep the three-day pacing, just make sure whatever ships each day is real and
working rather than a stub. Caught this after you flagged it directly. The eight extra
screens (Assessment, Employability Score, Skill Gap, Learning Roadmap, Certifications,
Career Suggestions, Analytics, Reports) were already written and are kept in the repo —
deleting working code just to redo it later would be wasteful — but I disconnected them
from the running app (`app.py`'s `SCREENS` dict and `utils/state.py`'s `LIVE_SCREENS` set
both only list what ships today) so the nav doesn't advertise anything that isn't really
live.

**7. Wiring in the remaining eight screens.**
Once you confirmed you wanted the full set live (not held back for later days), I added
Assessment, Employability Score, Skill Gap, Learning Roadmap, Certifications, Career
Suggestions, Analytics, and Reports to `app.py`'s `SCREENS` dict and `utils/state.py`'s
`LIVE_SCREENS` set, then clicked through every one of them in the running app rather than
assuming the syntax check meant they'd render correctly. All eleven rendered without
errors on the first pass. One cosmetic-only thing noticed and left as is: the emoji icons
on the Reports cards (📄 📈 🔗) sit slightly close to the heading text in the browser —
the HTML has a normal space character before the text, this is just how that particular
emoji glyph measures in the browser's font, not a code bug.

**8. Sidebar had no real icons, and the active-page highlight was broken by a
Streamlit DOM quirk.**
You pointed out the sidebar looked plain and had no icons next to the nav items. True —
the original build used plain text labels only. Fixed by building a small hand-drawn SVG
icon set (`components/icons.py`, one outlined icon per screen, matching the "single icon
family, rounded ends" rule from the design pack) and placing one next to every nav item
and bottom-nav item.

While wiring the icons in, I found a real bug in code that had shipped earlier: the
purple "active page" highlight was built by opening a `<div class="ea-nav-active">` in
one `st.markdown()` call and closing it with `</div>` in a later one, with the icon and
button rendered in between. That looks like normal HTML, but Streamlit gives every
`st.markdown()` call its own isolated container — the opening and closing tags never
actually end up wrapping anything in the real DOM; each one silently self-closes into an
empty, invisible element. I only found this by checking the actual rendered DOM in the
browser (an element's box was reporting zero height when it should have been a full nav
row), not by reading the code. Rewrote it using `st.container(key=...)`, which does
create one real wrapping element per row, and moved the active-page background to a
small CSS block keyed off that container's class. This also means whatever visual
"highlighting" appeared to work in earlier screenshots wasn't reliably doing what it
looked like it was doing — worth flagging since it's the kind of bug that's easy to miss
by eye and only shows up when you inspect the actual markup.

## What was actually verified, not just assumed

I ran the app locally, signed in, and clicked through every one of the eleven screens —
Dashboard, Profile, Assessment, Employability Score, Skill Gap, Learning Roadmap,
Certifications, Career Suggestions, Analytics, Reports, Settings — at three widths:
1280px (desktop), 768px (tablet), and 375px (phone). Checked the server logs for runtime
errors after each pass (none found). Specifically re-checked the table → stacked-card
behaviour on Skill Gap and Certifications at phone width, since those two screens are the
ones that actually exercise `components/tables.py`'s responsive pattern — it held up
correctly on both.

## What's not done yet

Nothing in the eleven-screen scope. All eleven screens are wired in, tested at three
breakpoints, and free of runtime errors. Still open: this hasn't been pushed to GitHub —
staying local until you say otherwise — and the underlying data is still the static
placeholder set in `data/dummy_data.py`, not real backend/ML output.

## The v5 "fun, no-orange" restyle (24 Sep)

**What changed:** full colour-token rewrite in `assets/styles.css` (purple/violet
primary, green/pink/red status, two new fun accents), `components/charts.py` recoloured
with the same rule applied to Plotly's own colour args (not CSS-reachable), a systematic
hex sweep across every screen and component file that had a colour value hardcoded
outside the token system, four new hand-drawn SVG illustrations in `assets/images/`, a
new `components/fun.py` (streak/level chips, achievement badges, mascot, celebration,
empty-state), new `STREAK`/`ACHIEVEMENTS` data in `dummy_data.py`, and warmer copy on the
dashboard greeting and login hero.

**Bug avoided, not hit:** `st.balloons()` was the obvious choice for the "milestone"
celebration, but its colours are compiled into Streamlit's frontend bundle - there's no
way to grep the running app's source for them, which conflicts directly with "confirm no
orange remains." Used a custom SVG celebration illustration instead, gated behind a
`assessment_celebrated` session-state flag so it fires once per submission rather than
replaying on every rerun while the results page stays open (a rerun happens if you expand
the "review answers" section, for instance - without the flag it would restart every
time).

**Verification caveat, stated plainly:** this environment has no browser tool available,
so "click through all eleven screens at 1280px/768px/375px" was not literally done by
eye. What was actually run: `ast.parse` on every changed file (syntax), then Streamlit's
own `AppTest` harness executing the real `app.py` script end-to-end for the login screen
and all eleven authenticated screens (including a scripted assessment-submit to exercise
the celebration path), catching zero exceptions. That confirms the code runs; it does not
confirm pixel-level layout at each breakpoint the way an actual screenshot would. If a
browser becomes available, that's the next thing to actually do, not assume passed.
