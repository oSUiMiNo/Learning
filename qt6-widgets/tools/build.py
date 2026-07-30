"""教材のソースから、GitHub Pages で公開する docs/ を組み立てる。

    python tools/build.py            # ビルド
    python tools/build.py --check    # 壊れている箇所がないかだけ調べる

本文 (book/*.html) の中では、次の 3 つの指示子が使える。

    <!--code: ch02_hello.py-->                  examples/ の実ファイルを構文強調して差し込む
    <!--shot: ch02-window | キャプション-->      実際に撮影したスクリーンショットを差し込む
    <!--figure: event-loop | キャプション-->     assets/figures/ の SVG 図をそのまま差し込む

コードは「本文用に書き写したもの」ではなく examples/ の実物を読み込む。
スクリーンショットもその実物を動かして撮っている。
だから本文・コード・画面写真が食い違うことが原理的に起きない。
"""

from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer, get_lexer_by_name

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
BOOK = ROOT / "book"
EXAMPLES = ROOT / "examples"
ASSETS = ROOT / "assets"
FIGURES = ASSETS / "figures"
SITE = REPO / "docs"          # GitHub Pages の公開ルート（教材一覧のハブ）
DOCS = SITE / "qt6-widgets"   # この教材の出力先。ハブの下に 1 冊ぶんとして入る

sys.path.insert(0, str(BOOK))
import toc  # noqa: E402

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


