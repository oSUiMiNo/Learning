# Claude Code / Claude Agent SDK と Codex App Server の内部関係

| 内容 | 反映状況 |
| --- | --- |
| 初回 | [ ] |

## 1. 調べた疑問

次の2点を区別して確認した。

1. Claude Code本体は、内部でClaude Agent SDKを呼び出して実装されているのか
2. Codex CLI / TUIは、内部でCodex App Serverを使っているのか

## 2. 結論

- **Claude CodeがClaude Agent SDKを内部依存として呼ぶ構造ではない。**
  公開されているAgent SDK側が、Claude Codeのネイティブ実行ファイルを
  子プロセスとして起動し、標準入出力のストリームを介して制御する。
- **現在のCodex TUIと`codex exec`は、Codex App Serverのプロトコルを使う。**
  通常は別プロセスのサーバーへ接続するのではなく、同一プロセス内に
  App Serverを埋め込むin-process構成を使える。リモート接続経路も存在する。
- 両者は似て見えるが、境界の置き方が異なる。
  - Claude: 完成済みのClaude CodeランタイムをSDKが外側から駆動する
  - Codex: TUI、exec、外部クライアントが共通のApp Server境界を使う

## 3. Claude Agent SDKから確認できる依存方向

Python版SDKの
`src/claude_agent_sdk/_internal/transport/subprocess_cli.py`には、
`SubprocessCLITransport`が実装されている。

ソース上で確認できること:

- コメントが「Claude Code CLIを使うサブプロセストランスポート」となっている
- SDKパッケージに同梱された`claude` / `claude.exe`を先に探す
- 見つからなければPATH上などからClaude Code CLIを探す
- `--output-format stream-json --verbose`を付けてCLIを起動する
- stdoutのNDJSONを行単位で読み取る
- SDKの各オプションをClaude CodeのCLI引数や初期化要求へ変換する

したがって、Agent SDKがClaude CodeのエージェントループをPythonやTypeScriptで
再実装しているわけではない。主要な実行能力は、起動されたClaude Code
ランタイム側にあると判断できる。

概念図:

```text
SDKを使うアプリ
    ↓
Claude Agent SDK
    ↓ 子プロセス + stream-json / 制御メッセージ
Claude Codeランタイム
    ↓
モデル、組み込みツール、セッション、権限、MCPなど
```

### Agent SDKだけでClaude Code製品そのものになるわけではない

Agent SDKを使うと、Claude Codeランタイムが持つエージェント能力を
プログラムから利用できる。一方、完成したClaude Codeアプリの次のような部分は、
SDK利用側で別途用意する必要がある。

- 対話型ターミナルUI
- 入力編集、キーバインド、補完、ストリーミング表示
- 差分や権限確認の表示
- セッション一覧や履歴選択のUI
- アプリ固有の認証、ホスティング、マルチユーザー分離
- 自動更新、通知、クラッシュ時の運用

「SDKでは実現不可能」というより、SDKはエージェント実行を組み込むための境界で、
製品UIや運用部分までは自動では提供しない、という区別が適切。

## 4. Codex TUI / execから確認できるApp Server利用

Codexの公開ソースでは、TUIの`Cargo.toml`が
`codex-app-server-client`と`codex-app-server-protocol`へ依存している。

`codex-rs/tui/src/app_server_session.rs`には、TUIイベントループ用の
App Serverセッションファサードであることが明記され、次のような要求を扱う。

- thread start / resume / fork / compact / archive
- turn start / steer / interrupt
- model list
- skills list
- shell command
- review
- permission profile

`codex-rs/tui/src/lib.rs`には次の接続形態がある。

- `Embedded`: 同一プロセス内のApp Server
- `LocalDaemon`: ローカルの外部App Server
- `Remote`: リモートApp Server

通常のCLIでは`InProcessAppServerClient`を使って埋め込みApp Serverを開始できる。
`codex exec`も`InProcessAppServerClient`とApp Server Protocolの
`ThreadStart`、`TurnStart`などを使う。

概念図:

```text
Codex TUI / codex exec / IDE等
    ↓ App Server Protocol
Codex App Server
    ↓
codex-core
    ↓
モデル、ツール、サンドボックス、セッション、承認など
```

### 完全にApp Serverだけへ分離済みではない

App Serverクライアントには`legacy_core`という移行用モジュールがあり、
新しいTUI動作はApp Server Protocolを優先しつつも、起動や設定の一部には
coreへの直接依存が残っている。よって、現時点では
「主要なセッション・ターン経路はApp Serverを使うが、全コードがApp Server越し」
とまでは言えない。

## 5. 比較

| 観点 | Claude Code / Agent SDK | Codex / App Server |
| --- | --- | --- |
| 公開境界 | 高水準SDK | JSON-RPC型のプロトコル境界 |
| 実行の中心 | 非公開Claude Codeランタイム | 公開`codex-core` |
| 通常の接続 | SDKがCLI子プロセスを起動 | TUI/execがApp Serverをin-process起動 |
| 主目的 | 独自アプリからClaude Code能力を使う | 複数フロントエンドで共通バックエンドを使う |
| 外部接続 | stdin/stdoutのストリーム | in-process channel、stdio、WebSocket、Unix socket |

## 6. 未解決・今後確認すること

- Claude Codeランタイム内部で、UI層とエージェントエンジン層がどのように
  モジュール分割されているか。Claude Code本体が非公開なので公開情報だけでは限界がある
- Claude Agent SDKのTypeScript版とPython版で、制御プロトコルや同梱バイナリの
  取り扱いにどの程度差があるか
- CodexでApp Server移行が完了した範囲と、`legacy_core`が残る具体的な箇所
- OpenCodeとKimi Codeが、同様の「UIとエージェントコアの境界」を
  どのモジュールに置いているか

## 7. 一次情報

- Anthropic Claude Agent SDK Python:
  https://github.com/anthropics/claude-agent-sdk-python
- `SubprocessCLITransport`:
  https://github.com/anthropics/claude-agent-sdk-python/blob/main/src/claude_agent_sdk/_internal/transport/subprocess_cli.py
- OpenAI Codex:
  https://github.com/openai/codex
- Codex TUI App Server session:
  https://github.com/openai/codex/blob/main/codex-rs/tui/src/app_server_session.rs
- Codex TUI startup / embedded App Server:
  https://github.com/openai/codex/blob/main/codex-rs/tui/src/lib.rs
- Codex exec:
  https://github.com/openai/codex/blob/main/codex-rs/exec/src/lib.rs
- Codex App Server client:
  https://github.com/openai/codex/blob/main/codex-rs/app-server-client/src/lib.rs
