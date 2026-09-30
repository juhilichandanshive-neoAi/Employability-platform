# Progress — Task 3 (frontend build)

Honest, dated log. One entry per day this was actually worked on — nothing backdated,
nothing written in advance for days that haven't happened yet.

---

## 2026-08-11

**Work completed**
- Read the full v2 design pack (design system, component library, responsive rules, all
  eleven screens) and set up `phase8_frontend/` as the Streamlit frontend.
- Built the shared foundation: design-token CSS (`assets/styles.css`), the reusable
  component library (`components/` — navigation, cards, charts, badges, tables, modals),
  and the static dummy-data module (`data/dummy_data.py`).
- Shipped three fully working, tested screens: **Login, Dashboard, Student Profile** —
  wired into `app.py`, verified in-browser at desktop (1280px), tablet (768px), and
  phone (375px) widths.
- Also wrote (but did not wire into the running app) the remaining eight screens:
  Assessment, Employability Score, Skill Gap, Learning Roadmap, Certifications, Career
  Suggestions, Analytics, Reports. These exist as real code in `screens/`, pass a syntax
  check, but aren't switched on yet — see `decisions.md` for why.
- Found and fixed three real bugs by actually testing in the browser rather than just
  reading the code: a startup path crash, a tablet-width sidebar text bug, and a mobile
  bottom-nav layout bug caused by Streamlit's own responsive CSS. Full detail in
  `processes.md`.

**Current progress**
3 of 11 screens live and verified working (desktop/tablet/mobile). Foundation
(design system, component library, dummy data, routing) is done and doesn't need to be
redone for the remaining screens — wiring each one in from here is mechanical.

**Blockers / issues**
None blocking. Two things worth flagging:
- Local git is set to `nehak1122` / `nehakhetawat2@gmail.com`; if commits should show a
  different name, that needs to be changed in git config directly (not something I do
  automatically).
- Nothing has been pushed to GitHub yet — the repo has a remote configured
  (`neoaitech/Employability_Framework`), but pushing wasn't part of today's session.

**Next-day plan**
Wire in the next batch of already-written screens (Assessment, Employability Score are
the natural next two, since Profile → Assessment → Score is the flow order), then
Skill Gap and Learning Roadmap. Test each one in-browser the same way as today before
calling it done, same as today.

---

## 2026-08-13

**Work completed**
- Wired in all eight remaining screens — Assessment, Employability Score, Skill Gap,
  Learning Roadmap, Certifications, Career Suggestions, Analytics, Reports — plus
  Settings, into `app.py` and `utils/state.py`'s `LIVE_SCREENS` set. All eleven screens
  from the design pack are now live in the nav.
- Clicked through every single screen in the running app (not just a syntax check) at
  desktop (1280px), tablet (768px), and phone (375px) widths, and checked the server logs
  for runtime errors after each pass. Nothing broke.
- Specifically re-checked the table → stacked-card responsive pattern on Skill Gap and
  Certifications at phone width, since those are the two screens that actually use it —
  both held up correctly.
- One cosmetic-only note, not fixed because there's nothing to fix in the code: the emoji
  icons on the Reports cards sit a little close to their heading text in the browser —
  the markup has a normal space, it's just how that emoji glyph measures.

**Current progress**
All 11 of 11 screens live, wired, and verified working across all three breakpoints. No
open bugs. Still running entirely on static dummy data — no backend/ML integration.

**Blockers / issues**
None. Explicitly holding off on pushing to GitHub until told to — everything so far is
local commits only.

**Next-day plan**
Nothing scheduled yet — next steps depend on what the project lead wants reviewed first
(a live walkthrough, or pushing once given the go-ahead).

---

## 2026-08-18

Project lead sent detailed review feedback (16 items) covering colour theme, spacing,
button placement, assessment flow, results, and per-page UI refinement across all 11
screens. Given the 18–20 Aug timeline, splitting this across the three days rather than
doing it all in one sitting — today is item 1 (colour palette) and item 6 (sidebar
spacing), the two foundational changes everything else builds on.

