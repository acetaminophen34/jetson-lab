# CUDA10.2向けGPUビルド

## 概要・背景

GPU版は、CPUのホストコードに加えCUDAのdevice codeをコンパイルし、CUDA runtime・cuBLASなどをリンクします。新しいllama.cppの要求を古いCUDA10.2へ合わせるため、ソースcommitと互換patchをセットにします。

**ユーザー申告**ではGPU起動時に電源容量不足で落ちました。安定したGPU推論は未検証で、AC電源対策を済ませるまではCPU経路を基本にします。この文書のビルド・起動は今回実行していません。

## 環境と構成を選ぶ

[共通変数](../../getting-started.md)、GCC/G++8.4.0、CMake3.28.6、nvcc10.2.300を前提にします。二つの構成を別々の作業先へ置きます。

| プロファイル | 目的 | ソース/patch |
|---|---|---|
| qwen3-gpu | Qwen3対応branchを基準にする | d3bd7193… + llama-qwen3-gpu.patch |
| b5050-gpu | 古い互換修正を原状態で保全・再現する | 23106f94… + llama5050gpu.patch |

完全commitと変更内容は [patch解説](patches.md)。b5050をQwen3対応済みとは扱いません。新しいCPU用commitへb5050の置換ファイルをコピーしてはいけません。

## 固定ソースとpatchを復元

```bash
bash "$LAB_ROOT/scripts/restore-llama.sh" qwen3-gpu "$BACKUP" "$LAB_WORK"
export GPU_SOURCE="$LAB_WORK/llama-qwen3-gpu"
export GPU_BUILD="$GPU_SOURCE/build-gpu"
git -C "$GPU_SOURCE" rev-parse HEAD
git -C "$GPU_SOURCE" diff --stat
```

成功条件は固定HEADと6ファイルの変更。補助スクリプトは新規clone先だけへ適用し、既存ツリーを触りません。失敗時はプロファイル、bundleの有無、既存先、適用先HEADを確認します。

## BF16代替ヘッダの配置

元の実使用先は`/usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h`です。repoルートの保存版と同じ144bytesで、依存ファイルにも同じinclude先が残っています。`.hpp`は調べたCUDA include先にはありませんでした。

初期化後、同ファイルが無い場合だけ配置します。既存ファイルがある時は上書きせずhashを比べます。

```bash
export BF16_TARGET=/usr/local/cuda-10.2/targets/aarch64-linux/include/cuda_bf16.h
if test ! -e "$BF16_TARGET"; then
  sudo install -m 0644 "$LAB_ROOT/patches/compat-headers/cuda_bf16.h" "$BF16_TARGET"
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
bash "$LAB_ROOT/scripts/restore-llama.sh" b5050-gpu "$BACKUP" "$LAB_WORK"
export GPU_SOURCE="$LAB_WORK/llama-b5050-gpu"
export GPU_BUILD="$GPU_SOURCE/build-gpu"
```

この後は上のヘッダ確認とconfigure/buildを使いますが、原patchの条件式によりcache53でも生成コードは50/61になり得ます。これは保存された原状態です。53へ直す場合は別の改善patchとしてレビューし、生成コマンドを確認してください。原patchへ無言で修正を混ぜません。

## 失敗時・動作確認の範囲

nvccの引数、G++の選択、C++14、BF16 include、cuBLASの配置を順に確認します。詳しくは [CUDA](../../environment/cuda.md) と [トラブルシューティング](../../troubleshooting.md)。

保存時点では旧GPU/Qwen3のbenchとCUDA共有ライブラリは存在しますが、GPUのCLI/serverは調べた配置にありませんでした。生成物の存在から過去の全ビルド成功や現在ソースとの対応を断定しません。GPU起動・性能・安定性の確認は、電源対策後の独立した未検証工程です。

## 参照資料

- [出典S2・S3・S8](../../../reference/sources.md)、[保存生成物](../../../reference/details/binary-inventory.md)
- [patch解説](patches.md)、[ハードウェア](../../hardware.md)
