# 既存TX2 CUDA環境にllama-serverを追加する

build5092（commit `d3bd7193ba66c15963fd1c59448f22019a8caf6e`）のCUDA 10.2パッチ適用済み環境を使います。Robiなどのアプリケーション固有の対話実装は、このリポジトリには配置しません。

## スクリプトで追加する

jetson-labをcloneし、構築済みのCUDA環境にサーバーを追加できます。JetPack・CUDA・GCC・llama.cppの初回構築は[環境構築手順](README.md)を先に済ませてください。このスクリプトはパッケージやモデルのダウンロード、sudo操作、既存ソースのリセットを行いません。

```bash
git clone https://github.com/acetaminophen34/jetson-lab.git
cd jetson-lab
# 既にclone済みなら、そのフォルダへ移動して以下を実行
bash llama-cpp/tools/setup-server.sh --check
bash llama-cpp/tools/setup-server.sh
```

標準ではclone先の`work/llama-cuda/build-gpu`を参照します。別の場所に既存環境がある場合は、例えば次のように指定します。個々の環境の配置に合わせてください。

```bash
export LLAMA_SRC="$HOME/jetson-work/llama-tx2"
export LLAMA_BUILD="$LLAMA_SRC/build-gpu"
bash llama-cpp/tools/setup-server.sh --check
bash llama-cpp/tools/setup-server.sh
```

実行場所に関係なくスクリプト自身からリポジトリを特定します。CMakeは既存キャッシュの`CMAKE_COMMAND`を使います。移動などで無効な場合は`CMAKE=/path/to/cmake`で指定できます。並列数はメモリ消費を抑えるため1で、`BUILD_JOBS=2`などで変更できます。

| オプション | 動作 |
|---|---|
| なし | 検査後、未導入なら既存キャッシュでllama-serverだけをビルド |
| `--check` | 検査だけ。設定変更・ビルドを行わない |
| `--rebuild` | 導入済みでもサーバーを再ビルド |
| `--help` | オプションと環境変数の説明 |

commit、CUDA有効化、arch62、GCC8、CUDA10.2、BF16ヘッダ参照、適用済みパッチが期待と違う場合は、変更前に停止します。既存CMake設定を維持して`LLAMA_BUILD_SERVER=ON`だけを指定します。ビルド失敗時は非ゼロ終了し、ソースやビルド成果物を削除しません。途中のビルド成果物は残ることがあります。モデルは使わず、最後に`llama-server --version`で実行ファイルを確認します。HTTP推論の確認は後述の「起動とHTTP確認」で行います。

開発用のモックテストは次のコマンドで実行できます。実コンパイラ・GPU・ネットワークを使いません。

```bash
python3 llama-cpp/tools/test_setup_server.py -v
```

実機での追加ビルドは未検証です。以下に同じ処理の手動手順も残しています。

## 導入の流れ

CUDA版llama-cliが動く既存環境に、同じソース・設定で`llama-server`実行ファイルを追加します。

1. 以下の実機パスを設定し、commit・CUDA・既存パッチを確認する。
2. `build-gpu/bin/llama-server`が未作成なら、既存CMakeキャッシュを使ってサーバーのターゲットだけをビルドする。
3. サーバーをlocalhostで起動し、`/health`と`/completion`を確認する。
4. 確認用サーバーを停止し、利用するアプリケーションを起動する。

すでに同じbuild5092のサーバーが導入済みなら、追加ビルドを繰り返す必要はありません。下のパス設定後、次のコマンドで実行ファイルを確認できます。

```bash
test -x "$LLAMA_BUILD/bin/llama-server"
LD_LIBRARY_PATH="$LLAMA_BUILD/bin${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  "$LLAMA_BUILD/bin/llama-server" --version
```

初めてllama.cpp自体を構築する場合は、先に[CPU/CUDA環境構築](README.md)を使ってください。ここではJetPack、CUDA、コンパイラ、モデルの導入済み環境を扱います。パッケージの追加インストールやモデルの再取得は不要です。

## 参照先を設定する

cloneしたjetson-labのルートで、環境に合わせて参照先を設定します。以下は標準手順の`work/`に構築した場合です。別の作業ディレクトリで構築済みの場合は、`LLAMA_SRC`と`LLAMA_MODEL`をその配置に変更してください。既存環境を移動したりモデルを取り直す必要はありません。

