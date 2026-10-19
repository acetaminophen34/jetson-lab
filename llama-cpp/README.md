# llama.cppを構築してQwen3を動かす

Nano/TX2のJetPack環境とGit・wgetを用意したら、cloneした `jetson-lab` の直下で開始します。

```bash
export JETSON_LAB="$PWD"
mkdir -p "$JETSON_LAB/work"
```

CPUだけ使う場合は手順2、CUDAを使う場合は手順3を選び、その後は手順4〜6へ進みます。CUDA版も `-ngl 0` でCPU実行できます。

| ビルド | ソースcommit | パッチ |
|---|---|---|
| CPU | 62df1815bc053066761f4eac58e288f23778e164 | llama.patch |
| CUDA | d3bd7193ba66c15963fd1c59448f22019a8caf6e | llama-qwen3-gpu.patch |

## 1. GCCとCMakeを用意する

GCC/G++8.4.0、CMake3.28.6を使います。CUDA版ではJetPackのCUDA10.2も必要です。導入済みならソース取得へ進みます。

```bash
sudo apt update
sudo apt install --no-install-recommends --no-upgrade gcc-8 g++-8 libssl-dev
gcc-8 --version
g++-8 --version
mkdir -p ~/opt ~/Downloads
cd ~/Downloads
wget https://github.com/Kitware/CMake/releases/download/v3.28.6/cmake-3.28.6-linux-aarch64.tar.gz
tar -xzf cmake-3.28.6-linux-aarch64.tar.gz -C ~/opt
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

[CMake配布元](https://github.com/Kitware/CMake/releases/tag/v3.28.6)。Nanoで使用したaptパッケージはgcc-8/g++-8が `8.4.0-1ubuntu1~18.04`、libssl-devが `1.1.1-1ubuntu2.1~18.04.23` でした。

## 2. CPU版をビルドする

### 1. ソース取得とpatch適用

[llama.cpp](https://github.com/ggml-org/llama.cpp) を取得し、使用したバージョンへ切り替えます。続けて [修正パッチ](patches/llama.patch) を適用し、古いARM環境とGCC8でビルドできるようにします。詳しい変更点は [パッチの説明](patches/README.md) にあります。

```bash
mkdir -p "$JETSON_LAB/work"
cd "$JETSON_LAB/work"
git clone https://github.com/ggml-org/llama.cpp.git llama-cpu
cd llama-cpu
git checkout 62df1815bc053066761f4eac58e288f23778e164
git apply --check "$JETSON_LAB/llama-cpp/patches/llama.patch"
git apply "$JETSON_LAB/llama-cpp/patches/llama.patch"
```

### 2. ビルド

GPUを使わず、GCC8でビルドします。このバージョンでは文章生成コマンドを作るために `LLAMA_BUILD_SERVER=ON` も必要です。

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

完了すると `build-cpu/bin/` に `llama-cli` と `llama-bench` ができます。`LLAMA_USE_PREBUILT_UI=OFF` は、不要なWeb画面のデータをダウンロードしないための指定です。

CPU版を使う場合は、実行先を設定します。

```bash
LLAMA_BIN="$JETSON_LAB/work/llama-cpu/build-cpu/bin"
GPU_LAYERS=0
```

## 3. CUDA版をビルドする

GPUの種類とビルドの並列数だけを選びます。ソースとパッチは共通です。

```bash
# Nano
CUDA_ARCH=53
BUILD_JOBS=1
```

```bash
# TX2（Nanoの場合は上の設定を使う）
CUDA_ARCH=62
BUILD_JOBS=2
```

NanoではGPU起動時の電源不足による停止があったため、GPUを使う場合は適合するAC電源を用意します。

### ソース取得とパッチ適用

[llama.cpp](https://github.com/ggml-org/llama.cpp) を取得し、Qwen3を使えるバージョンへ切り替えます。[修正パッチ](patches/llama-qwen3-gpu.patch) は、CUDA10.2にない機能を使う箇所を修正します。

```bash
mkdir -p "$JETSON_LAB/work"
cd "$JETSON_LAB/work"
git clone https://github.com/ggml-org/llama.cpp.git llama-cuda
cd llama-cuda
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e
git apply --check "$JETSON_LAB/llama-cpp/patches/llama-qwen3-gpu.patch"
git apply "$JETSON_LAB/llama-cpp/patches/llama-qwen3-gpu.patch"
```

### BF16ヘッダを配置する

CUDA10.2には、ソースが必要とする `cuda_bf16.h` がありません。リポジトリ内の [代替ヘッダ](patches/compat-headers/cuda_bf16.h) をコピーし、次のビルド設定から読み込ませます。BF16用の型を既存のhalf型で代用するもので、BF16演算への対応ではありません。

```bash
mkdir -p "$JETSON_LAB/work/cuda-compat"
cp "$JETSON_LAB/llama-cpp/patches/compat-headers/cuda_bf16.h" \
  "$JETSON_LAB/work/cuda-compat/"
```

### ビルド

CUDA10.2、G++8、GPUの種類を指定してビルド設定を作ります。`CMAKE_CUDA_FLAGS` は、先ほどコピーしたヘッダの場所です。

```bash
cd "$JETSON_LAB/work/llama-cuda"

~/opt/cmake-3.28.6-linux-aarch64/bin/cmake -S . -B build-gpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-8 \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-10.2/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES="$CUDA_ARCH" \
  -DCMAKE_CUDA_STANDARD=14 \
  -DCMAKE_CUDA_STANDARD_REQUIRED=ON \
  -DCMAKE_CUDA_FLAGS="-I\"$JETSON_LAB/work/cuda-compat\"" \
  -DGGML_CUDA=ON \
  -DGGML_NATIVE=OFF \
  -DGGML_CPU_ARM_ARCH=armv8-a \
  -DGGML_BLAS=OFF \
  -DGGML_OPENMP=ON \
  -DLLAMA_CURL=OFF
