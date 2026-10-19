# CUDA10.2のビルド

[作業場所の設定](../README.md#作業場所を用意する) を済ませ、同じターミナルで進めます。

[共通開発ツール](../setup/packages.md) のGCC/G++8.4.0、CMake3.28.6を使います。

| 設定 | Nano | TX2 |
|---|---|---|
| 作業ディレクトリ名 | llama-qwen3-gpu | llama-tx2 |
| CMAKE_CUDA_ARCHITECTURES | 53 | 62 |
| 並列数 | 1 | 2 |
| 使用するプログラム | llama-bench | llama-bench、llama-cli |

以下はTX2の手順です。Nano向けにビルドする場合は、フォルダ名を `llama-qwen3-gpu`、`CMAKE_CUDA_ARCHITECTURES` を `53`、`--parallel` を `1` に変更します。

Nanoでは電源容量不足でGPU起動時に落ちたため、ACアダプタへ切り替えるまではCPUで運用していました。

## 1. ソース取得とpatch適用

[llama.cpp](https://github.com/ggml-org/llama.cpp) を取得し、Qwen3を使えるバージョンへ切り替えます。[修正パッチ](patches/llama-qwen3-gpu.patch) は、CUDA10.2にない機能を使う箇所を修正します。

```bash
mkdir -p "$JETSON_LAB/work"
cd "$JETSON_LAB/work"
git clone https://github.com/ggml-org/llama.cpp.git llama-tx2
cd llama-tx2
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e
git apply --check "$JETSON_LAB/llama-cpp/patches/llama-qwen3-gpu.patch"
git apply "$JETSON_LAB/llama-cpp/patches/llama-qwen3-gpu.patch"
```

## 2. BF16代替ヘッダ

CUDA10.2には、ソースが必要とする `cuda_bf16.h` がありません。リポジトリ内の [代替ヘッダ](patches/compat-headers/cuda_bf16.h) をコピーし、次のビルド設定から読み込ませます。BF16用の型を既存のhalf型で代用するもので、BF16演算への対応ではありません。

```bash
mkdir -p "$JETSON_LAB/work/cuda-compat"
cp "$JETSON_LAB/llama-cpp/patches/compat-headers/cuda_bf16.h" \
  "$JETSON_LAB/work/cuda-compat/"
```

<details>
<summary>以前のNanoと同じ場所へヘッダを置く場合</summary>

以前はCUDAのインストール先へ直接置いていました。上のコピーを行った場合は、この操作は不要です。

```bash
if [ ! -e /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h ]; then
  sudo install -m 0644 "$JETSON_LAB/llama-cpp/patches/compat-headers/cuda_bf16.h" \
    /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
fi
```

</details>

## 3. ビルド

CUDA10.2、G++8、GPUの種類を指定してビルド設定を作ります。`CMAKE_CUDA_FLAGS` は、先ほどコピーしたヘッダの場所です。

```bash
cd "$JETSON_LAB/work/llama-tx2"

~/opt/cmake-3.28.6-linux-aarch64/bin/cmake -S . -B build-gpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-8 \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-10.2/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=62 \
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

性能測定用の `llama-bench` を作り、TX2では続けて文章生成用の `llama-cli` を作ります。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-bench --parallel 2

~/opt/cmake-3.28.6-linux-aarch64/bin/cmake \
  --build build-gpu --target llama-cli --parallel 2
```

完了すると `build-gpu/bin/` に実行ファイルができます。実行にはCUDA10.2のライブラリ（libcudart.so.10.2、libcublas.so.10、libcuda.so.1）が必要です。

## 旧b5050版

Qwen3用ではない旧構成です。別ツリーに専用patchを適用します。ビルドはこのツリー内で、上のCMake設定・ビルドコマンドを実行します（先頭の `cd` は省略）。

```bash
cd "$JETSON_LAB/work"
git clone https://github.com/ggml-org/llama.cpp.git llama-b5050-gpu
cd llama-b5050-gpu
git checkout 23106f94ea2bc3da929afb7330655fd5515d08dc
git apply "$JETSON_LAB/llama-cpp/patches/llama5050gpu.patch"
cp "$JETSON_LAB/llama-cpp/patches/compat-headers/cuda_bf16.h" .
cp "$JETSON_LAB/llama-cpp/patches/compat-headers/cuda_bf16.hpp" .
```

`if(NOT DEFINED ${CMAKE_CUDA_ARCHITECTURES})` の問題により、設定で53を指定しても、実際には別のGPU向け（50/61）にビルドされる問題があります。CMakeの設定時に `-DCMAKE_EXPORT_COMPILE_COMMANDS=ON` を追加すると、次のコマンドで実際のGPU指定を読めます。

```bash
grep -- '--generate-code' build-gpu/compile_commands.json
```

次へ：[モデル取得](README.md#モデルを用意する) → [実行・ベンチマーク](usage.md)。