## 既存ビルドの検査と追加ビルド

実機のターミナルで実行します。`CMAKE`は導入済みの3.28.6を指定します。既存環境の配置が異なる場合は`LLAMA_SRC`を変更してください。

```bash
export JETSON_LAB="$PWD"   # cloneしたjetson-labのルートで実行
export LLAMA_SRC="$JETSON_LAB/work/llama-cuda"
export LLAMA_BUILD="$LLAMA_SRC/build-gpu"
export CMAKE="$HOME/opt/cmake-3.28.6-linux-aarch64/bin/cmake"
```

まず設定を読むだけで現状を確認します。

```bash
git -C "$LLAMA_SRC" rev-parse HEAD
git -C "$LLAMA_SRC" status --short
cat "$LLAMA_BUILD/CMakeCache.txt" | grep -E '^(CMAKE_(HOME_DIRECTORY|CXX_COMPILER|CUDA_COMPILER|CUDA_HOST_COMPILER|CUDA_ARCHITECTURES|CUDA_FLAGS)|GGML_CUDA|LLAMA_BUILD_SERVER|LLAMA_CURL):'
LD_LIBRARY_PATH="$LLAMA_BUILD/bin${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  "$LLAMA_BUILD/bin/llama-cli" --version
```

期待値は固定commit、G++8、CUDA10.2、TX2のarch 62、`GGML_CUDA=ON`です。`CMAKE_CUDA_FLAGS`に既存BF16互換ヘッダのincludeパスがあり、そのファイルが存在することも確認します。READMEの新規構築例にあるヘッダ配置先と異なっていても、実機の有効な既存パスを維持します。

以下は既存パッチとビルドディレクトリを検査し、同じCMakeキャッシュを使って追加ビルドする手順です。失敗したら理由を調べてから進めます。ソースのcheckout/reset、パッチの再適用、ビルドディレクトリの削除は行いません。

```bash
(
  set -eu
  test -x "$CMAKE"
  test -f "$LLAMA_BUILD/CMakeCache.txt"
  test "$(git -C "$LLAMA_SRC" rev-parse HEAD)" = d3bd7193ba66c15963fd1c59448f22019a8caf6e
  grep -q '^GGML_CUDA:BOOL=ON$' "$LLAMA_BUILD/CMakeCache.txt"
  grep -Fqx "CMAKE_HOME_DIRECTORY:INTERNAL=$LLAMA_SRC" "$LLAMA_BUILD/CMakeCache.txt"
  git -C "$LLAMA_SRC" apply --reverse --check \
    "$JETSON_LAB/llama-cpp/patches/llama-qwen3-gpu.patch"
  # 他の既存設定を維持し、serverのビルド対象だけを有効化する。
  "$CMAKE" -S "$LLAMA_SRC" -B "$LLAMA_BUILD" -DLLAMA_BUILD_SERVER=ON
  "$CMAKE" --build "$LLAMA_BUILD" --target llama-server --parallel 1
)
```

`git apply --reverse --check`はパッチが適用済みか確認するだけで、ソースを変更しません。追加の実機修正でチェックが失敗する場合もあります。その場合は既存差分を確認し、上書きして「修復」しないでください。コンパイラ・CUDA・BF16ヘッダの設定を変えて再構成する操作も不要です。リンク／コンパイルエラーが出た場合のサーバー向け追加修正の要否は実機で確認が必要です。

この版は`examples/server/`のCMakeターゲットを使い、HTTPライブラリと画面用アセットをソースに同梱しています。新しいCPU版向けの`LLAMA_BUILD_UI`等を持ち込まないでください。SSLは既定でOFF、ローカルHTTP利用に追加pipパッケージは不要です。ビルド中のメモリを抑えるため並列数1にしています。完了後もllama-cliと既存モデルはそのまま使えます。

## 起動とHTTP確認

