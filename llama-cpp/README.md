# llama.cppの導入・ビルド

[共通開発ツール](../setup/packages.md) のGCC/G++8.4.0、CMake3.28.6を使います。

| 構成 | ソースcommit | 作業先 | 手順 |
|---|---|---|---|
| Nano CPU | 62df1815bc053066761f4eac58e288f23778e164 | ~/jetson-work/llama-cpu | 以下 |
| Nano CUDA | d3bd7193ba66c15963fd1c59448f22019a8caf6e | ~/jetson-work/llama-qwen3-gpu | [CUDAビルド](gpu.md) |
| TX2 CUDA | d3bd7193ba66c15963fd1c59448f22019a8caf6e | ~/jetson-work/llama-tx2 | [CUDAビルド](gpu.md) |

## CPU版

### 1. ソース取得とpatch適用

[llama.cpp](https://github.com/ggml-org/llama.cpp) を取得し、固定commitに [CPU用patch](patches/llama.patch) を適用します。[修正理由](patches/README.md) はNEON互換、stdc++fsリンク、include・型指定の補完です。

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

CUDAを無効化してGCC8を指定します。このcommitのCLIにはSERVER=ONが必要です。

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

実行ファイルと.soは `build-cpu/bin/` に生成されます。PREBUILT_UI=OFFは外部UI資産を取得しないための指定です。

## モデルを用意する

いずれか一方を `~/jetson-work/models/` に配置します。Nanoの元GGUFとTX2で使ったUnsloth版は別ファイルです。

### Unsloth版

TX2では [Unsloth Qwen3-0.6B-Q4_K_M](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) を使用しました（Apache-2.0）。測定時の配布revisionは記録していません。

```bash
mkdir -p ~/jetson-work/models
cd ~/jetson-work/models
wget -O Qwen3-0.6B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf
```

固定版を使う場合の [revision指定URL](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/50968a4468ef4233ed78cd7c3de230dd1d61a56b/Qwen3-0.6B-Q4_K_M.gguf) とSHA256です。上のwgetのURLを置き換えます。

```bash
echo 'ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a  Qwen3-0.6B-Q4_K_M.gguf' | sha256sum -c -
```

### Nanoで使った元GGUF

公開URLは不明です。484220000bytesの元ファイルを使います。運用時の保存先は `~/robi-llm/models/` でした。

```bash
mkdir -p ~/jetson-work/models
cp ~/Downloads/Qwen3-0.6B-Q4_K_M.gguf ~/jetson-work/models/
cd ~/jetson-work/models
echo '7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d  Qwen3-0.6B-Q4_K_M.gguf' | sha256sum -c -
```

次へ：[モデルの実行・設定・ベンチマーク](usage.md)。
