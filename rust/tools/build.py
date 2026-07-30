"""教材のソースから、GitHub Pages で公開する docs/rust/ を組み立てる。

    python tools/build.py            # ビルド
    python tools/build.py --check    # 壊れている箇所がないかだけ調べる

本文 (book/*.html) の中では、次の 4 つの指示子が使える。

    <!--code: 06-ownership/src/main.rs-->    examples/ の実ファイルを構文強調して差し込む
    <!--figure: move | キャプション-->        assets/figures/ の SVG 図をそのまま差し込む
    <!--term: e0382 | キャプション-->         ★ 実際に走らせて捕獲した出力（実測バッジ）
    <!--termx: rustup-init | キャプション-->  ★ 公式情報どおりに再現した画面（再現バッジ）

コードは「本文用に書き写したもの」ではなく examples/ の実物を読み込む。
ターミナル出力も実際にコマンドを走らせて捕獲したものを読み込む。
だから本文・コード・出力が食い違うことが原理的に起きない。

実機でしか出せない画面（Windows のインストーラなど）だけは再現になるが、
<!--termx:--> で入れたものには必ず「再現」バッジと出典が付く。
実測と再現が見た目で混ざらないようにしてある。
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
from pygments.lexers import get_lexer_by_name

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT.parent
BOOK = ROOT / "book"
EXAMPLES = ROOT / "examples"
ASSETS = ROOT / "assets"
FIGURES = ASSETS / "figures"
OUTPUTS = ROOT / "outputs"
SITE = REPO / "docs"
DOCS = SITE / "rust"

sys.path.insert(0, str(BOOK))
import toc  # noqa: E402

try:
    import repro  # 再現画面の定義（book/repro.py）
except ModuleNotFoundError:
    repro = None

errors: list[str] = []


def fail(message: str) -> None:
    errors.append(message)


# ---------------------------------------------------------------------------
# 環境情報（教材が何で検証されたかをページに明記するため、ビルド時に実測する）
# ---------------------------------------------------------------------------
def run(*args: str) -> str:
    out = subprocess.run(args, capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else ""


def collect_versions() -> dict:
    """rustc / cargo / エディションを、いま入っているツールチェインから読む。"""
    rustc_v = run("rustc", "--version")           # 例: rustc 1.97.1 (8bab26f4f 2026-07-14)
    cargo_v = run("cargo", "--version")
    clippy_v = run("cargo", "clippy", "--version")

    m = re.search(r"rustc (\S+)", rustc_v)
    if not m:
        fail("rustc のバージョンを取得できませんでした（rustc は入っていますか？）")
    rustc = m.group(1) if m else "?"

    m = re.search(r"cargo (\S+)", cargo_v)
    cargo = m.group(1) if m else "?"

    # `cargo new` が既定で書き込むエディションを、実際に作らせて確かめる。
    # 本文の「いまの既定は 2024 です」という記述の裏取りになる。
    edition = detect_default_edition()

    return {
        "rustc": f"rustc {rustc}",
        "rustc_version": rustc,
        "cargo": cargo,
        "clippy": clippy_v,
        "edition": f"edition {edition}",
        "edition_year": edition,
        "host": run("rustc", "-vV").split("host: ")[-1].splitlines()[0] if run("rustc", "-vV") else "?",
        "date": date.today().isoformat(),
    }


def detect_default_edition() -> str:
    """一時ディレクトリで cargo new を実行し、生成された Cargo.toml から読む。"""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        out = subprocess.run(
            ["cargo", "new", "--quiet", "--name", "probe", str(Path(tmp) / "probe")],
            capture_output=True, text=True)
        manifest = Path(tmp) / "probe" / "Cargo.toml"
        if out.returncode != 0 or not manifest.exists():
            fail("cargo new が実行できず、既定のエディションを確認できませんでした")
            return "?"
        m = re.search(r'edition\s*=\s*"(\d+)"', manifest.read_text(encoding="utf-8"))
        if not m:
            fail("生成された Cargo.toml にエディションの記載がありません")
            return "?"
        return m.group(1)


# ---------------------------------------------------------------------------
# コードの構文強調
# ---------------------------------------------------------------------------
TAG_RE = re.compile(r"(<span[^>]*>|</span>)")


def split_into_lines(marked_up: str) -> str:
    """Pygments の出力を 1 行ずつ <span class="cl"> で包む。

    複数行にまたがる span（ブロックコメントなど）があるので、
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


PLAIN_LABEL = {
    "bash": "PowerShell",
    "powershell": "PowerShell",
    "console": "ターミナル",
    "text": "テキスト",
    "toml": "TOML",
    "csharp": "C#",
    "rust": "Rust",
    "json": "JSON",
    "diff": "差分",
}


