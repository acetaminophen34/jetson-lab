# CUDAビルドの補足

通常のCPU/CUDAビルド・モデル取得・推論は [README](README.md) にまとめています。このページは以前のソースを使う場合だけ参照します。

## 旧b5050版

Qwen3用ではない旧構成です。別ツリーに専用patchを適用します。ビルドはこのツリー内で、[READMEのCUDA設定・ビルドコマンド](README.md#3-cuda版をビルドする)を実行します（先頭の `cd` は省略）。

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
