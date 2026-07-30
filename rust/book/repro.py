"""実機でしか出せない画面の「再現」。

この教材のターミナル画面は、原則として実際にコマンドを走らせて捕獲したもの
（`<!--term:-->`、実測バッジ）です。

しかし Windows のインストーラのように、この教材をビルドしている環境
（Linux コンテナ）では絶対に出せない画面があります。それを本文から
省いてしまうと、いちばん最初につまずく環境構築の章が文字だけになってしまう。

そこで、そういう画面だけを `<!--termx:-->` で入れます。こちらには必ず
**再現バッジと出典**が付き、実測と見た目で区別できるようになっています。

出典の方針:
  ・rustup の表示は、rustup 自身のソース（表示文字列の定義そのもの）から取る
  ・推測で文言を作らない。確認できないものは載せない

各項目:
    title  … ウィンドウのタイトルバーに出す文字
    source … 何に基づく再現か（キャプションに必ず出る）
    text   … 画面の中身。ANSI エスケープを入れると色が付く
"""

# 太字にするための ANSI。rustup は見出しを太字で描く。
B = "\x1b[1m"
R = "\x1b[0m"
GREEN = "\x1b[1m\x1b[92m"
CYAN = "\x1b[1m\x1b[96m"

REPRODUCTIONS = {
    # ------------------------------------------------------------------
    "rustup-init": dict(
        title="rustup-init.exe",
        source="rustup 1.29.0 のソース src/cli/self_update.rs にある"
               "インストーラの表示文字列（Windows 版）",
        text=f"""{B}Welcome to Rust!{R}

This will download and install the official compiler for the Rust
programming language, and its package manager, Cargo.

Rustup metadata and toolchains will be installed into the Rustup
home directory, located at:

    C:\\Users\\you\\.rustup

This can be modified with the RUSTUP_HOME environment variable.

The Cargo home directory is located at:

    C:\\Users\\you\\.cargo

This can be modified with the CARGO_HOME environment variable.

The `cargo`, `rustc`, `rustup` and other commands will be added to
Cargo's bin directory, located at:

    C:\\Users\\you\\.cargo\\bin

This path will then be added to your `PATH` environment variable by
modifying the `PATH` registry key at `HKEY_CURRENT_USER\\Environment`.

You can uninstall at any time with `rustup self uninstall` and
these changes will be reverted.

{B}Current installation options:{R}


   default host triple: x86_64-pc-windows-msvc
     default toolchain: stable (default)
               profile: default
  modify PATH variable: yes

1) Proceed with standard installation (default - just press enter)
2) Customize installation
3) Cancel installation
>""",
    ),

    # ------------------------------------------------------------------
    "rustup-init-msvc": dict(
        title="rustup-init.exe — C++ ビルドツールの確認",
        source="rustup 1.29.0 のソース src/cli/self_update/windows.rs にある"
               "MSVC_AUTO_INSTALL_MESSAGE と choose_vs_install の表示文字列",
        text=f"""{B}Rust Visual C++ prerequisites{R}

Rust requires a linker and Windows API libraries but they don't seem to be available.

These components can be acquired through a Visual Studio installer.


1) Quick install via the Visual Studio Community installer
   (free for individuals, academic uses, and open source).

2) Manually install the prerequisites
   (for enterprise and advanced users).

3) Don't install the prerequisites
   (if you're targeting the GNU ABI).

>""",
    ),

    # ------------------------------------------------------------------
    "rustup-init-done": dict(
        title="rustup-init.exe — 完了",
        source="rustup 1.29.0 のソース src/cli/self_update.rs の"
               "post_install_msg_win",
        text=f"""{GREEN}  stable-x86_64-pc-windows-msvc installed{R} - rustc 1.97.1 (8bab26f4f 2026-07-14)

{B}Rust is installed now. Great!{R}


To get started you may need to restart your current shell.
This would reload its `PATH` environment variable to include
Cargo's bin directory (C:\\Users\\you\\.cargo\\bin).

Press the Enter key to continue.""",
    ),

    # ------------------------------------------------------------------
    # これは実際に走らせられるが、Linux で撮ると host triple が
    # x86_64-unknown-linux-gnu になってしまい、Windows の読者には嘘になる。
    # だから実測ではなく再現として置く。
    "rustup-show": dict(
        title="Windows PowerShell",
        source="rustup show の実際の出力（この教材のビルド環境で取得したもの）を、"
               "Windows の既定ターゲット x86_64-pc-windows-msvc に読み替えたもの",
        text=f"""{CYAN}PS C:\\rust>{R} rustup show
{GREEN}Default host: {R}x86_64-pc-windows-msvc
{GREEN}rustup home:  {R}C:\\Users\\you\\.rustup

{GREEN}installed toolchains{R}
{GREEN}--------------------{R}
stable-x86_64-pc-windows-msvc{B}\x1b[94m (active, default){R}

{GREEN}active toolchain{R}
{GREEN}----------------{R}
name: stable-x86_64-pc-windows-msvc
active because: it's the default toolchain
installed targets:
  x86_64-pc-windows-msvc""",
    ),
}
