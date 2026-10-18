# CPU版をビルドし、Qwen3を確認する

## 概要・背景

この経路はCUDAを使わず、既存のQwen3 GGUFをCPUで動かします。CMakeによるconfigureはビルドコマンドを生成する段階、buildはコンパイル/リンクを実施する段階です。configureが成功しただけでは実行ファイルは完成していません。

**既存CPUバイナリの推論は実機確認済み**です。以下の新規復元・ビルドは静的に組み立てた手順で、クリーンビルド自体は未検証です。[再構築の入口](../../getting-started.md)と[ビルドツール](../../environment/build-tools.md)を先に済ませ、共通変数を同じbashセッションで設定します。

## ソースと原patchを復元する

補助スクリプトはローカルbundleから新規作業先へcloneし、固定commitへ移動して原patchを適用します。ダウンロードや既存ツリーのresetは行いません。

```bash
bash "$LAB_ROOT/scripts/restore-llama.sh" cpu "$BACKUP" "$LAB_WORK"
export CPU_SOURCE="$LAB_WORK/llama-cpu"
export CPU_BUILD="$CPU_SOURCE/build-cpu"
git -C "$CPU_SOURCE" rev-parse HEAD
git -C "$CPU_SOURCE" diff --stat
```

成功条件はHEADが`62df1815bc053066761f4eac58e288f23778e164`で、原patchの5ファイル変更が入ることです。失敗時はbundleの配置、プロファイル、既存作業先、二重適用を確認します。ソース変更の意味は [patch解説](patches.md) に分けています。

## configureとbuild

```bash
set -o pipefail
"$LAB_CMAKE" -S "$CPU_SOURCE" -B "$CPU_BUILD" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/usr/bin/gcc-8 \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGGML_CUDA=OFF -DGGML_NATIVE=OFF -DGGML_BLAS=OFF -DGGML_OPENMP=ON \
  -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_TOOLS=ON \
  -DLLAMA_OPENSSL=ON -DOPENSSL_NO_ASM=ON \
  -DLLAMA_BUILD_MTMD=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF \
  2>&1 | tee "$RUNLOG/cpu-configure.log"
configure_rc=${PIPESTATUS[0]}
test "$configure_rc" -eq 0 || exit "$configure_rc"
"$LAB_CMAKE" --build "$CPU_BUILD" --target llama-cli llama-bench --parallel 1 \
  2>&1 | tee "$RUNLOG/cpu-build.log"
build_rc=${PIPESTATUS[0]}
test "$build_rc" -eq 0 || exit "$build_rc"
file "$CPU_BUILD/bin/llama-cli"
readelf -d "$CPU_BUILD/bin/llama-cli"
sha256sum "$CPU_BUILD/bin/llama-cli"
```

`PIPESTATUS[0]`はteeではなくCMakeの終了値を取ります。`--parallel 1`は今回の手順としての抑制で、過去に使ったジョブ数は不明です。CUDAをOFF、NativeをOFFにして、CPU向けの既存設定に合わせます。

成功はconfigure/buildとも終了0、CLI/benchと依存共有ライブラリの生成で判定します。推論成功は次段階です。失敗したら最初のエラーと使用コンパイラを確認し、[保存link定義](../../../reference/details/current-build-links.md)と比較します。

## 元設定との違いと未確定のリンク処置

原cacheでは`LLAMA_USE_PREBUILT_UI=ON`でした。上の手順は外部UI資産を取りに行かないようOFFにしています。`BUILD_UI=OFF`でもUIのライブラリtargetは存在し、資産無しの生成経路になります。CLIのテキスト推論を目的にした構成であり、元のWeb UIや生成バイナリとのバイト一致を保証しません。

`LLAMA_BUILD_MTMD=OFF`でもtoolsがmtmdを追加し、server-contextがリンクすることは固定ソースで静的確認済みです。またOpenSSL1.1.1をcacheで検出しても、通常OpenSSL>=3を要求するこのソースのHTTPS supportは有効とは限りません。保存compile_commandsにもsupport定義はありません。

benchの原link.txt末尾には`-Wl,--whole-archive -lstdc++fs -Wl,--no-whole-archive`が残ります。その追加経緯はsource patch/cacheから確定できません。filesystemの未解決参照が出た場合は原linkと生成linkを比較し、新しい作業先で必要なリンク処置を検証してください。原因未確認のまま全targetへ強制適用する手順にはしていません。これがクリーンビルドの残る検証点です。

## モデルの配置と識別

対象は`Qwen3-0.6B-Q4_K_M.gguf`です。配布元URL・revision・ライセンスが不明なので、同名の最新モデルを自動取得するコマンドは書けません。既存ファイルを初期化前に別途保全し、hashで同一性を確認します。

```bash
export SAVED_MODEL=/absolute/private/path/Qwen3-0.6B-Q4_K_M.gguf
export MODEL="$LAB_WORK/models/Qwen3-0.6B-Q4_K_M.gguf"
mkdir -p "$LAB_WORK/models"
test ! -e "$MODEL" || exit 1
cp "$SAVED_MODEL" "$MODEL"
printf '%s  %s\n' 7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d "$MODEL" | sha256sum -c -
wc -c < "$MODEL"
```

成功条件は484220000bytesとhash一致。失敗時は取り違え・欠落・転送不全を確認します。モデル本体をGitへ追加しません。

## 軽量CPU推論

補助スクリプトは、実機で確認した引数と同じ軽量設定を使います。2スレッド、ctx512、生成上限32、短いプロンプト、GPUなしです。モデルhashを先に確認し、空きRAMが1GiB未満なら実施せず、120秒上限を設けます。

```bash
python3 -B "$LAB_ROOT/scripts/cpu-smoke.py" \
  --exe "$CPU_BUILD/bin/llama-cli" --model "$MODEL" \
  --out "$RUNLOG/cpu-smoke"
```

出力先は新規ディレクトリに限り、終了値・stdout/stderr・RAMサンプルを保存します。LLAMA_ARG_*/MTMD_*環境変数は子プロセスから除き、LD_LIBRARY_PATHを選択CLIのbinへ向けます。元ファイルを変更しません。

**実機で得た値**：既存CLIは`CPU test OK.`を出力し終了0、生成3.8tokens/sでした。詳細なRAM/速度/バイナリhashは [検証結果](../../../reference/validation-results.md)。この新規buildで同じ動作を確認するのは未実施です。

失敗時はresult.jsonの実際の終了値、stderr、hash、共有ライブラリ、メモリを確認します。`no usable GPU found`の警告だけではCPU推論失敗と判定せず、終了値と応答を見ます。GPUへ切り替えて再試行する必要はありません。

## 参照資料

- [出典S2〜S4](../../../reference/sources.md)、[patch解説](patches.md)
- [版一覧](../../../reference/environment-versions.md)、[トラブルシューティング](../../troubleshooting.md)
