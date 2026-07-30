"""公開サイトのルート（教材一覧のハブ）と、旧 URL のリダイレクトを組み立てる。

    python tools/build_hub.py

各教材は自分の `tools/build.py` で `docs/<教材名>/` を生成する。
このスクリプトは教材をまたぐ部分だけを受け持つ。

    docs/index.html      教材一覧（このファイルが生成する）
    docs/.nojekyll       Jekyll を止める
    docs/<旧 slug>/      Qt6 本がルートに居た時代の URL からの転送

ハブは 1 ページしかないので、CSS は外部ファイルにせず埋め込んでいる。
こうすると、どの教材の assets にも依存しない。
"""

from __future__ import annotations

import html
import importlib.util
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "docs"

# --- 教材の一覧 -------------------------------------------------------------
# 3 冊目を足すときは、ここに 1 項目加えるだけでハブに並ぶ。
BOOKS = [
    dict(
        slug="rust",
        source="rust",
        mark="Rs",
        title="Rust 入門",
        subtitle="C# が書ける人のための、所有権から async まで",
        lede="Windows 11 と最新の stable Rust で学ぶ入門書。掲載コードは実際にビルドして"
             "動作確認し、「コンパイルが通らない例」もすべて実際に rustc に通して"
             "エラーコードまで確かめています。",
        # 検証環境の表示に使うキー（各教材の assets/versions.json から読む）。
        # 値そのままだと何の版か分からないので、表示用の見出しを添える。
        badge=[("rustc", ""), ("edition", "")],
    ),
    dict(
        slug="qt6-widgets",
        source="qt6-widgets",
        mark="Qt",
        title="Qt6 Widgets 入門",
        subtitle="Python (PySide6) ではじめるデスクトップ GUI",
        lede="ボタンやレイアウトから ToDo アプリの完成まで。本文のコードは実行可能な"
             "実ファイルそのもので、画面写真もそのコードを動かして撮影しています。",
        badge=[("qt", "Qt"), ("pyside", "PySide6")],
    ),
]

# 旧 URL（Qt6 本が公開ルートに居た時代）→ 移設先。既存のリンクを切らないため残す。
LEGACY_QT6_SLUGS = [
    "00-intro", "01-setup", "02-first-window", "03-signals", "04-layouts",
    "05-widgets", "06-mainwindow", "07-object-tree", "08-dialogs", "09-designer",
    "10-model-view", "11-styling", "12-todo-app", "13-pitfalls", "14-cpp",
]

BASE_URL = "https://osuimino.github.io/Learning"

SITE_TITLE = "Learning — 技術を学ぶための教材集"
SITE_DESCRIPTION = (
    "初心者向けの技術入門書を置いている場所です。載っているコードは実際に動かして"
    "確認したものだけを使い、古い情報でつまずかないことを最優先にしています。"
)


def load_toc(source: str):
    """教材の book/toc.py を読み込んで、章数と通読時間を得る。"""
    path = ROOT / source / "book" / "toc.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(f"toc_{source}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_versions(slug: str) -> dict:
    path = SITE / slug / "assets" / "versions.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


