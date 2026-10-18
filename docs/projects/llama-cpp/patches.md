# ソース修正を読む・再適用する

## 概要と前提

原patchは実機の追跡ファイル差分を保全したものです。ビルドを通す互換処置と、数値演算の正しさの保証は同じではありません。エラーログや変更理由が保存されていない場合は、コードの意味からの説明と実際の動機を区別します。

## 固定commitと適用単位

| 構成 | ベースcommit | 原patch | 変更数 |
|---|---|---|---:|
| CPU | 62df1815bc053066761f4eac58e288f23778e164 | [llama.patch](../../../patches/llama.patch) | 5 |
| b5050 GPU | 23106f94ea2bc3da929afb7330655fd5515d08dc | [llama5050gpu.patch](../../../patches/llama5050gpu.patch) | 7 |
| Qwen3 GPU | d3bd7193ba66c15963fd1c59448f22019a8caf6e | [llama-qwen3-gpu.patch](../../../patches/llama-qwen3-gpu.patch) | 6 |

原patchのバイトは旧成果物と一致させています。最新branchへ適用するために加工していません。`jetson-patches`の参照commitはcba793e345442fc9f542f3418ae4b0070bd37b06で、ローカル追跡変更はありません。Qwen3のベースは既存llama bundleにも含まれています。

## CPU側の変更と意味

| ファイル | 変更 | 技術的な意味・根拠の限界 |
|---|---|---|
| ggml/src/ggml-cpu/ggml-cpu-impl.h | NEONのx4ロードを4回の単独ロードにする | 16byteずつ4回読み、元の4ベクトルを組み立てる。古いARMヘッダでのintrinsic不足を避ける解析。実エラーのGCC revisionは未保存 |
| tools/cli/CMakeLists.txt | stdc++fsをリンク | GCC8系のfilesystem実装を明示リンクする処置 |
| tools/llama-bench/CMakeLists.txt | stdc++fsをリンク | benchでも同じリンク要件を扱う |
| tools/server/server-context.cpp | iomanipをinclude | 書式操作の宣言を明示的に読み込む |
| tools/server/server-schema.cpp | field_numのテンプレート型を明示 | decltypeで元の値の型を指定。古いコンパイラの型推論への対応という解析 |

stdc++fsの指定と、原benchのlink.txt末尾にあるwhole-archive追加は別です。後者はpatchだけに現れないため、追加経緯は未確定です。[CPUビルド](cpu-build.md)で残る検証点として扱っています。

## CUDA10.2側の変更

b5050はCPUのNEON代替に加え、次の6ファイルを変更します。6ファイルと追加ヘッダ2個は既存解析でjetson-patchesのb5050用ファイルと完全一致しています。

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

CUDA10.2向けに保存された [cuda_bf16.h](../../../patches/compat-headers/cuda_bf16.h) は、`nv_bfloat16`を`half`へtypedefする144byteの代替です。[cuda_bf16.hpp](../../../patches/compat-headers/cuda_bf16.hpp)は変換用の小さなラッパーです。

BF16とFP16は指数部・仮数部の配分が異なります。typedefはコンパイル時の型を用意するもので、BF16ビット列の解釈や精度を正しく再現する実装ではありません。BF16モデルが正しく動いたという検証はありません。

**実機のファイル/依存記録で確認済み**なのはCUDA10.2のinclude先の`.h`です。`.hpp`は確認したtoolkit include先に無く、repoルートに保存版があります。配置方法は [GPUビルド](gpu-build.md)へ集約しています。

## 適用と確認

補助スクリプトは内部で次の順を実行します。

```text
git checkout --detach <固定commit>
git apply --check <そのcommit用の原patch>
git apply <そのcommit用の原patch>
git diff --stat
```

これは説明用の表記で、具体的なコマンドは各ビルド記事を使います。三つの固定commitへの適用チェックは既存資料で静的確認済みです。編集工程ではこの適用を実機ビルド成功と読み替えません。

3個の.bakは原保全先に残し、独自変更が残った1個を [試作guardの独立patch](../../../patches/llama-cpu-legacy-neon-guard.patch) として新たに保全しました。他2個はベースHEADと同一です。画像の回収件数の訂正は [棚卸し](../../../reference/code-inventory.md) を参照してください。原patchに追加ファイルは含まれないため、BF16ヘッダは別ファイルとして管理します。

## 参照資料・ライセンス

- [出典S2・S3・S7](../../../reference/sources.md)、[原リンク記録](../../../reference/details/current-build-links.md)
- [LICENSE](../../../LICENSE)、[第三者MIT通知](../../../licenses/jetson-patches-LICENSE)

## 試作と実装の参照

現行3patchと独立したNEON guard原案、自作カメラへの未適用互換案、各ベースと適用方法は [patches README](../../../patches/README.md) に一覧化しました。保全・環境・検証に使った旧スクリプトも [scripts README](../../../scripts/README.md) から参照できます。