**Work completed**
- Replaced the entire purple palette (`#6C5CE7` / `#8B5CF6`) with the requested teal/cyan
  palette (`#0EA4AF` primary, `#AFDDE5` secondary) — updated the CSS design tokens first,
  then swapped every hardcoded hex value across 9 files (`screens/login.py`,
  `dashboard.py`, `roadmap.py`, `profile.py`, `careers.py`, `certifications.py`,
  `components/charts.py`, `components/navigation.py`) so nothing was left on the old
  colour by accident.
- Kept the semantic status colours (green/amber/red for success/warning/error) as-is —
  those carry meaning, not just decoration, so changing them wasn't part of "unify the
  palette." Replaced the one purely decorative off-palette colour (a violet donut-chart
  slice) with a teal-family shade instead.
- Fixed sidebar crowding: nav row height 38px → 44px, spacing between rows 2px → 6px,
  more breathing room around section labels (MAIN/INSIGHTS/OUTPUT) and sidebar padding.
- Verified in the running app (not just reading the CSS) — Dashboard and Learning Roadmap
  checked directly, other screens spot-checked via the shared component/token system
  since they all pull from the same `styles.css` and `components/` — a colour-only change
  doesn't need a full per-screen browser pass the way a layout change would.

**Current progress**
Colour palette and sidebar spacing done, consistent across the app. Remaining 14 items
from the feedback (card alignment, button placement on Profile/Skill Gap/Assessment,
assessment step flow + results page, domain selection at start, user-created ID,
Employability Score chart cleanup, Roadmap/Certifications/Career Suggestions page
redesigns, full cross-page consistency pass) are not started — deliberately, to keep
today's slice real and reviewable rather than showing 14 half-finished changes.

**Blockers / issues**
None.

**Next-day plan (19 Aug)**
Card alignment/spacing pass, button repositioning (Save Changes → bottom of Profile,
Submit Session → end of Assessment, Build Resume/Download Plan → end of Skill Gap flow),
and the Assessment box/flow clarity work — these are the layout-level items and make
sense to batch together before touching the deeper per-page content work on the 20th.

---

## 2026-08-19

**Work completed**
- Moved "Save changes" on the Profile page from the top-right (item 3) to a footer bar at
  the bottom of the page, with a one-line caption explaining what it does.
- Moved "Submit section" on the Assessment page from the top-right to the bottom of the
  question flow (item 4), disabled until all 30 questions are answered, with a line above
  it explaining why it's greyed out. Also rebuilt the top of the page into a clear intro
  banner — what the assessment is, how many questions, current section — instead of just
  a bare title (item 5).
- On Skill Gap, moved "Download plan" and "Build my roadmap" from the top-right to a
  footer action bar after the full gap table, so both only appear once there's something
  to act on (item 12).
- Standardised spacer heights across `profile.py`, `score.py`, `settings.py` to the
  design system's allowed spacing values (8/16/24/32/48px) — a few screens had stray
  12px/6px gaps left over from earlier passes.
- Tested all three changed screens in the running app after editing, not just read the
  code — clicked into Profile, Assessment, and Skill Gap, confirmed the buttons render
  and behave correctly at their new positions, and checked the server logs for errors
  (none found).

**Current progress**
5 of 16 review items done (colour palette, sidebar spacing, Save Changes placement,
Submit Session placement, Skill Gap CTA placement) plus the assessment box clarity work.
Remaining: full card alignment/spacing audit across the rest of the app, the step-by-step
assessment flow itself (item 7), the results page (item 8), domain selection at the start
(item 9), user-created ID (item 10), Employability Score chart cleanup (item 11), and the
Roadmap/Certifications/Career Suggestions redesigns (items 13-15) — saved for the 20th.

**Blockers / issues**
None.

**Next-day plan (20 Aug)**
The remaining content-level items: assessment step flow + domain selection at the start,
a proper results page at the end of the assessment, user ID creation during setup, the
Employability Score page cleanup, and the Roadmap/Certifications/Career Suggestions UI
passes — then a final cross-page consistency check against all 16 items before calling
the review done.