CSS = """
:root {
  --bg: #fbfaf7; --bg-sunken: #f3f1ec; --surface: #ffffff;
  --text: #1e2227; --text-soft: #4a525c; --text-mute: #6f7883;
  --border: #e4e0d8; --border-strong: #d2ccc0;
  --accent: #17803d; --accent-hover: #0f6330;
  --shadow-sm: 0 1px 2px rgb(28 25 20 / 6%), 0 2px 6px rgb(28 25 20 / 5%);
  --shadow-md: 0 4px 12px rgb(28 25 20 / 8%), 0 12px 28px rgb(28 25 20 / 7%);
  --radius: 14px;
  --font-jp: "Hiragino Kaku Gothic ProN", "Hiragino Sans", "Yu Gothic Medium",
             "Yu Gothic", "Noto Sans JP", "Noto Sans CJK JP", Meiryo, system-ui, sans-serif;
  --font-ui: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, var(--font-jp);
  --font-mono: "SFMono-Regular", "SF Mono", Menlo, Consolas, "Roboto Mono", monospace;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #14171b; --bg-sunken: #101317; --surface: #1a1e23;
    --text: #e7eaee; --text-soft: #b9c1cb; --text-mute: #8d97a3;
    --border: #2b3138; --border-strong: #3a424b;
    --accent: #5fd873; --accent-hover: #85e694;
    --shadow-sm: 0 1px 2px rgb(0 0 0 / 40%), 0 2px 6px rgb(0 0 0 / 30%);
    --shadow-md: 0 6px 16px rgb(0 0 0 / 45%), 0 16px 40px rgb(0 0 0 / 35%);
  }
}

*, *::before, *::after { box-sizing: border-box; }

body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(70rem 32rem at 82% -8%, color-mix(in srgb, var(--accent) 9%, transparent), transparent 70%),
    var(--bg);
  color: var(--text);
  font-family: var(--font-ui);
  font-size: 17px;
  line-height: 1.9;
  font-feature-settings: "palt" 1;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

a { color: var(--accent); text-underline-offset: .18em; }
a:hover { color: var(--accent-hover); }
:focus-visible { outline: 2.5px solid var(--accent); outline-offset: 3px; border-radius: 6px; }

.wrap { max-width: 54rem; margin: 0 auto; padding: 4.5rem 1.5rem 5rem; }

.masthead { margin-bottom: 3.5rem; }
.eyebrow {
  margin: 0 0 .5rem;
  color: var(--text-mute);
  font-size: .76rem;
  font-weight: 700;
  letter-spacing: .16em;
  text-transform: uppercase;
}
h1 {
  margin: 0 0 .7rem;
  font-size: clamp(1.9rem, 5vw, 2.7rem);
  line-height: 1.35;
  letter-spacing: -.01em;
}
.tagline { margin: 0; max-width: 40rem; color: var(--text-soft); }

h2 {
  margin: 0 0 1.5rem;
  padding-top: 1.6rem;
  border-top: 1px solid var(--border);
  font-size: 1.12rem;
  letter-spacing: .01em;
}

/* --- 教材カード --------------------------------------------------------- */
.books { display: grid; gap: 1.25rem; margin: 0 0 3.5rem; padding: 0; list-style: none; }

.book {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  box-shadow: var(--shadow-sm);
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.book:hover {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--accent) 40%, var(--border));
  box-shadow: var(--shadow-md);
}

.book > a {
  display: grid;
  grid-template-columns: 3.4rem 1fr;
  gap: 0 1.15rem;
  padding: 1.5rem 1.6rem;
  color: inherit;
  text-decoration: none;
}

.mark {
  display: grid;
  place-items: center;
  width: 3.4rem;
  height: 3.4rem;
  border-radius: 12px;
  background: color-mix(in srgb, var(--accent) 13%, var(--surface));
  border: 1px solid color-mix(in srgb, var(--accent) 30%, var(--border));
  color: var(--accent);
  font-family: var(--font-mono);
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: -.02em;
}

.book-body { min-width: 0; }
.book-title { display: block; font-size: 1.22rem; font-weight: 700; line-height: 1.5; }
.book-sub { display: block; margin-top: .1rem; color: var(--text-mute); font-size: .89rem; }
.book-lede { margin: .7rem 0 0; color: var(--text-soft); font-size: .95rem; line-height: 1.85; }

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: .45rem;
  margin: 1rem 0 0;
  padding: 0;
  list-style: none;
}
.meta li {
  padding: .18rem .6rem;
  border: 1px solid var(--border-strong);
  border-radius: 999px;
  background: var(--bg-sunken);
  color: var(--text-mute);
  font-family: var(--font-mono);
  font-size: .74rem;
  letter-spacing: .02em;
}
.meta li.is-accent {
  border-color: color-mix(in srgb, var(--accent) 38%, var(--border));
  background: color-mix(in srgb, var(--accent) 11%, var(--surface));
  color: var(--accent);
}

.go { display: block; margin-top: 1rem; color: var(--accent); font-size: .9rem; font-weight: 700; }
.book:hover .go { color: var(--accent-hover); }

/* --- 約束 --------------------------------------------------------------- */
.promise { margin: 0 0 3rem; padding: 0; list-style: none; display: grid; gap: 1.1rem; }
.promise li {
  padding-left: 1.9rem;
  position: relative;
  color: var(--text-soft);
  font-size: .95rem;
}
.promise li::before {
  content: "";
  position: absolute;
  left: .35rem; top: .72rem;
  width: .5rem; height: .5rem;
  border-radius: 50%;
  background: var(--accent);
}
.promise strong { display: block; color: var(--text); font-size: 1rem; }

footer {
  margin-top: 1rem;
  padding-top: 1.7rem;
  border-top: 1px solid var(--border);
  color: var(--text-mute);
  font-size: .82rem;
}
footer p { margin: .2rem 0; }
code { font-family: var(--font-mono); font-size: .88em; }

@media (max-width: 34rem) {
  body { font-size: 16px; }
  .wrap { padding: 3rem 1.15rem 3.5rem; }
  .book > a { grid-template-columns: 1fr; gap: .9rem; }
  .mark { width: 2.8rem; height: 2.8rem; font-size: 1rem; }
}
"""


