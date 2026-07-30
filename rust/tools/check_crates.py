"""外部クレートの API について本文が書いていることを、実際に compile して確かめる。

    python tools/check_crates.py
    python tools/check_crates.py rand      # 名前で絞り込む

tools/check_errors.py は標準ライブラリだけで完結する例を見る。
こちらは crates.io のクレートを実際に取ってきて、
「昔の記事の書き方は今どうなるか」を実物で確かめる。

なぜこれが必要か:

  数当てゲームは Rust 入門の定番だが、rand クレートの API は
  0.8 → 0.9 → 0.10 と 2 回変わっている。ネット上の記事の大半は
  0.8 の書き方（thread_rng / gen_range）のままで、そのまま書くと動かない。
  しかも 0.10 では `use rand::Rng;` が「コンパイルは通るのにメソッドが生えない」
  という、いちばん分かりにくい失敗のしかたをする。

  この表は本文でいちばん間違えてはいけない箇所なので、
  執筆時の記憶ではなく、毎回実物で確かめる。

各項目の期待値:
    "ok"        … コンパイルが通る
    "E0599" 等  … その診断コードで落ちる
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- 確かめたい主張 --------------------------------------------------------
# (名前, クレートと版指定, ソース, 期待, 説明)
CLAIMS = [
    dict(
        name="rand-current-free-fn",
        crate="rand",
        source='fn main() { let n: u32 = rand::random_range(1..=100); println!("{n}"); }',
        expect="ok",
        note="いまの最短の書き方。トレイトの import が要らない",
    ),
    dict(
        name="rand-current-rngext",
        crate="rand",
        source="use rand::RngExt;\n"
               'fn main() { let mut r = rand::rng(); let n: u32 = r.random_range(1..=100); println!("{n}"); }',
        expect="ok",
        note="いまの標準的な書き方。RngExt を import する",
    ),
    dict(
        name="rand-current-prelude",
        crate="rand",
        source="use rand::prelude::*;\n"
               'fn main() { let mut r = rand::rng(); let n: u32 = r.random_range(1..=100); println!("{n}"); }',
        expect="ok",
        note="prelude をまとめて import しても通る",
    ),
    dict(
        name="rand-0.9-style-Rng-trait",
        crate="rand",
        source="use rand::Rng;\n"
               'fn main() { let mut r = rand::rng(); let n: u32 = r.random_range(1..=100); println!("{n}"); }',
        expect="E0599",
        note="0.9 までの書き方。Rng は今も存在するので import は通るが、"
             "メソッドが RngExt に移ったので生えない",
    ),
    dict(
        name="rand-0.8-style-thread-rng",
        crate="rand",
        source="use rand::Rng;\n"
               'fn main() { let mut r = rand::thread_rng(); let n: u32 = r.gen_range(1..=100); println!("{n}"); }',
        expect="E0425",
        note="0.8 の書き方。ネット記事にいちばん多い形。thread_rng ごと無くなっている",
    ),
]

failures: list[str] = []


def run_claim(claim: dict) -> tuple[bool, str]:
    """一時プロジェクトを作り、依存を足して、そのソースをビルドする。"""
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        project = work / "probe"
        subprocess.run(["cargo", "new", "--quiet", "--vcs", "none", str(project)],
                       capture_output=True, text=True, check=True)
        add = subprocess.run(["cargo", "add", "--quiet", claim["crate"]],
                             cwd=project, capture_output=True, text=True)
        if add.returncode != 0:
            return False, f"cargo add {claim['crate']} に失敗: {add.stderr.strip()[:120]}"

        # 実際に解決された版を控えておく（本文に載せる版と突き合わせるため）
        manifest = (project / "Cargo.toml").read_text(encoding="utf-8")
        m = re.search(rf'{claim["crate"]}\s*=\s*"([^"]+)"', manifest)
        resolved = m.group(1) if m else "?"

        (project / "src" / "main.rs").write_text(claim["source"], encoding="utf-8")
        build = subprocess.run(
            ["cargo", "build", "--quiet", "--message-format=json"],
            cwd=project, capture_output=True, text=True)

        codes: list[str] = []
        for line in build.stdout.splitlines():
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = data.get("message") or {}
            if msg.get("level") == "error":
                code = (msg.get("code") or {}).get("code")
                if code:
                    codes.append(code)

        ok_build = build.returncode == 0
        expect = claim["expect"]

        if expect == "ok":
            if ok_build:
                return True, resolved
            return False, (f"通るはずが落ちました（{', '.join(codes) or '不明'}）"
                           f" / 解決された版 {resolved}")

        if ok_build:
            return False, (f"{expect} で落ちるはずが、通ってしまいました"
                           f" / 解決された版 {resolved}")
        if expect not in codes:
            return False, (f"期待 {expect} / 実際 {', '.join(codes) or '不明'}"
                           f" / 解決された版 {resolved}")
        return True, resolved


def main() -> int:
    if shutil.which("cargo") is None:
        print("cargo が見つかりません。", file=sys.stderr)
        return 1

    only = [a.lower() for a in sys.argv[1:] if not a.startswith("-")]
    claims = [c for c in CLAIMS if not only or any(o in c["name"].lower() for o in only)]
    if not claims:
        print("該当する項目がありません。", file=sys.stderr)
        return 1

    print(f"{len(claims)} 件のクレート API の主張を、実物で確かめます\n")
    resolved_versions: dict[str, str] = {}

    for claim in claims:
        ok, detail = run_claim(claim)
        mark = "✓" if ok else "✗"
        expect = claim["expect"]
        print(f"  {mark} {claim['name']:30} 期待 {expect:6} {claim['note'][:44]}")
        if ok:
            resolved_versions[claim["crate"]] = detail
        else:
            failures.append(f"{claim['name']}: {detail}")

    if resolved_versions:
        print("\n実際に解決された版:")
        for crate, version in sorted(resolved_versions.items()):
            print(f"  {crate} = {version}")

    if failures:
        print(f"\n本文の主張と実物が食い違っています（{len(failures)} 件）:", file=sys.stderr)
        for f in failures:
            print(f"  ✗ {f}", file=sys.stderr)
        print("\n付録の早見表を、実物に合わせて直してください。", file=sys.stderr)
        return 1

    print(f"\n{len(claims)} 件すべて、本文の記述どおりでした。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
