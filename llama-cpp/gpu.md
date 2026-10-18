# CUDA10.2のビルド

[共通開発ツール](../setup/packages.md) のGCC/G++8.4.0、CMake3.28.6を使います。

| 設定 | Nano | TX2 |
|---|---|---|
| 作業ディレクトリ名 | llama-qwen3-gpu | llama-tx2 |
| CMAKE_CUDA_ARCHITECTURES | 53 | 62 |
| 並列数 | 1 | 2 |
| 使用するプログラム | llama-bench | llama-bench、llama-cli |

以下のコマンドはTX2の値です。Nanoではディレクトリ名・arch・並列数を表の値へ置き換えます。

Nanoでは電源容量不足でGPU起動時に落ちたため、ACアダプタへ切り替えるまではCPUで運用していました。

## 1. ソース取得とpatch適用

記事・patchが手元にない場合だけ取得します。

```bash
mkdir -p ~/Projects ~/jetson-work
cd ~/Projects
git clone https://github.com/acetaminophen34/jetson-lab.git
```

[llama.cpp](https://github.com/ggml-org/llama.cpp) のQwen3対応commitへ [CUDA10.2用patch](patches/llama-qwen3-gpu.patch) を適用します。

```bash
mkdir -p ~/jetson-work
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-tx2
cd llama-tx2
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
```

## 2. BF16代替ヘッダ

[ヘッダ](patches/compat-headers/cuda_bf16.h) を作業先へ置き、CMakeの `-I` で参照します。nv_bfloat16をhalfへ置換する処置で、BF16演算そのものの実装ではありません。

```bash
mkdir -p ~/jetson-work/cuda-compat
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h \
  ~/jetson-work/cuda-compat/
```

Nanoで従来使ったtoolkit側の配置方法です。作業先のヘッダを `-I` で使う場合、この操作は不要です。

```bash
if [ ! -e /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h ]; then
  sudo install -m 0644 ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h \
    /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
fi
```

## 3. ビルド

CUDA C++14とhost compilerのG++8を指定します。[patchの変更理由](patches/README.md) も参照してください。

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

Nanoで生成コマンドを記録する場合は `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` も指定します。benchをビルドし、TX2では続けてCLIもビルドします。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-bench --parallel 2

~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-cli --parallel 2
```

生成先は `build-gpu/bin/` です。CUDA側の依存はlibcudart.so.10.2、libcublas.so.10、libcuda.so.1です。

## 旧b5050版

Qwen3用ではない旧構成です。別ツリーに専用patchを適用します。ビルドはこのツリー内で、上のCMake設定・ビルドコマンドを実行します（先頭の `cd` は省略）。

```bash
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-b5050-gpu
cd llama-b5050-gpu
git checkout 23106f94ea2bc3da929afb7330655fd5515d08dc
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama5050gpu.patch
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h .
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.hpp .
```

`if(NOT DEFINED ${CMAKE_CUDA_ARCHITECTURES})` の問題により、cacheが53でも生成対象が50/61になります。`-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` を付け、生成指定を見ます。

```bash
grep -- '--generate-code' build-gpu/compile_commands.json
```

次へ：[モデル取得](README.md#モデルを用意する) → [実行・ベンチマーク](usage.md)。
