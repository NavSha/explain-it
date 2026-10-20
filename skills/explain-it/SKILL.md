---
name: explain-it
description: Turn research, a plan, options, a comparison, results or a progress report into one diagram-first, plain-English HTML page the reader can understand fast and decide on. Use when the user says "explain it", "help me understand", "make this easy to digest", "show me the plan", "put this on a page", or when they must review or approve something before work continues. Do NOT use for short answers, small fixes or one-line status updates.
---

# Explain it

The reader needs to *get it* fast, then decide. A wall of bullet points fails them: they skim,
approve, and miss the one thing that mattered. This skill turns the output into one page built
for understanding.

Idea: Andrej Karpathy's ladder for how AI should explain things: plain writing → diagrams →
an interactive page → video. This skill is step three.

## 0. Route first

| Output | Use |
|---|---|
| A fact, a yes/no, a one-line status | A plain reply. Skip this skill. |
| One mechanism or flow | One diagram (mermaid or inline SVG) in the reply. |
| Research, options, a comparison, results, progress, a review, a plan | **This skill.** |

## 1. Shape every page the same way

1. **Title = the answer**, not the topic. "Almost no one builds AI tools for small shops", not "Competitor research".
2. **"The answer" paragraph** under the title: 2–4 plain sentences. End with what the reader should do or decide.
3. **Sections are questions.** "Where is the open space?" "Is our price right?" Put the answer in the first line under each question.
4. **Diagram before prose.** Each section leads with a visual. Text explains the visual. It does not replace it.
5. **2–3 "what this means" bullets** under each diagram. Bold the claim, then one plain sentence.
6. **Assumptions and open questions up front.** A page that hides an assumption in paragraph four is wrong in a way nobody sees.
7. **End with "What we still do not know" + "Next steps".**
8. **Footer:** sources (files, links) and the date.

## 2. Pick the diagram by content

| Content | Diagram |
|---|---|
| Many items placed against two questions (competitors, options, risks) | **2×2 map**: dots, labelled axes, a shaded target zone |
| How parts connect, who pays whom, a data or request flow | **Flow diagram**: boxes + arrows with short verb labels; 12 boxes at most |
| Steps over time, a rollout | **Step row** with arrows, one card per step |
| Amounts | **Bars to scale** with the real values on them; say so if you use a log scale |
| A choice between 2–4 options | **Comparison table** + one "Recommended" mark |
| A screen or UI change | **HTML mockup** of the screen, before anyone builds it |
| Status of many items | **Scorecard**: one pill per item (done / at risk / blocked) |

Rules: draw to scale, label values, color by meaning (one color per group plus one for
"recommended"), keep labels clear of each other, at most 3 columns so it reads on a phone.

## 3. Calm design

- One type scale with 4–5 sizes. One display face, one body face, one mono face for labels and numbers.
- Same card padding, corner radius and label position everywhere.
- One accent color. Good / risk / blocked colors are separate and used only for state.
- Works in light and dark mode, and at phone width with no sideways scroll.

## 4. Simple / Detailed switch

One switch at the top. **Simple** (the default) shows titles, answers, diagrams and bullets.
**Detailed** also shows tables, long notes, code and full source lists. Mark detail-only blocks
with `class="detail"` and hide them with `body:not(.detailed) .detail{display:none}`.

## 5. Decisions in place

- Put each decision on the section it changes, not in a list at the end.
- Give 2–4 options as radio buttons. Pre-select the one you would pick, mark it *Suggested*, and add one short reason.
- Wrap each one as `<fieldset data-decision="id">` and number them ("Decision 2 of 4").
- A sticky button counts the open ones ("3 to answer") and jumps to the next one.
- A **"Copy my answers"** button builds plain text (`Decision 2: … → …`), copies it with
  `navigator.clipboard.writeText` inside the click handler, and on failure shows the text in a
  selectable box. The reader pastes it back to you.

## 6. Write plainly

Short sentences, one idea each. Common words. Active voice. Answer first. Name things the way
the reader says them, not the way the code names them.

## 7. Keep a Markdown copy

Save the content as `<name>.md` beside the HTML. The HTML is the view. The Markdown is the record
the next session (or a teammate) can read without the page. When you update the page, add a
"Changed since last version" box at the top with 2–5 lines.

## 8. Write, lint, look, deliver

1. Write the page as one self-contained HTML file (inline CSS and JS).
2. **Lint** (optional, if `lint.py` sits next to this file): `python3 lint.py page.html`.
   Fix errors. Judge warnings.
3. **Look once** in light and dark, and at phone width. Fix overlaps, clipping and low contrast. Do not loop.
4. **Deliver:** open or share the page, and reply with 3–5 plain bullets on what it shows and which decisions are open.

## Checklist

- [ ] Title states the answer; assumptions and open questions are up front
- [ ] Every section is a question answered in its first line, with a visual
- [ ] Numbers drawn to scale
- [ ] Decisions have a suggested option and a "Copy my answers" button
- [ ] Simple / Detailed switch works
- [ ] Light, dark and phone width checked
- [ ] Markdown copy saved
