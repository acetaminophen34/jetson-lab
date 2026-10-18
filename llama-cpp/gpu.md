# CUDA10.2のGPUビルド

| 機種 | CUDA arch | 手順 |
|---|---:|---|
| Nano | 53 | [Nano](#nano) |
| TX2（Pascal） | 62 | [TX2](#tx2) |

## Nano

[GCC8.4・CMake3.28.6](README.md#1-gcc84とcmake3286を入れる) とCUDA10.2を使います。新規ビルド・GPU安定動作は未検証です。

### 1. ソース取得とpatch適用

CPU版とは別ツリーで [Qwen3対応コミット](https://github.com/ggml-org/llama.cpp/commit/d3bd7193ba66c15963fd1c59448f22019a8caf6e) を取得します。

```bash
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-qwen3-gpu
cd llama-qwen3-gpu
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
```

### 2. BF16代替ヘッダ

CUDA10.2のinclude先へ [cuda_bf16.h](patches/compat-headers/cuda_bf16.h) を追加します。既存ファイルは上書きしません。

```bash
if [ ! -e /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h ]; then
  sudo install -m 0644 ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h \
    /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
fi
```

これはnv_bfloat16をhalfへ置き換える互換処置で、BF16演算を正しく実装したものではありません。同梱の.hppはtoolkitへ追加する手順には含めません。

### 3. ビルド

Nano向けarch53、CUDA C++14、host compilerにG++8を指定します。[patchの変更理由](patches/README.md) も参照してください。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake -S . -B build-gpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-8 -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-10.2/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=53 -DCMAKE_CUDA_STANDARD=14 \
  -DCMAKE_CUDA_STANDARD_REQUIRED=ON -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DGGML_CUDA=ON -DGGML_NATIVE=OFF -DGGML_CPU_ARM_ARCH=armv8-a \
  -DGGML_BLAS=OFF -DGGML_OPENMP=ON -DLLAMA_CURL=OFF
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --build build-gpu \
  --target llama-bench --parallel 1
```

生成物は `build-gpu/bin/llama-bench` と `libggml-cuda.so` です。CUDA側の依存はlibcudart.so.10.2、libcublas.so.10、libcuda.so.1です。

### 旧b5050版

[旧コミット](https://github.com/ggml-org/llama.cpp/commit/23106f94ea2bc3da929afb7330655fd5515d08dc) と専用patchで別ツリーを作り、上のCMakeコマンドを使います。Qwen3用ではありません。

```bash
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-b5050-gpu
cd llama-b5050-gpu
git checkout 23106f94ea2bc3da929afb7330655fd5515d08dc
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama5050gpu.patch
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h .
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.hpp .
```

このpatchの `if(NOT DEFINED ${CMAKE_CUDA_ARCHITECTURES})` により、cacheが53でも生成対象が50/61になります。生成指定は次で確認します。

```bash
grep -- '--generate-code' build-gpu/compile_commands.json
```

## TX2

[TX2の環境構築](../setup/tx2.md) を済ませてから進めます。以下の構成でllama-bench・llama-cliのビルド、全レイヤーGPUオフロード、文章生成とベンチマークに成功しました。

### 1. ソース取得とpatch適用

[llama.cpp](https://github.com/ggml-org/llama.cpp) の固定コミットへ [Qwen3 GPU用patch](patches/llama-qwen3-gpu.patch) を適用します。jetson-labが既にある場合は、そのcloneを省略します。

```bash
mkdir -p ~/Projects ~/jetson-work
cd ~/Projects
git clone https://github.com/acetaminophen34/jetson-lab.git

cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-tx2
cd llama-tx2
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e

git apply ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
```

### 2. BF16互換ヘッダ

[ヘッダ](patches/compat-headers/cuda_bf16.h) を作業先へ置き、CUDAのincludeパスへ追加します。TX2ではtoolkit側のヘッダを変更せずにビルドしました。

```bash
mkdir -p ~/jetson-work/cuda-compat
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h \
  ~/jetson-work/cuda-compat/
```

### 3. ビルド

TX2はarch62、CUDA C++14、GCC/G++8.4.0を指定します。

```bash
cd ~/jetson-work/llama-tx2

~/opt/cmake-3.28.6-linux-aarch64/bin/cmake -S . -B build-gpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-8 \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-10.2/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=62 \
  -DCMAKE_CUDA_STANDARD=14 \
  -DCMAKE_CUDA_STANDARD_REQUIRED=ON \
  -DCMAKE_CUDA_FLAGS="-I$HOME/jetson-work/cuda-compat" \
  -DGGML_CUDA=ON \
  -DGGML_NATIVE=OFF \
  -DGGML_CPU_ARM_ARCH=armv8-a \
  -DGGML_BLAS=OFF \
  -DGGML_OPENMP=ON \
  -DLLAMA_CURL=OFF
```

benchとCLIを並列数2でビルドします。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-bench --parallel 2

~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-cli --parallel 2
```

### 4. モデルを配置する

[Unsloth版Qwen3-0.6B-Q4_K_M](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) を使用しました（約596.05Mパラメータ、モデル容量表示約372.65MiB）。Nanoの元GGUFとは別ファイルです。

取得例です。測定時の配布revisionは不明です。

```bash
mkdir -p ~/jetson-work/models
cd ~/jetson-work/models
wget -O Qwen3-0.6B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/main/Qwen3-0.6B-Q4_K_M.gguf
```

### 5. GPU推論

全レイヤーをGPUへオフロードして起動します。

```bash
cd ~/jetson-work/llama-tx2

LD_LIBRARY_PATH=./build-gpu/bin \
  ./build-gpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -c 512 -n 64 \
  -p "こんにちは。簡単に自己紹介してください。"
```

実行時の表示です。CUDAでモデルを読み込み、文章生成が始まりました。

```text
Device 0: NVIDIA Tegra X2, compute capability 6.2
offloaded 29/29 layers to GPU
CUDA0 model buffer size = 372.65 MiB
```

### 6. GPUベンチマーク

prompt128・生成32トークン、3回反復で測定しました。

```bash
cd ~/jetson-work/llama-tx2

LD_LIBRARY_PATH=./build-gpu/bin \
  ./build-gpu/bin/llama-bench \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -p 128 -n 32 -r 3
```

| テスト | 速度 |
|---|---:|
| pp128（入力処理） | 77.88 ± 0.59 tokens/s |
| tg32（文章生成） | 20.47 ± 0.09 tokens/s |