---

## 2026-08-20 (final day)

**Work completed**
- Assessment now starts with a **domain-selection screen** (Cloud Computing / Cybersecurity
  cards, question count and time shown) before any questions load — item 9. Domain is
  held in session state; switching it mid-assessment resets the current section, matching
  the design pack's own rule.
- Added a **step tracker** across the top of the question flow — done/current/locked
  sections shown as numbered dots with a connecting line, so it's clear at a glance where
  you are and what's next (item 7).
- Built a proper **assessment results page** — overall score, a per-section bar chart,
  a strengths list, a "where you lost points" list, and a plain-language "what this means
  for your score" callout — shown after Submit (item 8). Added a small dataset for this
  (`ASSESSMENT_RESULT` in `data/dummy_data.py`) rather than reusing the dashboard score
  data, since the two represent different things (overall score vs. one section's result).
- Login page now has a real **Create Account** form with a **User ID field** or item 10 —
  live-checks the ID as you type (length/character rules) and shows an "available" message,
  same pattern a real signup flow would use.
- Employability Score, Certifications, and Career Suggestions: wrapped the charts and
  info panels that were sitting bare in bordered cards, matching every other card on the
  site, and tightened the spacing between sections (item 11, part of item 16).
- Learning Roadmap: phase cards now show numbered step dots (done/current/pending) instead
  of relying on the badge text alone, and the "this week" / "courses" lists moved into
  proper card containers (item 13).

**Bug check before pushing**
Clicked through all 11 screens plus the full new assessment flow (domain picker → question
flow → submit → results) and the new signup form, at desktop and tablet widths. Checked
the server logs after each pass. No errors found — this is the first day's work that went
straight to a clean run with nothing to fix along the way.

**Current progress**
All 16 review items from the 18 Aug feedback are addressed. This is the last day of the
window (18–20 Aug), so today's commit is being pushed once the write-up is done.

**Blockers / issues**
None.

**What's next**
Nothing scheduled — next steps depend on what the project lead wants to review, and
whether backend/ML integration replacing `data/dummy_data.py` becomes the next task.

---

## 2026-08-21

Project lead sent a second round of feedback with a reference image (not a literal spec —
confirmed scope with them first: redesign the 11 existing pages to match the reference's
polish/spacing/consistency, don't build the three extra sidebar sections shown in it
Live Lectures, Skill Edge, Leaderboard - and do it in one sitting rather than splitting
across days, since this is a visual refresh of finished work, not a fresh build.

**Work completed**
- Fixed a real inconsistency: `st.container(border=True)` was rendering with Streamlit's
  own plain square-cornered default instead of matching the app's own `.ea-card` style
  (rounded corners, shadow). Found by inspecting the DOM directly, not guessing - added a
  global CSS override so every bordered container now looks identical to a hand-built
  card. Documented the fragility of that selector (it targets a Streamlit-generated class
  name) directly in the CSS comment.
- Added `icon_header()` - an icon-in-a-circle + title pattern - and applied it to every
  section header across all 11 screens, replacing plain text headings. This was the
  biggest lever for "looks more professional and consistent."
- Found and fixed three genuine leftover bugs from the 18 Aug colour migration that a
  plain hex search had missed: two chart fill colours were still hardcoded as the old
  purple's RGB triplet (`rgba(108,92,231,...)` instead of the hex form `#6C5CE7`, so the
  original find/replace walked right past them), and the heatmap's light-end colour was
  still a pale lavender left over from the same palette. All three are teal now.
- Removed every remaining red/amber/green fill from progress bars and Skill Overview per
  the explicit request - `progress_bar_card()` now scales through teal opacity by value
  instead of switching hue, and chart bars below a threshold go pale teal instead of red.
  Kept colour on badges only (they're always paired with a word, per the design system's
  own rule) and on two genuinely bidirectional cases (score drivers, roadmap timeline)
  where a single hue can't carry the "up vs down" or "done vs not done" meaning - those
  use teal-family light/dark pairs instead of red/green.
- Moved "Continue assessment" on the Dashboard from a top-right button to a full-width
  gradient CTA bar at the bottom, matching the reference. Caught and fixed a real contrast
  bug while building it - the subtitle text was inheriting the default grey colour instead
  of white against the teal gradient, unreadable until fixed.
- Replaced the three emoji icons on the Reports cards with the same icon-badge component
  used everywhere else, closing out the "consistent icon style" ask and the earlier
  emoji-spacing cosmetic note from the same file.

**Bug check before wrapping up**
Clicked through all 11 screens plus the full assessment flow again after all the changes,
at desktop, tablet, and mobile widths. Checked the server logs - no errors. Also grepped
the whole codebase for any remaining old-palette hex or rgb values in any form; only hit
was the "Saved" label on the assessment question page, which was left as green
deliberately (a one-word status flash, not a decorative colour choice).

**Current progress**
All 11 screens now share one consistent visual language - same card treatment, same
header pattern, same colour discipline. Not committed to GitHub yet - holding for the
go-ahead, same as every other round.

**What's next**
Nothing scheduled - waiting on review.

---

## 2026-08-23

Project lead came back after seeing the previous pass rendered: still seeing red and
yellow in places, wants strictly the teal/cyan palette everywhere with no exceptions -
same reference image, more explicit this time.

**Work completed**
- Found the actual sources, which were narrower than they sounded: badges (High/Medium/
  Met, Verified, Empty, etc.) were still on the original green/amber/red status colours,
  and two spots used Streamlit's *native* `st.info()` / `st.warning()` widgets, which
  render in Streamlit's own fixed blue/amber and completely ignore the app's theme - no
  amount of CSS on our side touches those.
- Redefined the app's status colour tokens as a single teal-intensity scale instead of
  three hues: pale tint for "fine," light cyan for "worth a look," solid teal for "needs
  attention." Every badge, priority tag, and progress bar pulls from these same three
  tokens now, so the fix applied everywhere at once instead of screen-by-screen.
- Replaced both native `st.info`/`st.warning` calls with the app's own themed banner
  component instead, matching the card language everywhere else, not just the colour.
- Found a second, easy-to-miss source: emoji glyphs (⚠️ ✅ ⚡) carry their own fixed
  colour that CSS cannot override no matter what - swept the whole codebase for every
  one and replaced each with the same teal SVG icon set already used in the sidebar and
  headers.
- Hit a real testing trap while verifying: the running server had been started before
  these edits, and Streamlit's file-watcher (no `watchdog` installed, so it's on a slow
  polling fallback) hadn't picked up the change - a page reload alone still showed the
  old blue box. Caught this by checking the DOM for text that should have been there and
  finding it genuinely absent, not just mis-styled. Fixed by restarting the server
  process outright, then re-verified every screen again from a clean start.