def render_code(source: str, *, language: str = "rust", filename: str = "",
                caption: str = "", source_file: str = "") -> str:
    lexer = get_lexer_by_name(language)
    body = split_into_lines(highlight(source, lexer, HtmlFormatter(nowrap=True)).rstrip("\n"))
    label = filename or PLAIN_LABEL.get(language, language)
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
# ANSI エスケープ → HTML
# ---------------------------------------------------------------------------
# rustc / cargo は色付きで出力する。その色をそのままページで再現するため、
# SGR シーケンスを .a-* クラスの span に変換する。
# 配色は style.css 側で Windows コンソールの既定（Campbell）に合わせている。
SGR_RE = re.compile(r"\x1b\[([0-9;]*)m")
# 色以外の制御シーケンスを捨てるための式。終端文字から m だけを外してあるので、
# 色指定（\x1b[1m など）はここでは消えずに SGR_RE の側に残る。
# この 1 文字を外し忘れると、色が全部落ちて白黒の出力になる。
OTHER_CSI_RE = re.compile(r"\x1b\[[0-9;?]*[a-ln-zA-Z]|\x1b[()][A-Z0-9]|\x1b[=>]")

ATTR_BY_CODE = {1: "a-b", 2: "a-dim", 3: "a-i", 4: "a-u"}
ATTR_OFF = {22: ("a-b", "a-dim"), 23: ("a-i",), 24: ("a-u",)}


def ansi_to_html(text: str) -> str:
    """ANSI 付きのテキストを、色クラスつきの HTML に変換する。"""
    # cargo の進捗表示は \r で同じ行を上書きする。最後の状態だけを残す。
    lines = []
    for raw in text.replace("\r\n", "\n").split("\n"):
        lines.append(raw.split("\r")[-1] if "\r" in raw else raw)
    text = "\n".join(lines)

    # 色以外の制御シーケンス（カーソル移動・行消去など）は捨てる。
    text = OTHER_CSI_RE.sub("", text)

    out: list[str] = []
    attrs: set[str] = set()
    fg: str | None = None
    open_span = False

    def close() -> None:
        nonlocal open_span
        if open_span:
            out.append("</span>")
            open_span = False

    def open_() -> None:
        nonlocal open_span
        classes = sorted(attrs) + ([fg] if fg else [])
        if classes:
            out.append(f'<span class="{" ".join(classes)}">')
            open_span = True

    pos = 0
    for m in SGR_RE.finditer(text):
        chunk = text[pos:m.start()]
        if chunk:
            close()
            open_()
            out.append(html.escape(chunk))
            close()
        pos = m.end()

        params = [int(p) for p in m.group(1).split(";") if p != ""] or [0]
        for code in params:
            if code == 0:
                attrs.clear()
                fg = None
            elif code in ATTR_BY_CODE:
                attrs.add(ATTR_BY_CODE[code])
            elif code in ATTR_OFF:
                for name in ATTR_OFF[code]:
                    attrs.discard(name)
            elif 30 <= code <= 37 or 90 <= code <= 97:
                fg = f"a-{code}"
            elif code == 39:
                fg = None
            # 背景色（40-47 / 100-107）は rustc が使わないので無視する。

    chunk = text[pos:]
    if chunk:
        close()
        open_()
        out.append(html.escape(chunk))
        close()
    close()
    return "".join(out).rstrip("\n")


def term_frame(*, title: str, body_html: str, real: bool, caption: str) -> str:
    """ターミナル枠。実測か再現かのバッジを必ず付ける。"""
    if real:
        badge = ('<span class="term-badge term-badge--real" '
                 'title="実際にこのコマンドを走らせて捕獲した出力です">実測</span>')
    else:
        badge = ('<span class="term-badge term-badge--repro" '
                 'title="この環境では撮影できないため、公式の情報どおりに再現したものです">再現</span>')
    cap = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (
        '<figure class="term">'
        '<div class="term-frame">'
        f'<div class="term-bar"><span class="term-title">{html.escape(title)}</span>'
        f'{badge}<span class="term-dots"></span></div>'
        f'<pre class="term-body"><code>{body_html}</code></pre>'
        "</div>"
        f"{cap}</figure>"
    )


