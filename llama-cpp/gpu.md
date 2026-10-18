# CUDA10.2向けGPUビルド

## 概要・背景

GPU版は、CPUのホストコードに加えCUDAのdevice codeをコンパイルし、CUDA runtime・cuBLASなどをリンクします。新しいllama.cppの要求を古いCUDA10.2へ合わせるため、ソースcommitと互換patchをセットにします。

**ユーザー申告**ではGPU起動時に電源容量不足で落ちました。安定したGPU推論は未検証で、AC電源対策を済ませるまではCPU経路を基本にします。

## 環境と構成を選ぶ

[共通変数](../setup/nano.md)、GCC/G++8.4.0、CMake3.28.6、nvcc10.2.300を前提にします。二つの構成を別々の作業先へ置きます。

| プロファイル | 目的 | ソース/patch |
|---|---|---|
| qwen3-gpu | Qwen3対応branchを基準にする | d3bd7193… + llama-qwen3-gpu.patch |
| b5050-gpu | 古い互換修正を原状態で保全・再現する | 23106f94… + llama5050gpu.patch |

完全commitと変更内容は [patch解説](patches/README.md)。b5050をQwen3対応済みとは扱いません。新しいCPU用commitへb5050の置換ファイルをコピーしてはいけません。

## 固定ソースとpatchを復元

```bash
bash "$LAB_ROOT/llama-cpp/tools/restore-llama.sh" qwen3-gpu "$BACKUP" "$LAB_WORK"
export GPU_SOURCE="$LAB_WORK/llama-qwen3-gpu"
export GPU_BUILD="$GPU_SOURCE/build-gpu"
git -C "$GPU_SOURCE" rev-parse HEAD
git -C "$GPU_SOURCE" diff --stat
```

成功条件は固定HEADと6ファイルの変更。補助スクリプトは新規clone先だけへ適用し、既存ツリーを触りません。失敗時はプロファイル、bundleの有無、既存先、適用先HEADを確認します。

## BF16代替ヘッダの配置

元の実使用先は`/usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h`です。同梱のヘッダと同じ144bytesで、依存ファイルにも同じinclude先が残っています。`.hpp`は調べたCUDA include先にはありませんでした。

初期化後、同ファイルが無い場合だけ配置します。既存ファイルがある時は上書きせずhashを比べます。

```bash
export BF16_TARGET=/usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
if test ! -e "$BF16_TARGET"; then
  sudo install -m 0644 "$LAB_ROOT/llama-cpp/patches/compat-headers/cuda_bf16.h" "$BF16_TARGET"
fi
printf '%s  %s\n' bfe47be09ef61153bea805be2c8121e47cd400686ac40a396e373679ebbe8490 "$BF16_TARGET" | sha256sum -c -
```

このヘッダはFP16による代替で、正しいBF16演算を保証しません。`.hpp`をtoolkitへ推測で追加せず、BF16モデルの動作確認済みとも扱いません。

## configureとbuild（将来手順・未検証）

```bash
set -o pipefail
"$LAB_CMAKE" -S "$GPU_SOURCE" -B "$GPU_BUILD" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=/usr/bin/gcc-8 \
  -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 -DCMAKE_CUDA_HOST_COMPILER=/usr/bin/g++-8 \
  -DCMAKE_CUDA_COMPILER=/usr/local/cuda-10.2/bin/nvcc \
  -DCMAKE_CUDA_ARCHITECTURES=53 -DCMAKE_CUDA_STANDARD=14 -DCMAKE_CUDA_STANDARD_REQUIRED=ON \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DGGML_CUDA=ON -DGGML_NATIVE=OFF \
  -DGGML_CPU_ARM_ARCH=armv8-a -DGGML_BLAS=OFF -DGGML_OPENMP=ON -DLLAMA_CURL=OFF \
  2>&1 | tee "$RUNLOG/gpu-configure.log"
configure_rc=${PIPESTATUS[0]}
test "$configure_rc" -eq 0 || exit "$configure_rc"
"$LAB_CMAKE" --build "$GPU_BUILD" --target llama-bench --parallel 1 \
  2>&1 | tee "$RUNLOG/gpu-build.log"
build_rc=${PIPESTATUS[0]}
test "$build_rc" -eq 0 || exit "$build_rc"
file "$GPU_BUILD/bin/llama-bench" "$GPU_BUILD/bin/libggml-cuda.so"
readelf -d "$GPU_BUILD/bin/libggml-cuda.so"
```