**Bug check before wrapping up**
Grepped the entire codebase for any remaining non-palette hex colour and any status-
carrying emoji - both came back clean except two deliberate, reasoned exceptions (a
neutral grey for one text label, a light teal tint already in the palette). Re-checked
Dashboard, Skill Gap, Careers, Analytics, Assessment (full flow through to results), and
Profile directly in the browser after the server restart to make sure what shipped
matches what was actually tested, not a stale cache.

**Current progress**
No red, amber, or green left anywhere in the app - status now reads through teal
intensity and icon shape, not hue. Not pushed - same as always, waiting for the go-ahead.

**What's next**
Nothing scheduled - waiting on review.

---

## 2026-08-24

Project lead sent the same feedback a third time with the same reference image - the
23 Aug pass wasn't actually complete. Went looking for what it missed instead of
re-explaining the same fix.

**Work completed**
- The 23rd's emoji sweep had only checked for the three symbols mentioned in that
  session (⚠️ ✅ ⚡) rather than scanning for the whole class of problem. Wrote a proper
  Unicode-range regex sweep this time instead of grepping for characters I remembered,
  and it turned up five more: a yellow star rating icon on Certifications, a blue book
  and a few other plain-color icons in the Dashboard's Quick Actions row, a waving-hand
  emoji in the greeting, and a document emoji on the Profile page's resume card sitting
  right next to an icon-badge header that already covered the same thing. All replaced
  with the app's own teal SVG icon set; the waving hand was just dropped, since a
  decorative greeting emoji isn't worth building a custom icon for.
