# llama.cppの導入・ビルド

llama.cppは、GGUF形式のモデルを使って文章を生成するプログラムです。[共通開発ツール](../setup/packages.md) のGCC/G++8.4.0とCMake3.28.6を準備してから進めます。

NanoでCPUを使う場合はこのページ、TX2でGPUを使う場合は [CUDAビルド](gpu.md) へ進みます。

| 構成 | ソースcommit | 作業先 | 手順 |
|---|---|---|---|
| Nano CPU | 62df1815bc053066761f4eac58e288f23778e164 | ~/jetson-work/llama-cpu | 以下 |
| Nano CUDA | d3bd7193ba66c15963fd1c59448f22019a8caf6e | ~/jetson-work/llama-qwen3-gpu | [CUDAビルド](gpu.md) |
| TX2 CUDA | d3bd7193ba66c15963fd1c59448f22019a8caf6e | ~/jetson-work/llama-tx2 | [CUDAビルド](gpu.md) |

## CPU版

### 1. ソース取得とpatch適用

[llama.cpp](https://github.com/ggml-org/llama.cpp) を取得し、使用したバージョンへ切り替えます。続けて [修正パッチ](patches/llama.patch) を適用し、古いARM環境とGCC8でビルドできるようにします。詳しい変更点は [パッチの説明](patches/README.md) にあります。

```bash
mkdir -p ~/jetson-work
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-cpu
cd llama-cpu
git checkout 62df1815bc053066761f4eac58e288f23778e164
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama.patch
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

## モデルを用意する

文章生成に使うQwen3-0.6BのGGUFファイルをダウンロードします。[Unslothの配布ページ](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) のQ4_K_M版です（Apache-2.0）。TX2ではこの配布元のモデルを使用しました。

```bash
mkdir -p ~/jetson-work/models
cd ~/jetson-work/models
wget -O Qwen3-0.6B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf
```

配布内容を固定して取得したい場合は、上のURLを [バージョン固定のURL](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/50968a4468ef4233ed78cd7c3de230dd1d61a56b/Qwen3-0.6B-Q4_K_M.gguf) に置き換えます。

ダウンロードが終わったら [モデルの実行・設定・ベンチマーク](usage.md) へ進みます。

### Nanoで以前使ったモデルを使う場合

以前のモデルは `~/robi-llm/models/` に保存していました。入手元は不明のため、同じファイルが必要な場合は手元に残したものをコピーします。次は、そのファイルをDownloadsへ置いた場合の例です。上のダウンロードとどちらか一方を行ってください。

```bash
mkdir -p ~/jetson-work/models
cp ~/Downloads/Qwen3-0.6B-Q4_K_M.gguf ~/jetson-work/models/
```

NanoとTX2の測定には別の配布ファイルを使用しています。測定結果は [使い方](usage.md#6-ベンチマーク) にまとめています。