def book_card(book: dict) -> str:
    toc = load_toc(book["source"])
    versions = load_versions(book["slug"])

    chips: list[str] = []
    if toc is not None:
        chapters = len(toc.CHAPTERS)
        minutes = sum(c["minutes"] for c in toc.CHAPTERS)
        hours, mins = divmod(minutes, 60)
        span = f"約 {hours} 時間 {mins} 分" if hours else f"約 {mins} 分"
        chips.append(f"<li>全 {chapters} 章</li>")
        chips.append(f"<li>通読 {span}</li>")
    for key, label in book["badge"]:
        value = versions.get(key)
        if value:
            shown = f"{label} {value}".strip()
            chips.append(f'<li class="is-accent">{html.escape(shown)}</li>')
    if versions.get("date"):
        chips.append(f'<li>{html.escape(versions["date"])} 検証</li>')

    return f"""      <li class="book">
        <a href="{book['slug']}/">
          <span class="mark" aria-hidden="true">{html.escape(book['mark'])}</span>
          <span class="book-body">
            <span class="book-title">{html.escape(book['title'])}</span>
            <span class="book-sub">{html.escape(book['subtitle'])}</span>
            <span class="book-lede">{html.escape(book['lede'])}</span>
            <ul class="meta">
{chr(10).join('              ' + c for c in chips)}
            </ul>
            <span class="go">読みはじめる →</span>
          </span>
        </a>
      </li>"""


def build_index() -> str:
    cards = "\n".join(book_card(b) for b in BOOKS if (SITE / b["slug"]).exists())
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(SITE_TITLE)}</title>
<meta name="description" content="{html.escape(SITE_DESCRIPTION)}">
<meta name="color-scheme" content="light dark">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>&#128218;</text></svg>">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <header class="masthead">
    <p class="eyebrow">Learning</p>
    <h1>技術を学ぶための教材集</h1>
    <p class="tagline">{html.escape(SITE_DESCRIPTION)}</p>
  </header>

  <main>
    <h2>教材一覧</h2>
    <ul class="books">
{cards}
    </ul>

    <h2>どの教材にも共通していること</h2>
    <ul class="promise">
      <li>
        <strong>載っているコードは、実際に動かして確認したものだけ</strong>
        本文のコードは実行可能な実ファイルをそのまま読み込んで表示しています。
        書き写す途中で壊れる、ということが起きません。
      </li>
      <li>
        <strong>画面や出力は、そのコードを動かして得たもの</strong>
        イラストや作図ではなく、実際に走らせた結果を載せています。
        再現でしか示せないものは、そうと明記します。
      </li>
      <li>
        <strong>「古い記事どおりに書いたのに動かない」を先に片付ける</strong>
        入門でいちばん多い挫折はここです。バージョンによって変わった箇所は
        本文中で名指しし、いま何が正しいかを実測に基づいて書いています。
      </li>
    </ul>
  </main>

  <footer>
    <p>ソースは <a href="https://github.com/oSUiMiNo/Learning">github.com/oSUiMiNo/Learning</a></p>
    <p>{date.today().isoformat()} 更新</p>
  </footer>
</div>
</body>
</html>
"""


def redirect_page(to: str, label: str) -> str:
    """旧 URL に置く転送ページ。JS を切っていても手で辿れるようにリンクも出す。"""
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>移転しました — {html.escape(label)}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{BASE_URL}/{to}">
<meta http-equiv="refresh" content="0; url=../{to}">
<style>
body {{ margin: 0; display: grid; place-items: center; min-height: 100vh;
  background: #fbfaf7; color: #1e2227; line-height: 1.9;
  font-family: -apple-system, "Segoe UI", "Hiragino Kaku Gothic ProN", "Yu Gothic Medium",
               "Noto Sans JP", Meiryo, sans-serif; }}
@media (prefers-color-scheme: dark) {{ body {{ background: #14171b; color: #e7eaee; }} }}
.card {{ max-width: 30rem; padding: 2rem 1.5rem; text-align: center; }}
a {{ color: #17803d; }}
@media (prefers-color-scheme: dark) {{ a {{ color: #5fd873; }} }}
</style>
</head>
<body>
<div class="card">
  <p>このページは移転しました。</p>
  <p><a href="../{to}">{html.escape(label)} へ移動する</a></p>
</div>
</body>
</html>
"""


def main() -> int:
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(build_index(), encoding="utf-8")
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    # Qt6 本が公開ルートに居た時代の URL からの転送。
    qt6_toc = load_toc("qt6-widgets")
    labels = {c["slug"]: c["title"] for c in qt6_toc.CHAPTERS} if qt6_toc else {}
    for slug in LEGACY_QT6_SLUGS:
        out = SITE / slug / "index.html"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            redirect_page(f"qt6-widgets/{slug}/", labels.get(slug, slug)),
            encoding="utf-8")

    listed = [b["slug"] for b in BOOKS if (SITE / b["slug"]).exists()]
    print(f"docs/index.html を生成しました（教材 {len(listed)} 冊: {', '.join(listed)}）")
    print(f"旧 URL の転送ページを {len(LEGACY_QT6_SLUGS)} 件置きました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