成功条件はconfigure/buildとも0、ELF生成、CUDA依存が意図どおりであることです。CLI/serverも必要なら追加targetとしてビルドしますが、その成功は確認していません。ここでbenchの**実行**はしません。

## b5050原状態を選ぶ場合

```bash
bash "$LAB_ROOT/llama-cpp/tools/restore-llama.sh" b5050-gpu "$BACKUP" "$LAB_WORK"
export GPU_SOURCE="$LAB_WORK/llama-b5050-gpu"
export GPU_BUILD="$GPU_SOURCE/build-gpu"
```

この後は上のヘッダ確認とconfigure/buildを使いますが、原patchの条件式によりcache53でも生成コードは50/61になり得ます。これは保存された原状態です。53へ直す場合は別の改善patchとしてレビューし、生成コマンドを確認してください。原patchへ無言で修正を混ぜません。

## 失敗時・動作確認の範囲

nvccの引数、G++の選択、C++14、BF16 include、cuBLASの配置を順に確認します。アーキテクチャとリンクの確認方法は以下に示します。

保存時点では旧GPU/Qwen3のbenchとCUDA共有ライブラリは存在しますが、GPUのCLI/serverは調べた配置にありませんでした。生成物の存在から過去の全ビルド成功や現在ソースとの対応を断定しません。GPU起動・性能・安定性の確認は、電源対策後の独立した未検証工程です。

## アーキテクチャ指定を確認する

`CMAKE_CUDA_ARCHITECTURES`は生成するGPUコードの対象です。CMakeCacheは設定の保存値、compile_commandsは生成コマンドの記録で、両方を見る必要があります。

| 構成 | cache値 | 生成コマンド | 判定 |
|---|---|---|---|
| 新しいllama.cpp/build-gpu | 53 | compute_53 / sm_53 | 設定は一致、新規ビルド成功は未確認 |
| llama5050gpu.cpp/build | 53 | compute_50 / sm_50 と compute_61 / sm_61 | 原patchの条件式による上書きが説明になる |
| llama-qwen3-gpu/build | 53 | compute_53 / sm_53 | 設定は一致、既存bench/.soは存在 |

b5050の`if(NOT DEFINED ${CMAKE_CUDA_ARCHITECTURES})`は、変数名ではなく展開した値を存在確認へ渡します。そのためcache53でも通常変数を50/61へ変更する解析が成り立ちます。原patchはこの状態のまま保存しており、修正案を混ぜていません。

## 再構築時の確認方法

```sh
/usr/local/cuda-10.2/bin/nvcc --version
readlink -f /usr/local/cuda
# GPU configureを実施した後の確認例。ここではビルドを開始しない。
rg 'CMAKE_CUDA_(ARCHITECTURES|STANDARD|HOST_COMPILER)' "$GPU_BUILD/CMakeCache.txt"
rg -- '--generate-code' "$GPU_BUILD/compile_commands.json"
```

`rg`が未導入なら`grep -E`へ読み替えられます。成功条件は、選んだ構成の記録と生成対象が説明できることです。失敗時はPATH、host compiler、別構成のpatch、CMake条件式を確認します。

## CUDAのコンパイルとリンクを理解する

nvccはdevice codeとCPU側host codeを扱います。GPU経路はG++8.4をhost compilerとして指定し、CUDA側はC++14です。CPU側C++17とは別の指定です。nvcc表示10.2.300とtoolkit package10.2.460-1も別の版識別子です。

保存ELFで直接依存を確認したのはlibcudart.so.10.2、libcublas.so.10、libcuda.so.1です。libggml-cuda.soからこれらを使い、CLI/benchはlibllama、libggml、libggml-cpu、libggml-baseやpthreadもリンクします。cuDNN/TensorRTの導入をllama.cppの利用と読み替えません。

CUDAのC++17要求、builtin_assume、constexpr device配列、BF16で止まる場合は [修正解説](patches/README.md) とconfigureのC++14・host compiler・include先を確認します。ライブラリ未検出は/usr/local/cuda-10.2/targets/aarch64-linux/libを確認します。リンク用stubs/libcudaは実行時ドライバの代わりにはなりません。