# ---------------------------------------------------------------------------
# 指示子の展開
# ---------------------------------------------------------------------------
CODE_RE = re.compile(r"<!--\s*code:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)
FIG_RE = re.compile(r"<!--\s*figure:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)
TERM_RE = re.compile(r"<!--\s*term:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)
TERMX_RE = re.compile(r"<!--\s*termx:\s*([^|>]+?)\s*(?:\|\s*(.*?)\s*)?-->", re.S)

LANGUAGE_BY_SUFFIX = {
    ".rs": "rust", ".toml": "toml", ".cs": "csharp",
    ".json": "json", ".md": "markdown", ".txt": "text",
}


def expand_code(text: str, chapter: str) -> str:
    def repl(m: re.Match) -> str:
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        path = EXAMPLES / name
        if not path.exists():
            fail(f"[{chapter}] サンプルが見つかりません: examples/{name}")
            return f'<p class="missing">サンプル未作成: {name}</p>'
        language = LANGUAGE_BY_SUFFIX.get(path.suffix, "text")
        # 表示上のファイル名は、章ごとのディレクトリ名を落として短く見せる。
        # 例: 06-ownership/src/main.rs → src/main.rs
        parts = Path(name).parts
        label = "/".join(parts[1:]) if len(parts) > 1 else name
        return render_code(path.read_text(encoding="utf-8"), language=language,
                           filename=label, caption=caption, source_file=name)

    return CODE_RE.sub(repl, text)


SRC_RE = re.compile(
    r'<div class="src"((?:\s+data-[a-z]+="[^"]*")*)\s*>\n?(.*?)</div>', re.S)
ATTR_RE = re.compile(r'data-([a-z]+)="([^"]*)"')


def expand_snippets(text: str, chapter: str) -> str:
    """本文中に直接書かれた短いコード（コマンドなど）を構文強調する。

        <div class="src" data-lang="bash" data-file="PowerShell">
        cargo run
        </div>
    """

    def repl(m: re.Match) -> str:
        attrs = dict(ATTR_RE.findall(m.group(1) or ""))
        body = html.unescape(m.group(2)).strip("\n")
        if not body.strip():
            fail(f"[{chapter}] 中身が空のコードブロックがあります")
        return render_code(
            body,
            language=attrs.get("lang", "rust"),
            filename=attrs.get("file", ""),
            caption=attrs.get("cap", ""),
        )

    return SRC_RE.sub(repl, text)


def expand_terms(text: str, chapter: str, captures: dict) -> str:
    """実測の（＝実際に走らせて捕獲した）ターミナル出力を差し込む。"""

    def repl(m: re.Match) -> str:
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        meta = captures.get(name)
        if meta is None:
            fail(f"[{chapter}] ターミナル出力が未捕獲です: {name}"
                 "（tools/capture.py を実行してください）")
            return f'<p class="missing">ターミナル出力 未捕獲: {name}</p>'
        body = render_capture(meta)
        return term_frame(title=meta.get("title") or "Windows PowerShell",
                          body_html=body, real=True, caption=caption)

    return TERM_RE.sub(repl, text)


def render_capture(meta: dict) -> str:
    """捕獲した内容を、プロンプト行 ＋ 出力の形に組み立てる。"""
    parts = []
    for step in meta["steps"]:
        prompt = html.escape(step.get("prompt", "PS C:\\rust>"))
        command = html.escape(step["command"])
        parts.append(
            f'<span class="term-cmd"><span class="term-prompt">{prompt}</span> {command}</span>')
        rendered = ansi_to_html(step["output"])
        if rendered:
            parts.append(rendered)
    return "\n".join(parts)


def expand_termx(text: str, chapter: str) -> str:
    """再現のターミナル画面を差し込む。出典をキャプションに必ず載せる。"""

    def repl(m: re.Match) -> str:
        name, caption = m.group(1).strip(), (m.group(2) or "").strip()
        entry = (repro.REPRODUCTIONS.get(name) if repro else None)
        if entry is None:
            fail(f"[{chapter}] 再現画面の定義がありません: book/repro.py の {name}")
            return f'<p class="missing">再現画面 未定義: {name}</p>'
        body = ansi_to_html(entry["text"])
        note = (f'<span class="repro-src">この画面は実機でしか出せないため再現です。'
                f'出典: {html.escape(entry["source"])}</span>')
        full_caption = f"{caption} {note}" if caption else note
        return term_frame(title=entry["title"], body_html=body,
                          real=False, caption=full_caption)

    return TERMX_RE.sub(repl, text)


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
        num = "はじめに" if i == 0 else ("付録" if ch["slug"].startswith("99") else f"第{i}章")
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
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'><text y='26' font-size='26'>&#129408;</text></svg>">
<script>
// テーマのちらつき防止のため、CSS より先に実行する。
(function () {{
  try {{
    var saved = localStorage.getItem('rustbook-theme');
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
    <span class="brand-mark" aria-hidden="true">Rs</span>
    <span class="brand-text">{html.escape(toc.BOOK_TITLE)}</span>
  </a>
  <span class="verbadge" title="この教材の全コードは、この構成で実際にビルドして動作確認されています">
    {versions['rustc']} / {versions['edition']}
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
    {versions['rustc']} / cargo {versions['cargo']} / {versions['edition']} で検証（{versions['date']} 時点）
  </p>
  <p class="footer-meta"><a href="../../">ほかの教材を見る</a></p>
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


def build_chapter(index: int, chapter: dict, captures: dict, versions: dict) -> str:
    src = BOOK / f"{chapter['slug']}.html"
    if not src.exists():
        fail(f"本文がありません: book/{chapter['slug']}.html")
        return ""

    text = src.read_text(encoding="utf-8")
    text = expand_code(text, chapter["slug"])
    text = expand_snippets(text, chapter["slug"])
    text = expand_terms(text, chapter["slug"], captures)
    text = expand_termx(text, chapter["slug"])
    text = expand_figures(text, chapter["slug"])
    text = add_heading_ids(text)

    if index == 0:
        eyebrow = "はじめに"
    elif chapter["slug"].startswith("99"):
        eyebrow = "付録"
    else:
        eyebrow = f"第 {index} 章"

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
        if i == 0:
            num = "はじめに"
        elif ch["slug"].startswith("99"):
            num = "付録"
        else:
            num = f"第 {i} 章"
        cards.append(f"""      <li class="toc-card">
        <a href="{ch['slug']}/">
          <span class="toc-num">{num}</span>
          <span class="toc-title">{html.escape(ch['label'])}</span>
          <span class="toc-lede">{html.escape(ch['lede'])}</span>
          <span class="toc-time">{ch['minutes']} 分</span>
        </a>
      </li>""")
    total = sum(c["minutes"] for c in toc.CHAPTERS)
    hours, mins = divmod(total, 60)

    body = f"""    <article class="cover">
      <header class="cover-head">
        <p class="eyebrow">C# が書ける人のための</p>
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
            <strong>載っているコードは、すべて実際にビルドして確認済み</strong>
            本文のコードは <code>examples/</code> にある実ファイルをそのまま読み込んで表示しています。
            書き写す途中で壊れる、ということが起きません。
          </li>
          <li>
            <strong>「コンパイルが通らない例」も、本当に通らないことを確認している</strong>
            所有権の章などで出てくる失敗例は、実際に <code>rustc</code> に通して
            <strong>エラーコードまで一致すること</strong>を機械的に検証しています。
            載っているエラーメッセージは、実物の出力そのものです。
          </li>
          <li>
            <strong>ターミナルの画面は、実際に走らせて捕獲したもの</strong>
            色まで含めて本物です。Windows のインストーラなど、この環境で撮れないものだけは
            再現ですが、その場合は必ず<strong>「再現」と明記</strong>して出典を添えます。
          </li>
          <li>
            <strong>C# の知識を足がかりにし、裏切られる箇所を名指しする</strong>
            対応表を並べるだけでなく、<code>async</code> や文字列のように
            <strong>C# の直感がかえって邪魔になる箇所</strong>を各章で警告します。
          </li>
        </ul>
        <p class="verline">
          検証環境: <strong>{versions['rustc']}</strong> ／
          <strong>cargo {versions['cargo']}</strong> ／
          <strong>{versions['edition']}</strong>（{versions['date']} 時点の最新）
        </p>
      </section>

      <section class="toc-section">
        <h2>目次<span class="toc-total">全 {len(toc.CHAPTERS)} 章 · 通読 約 {hours} 時間 {mins} 分</span></h2>
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


def load_captures() -> dict:
    """outputs/*.json を読み込む。tools/capture.py が書き出したもの。"""
    captures = {}
    for path in sorted(OUTPUTS.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        captures[data["name"]] = data
    return captures


def main() -> int:
    check_only = "--check" in sys.argv

    known = {c["slug"] for c in toc.CHAPTERS}
    for src in BOOK.glob("*.html"):
        if src.stem not in known:
            fail(f"toc.py に登録されていない本文があります: book/{src.name}")

    versions = collect_versions()
    captures = load_captures()
    if not captures:
        fail("ターミナル出力が 1 件も捕獲されていません"
             "（先に tools/capture.py を実行してください）")

    check_internal_links()

    pages = {"index.html": build_index(versions)}
    for i, chapter in enumerate(toc.CHAPTERS):
        rendered = build_chapter(i, chapter, captures, versions)
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
    # .nojekyll はサイト全体に効かせたいので公開ルートに置く。
    (SITE / ".nojekyll").write_text("", encoding="utf-8")
    (out_assets / "versions.json").write_text(
        json.dumps(versions, ensure_ascii=False, indent=2), encoding="utf-8")

    total_kb = sum(p.stat().st_size for p in DOCS.rglob("*") if p.is_file()) / 1024
    print(f"docs/rust/ に {len(pages)} ページを出力しました（{total_kb:.0f} KB）")
    print(f"確認: python -m http.server -d {SITE} 8000")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