```bash
export LLAMA_MODEL="$JETSON_LAB/work/models/Qwen3-1.7B-Q4_K_M.gguf"
mkdir -p "$JETSON_LAB/logs"
LD_LIBRARY_PATH="$LLAMA_BUILD/bin${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" \
  "$LLAMA_BUILD/bin/llama-server" \
  -m "$LLAMA_MODEL" -ngl 99 -t 4 -c 4096 -b 128 -ub 128 \
  -np 1 --no-context-shift --host 127.0.0.1 --port 8080 \
  > "$JETSON_LAB/logs/llama-server.log" 2>&1
```

このターミナルはサーバー起動中のままにします。終了はCtrl+Cです。別ターミナルで確認します。読み込み中は`/health`が503、準備完了後は200と`{"status":"ok"}`になります。

```bash
curl --noproxy '*' -fsS http://127.0.0.1:8080/health
curl --noproxy '*' -fsS http://127.0.0.1:8080/completion \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"<|im_start|>system\n日本語で短く答えて。/no_think<|im_end|>\n<|im_start|>user\nこんにちは<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n\n","n_predict":96,"temperature":0.6,"id_slot":0,"cache_prompt":true,"stream":false,"json_schema":{"type":"object","properties":{"speech":{"type":"string"}},"required":["speech"],"additionalProperties":false}}'
```

同じPOSTを繰り返し、`content`内のJSON、`stop_type`、`truncated`、`timings.prompt_n`とログのprompt eval時間を確認します。JSONは`content`に文字列として格納されます。`stop_type=limit`や`truncated=true`は正常完了として扱わず、入力や生成上限を調整します。全29層のGPU配置はサーバーログで確認します。

上のcurl例は外部公開しない検証専用です。Robi側は別途子サーバーを起動するため、この検証用サーバーをCtrl+Cで止めてからRobiを起動してください。同時にモデルを2つロードすると8GB共有メモリを圧迫します。

## KVキャッシュとメモリ

`/completion`はこの版のネイティブAPIです。`cache_prompt:true`はスロットに残るトークン列と新しいプロンプトの共通接頭辞を比較し、再計算を省きます。`-np 1`と`id_slot:0`で同じスロットを使い続けます。モデルはプロセス存続中メモリに常駐します。履歴を保持するのは呼び出し側の責務で、毎回完全なプロンプトを送る必要があります。

これはllama-cliの`--prompt-cache`によるセッションファイルとは別の仕組みです。サーバーはprompt-cache.binを読み書きせず、`/slots/...save`やrestoreも使いません。再起動するとメモリ内キャッシュは失われ、初回はプロンプト全体を評価します。壊れた旧セッションファイルを削除しなくても、この方式は影響を受けません。

共通接頭辞以降は変更時に再計算されます。会話履歴の先頭を落とした場合も、固定の性格・例文・候補部分までは再利用できます。再利用を要求しても毎回同じ速度になる保証はありません。

このcommitのソースでは`tokens_cached`に完了時の`slot.n_past`を返すため、その値だけで「今回ヒットしたトークン数」と判断しないでください。実際に処理した入力数`timings.prompt_n`、総入力数`tokens_evaluated`、処理時間とサーバーログを合わせて比較します。

TX2はCPU/GPUで8GBを共有します。モデル、KV、計算バッファ、OSの空きメモリが必要です。スロット数1、バッチ128を初期値にし、まず`free -h`と`tegrastats`で監視します。コンテキスト長を増やすとKVメモリも増えます。上の汎用確認例は4096、Robiは保守的な入力予算の都合で8192が初期値です。どちらも実機で使用量を測定して調整してください。OOM時にモデルや環境を作り直す必要はなく、ほかの推論プロセスを止め、コンテキスト・バッチ・GPU配置を見直します。

## バージョンと既存CLI

この手順のAPI・CMake仕様は[固定版server README](https://github.com/ggml-org/llama.cpp/blob/d3bd7193ba66c15963fd1c59448f22019a8caf6e/examples/server/README.md)と[server.cpp](https://github.com/ggml-org/llama.cpp/blob/d3bd7193ba66c15963fd1c59448f22019a8caf6e/examples/server/server.cpp)に基づきます。最新のllama.cppや、CPU用62df1815b、旧b5050と混ぜないでください。新しい版に更新する場合はCUDA10.2パッチとAPIの互換性を別途確認します。

[README](README.md)と[usage.md](usage.md)のllama-cli手順は引き続き利用できます。既存CLIを消したり、置き換えたりしません。