```

文章生成用の `llama-cli` と性能測定用の `llama-bench` を作ります。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-cli llama-bench --parallel "$BUILD_JOBS"
LLAMA_BIN="$JETSON_LAB/work/llama-cuda/build-gpu/bin"
GPU_LAYERS=99
```

実行にはCUDA10.2のlibcudart.so.10.2、libcublas.so.10、libcuda.so.1を使います。

## 4. モデルを用意する

文章生成に使うQwen3-0.6BのGGUFファイルをダウンロードします。[Unslothの配布ページ](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) のQ4_K_M版です（Apache-2.0）。TX2ではこの配布元のモデルを使用しました。

```bash
mkdir -p "$JETSON_LAB/work/models"
cd "$JETSON_LAB/work/models"
wget -O Qwen3-0.6B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf
```

配布内容を固定して取得したい場合は、上のURLを [バージョン固定のURL](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/50968a4468ef4233ed78cd7c3de230dd1d61a56b/Qwen3-0.6B-Q4_K_M.gguf) に置き換えます。

ダウンロードが終わったら、この下の実行手順へ進みます。

### Nanoで以前使ったモデルを使う場合

以前のモデルは `~/robi-llm/models/` に保存していました。入手元は不明のため、同じファイルが必要な場合は手元に残したものをコピーします。次は、そのファイルをDownloadsへ置いた場合の例です。上のダウンロードとどちらか一方を行ってください。

```bash
mkdir -p "$JETSON_LAB/work/models"
cp ~/Downloads/Qwen3-0.6B-Q4_K_M.gguf "$JETSON_LAB/work/models/"
```

NanoとTX2の測定には別の配布ファイルを使用しています。測定結果はこのページの末尾にまとめています。

## 5. 文章を生成する

ビルド時に設定した `LLAMA_BIN` と `GPU_LAYERS` を使います。CPU版は0、CUDA版は99で、モデルの全レイヤーをGPUへ配置する指定です。

```bash
cd "$LLAMA_BIN"
LD_LIBRARY_PATH=. ./llama-cli \
  -m "$JETSON_LAB/work/models/Qwen3-0.6B-Q4_K_M.gguf" \
  -ngl "$GPU_LAYERS" -t 4 -c 512 -n 64 -st \
  -p "こんにちは。簡単に自己紹介してください。"
```

文章が表示されれば起動成功です。日本語対話や回答の長さを変える場合は [設定ガイド](usage.md) を使います。

## 6. ベンチマーク

```bash
cd "$LLAMA_BIN"
LD_LIBRARY_PATH=. ./llama-bench \
  -m "$JETSON_LAB/work/models/Qwen3-0.6B-Q4_K_M.gguf" \
  -ngl "$GPU_LAYERS" -t 4 -p 128 -n 32 -r 3
```

`pp128` は入力128トークンの処理速度、`tg32` は32トークンの生成速度（tokens/s）です。CPU比較は `-ngl 0 -t 1,2,4` で測ります。

### Nano CPU：以前から使用していたモデル

| スレッド | pp128 | tg32 |
|---:|---:|---:|
| 1 | 3.85 | 1.98 |
| 2 | 7.63 | 3.85 |
| 4 | 13.65 | 5.62 |

### TX2 CUDA：Unsloth版

| モデル | pp128 | tg32 |
|---|---:|---:|
| Qwen3-0.6B Q4_K_M | 77.88 ± 0.59 | 20.47 ± 0.09 |
| Qwen3-1.7B Q4_K_M | 25.25 | 9.84 |

0.6Bでは全29レイヤーをGPUへオフロードしました。

```text
Device 0: NVIDIA Tegra X2, compute capability 6.2
offloaded 29/29 layers to GPU
CUDA0 model buffer size = 372.65 MiB
```

### Nanoの短いプロンプト測定

上のベンチマークとは別に、62df1815bを使って短い質問への応答速度を測りました。CPUは2スレッド、会話を保持する枠は512トークン、回答の上限は32トークンです。

```bash
cd "$JETSON_LAB/work/llama-cpu"
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  LD_LIBRARY_PATH=./build-cpu/bin \
  ./build-cpu/bin/llama-cli -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  --device none --n-gpu-layers 0 --no-kv-offload \
  --threads 2 --threads-batch 2 --ctx-size 512 \
  --batch-size 32 --ubatch-size 32 --n-predict 32 --single-turn \
  --reasoning off --no-warmup --perf --seed 1 --temp 0 --simple-io \
  -p 'Reply with exactly: CPU test OK.' < /dev/null
```

| 応答 / 終了コード | Prompt / Generation | 時間 / 最大RSS |
|---|---|---|
| CPU test OK. / 0 | 7.4 / 3.8 tokens/s | 7.326秒 / 約583MiB |

`no usable GPU found` 警告は出ましたが、CPU推論は成功しました。

互換修正の詳細は [patches/README.md](patches/README.md)、旧b5050版だけを使う場合は [gpu.md](gpu.md) を参照してください。


## 既存TX2環境でモデルを常駐させる

[llama-server追加ビルド・HTTP確認](server.md)では、実機の`/home/a62ss/jetson-work/llama-tx2`にあるCUDA環境を維持してサーバーを追加します。このREADMEの`$JETSON_LAB/work/llama-cuda`は新規構築例で、実機の配置とは異なります。既存CLIの使い方は変更しません。