- Found a real, unrelated layout bug while checking the result, not something the colour
  feedback asked for: the "Recommended" badge on the Reports page was rendering as a
  stretched 97x75px blob instead of a small pill. Traced it with the DOM inspector rather
  than guessing - a flex row had the badge and a title that wraps to multiple lines as
  siblings with no `align-items` set, so the browser's flex default (`stretch`) pulled the
  badge to match the taller title. Fixed that one, then grepped for the same pattern
  elsewhere in the codebase and fixed four more before they became visible bugs too.

**Bug check before pushing**
Full server restart, then clicked through every screen again - including ones this round
didn't directly touch - at desktop and mobile widths. Checked server logs after each
pass, none found. Re-ran both sweeps (colour hex/rgb and the Unicode emoji regex) at the
very end against the final state of the code, not against what I remembered changing.

**Current progress**
Every screen re-verified clean of both stray colour and layout regressions. Committing
and pushing this round, per direct instruction.

---

## 2026-09-02

Project lead sent three reference screenshots (assessment results page, question page,
domain/difficulty picker) as style direction for the assessment flow specifically -
confirmed with them these were reference-only, not literal specs, and that the domain
names stay as our own (Cloud Computing / Cybersecurity), not the five shown in the
screenshots.

**Work completed**
- Domain selection now includes a **difficulty picker** (Easy/Moderate/Hard, Easy
  pre-selected as recommended) on the same screen, styled as clickable icon tiles
  instead of the old plain description cards.
- Rebuilt the question screen to match the reference: each option is a bordered box with
  a circular letter badge, the selected one highlighted in teal. Selecting an option now
  locks it in and immediately shows **why it's right or wrong** - a real explanation for
  every option, not just the correct one, pulled from a proper 6-question bank per domain
  (`QUESTION_BANK` in `data/dummy_data.py`) instead of the single hardcoded sample
  question the flow used before.
- Rebuilt the results page: a score ring (new `charts.score_ring()`), Strengths and
  Improvement Areas computed live from actual answers grouped by category, a
  "recommended next step" callout, and three bottom action cards (Review Answers - an
  expandable per-question breakdown, View Skill Gap, Back to Dashboard).
- Added a "Retake this assessment" option and an "Exit to domain selection" escape hatch,
  since the flow is now stateful (current question, answers so far) rather than a single
  static screen.

**Bugs found and fixed while building this**
- The option buttons' text was rendering centred instead of left-aligned next to the
  letter badge. Root cause took real digging: Streamlit centres a button's label by
  wrapping it in a shrink-to-fit flex child and centring *that* within the button, so
  `text-align` on the label itself does nothing - fixed one level up, on the wrapper div.
- The "Next question" button was functionally disabled (confirmed via the DOM) but looked
  identical to the enabled state, which would have read as broken to anyone testing it.
  Added a visible disabled style for buttons generally, not just this one case.
- A copy bug in the "recommended next step" text: it was reusing an explanation string
  written for a different context, so it read "start with: Correct. An IAM role gives..."
  - the leftover "Correct." read like a typo. Fixed the phrasing so reused text doesn't
  carry a stray prefix from its original context.

**Current progress**
The assessment flow is fully rebuilt and working end to end - domain/difficulty picker,
question-by-question with instant feedback, and a results page with real strengths/gaps.
Tested by actually answering questions (including deliberately wrong ones) through to the
results page and the answer-review expander, not just reading the code. Server logs clean.

**Blockers / issues**
None. Not pushed until confirmed, same as every round.
