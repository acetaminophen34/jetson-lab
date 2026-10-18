# CUDA10.2でGPU版をビルドする

GCC/G++8.4.0・CMake3.28.6は [CPU記事](README.md) と同じです。以下は既存cacheとpatchから整理した未検証手順で、GPUビルド・起動の成功を確認したものではありません。

## 1. CUDAの版を確認する

JetPack4.6.1のCUDA10.2を使います。nvcc10.2.300、toolkit package10.2.460-1が使用環境の版です。

```bash
/usr/local/cuda-10.2/bin/nvcc --version
dpkg-query -W cuda-toolkit-10-2
```

toolkitが無い場合は [JetPack4.6.1公式の導入手順](https://developer.nvidia.com/embedded/jetpack-sdk-461) で対応パッケージを入れます。GPUのhost側にはG++8.4、device側にはCUDA C++14を指定します。

## 2. Qwen3対応ソースを取得する

CPUツリーと混ぜず、別ディレクトリへcloneします。[Qwen3対応コミット](https://github.com/ggml-org/llama.cpp/commit/d3bd7193ba66c15963fd1c59448f22019a8caf6e) へ切り替えます。

```bash
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-qwen3-gpu
cd llama-qwen3-gpu
git checkout d3bd7193ba66c15963fd1c59448f22019a8caf6e
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama-qwen3-gpu.patch
```

patchはNEON互換処置、device配列のconstexpr除去、builtin_assume除外、CUDA11以降のBF16 cuBLAS分岐の無効化を行います。[変更内容](patches/README.md) に詳細があります。

## 3. BF16代替ヘッダを置く

使用環境ではCUDA include先に [cuda_bf16.h](patches/compat-headers/cuda_bf16.h) を追加していました。初期化後に同名ファイルが無い場合だけ、次のように配置します（既存ファイルは上書きしません）。

```bash
if [ ! -e /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h ]; then
  sudo install -m 0644 ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h \
    /usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
fi
```

この.hはnv_bfloat16をhalf（FP16）へtypedefする代替で、正しいBF16演算を実装したものではありません。.hppは同梱していますが、実際のtoolkit include配置は未確認なので推測で追加しません。

## 4. CMakeでビルドする

Nano向けはarch53です。CUDA C++14とhost compilerを明示し、メモリ負荷を抑えるため並列数1でbenchをビルドします。

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

`build-gpu/bin/llama-bench` と `libggml-cuda.so` の生成を確認します。旧環境にはこれらがありましたが、GPU CLI/serverは確認できていません。このビルドが成功してもGPU推論成功とは別です。

## 5. ビルドで詰まったとき

C++17要求・builtin_assume・constexpr・BF16で止まる場合は、適用コミットとpatch、CUDA C++14、BF16 include先を確認します。実際のエラーログが無い変更は、コードから読み取れる互換処置という位置づけです。

```bash
grep -E 'CMAKE_CUDA_(ARCHITECTURES|STANDARD|HOST_COMPILER)' build-gpu/CMakeCache.txt
grep -- '--generate-code' build-gpu/compile_commands.json
readelf -d build-gpu/bin/libggml-cuda.so
```

Qwen3構成の保存コマンドはcompute_53/sm_53でした。CUDA側の主な直接依存はlibcudart.so.10.2、libcublas.so.10、libcuda.so.1です。stubs/libcudaはリンク用で、実行時ドライバの代わりにはなりません。

## 旧b5050版を参照する場合

旧版も別ツリーで作ります。[b5050の固定コミット](https://github.com/ggml-org/llama.cpp/commit/23106f94ea2bc3da929afb7330655fd5515d08dc) と専用patchを組み合わせ、上のGPU用CMakeコマンドを使います。Qwen3対応済みの版とは扱いません。

```bash
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-b5050-gpu
cd llama-b5050-gpu
git checkout 23106f94ea2bc3da929afb7330655fd5515d08dc
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama5050gpu.patch
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.h .
cp ~/Projects/jetson-lab/llama-cpp/patches/compat-headers/cuda_bf16.hpp .
```

このpatchの `if(NOT DEFINED ${CMAKE_CUDA_ARCHITECTURES})` には、値を変数名として調べる問題があります。cacheが53でも生成対象は50/61となっていたため、compile_commandsの実際の生成指定を確認します。元patchは変更せず残しています。

GPU起動時に装置が落ちる電源問題はビルドエラーとは別です。電源対策後の安定動作が未確認なので、このメモではGPU起動・負荷試験までを成功済みの手順にしていません。
