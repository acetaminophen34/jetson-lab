# Nanoでllama.cppとQwen3を動かす

## 1. llama.cppとは

[llama.cpp](https://github.com/ggml-org/llama.cpp) はC/C++でLLMを実行する推論エンジンです。モデルを格納したGGUFを読み、ggmlのCPU/CUDAバックエンドで演算します。

ここではCPU版を基本にします。2026年10月14日の作業ではコミット62df1815bとQwen3-0.6B-Q4_K_M.ggufを使い、4スレッドでCPU実行していました。当時の履歴はユーザーが過去のChatGPT会話から復元した情報で、後日の軽量推論測定とは分けて記載します。取得・新規ビルド手順は既存設定から整理したもので、クリーンビルドは未検証です。

## CPU版

### 2. パッケージとコンパイラを用意する

[GCC/G++8.4.0、CMake3.28.6の導入](../setup/packages.md) を先に済ませます。使用するコンパイラとCMakeを確認します。

```bash
gcc-8 --version
g++-8 --version
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

### 3. GitHubからソースを取得する

公式リポジトリを新しい作業先へcloneします。以下のディレクトリ名が既にある場合は、新しい名前を使ってください。

```bash
mkdir -p ~/jetson-work
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-cpu
cd llama-cpu
```

### 4. 使用したコミットへ切り替える

使用したCPUソースを固定します。[このコミット](https://github.com/ggml-org/llama.cpp/commit/62df1815bc053066761f4eac58e288f23778e164) の公開と取得元を確認しています。

```bash
git checkout 62df1815bc053066761f4eac58e288f23778e164
```

### 5. Nano用のパッチを適用する

[llama.patch](patches/llama.patch) は古いARM NEONヘッダへの代替、GCC8のfilesystemリンク、iomanipのinclude、テンプレート型の明示を行います。変更ファイルと理由は [patch解説](patches/README.md) にまとめています。

```bash
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama.patch
```

### 6. CPU版をビルドする

CUDAを無効にし、GCC8を明示します。このコミットではCLIがserver-contextを使うためSERVER=ONが必要ですが、サーバーを起動する意味ではありません。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake -S . -B build-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-8 -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 \
  -DGGML_CUDA=OFF -DGGML_NATIVE=OFF -DGGML_BLAS=OFF -DGGML_OPENMP=ON \
  -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_TOOLS=ON \
  -DLLAMA_OPENSSL=ON -DOPENSSL_NO_ASM=ON \
  -DLLAMA_BUILD_MTMD=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --build build-cpu \
  --target llama-cli llama-bench --parallel 1
```

`build-cpu/bin/llama-cli` と `llama-bench`、共有ライブラリが生成されればビルド段階は完了です。元cacheはPREBUILT_UI=ONでしたが、この手順では外部UI資産を取らないようOFFにしています。ジョブ数1も今回の手順で選んだ値です。

MTMD=OFFでもこのソースのtools/server依存からmtmdは追加されます。またOpenSSL1.1.1を検出しても、HTTPS対応が要求するOpenSSL>=3を満たすとは限りません。ローカルGGUFでの推論にはHTTPS機能を使いません。

### 7. Qwen3モデルを入手・配置する

Qwenの [公式GGUF](https://huggingface.co/Qwen/Qwen3-0.6B-GGUF) はありますが、当時使ったQ4_K_Mと同じファイルの公開URLは特定できていません。モデルの保存先は `~/robi-llm/models/` でした。新規取得には [Unsloth配布版](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) の固定revisionを使えますが、**元モデルとは別の量子化ファイルで、このNanoでの動作・速度は未検証**です（配布表示Apache-2.0）。

```bash
mkdir -p ~/jetson-work/models
cd ~/jetson-work/models
wget -O Qwen3-0.6B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/50968a4468ef4233ed78cd7c3de230dd1d61a56b/Qwen3-0.6B-Q4_K_M.gguf
echo 'ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a  Qwen3-0.6B-Q4_K_M.gguf' | sha256sum -c -
```

元の推論結果を再現したい場合だけ、手元の元GGUFを使います。別の作業先を選び、既存モデルを上書きしないでください。

```bash
mkdir -p ~/jetson-work/original-model
cp ~/Downloads/Qwen3-0.6B-Q4_K_M.gguf ~/jetson-work/original-model/
cd ~/jetson-work/original-model
echo '7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d  Qwen3-0.6B-Q4_K_M.gguf' | sha256sum -c -
```

元ファイルは484220000bytesです。Unsloth版は396705472bytesで、上の2種類のSHA256を取り違えないでください。

### 8. CPUで推論する

#### 2026年10月14日：4スレッドでの運用とベンチマーク

当時は `~/robi-llm/models/Qwen3-0.6B-Q4_K_M.gguf` を使い、CPU実行オプションは `-ngl 0 -t 4` でした。次は判明した配置と引数を並べた起動例で、当時の完全なコマンド文字列・プロンプトまでは復元できていません。

```bash
cd ~/robi-llm/llama.cpp
./build/bin/llama-cli -m ~/robi-llm/models/Qwen3-0.6B-Q4_K_M.gguf -ngl 0 -t 4
```

ベンチマークの条件はprompt128トークン、生成32トークン、3回反復（`-p 128 -n 32 -r 3`）です。以下は1・2・4スレッドの測定条件をまとめた再実行例であり、今回実行したものではありません。

```bash
./build/bin/llama-bench -m ~/robi-llm/models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 1,2,4 -p 128 -n 32 -r 3
```

| スレッド | Prompt t/s | Generation t/s |
|---:|---:|---:|
| 1 | 3.85 | 1.98 |
| 2 | 7.63 | 3.85 |
| 4 | 13.65 | 5.62 |

これは過去会話から復元した当時の結果で、現在の環境では再測定していません。この記事の新規ビルドを使う場合は、作業先を `~/jetson-work/llama-cpu`、実行ファイルを `./build-cpu/bin/llama-cli` または `llama-bench` に読み替えます。

#### 後日の別測定：2スレッドの軽量CPU推論

2スレッド、ctx512、生成上限32で短く実行します。以下の引数は既存CPUバイナリで成功したときのものですが、今回の新規ビルド・新規配布モデルでの実行は未検証です。

```bash
cd ~/jetson-work/llama-cpu
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  LD_LIBRARY_PATH=./build-cpu/bin \
  ./build-cpu/bin/llama-cli -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  --device none --n-gpu-layers 0 --no-kv-offload \
  --threads 2 --threads-batch 2 --ctx-size 512 \
  --batch-size 32 --ubatch-size 32 --n-predict 32 --single-turn \
  --reasoning off --no-warmup --perf --seed 1 --temp 0 --simple-io \
  -p 'Reply with exactly: CPU test OK.' < /dev/null
```

元GGUFを使う場合は `-m ../original-model/Qwen3-0.6B-Q4_K_M.gguf` に変更します。LLAMA_ARG_*やMTMD_*を独自に設定している場合は、その影響を除いて実行してください。

| 後日（2026年10月18日）の既存CPU版・元モデルの実測 | 結果 |
|---|---|
| 表示build / 応答 / 終了コード | b11632-62df1815b / CPU test OK. / 0 |
| prompt / 生成速度 | 7.4 / **3.8 tokens/s** |
| 経過時間 / 最大RSS | 7.326秒 / 597096KiB（約583MiB） |

この測定は10月14日のベンチマークとプロンプト・測定方法が異なります。2スレッドの3.8 tokens/sは別測定として扱い、当時の4スレッド5.62 t/sと直接比較しません。

## GPU版

### 9. CUDA10.2向けの追加手順

GPU版は別コミット・別ディレクトリで作ります。[GPUビルド](gpu.md) に、ソース取得、BF16代替ヘッダ、CUDA用patch、CMakeコマンドをまとめています。

ユーザー申告ではGPU起動時に電源容量不足で落ち、ACアダプタへ切り替えるまではCPUのみで運用していました。GPU安定動作は未確認です。

## 10. エラーと対処

元のエラーログが無いものは、patchの内容から分かる対処として記載します。

| 症状・変更箇所 | 対処 |
|---|---|
| 古いARMヘッダでNEON x4ロードが使えない | patchで単独ロード4回へ置換 |
| filesystemの未解決参照 | CLI/benchへstdc++fsをリンク |
| iomanip・テンプレート型 | include追加とfield_numの型明示 |
| CPU実行時のno usable GPU found | 実測時にも出た警告。終了0と応答を確認すればCPU推論は成功 |
| 共有ライブラリを読み込めない | bin内の.soをCLIと一組で扱い、上のLD_LIBRARY_PATHを指定 |

元benchのlink.txtには `-Wl,--whole-archive -lstdc++fs -Wl,--no-whole-archive` もありました。追加経緯は不明で、patchだけで同じリンクが生成されるかは未検証です。benchでfilesystem参照が残る場合は生成されたlink.txtとリンク順を確認します。
