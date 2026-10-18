# ソース修正を読む・再適用する

## 概要と前提

原patchは実機の追跡ファイル差分を保全したものです。ビルドを通す互換処置と、数値演算の正しさの保証は同じではありません。エラーログや変更理由が保存されていない場合は、コードの意味からの説明と実際の動機を区別します。

## 固定commitと適用単位

| 構成 | ベースcommit | 原patch | 変更数 |
|---|---|---|---:|
| CPU | 62df1815bc053066761f4eac58e288f23778e164 | [llama.patch](llama.patch) | 5 |
| b5050 GPU | 23106f94ea2bc3da929afb7330655fd5515d08dc | [llama5050gpu.patch](llama5050gpu.patch) | 7 |
| Qwen3 GPU | d3bd7193ba66c15963fd1c59448f22019a8caf6e | [llama-qwen3-gpu.patch](llama-qwen3-gpu.patch) | 6 |

最新branchへ適用するために加工していません。`jetson-patches`の参照commitはcba793e345442fc9f542f3418ae4b0070bd37b06で、ローカル追跡変更はありません。Qwen3のベースは既存llama bundleにも含まれています。

## CPU側の変更と意味

| ファイル | 変更 | 技術的な意味・根拠の限界 |
|---|---|---|
| ggml/src/ggml-cpu/ggml-cpu-impl.h | NEONのx4ロードを4回の単独ロードにする | 16byteずつ4回読み、元の4ベクトルを組み立てる。古いARMヘッダでのintrinsic不足を避ける解析。実エラーのGCC revisionは未保存 |
| tools/cli/CMakeLists.txt | stdc++fsをリンク | GCC8系のfilesystem実装を明示リンクする処置 |
| tools/llama-bench/CMakeLists.txt | stdc++fsをリンク | benchでも同じリンク要件を扱う |
| tools/server/server-context.cpp | iomanipをinclude | 書式操作の宣言を明示的に読み込む |
| tools/server/server-schema.cpp | field_numのテンプレート型を明示 | decltypeで元の値の型を指定。古いコンパイラの型推論への対応という解析 |

stdc++fsの指定と、原benchのlink.txt末尾にあるwhole-archive追加は別です。後者はpatchだけに現れないため、追加経緯は未確定です。[CPUビルド](../cpu.md)で残る検証点として扱っています。

## CUDA10.2側の変更

b5050はCPUのNEON代替に加え、次の6ファイルを変更します。

| ファイル | 処置 | 意味 |
|---|---|---|
| CMakeLists.txt | archを50/61に設定する条件式を追加 | 新しい対象を避ける意図の参照資料。ただし条件式に問題がありcache53との相違を生む |
| ggml/CMakeLists.txt | stdc++fsとcopy-dt-needed-entries | 古いリンク環境への対処という参照資料の説明 |
| ggml/src/ggml-cuda/common.cuh | device配列のconstexprを除去 | 古いCUDAコンパイラの言語対応を避ける処置 |
| ggml/src/ggml-cuda/fattn-common.cuh | builtin_assumeをコメント化 | 未対応builtinをコンパイルさせない |
| ggml/src/ggml-cuda/fattn-vec-f16.cuh | 同上 | 同上 |
| ggml/src/ggml-cuda/fattn-vec-f32.cuh | 同上 | 同上 |

Qwen3構成は同じNEON/common/fattn系の処置に加え、`ggml/src/ggml-cuda/ggml-cuda.cu`のBF16 cuBLAS分岐を`CUDA_VERSION >= 11000`で囲みます。解析上、CUDA10.2で新しい分岐をコンパイル対象外にする処置です。

Qwen3のfattn-commonには`int(D/sizeof(int))`のcast除去5箇所、fattn-vec-f32にはGGML_UNUSEDブロックとloop castの除去も残っています。変更がある事実は確認済みですが、その場のエラーと実際の判断理由は未保存です。「すべてCUDA10.2の必須修正」とは断定しません。

## BF16ヘッダの役割と限界

CUDA10.2向けに保存された [cuda_bf16.h](compat-headers/cuda_bf16.h) は、`nv_bfloat16`を`half`へtypedefする144byteの代替です。[cuda_bf16.hpp](compat-headers/cuda_bf16.hpp)は変換用の小さなラッパーです。

BF16とFP16は指数部・仮数部の配分が異なります。typedefはコンパイル時の型を用意するもので、BF16ビット列の解釈や精度を正しく再現する実装ではありません。BF16モデルが正しく動いたという検証はありません。

**実機のファイル/依存記録で確認済み**なのはCUDA10.2のinclude先の`.h`です。`.hpp`は確認したtoolkit include先に無く、このディレクトリのcompat-headersに保存版があります。配置方法は [GPUビルド](../gpu.md)へ集約しています。

## 適用と確認

補助スクリプトは内部で次の順を実行します。

```text
git checkout --detach <固定commit>
git apply --check <そのcommit用の原patch>
git apply <そのcommit用の原patch>
git diff --stat
```

これは説明用の表記で、具体的なコマンドは各ビルド記事を使います。三つの固定commitへのpatch適用は静的確認済みですが、クリーンビルド成功は未検証です。

## 未使用の試作

[llama-cpu-legacy-neon-guard.patch](llama-cpu-legacy-neon-guard.patch) はCPUベース62df1815bc053066761f4eac58e288f23778e164に対する別案で、ggml/src/ggml-cpu/ggml-cpu-impl.hの互換ガードへGCC<9を追加します。現行CPU patchと併用せず、比較用に残しています。

試作guardはaarch64でも古いGCC時に互換側へ入れる変更が残っています。実際の採用理由・動作成功は未保存で、NEON互換対応を試した可能性という解析です。現行patchと自動併用しません。

試作を参照する場合だけ、**別の新規clone**を固定ベースへ移動してから適用します。

```bash
export TRIAL_SOURCE="$LAB_WORK/llama-neon-trial"
test ! -e "$TRIAL_SOURCE" || exit 1
git clone "$BACKUP/repos/llama/repository.bundle" "$TRIAL_SOURCE"
git -C "$TRIAL_SOURCE" checkout --detach 62df1815bc053066761f4eac58e288f23778e164
git -C "$TRIAL_SOURCE" apply --check "$LAB_ROOT/llama-cpp/patches/llama-cpu-legacy-neon-guard.patch"
git -C "$TRIAL_SOURCE" apply "$LAB_ROOT/llama-cpp/patches/llama-cpu-legacy-neon-guard.patch"
sha256sum "$TRIAL_SOURCE/ggml/src/ggml-cpu/ggml-cpu-impl.h"
# 期待: af1c3a87c9eacc9dbd62ecaefe7d83e5bae50f4c4da5c703e9dd8a6e2066b18c
```

## ライセンス

llama.cppとjetson-patches由来の通知は [licenses](../licenses/llama-LICENSE) と [jetson-patchesの通知](../licenses/jetson-patches-LICENSE) にあります。独自追加部分への新しい包括ライセンスは設定していません。
