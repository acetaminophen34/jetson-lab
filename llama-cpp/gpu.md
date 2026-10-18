# CUDA10.2のGPUビルド

[GCC8.4・CMake3.28.6](README.md#1-gcc84とcmake3286を入れる) とCUDA10.2を使います。新規ビルド・GPU安定動作は未検証です。

## 1. ソース取得とpatch適用

CPU版とは別ツリーで [Qwen3対応コミット](https://github.com/ggml-org/llama.cpp/commit/d3bd7193ba66c15963fd1c59448f22019a8caf6e) を取得します。

```bash
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-qwen3-gpu
cd llama-qwen3-gpu
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
```

## 2. BF16代替ヘッダ

CUDA10.2のinclude先へ [cuda_bf16.h](patches/compat-headers/cuda_bf16.h) を追加します。既存ファイルは上書きしません。

```bash
if [ ! -e /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h ]; then
  sudo install -m 0644 ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h \
    /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
fi
```

これはnv_bfloat16をhalfへ置き換える互換処置で、BF16演算を正しく実装したものではありません。同梱の.hppはtoolkitへ追加する手順には含めません。

## 3. ビルド

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

## 旧b5050版

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
