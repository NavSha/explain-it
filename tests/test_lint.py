"""Tests for skills/explain-it/lint.py. Run: python3 -m pytest tests/"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LINT = ROOT / "skills" / "explain-it" / "lint.py"

GOOD = """<title>Pricing Check</title>
<style>
:root{--bg:#fff;--ink:#111}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111;--ink:#eee}}
:root[data-theme="dark"]{--bg:#111;--ink:#eee}
body{background:var(--bg);color:var(--ink)}
</style>
<h1>Our price is 20% below the market, so we can raise it</h1>
<p class="answer">The answer: raise the price by 10%. Decide by Friday.</p>
<section><h2>Where do we sit?</h2><div class="chart"></div><p>We are the cheapest of five.</p></section>
<section><h2>What would change?</h2><table><tr><td>+10%</td></tr></table>
<fieldset data-decision="price"><label><input type="radio" data-suggested> Raise 10%</label></fieldset>
<button onclick="navigator.clipboard.writeText('x')">Copy my answers</button></section>
<section><h2>What do we still not know?</h2><table></table><p>Churn after a rise. Next steps: test on 5% of users.</p></section>
<footer>Sources: pricing.csv, 20 Oct 2026</footer>
"""


def run(tmp_path, html, *args):
    page = tmp_path / "page.html"
    page.write_text(html, encoding="utf-8")
    return subprocess.run([sys.executable, str(LINT), str(page), "--root", str(tmp_path), *args],
                          capture_output=True, text=True)


@pytest.mark.parametrize("example", sorted((ROOT / "examples").glob("*/index.html")),
                         ids=lambda p: p.parent.name)
def test_examples_have_no_errors(example):
    r = subprocess.run([sys.executable, str(LINT), str(example), "--root", str(ROOT)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout
    assert "ERROR" not in r.stdout


def test_good_page_passes(tmp_path):
    r = run(tmp_path, GOOD)
    assert r.returncode == 0, r.stdout
    assert "0 errors" in r.stdout


def test_no_args_prints_usage():
    r = subprocess.run([sys.executable, str(LINT)], capture_output=True, text=True)
    assert r.returncode != 0
    assert "Usage" in r.stderr


def test_missing_title_and_h1_fail(tmp_path):
    html = GOOD.replace("<title>Pricing Check</title>", "")
    html = html.replace("<h1>", "<h2>").replace("</h1>", "</h2>")
    r = run(tmp_path, html)
    assert r.returncode == 1
    assert "no <title>" in r.stdout and "no <h1>" in r.stdout


def test_missing_dark_theme_fails(tmp_path):
    html = GOOD.replace('@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111;--ink:#eee}}', "")
    r = run(tmp_path, html)
    assert r.returncode == 1
    assert "dark theme incomplete" in r.stdout


def test_body_without_background_fails(tmp_path):
    r = run(tmp_path, GOOD.replace("body{background:var(--bg);color:var(--ink)}", "body{color:var(--ink)}"))
    assert r.returncode == 1
    assert "body has no explicit background" in r.stdout


def test_decision_without_suggestion_fails(tmp_path):
    r = run(tmp_path, GOOD.replace(" data-suggested", ""))
    assert r.returncode == 1
    assert "fewer suggested options" in r.stdout


def test_decision_without_way_back_fails(tmp_path):
    r = run(tmp_path, GOOD.replace("navigator.clipboard.writeText('x')", "void 0"))
    assert r.returncode == 1
    assert "no way to send answers back" in r.stdout


def test_made_up_file_path_fails(tmp_path):
    r = run(tmp_path, GOOD.replace("<footer>", '<footer><code data-path="src/missing.ts:12">x</code>'))
    assert r.returncode == 1
    assert "src/missing.ts:12" in r.stdout


def test_real_file_path_passes(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.ts").write_text("")
    r = run(tmp_path, GOOD.replace("<footer>", '<footer><code data-path="src/app.ts:3">x</code>'))
    assert r.returncode == 0, r.stdout


def test_republish_needs_change_note(tmp_path):
    r = run(tmp_path, GOOD, "--republish")
    assert r.returncode == 1
    assert "Changed since last version" in r.stdout
    ok = run(tmp_path, GOOD.replace("<h1>", "<div>Changed since last version: price raised.</div><h1>"), "--republish")
    assert ok.returncode == 0, ok.stdout


def test_heading_not_a_question_warns_only(tmp_path):
    r = run(tmp_path, GOOD.replace("Where do we sit?", "Market position"))
    assert r.returncode == 0
    assert "heading is not a question" in r.stdout


def test_unplain_words_warn(tmp_path):
    r = run(tmp_path, GOOD.replace("We are the cheapest of five.", "We leverage a robust, seamless price."))
    assert r.returncode == 0
    assert "not plain" in r.stdout and "leverage" in r.stdout
