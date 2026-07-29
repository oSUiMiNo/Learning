"""出来上がったサイトをブラウザで巡回し、見た目と健全性を確認する。

    python tools/preview.py                 # 全ページを検査してスクショを保存
    python tools/preview.py 04-layouts      # 1 ページだけ

調べていること:
  ・JavaScript のコンソールエラーが出ていないか
  ・404 になっている画像やリンクがないか
  ・横スクロールが発生していないか（スマホ幅を含む）
  ・未展開の指示子や「未作成」の目印が残っていないか
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT.parent / "docs"
OUT = ROOT / "tools" / ".preview"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def free_port() -> int:
    """空いているポートを OS に選ばせる。固定にすると同時実行でぶつかる。"""
    import socket
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]

VIEWPORTS = {"desktop": (1280, 900), "mobile": (390, 844)}


def pages() -> list[str]:
    found = ["index.html"]
    found += sorted(f"{d.name}/index.html" for d in DOCS.iterdir()
                    if d.is_dir() and (d / "index.html").exists())
    return found


def main() -> int:
    if not DOCS.exists():
        print("docs/ がありません。先に tools/build.py を実行してください。", file=sys.stderr)
        return 1

    only = sys.argv[1] if len(sys.argv) > 1 else ""
    targets = [p for p in pages() if only in p]
    OUT.mkdir(parents=True, exist_ok=True)

    port = free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", "-d", str(DOCS), str(port)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1.2)

    problems: list[str] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path=CHROME)
            for theme in ("light", "dark"):
                for vp_name, (w, h) in VIEWPORTS.items():
                    if theme == "dark" and vp_name == "mobile":
                        continue          # 組み合わせ爆発を避ける
                    context = browser.new_context(
                        viewport={"width": w, "height": h},
                        device_scale_factor=2,
                        color_scheme=theme,
                    )
                    page = context.new_page()

                    errors: list[str] = []
                    page.on("console", lambda m: errors.append(f"console: {m.text}")
                            if m.type == "error" else None)
                    page.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
                    page.on("requestfailed",
                            lambda r: errors.append(f"読み込み失敗: {r.url}"))

                    for rel in targets:
                        errors.clear()
                        page.goto(f"http://127.0.0.1:{port}/{rel}",
                                  wait_until="networkidle")
                        # 遅延読み込みのままだと、画面外の画像が写らない。
                        page.evaluate(
                            "() => document.querySelectorAll('img[loading=lazy]')"
                            ".forEach(i => i.loading = 'eager')")
                        page.wait_for_function(
                            "() => Array.from(document.images).every(i => i.complete)",
                            timeout=15000)
                        page.wait_for_timeout(250)

                        label = rel.replace("/index.html", "") or "index"
                        label = "index" if label == "index.html" else label

                        for message in errors:
                            problems.append(f"[{label} / {theme} / {vp_name}] {message}")

                        overflow = page.evaluate(
                            "() => document.documentElement.scrollWidth "
                            "- document.documentElement.clientWidth")
                        if overflow > 1:
                            problems.append(
                                f"[{label} / {theme} / {vp_name}] 横スクロールが {overflow}px 発生")

                        leftovers = page.evaluate(
                            "() => document.querySelectorAll('.missing').length")
                        if leftovers:
                            problems.append(
                                f"[{label}] 未作成の目印が {leftovers} 個残っています")

                        raw = page.content()
                        for marker in ("<!--code:", "<!--shot:", "<!--figure:"):
                            if marker in raw:
                                problems.append(f"[{label}] 展開されていない指示子: {marker}")

                        # 教材の根幹: 表示されているコードが実ファイルと 1 文字も違わないこと。
                        shown = page.evaluate("""() => {
                          const out = {};
                          document.querySelectorAll('.code-block[data-src]').forEach(fig => {
                            const lines = fig.querySelectorAll('code .cl');
                            out[fig.dataset.src] =
                              Array.from(lines).map(el => el.textContent).join('\\n');
                          });
                          return out;
                        }""")
                        for name, text in shown.items():
                            actual = (ROOT / "examples" / name).read_text(encoding="utf-8")
                            if text != actual.rstrip("\n"):
                                problems.append(
                                    f"[{label}] 掲載コードが実ファイルと一致しません: {name}")

                        shot = OUT / f"{label}--{theme}-{vp_name}.png"
                        page.screenshot(path=str(shot), full_page=(vp_name == "desktop"))

                    context.close()
            browser.close()
    finally:
        server.terminate()

    print(f"{len(targets)} ページを検査し、{OUT} に画像を保存しました。")
    if problems:
        print(f"\n{len(problems)} 件の問題:", file=sys.stderr)
        for problem in problems:
            print(f"  ✗ {problem}", file=sys.stderr)
        return 1
    print("問題はありませんでした。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
