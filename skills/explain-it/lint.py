#!/usr/bin/env python3
"""Lint an explain-it page before publishing.

Usage: python3 lint.py page.html [--root <repo>] [--republish]

Errors stop the publish. Warnings are for you to judge.
Checks the things that go wrong most often: missing answer/structure, missing visuals,
a broken theme, decisions with no default, file references that do not exist, and
long or unplain sentences.
"""
import os
import re
import sys
from html.parser import HTMLParser

args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
path = args[0]
root = args[args.index("--root") + 1] if "--root" in args else os.getcwd()
republish = "--republish" in args
html = open(path, encoding="utf-8").read()
errors, warns = [], []


def strip(s):
    s = re.sub(r"<(script|style)[\s\S]*?</\1>", " ", s, flags=re.I)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


# 1. Title and answer
title = (re.search(r"<title>([^<]*)</title>", html, re.I) or [None, ""])[1].strip()
if not title:
    errors.append("no <title>: give the page a 2-4 word name")
elif len(title.split()) > 6 or re.search(r"[:—-]\s", title):
    warns.append(f'<title> "{title}" reads like a caption: use a short name')
h1 = re.search(r"<h1[^>]*>([\s\S]*?)</h1>", html, re.I)
if not h1:
    errors.append("no <h1>: the h1 must state the answer")
elif len(strip(h1.group(1)).split()) < 5:
    warns.append(f'<h1> "{strip(h1.group(1))}" looks like a topic, not an answer')
if not re.search(r"(the answer|class=\"answer\"|class='answer')", html, re.I):
    warns.append('no "answer" paragraph under the title')

# 2. Sections are questions, each with a visual
sections = re.split(r"(?=<section\b)", html)[1:]
if len(sections) < 2:
    warns.append("fewer than 2 <section> blocks: split the page by question")
visual = re.compile(r"<(svg|table|canvas|pre class=\"mermaid\")|class=\"[^\"]*(bar|stack|kpi|chart|step|ladder|map|scorecard)", re.I)
for i, sec in enumerate(sections, 1):
    h2 = re.search(r"<h2[^>]*>([\s\S]*?)</h2>", sec, re.I)
    name = strip(h2.group(1)) if h2 else f"section {i}"
    if h2 and not name.endswith("?"):
        warns.append(f'section "{name}": heading is not a question')
    if not visual.search(sec) and not re.search(r'id="[^"]*"[^>]*></(div|svg)>', sec):
        warns.append(f'section "{name}": no visual (svg, table, chart, steps)')
if not re.search(r"(still (do )?not know|gaps)", html, re.I):
    warns.append('no "what we still do not know" / gaps section')
if not re.search(r"next step", html, re.I):
    warns.append("no next steps")
if not re.search(r"source", html, re.I):
    warns.append("no sources listed")

# 3. Theme: both palettes, explicit body background
if "prefers-color-scheme" not in html or 'data-theme="dark"' not in html:
    errors.append('dark theme incomplete: need @media (prefers-color-scheme: dark) AND :root[data-theme="dark"]')
if not re.search(r"body\s*\{[^}]*background", html):
    errors.append("body has no explicit background: the host theme will show through")
for m in re.finditer(r"(color|background)\s*:\s*(#[0-9a-fA-F]{3,6})", html):
    ctx = html[max(0, m.start() - 300):m.start()]
    if ":root" not in ctx and "--" not in html[m.start() - 40:m.start()]:
        warns.append(f"hard-coded {m.group(1)} {m.group(2)} outside the tokens: check it in both themes")
        break

# 4. Decisions have a default and a way back
decisions = re.findall(r"data-decision=", html)
if decisions:
    if len(re.findall(r"data-suggested", html)) < len(decisions):
        errors.append(f"{len(decisions)} decisions but fewer suggested options: mark the one you would pick")
    if not re.search(r"(clipboard|window\.claude)", html):
        errors.append("decisions present but no way to send answers back (copy button or capability)")

# 5. File references exist
for ref in sorted(set(re.findall(r"data-path=\"([^\"]+)\"", html))):
    f = ref.split(":")[0]
    if not os.path.exists(os.path.join(root, f)):
        errors.append(f"data-path {ref}: file not found under {root} (made-up path?)")

# 6. Republish needs a change note
if republish and not re.search(r"changed since", html, re.I):
    errors.append('--republish: add a "Changed since last version" box at the top')

# 7. Plain English (rough: plain-writing has the full rules)
text = " ".join(strip(m) for m in re.findall(r"<(?:p|li)\b[^>]*>([\s\S]*?)</(?:p|li)>", re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I), re.I))
bad = ["utilize", "leverage", "facilitate", "commence", "prior to", "in order to", "ensure", "synergy",
       "robust", "seamless", "delve", "holistic", "paradigm"]
hits = sorted({w for w in bad if re.search(r"\b" + w + r"\b", text, re.I)})
if hits:
    warns.append("not plain: " + ", ".join(hits))
long = [s for s in re.split(r"(?<=[.!?])\s+", text) if len(s.split()) > 28]
if long:
    warns.append(f"{len(long)} sentences over 28 words, e.g. \"{long[0][:90]}...\"")

for e in errors:
    print("ERROR  " + e)
for w in warns:
    print("warn   " + w)
print(f"\n{len(errors)} errors, {len(warns)} warnings")
sys.exit(1 if errors else 0)