# ---------------------------------------------------------------------------
# 環境情報（教材が何で検証されたかをページに明記するため、ビルド時に実測する）
# ---------------------------------------------------------------------------
def collect_versions() -> dict:
    code = (
        "import sys, PySide6;"
        "from PySide6 import QtCore;"
        "print(PySide6.__version__);print(QtCore.qVersion());"
        "print('.'.join(map(str, sys.version_info[:3])))"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    if out.returncode != 0:
        fail("PySide6 のバージョンを取得できませんでした: " + out.stderr.strip())
        return {"pyside": "?", "qt": "?", "python": "?", "date": date.today().isoformat()}
    pyside, qt, python = out.stdout.split()
    return {"pyside": pyside, "qt": qt, "python": python, "date": date.today().isoformat()}


# ---------------------------------------------------------------------------
# コードの構文強調
# ---------------------------------------------------------------------------
TAG_RE = re.compile(r"(<span[^>]*>|</span>)")


def split_into_lines(marked_up: str) -> str:
    """Pygments の出力を 1 行ずつ <span class="cl"> で包む。

    複数行にまたがる span（docstring など）があるので、
    行末でいったん閉じ、次の行で開き直す。
    """
    open_tags: list[str] = []
    lines: list[str] = []
    current: list[str] = []

    def flush() -> None:
        lines.append(f'<span class="cl">{"".join(current)}{"</span>" * len(open_tags)}</span>')
        current.clear()
        current.extend(open_tags)

    current.extend(open_tags)
    for piece in TAG_RE.split(marked_up):
        if not piece:
            continue
        if piece.startswith("</span"):
            if open_tags:
                open_tags.pop()
            current.append(piece)
        elif piece.startswith("<span"):
            open_tags.append(piece)
            current.append(piece)
        else:
            parts = piece.split("\n")
            for i, part in enumerate(parts):
                if i:
                    flush()
                current.append(part)
    if "".join(current).strip():
        flush()
    while lines and not re.sub(r"<[^>]+>", "", lines[-1]).strip():
        lines.pop()
    # <pre> の中なので、行の間に改行文字を入れるとブロック要素の改行と二重になる。
    # 各行が display:block の span なので、区切り文字は不要。
    return "".join(lines)


def render_code(source: str, *, language: str = "python", filename: str = "",
                caption: str = "", source_file: str = "") -> str:
    lexer = PythonLexer() if language == "python" else get_lexer_by_name(language)
    body = split_into_lines(highlight(source, lexer, HtmlFormatter(nowrap=True)).rstrip("\n"))
    label = filename or {"bash": "ターミナル", "xml": "XML", "css": "スタイルシート",
                         "cpp": "C++", "cmake": "CMake"}.get(language, language)
    head = (
        '<div class="code-head">'
        f'<span class="code-file{"" if filename else " code-file--plain"}">'
        f"{html.escape(label)}</span>"
        '<button class="code-copy" type="button" data-copy>コピー</button>'
        "</div>"
    )
    cap = f'<figcaption class="code-cap">{caption}</figcaption>' if caption else ""
    # data-src が付いているブロックは、tools/preview.py が
    # 「表示されている内容 ＝ examples/ の実ファイル」であることを機械的に検証する。
    src_attr = f' data-src="{html.escape(source_file)}"' if source_file else ""
    return (
        f'<figure class="code-block" data-lang="{html.escape(language)}"{src_attr}>{head}'
        f'<pre><code>{body}</code></pre>{cap}</figure>'
    )


# ---------------------------------------------------------------------------
# 指示子の展開
# ---------------------------------------------------------------------------
CODE_RE = re.compile(r"<!--\s*code:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)
SHOT_RE = re.compile(r"<!--\s*shot:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)
FIG_RE = re.compile(r"<!--\s*figure:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)


# 拡張子から構文強調の種類を決める。examples/cpp/ の C++ 版サンプルのため。
LANGUAGE_BY_SUFFIX = {".py": "python", ".cpp": "cpp", ".h": "cpp",
                      ".ui": "xml", ".txt": "cmake", ".qss": "css"}


def expand_code(text: str, chapter: str) -> str:
    def repl(m: re.Match) -> str:
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        path = EXAMPLES / name
        if not path.exists():
            fail(f"[{chapter}] サンプルが見つかりません: examples/{name}")
            return f'<p class="missing">サンプル未作成: {name}</p>'
        language = LANGUAGE_BY_SUFFIX.get(path.suffix, "text")
        if path.name == "CMakeLists.txt":
            language = "cmake"
        return render_code(path.read_text(encoding="utf-8"), language=language,
                           filename=name, caption=caption, source_file=name)

    return CODE_RE.sub(repl, text)


SRC_RE = re.compile(
    r'<div class="src"((?:\s+data-[a-z]+="[^"]*")*)\s*>\n?(.*?)</div>', re.S)
ATTR_RE = re.compile(r'data-([a-z]+)="([^"]*)"')


def expand_snippets(text: str, chapter: str) -> str:
    """本文中に直接書かれた短いコード（シェルコマンドなど）を構文強調する。

        <div class="src" data-lang="bash" data-file="ターミナル">
        pip install pyside6
        </div>
    """

    def repl(m: re.Match) -> str:
        attrs = dict(ATTR_RE.findall(m.group(1) or ""))
        body = html.unescape(m.group(2)).strip("\n")
        if not body.strip():
            fail(f"[{chapter}] 中身が空のコードブロックがあります")
        return render_code(
            body,
            language=attrs.get("lang", "python"),
            filename=attrs.get("file", ""),
            caption=attrs.get("cap", ""),
        )

    return SRC_RE.sub(repl, text)


def expand_shots(text: str, chapter: str, shots: dict) -> str:
    def repl(m: re.Match) -> str:
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        meta = shots.get(name)
        if meta is None:
            fail(f"[{chapter}] スクリーンショットが未生成です: {name}")
            return f'<p class="missing">スクリーンショット未生成: {name}</p>'
        title = html.escape(meta["title"] or "（タイトル未設定）")
        alt = html.escape(caption or meta.get("note") or name)
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        return (
            '<figure class="shot">'
            '<div class="shot-frame">'
            f'<div class="shot-bar"><span class="shot-dots"></span>'
            f'<span class="shot-title">{title}</span></div>'
            f'<img src="../img/{name}.webp" alt="{alt}" '
            f'width="{meta["css_width"]}" height="{meta["css_height"]}" loading="lazy" '
            f'decoding="async">'
            "</div>"
            f"{cap}</figure>"
        )

    return SHOT_RE.sub(repl, text)


def expand_figures(text: str, chapter: str) -> str:
    def repl(m: re.Match) -> str:
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        path = FIGURES / f"{name}.svg"
        if not path.exists():
            fail(f"[{chapter}] 図が見つかりません: assets/figures/{name}.svg")
            return f'<p class="missing">図が未作成: {name}</p>'
        svg = path.read_text(encoding="utf-8")
        svg = re.sub(r"<\?xml[^>]*\?>\s*", "", svg)
        cap = f"<figcaption>{caption}</figcaption>" if caption else ""
        return f'<figure class="diagram">{svg}{cap}</figure>'

    return FIG_RE.sub(repl, text)


# ---------------------------------------------------------------------------
# 見出しに id を振る（「この章の内容」のリンク先になる）
# ---------------------------------------------------------------------------
HEADING_RE = re.compile(r"<(h2|h3)([^>]*)>(.*?)</\1>", re.S)


def slugify(text: str, used: set[str]) -> str:
    plain = re.sub(r"<[^>]+>", "", text)
    plain = html.unescape(plain).strip()
    base = re.sub(r"[\s　]+", "-", plain)
    base = re.sub(r"[^\w\-ぁ-んァ-ヶ一-龥ー]", "", base) or "section"
    slug, n = base, 2
    while slug in used:
        slug, n = f"{base}-{n}", n + 1
    used.add(slug)
    return slug


def add_heading_ids(text: str) -> str:
    used: set[str] = set()

    def repl(m: re.Match) -> str:
        tag, attrs, inner = m.groups()
        if "id=" in attrs:
            return m.group(0)
        return f'<{tag} id="{slugify(inner, used)}"{attrs}>{inner}</{tag}>'

    return HEADING_RE.sub(repl, text)


# ---------------------------------------------------------------------------
# ページの外枠
# ---------------------------------------------------------------------------
def sidebar_html(current: str | None) -> str:
    items = []
    for i, ch in enumerate(toc.CHAPTERS):
        cls = " class=\"is-current\"" if ch["slug"] == current else ""
        num = "はじめに" if i == 0 else f"第{i}章"
        items.append(
            f'<li{cls}><a href="../{ch["slug"]}/">'
            f'<span class="nav-num">{num}</span>'
            f'<span class="nav-label">{ch["label"]}</span></a></li>'
        )
    return "\n".join(items)


def page(*, title: str, description: str, body: str, current: str | None,
         versions: dict, root: str, extra_class: str = "") -> str:
    nav = sidebar_html(current)
    if root == "./":
        nav = nav.replace('href="../', 'href="')
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta name="color-scheme" content="light dark">
<link rel="stylesheet" href="{root}assets/style.css">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>&#129513;</text></svg>">
<script>
// テーマのちらつき防止のため、CSS より先に実行する。
(function () {{
  try {{
    var saved = localStorage.getItem('qt6book-theme');
    if (saved) document.documentElement.dataset.theme = saved;
  }} catch (e) {{}}
}})();
</script>
</head>
<body class="{extra_class}">
<a class="skip-link" href="#main">本文へスキップ</a>
<div class="reading-progress"><span id="reading-bar"></span></div>

<header class="topbar">
  <button class="icon-btn nav-toggle" type="button" aria-expanded="false" aria-controls="sidebar" aria-label="目次を開く">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>
  </button>
  <a class="brand" href="{root}">
    <span class="brand-mark" aria-hidden="true">Qt</span>
    <span class="brand-text">{html.escape(toc.BOOK_TITLE)}</span>
  </a>
  <span class="verbadge" title="この教材の全コードは、この構成で実際に動作確認されています">
    Qt {versions['qt']} / PySide6 {versions['pyside']}
  </span>
  <button class="icon-btn theme-toggle" type="button" aria-label="配色を切り替える">
    <svg class="i-sun" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="4.2"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M19.1 4.9L17 7M7 17l-2.1 2.1"/></svg>
    <svg class="i-moon" viewBox="0 0 24 24" aria-hidden="true"><path d="M20 14.5A8.5 8.5 0 0 1 9.5 4a8.5 8.5 0 1 0 10.5 10.5z"/></svg>
  </button>
</header>

<div class="shell">
  <nav class="sidebar" id="sidebar" aria-label="目次">
    <p class="sidebar-title">目次</p>
    <ol class="nav-list">
{nav}
    </ol>
  </nav>
  <div class="sidebar-scrim" hidden></div>

  <main id="main">
{body}
  </main>
</div>

<footer class="site-footer">
  <p>{html.escape(toc.BOOK_TITLE)} — {html.escape(toc.BOOK_SUBTITLE)}</p>
  <p class="footer-meta">
    Qt {versions['qt']} / PySide6 {versions['pyside']} / Python {versions['python']} で検証（{versions['date']} 時点）
  </p>
</footer>

<script src="{root}assets/book.js" defer></script>
</body>
</html>
"""


def pager_html(index: int) -> str:
    parts = ['<nav class="pager" aria-label="章の移動">']
    if index > 0:
        prev = toc.CHAPTERS[index - 1]
        parts.append(
            f'<a class="pager-link pager-prev" href="../{prev["slug"]}/">'
            f'<span class="pager-dir">← 前の章</span>'
            f'<span class="pager-title">{html.escape(prev["label"])}</span></a>'
        )
    else:
        parts.append('<span class="pager-link pager-empty"></span>')
    if index < len(toc.CHAPTERS) - 1:
        nxt = toc.CHAPTERS[index + 1]
        parts.append(
            f'<a class="pager-link pager-next" href="../{nxt["slug"]}/">'
            f'<span class="pager-dir">次の章 →</span>'
            f'<span class="pager-title">{html.escape(nxt["label"])}</span></a>'
        )
    parts.append("</nav>")
    return "\n".join(parts)


def build_chapter(index: int, chapter: dict, shots: dict, versions: dict) -> str:
    src = BOOK / f"{chapter['slug']}.html"
    if not src.exists():
        fail(f"本文がありません: book/{chapter['slug']}.html")
        return ""

    text = src.read_text(encoding="utf-8")
    text = expand_code(text, chapter["slug"])
    text = expand_snippets(text, chapter["slug"])
    text = expand_shots(text, chapter["slug"], shots)
    text = expand_figures(text, chapter["slug"])
    text = add_heading_ids(text)

    eyebrow = "はじめに" if index == 0 else f"第 {index} 章"
    body = f"""    <article class="chapter">
      <header class="chapter-head">
        <p class="eyebrow">{eyebrow}<span class="dot">·</span>読了目安 {chapter['minutes']} 分</p>
        <h1>{html.escape(chapter['title'])}</h1>
        <p class="lede">{html.escape(chapter['lede'])}</p>
      </header>
      <div class="prose">
{text}
      </div>
{pager_html(index)}
    </article>"""

    return page(
        title=f"{chapter['title']} | {toc.BOOK_TITLE}",
        description=chapter["lede"],
        body=body,
        current=chapter["slug"],
        versions=versions,
        root="../",
    )


def build_index(versions: dict) -> str:
    cards = []
    for i, ch in enumerate(toc.CHAPTERS):
        num = "はじめに" if i == 0 else f"第 {i} 章"
        cards.append(f"""      <li class="toc-card">
        <a href="{ch['slug']}/">
          <span class="toc-num">{num}</span>
          <span class="toc-title">{html.escape(ch['label'])}</span>
          <span class="toc-lede">{html.escape(ch['lede'])}</span>
          <span class="toc-time">{ch['minutes']} 分</span>
        </a>
      </li>""")
    total = sum(c["minutes"] for c in toc.CHAPTERS)

    body = f"""    <article class="cover">
      <header class="cover-head">
        <p class="eyebrow">Python ではじめる デスクトップ GUI</p>
        <h1>{html.escape(toc.BOOK_TITLE)}</h1>
        <p class="cover-sub">{html.escape(toc.BOOK_SUBTITLE)}</p>
        <p class="cover-lede">{html.escape(toc.BOOK_DESCRIPTION)}</p>
        <p class="cover-actions">
          <a class="btn btn-primary" href="{toc.CHAPTERS[0]['slug']}/">読みはじめる</a>
          <a class="btn" href="{toc.CHAPTERS[1]['slug']}/">環境構築から始める</a>
        </p>
      </header>

      <section class="promise">
        <h2>この教材の約束</h2>
        <ul class="promise-list">
          <li>
            <strong>載っているコードは、すべて実際に動かして確認済み</strong>
            本文のコードは <code>examples/</code> にある実ファイルをそのまま読み込んで表示しています。
            書き写す途中で壊れる、ということが起きません。
          </li>
          <li>
            <strong>画面写真は、その同じコードを動かして撮ったもの</strong>
            イラストでも作図でもなく、Qt {versions['qt']} が実際に描画した画面です。
          </li>
          <li>
            <strong>「昔はこう書いた」を毎回はっきり書く</strong>
            Qt5 時代の記事をそのまま真似すると動かない箇所は、
            ⚠️ つまずきポイントとして本文中で名指しします。
          </li>
        </ul>
        <p class="verline">
          検証環境: <strong>Qt {versions['qt']}</strong> ／
          <strong>PySide6 {versions['pyside']}</strong> ／
          <strong>Python {versions['python']}</strong>（{versions['date']} 時点の最新）
        </p>
      </section>

      <section class="toc-section">
        <h2>目次<span class="toc-total">全 {len(toc.CHAPTERS)} 章 · 通読 約 {total} 分</span></h2>
        <ol class="toc-cards">
{chr(10).join(cards)}
        </ol>
      </section>
    </article>"""

    return page(
        title=f"{toc.BOOK_TITLE} — {toc.BOOK_SUBTITLE}",
        description=toc.BOOK_DESCRIPTION,
        body=body,
        current=None,
        versions=versions,
        root="./",
        extra_class="is-cover",
    )


def check_internal_links() -> None:
    slugs = {c["slug"] for c in toc.CHAPTERS}
    for src in BOOK.glob("*.html"):
        for href in re.findall(r'href="\.\./([^"/#]+)/', src.read_text(encoding="utf-8")):
            if href not in slugs:
                fail(f"[{src.stem}] リンク先の章がありません: ../{href}/")


def main() -> int:
    check_only = "--check" in sys.argv

    known = {c["slug"] for c in toc.CHAPTERS}
    for src in BOOK.glob("*.html"):
        if src.stem not in known:
            fail(f"toc.py に登録されていない本文があります: book/{src.name}")

    versions = collect_versions()
    shots_file = DOCS / "img" / "shots.json"
    shots = json.loads(shots_file.read_text(encoding="utf-8")) if shots_file.exists() else {}
    if not shots:
        fail("スクリーンショットが 1 枚もありません（先に tools/shots.py を実行してください）")

    check_internal_links()

    pages = {"index.html": build_index(versions)}
    for i, chapter in enumerate(toc.CHAPTERS):
        rendered = build_chapter(i, chapter, shots, versions)
        if rendered:
            pages[f"{chapter['slug']}/index.html"] = rendered

    if errors:
        print(f"\n{len(errors)} 件の問題が見つかりました:\n", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        if check_only:
            return 1
        print("\n（問題のある箇所は目印を残したまま出力を続行します）\n", file=sys.stderr)

    if check_only:
        print("問題はありませんでした。")
        return 0

    for rel, content in pages.items():
        out = DOCS / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content, encoding="utf-8")

    out_assets = DOCS / "assets"
    out_assets.mkdir(parents=True, exist_ok=True)
    for name in ("style.css", "book.js"):
        shutil.copy2(ASSETS / name, out_assets / name)
    # .nojekyll はサイト全体に効かせたいので、教材ごとではなく公開ルートに置く。
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    (DOCS / "assets" / "versions.json").write_text(
        json.dumps(versions, ensure_ascii=False, indent=2), encoding="utf-8")

    total_kb = sum(p.stat().st_size for p in DOCS.rglob("*") if p.is_file()) / 1024
    print(f"docs/qt6-widgets/ に {len(pages)} ページを出力しました（{total_kb:.0f} KB）")
    # 公開ルートごと配信すれば、教材一覧からの行き来も確かめられる。
    print(f"確認: python -m http.server -d {SITE} 8000")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
