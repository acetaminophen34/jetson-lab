# llama.cppの互換修正

| 構成 | ベースcommit | patch |
|---|---|---|
| CPU | 62df1815bc053066761f4eac58e288f23778e164 | [llama.patch](llama.patch) |
| Qwen3 GPU | d3bd7193ba66c15963fd1c59448f22019a8caf6e | [llama-qwen3-gpu.patch](llama-qwen3-gpu.patch) |
| 旧b5050 GPU | 23106f94ea2bc3da929afb7330655fd5515d08dc | [llama5050gpu.patch](llama5050gpu.patch) |

## CPU

| 変更ファイル | 修正理由・内容 |
|---|---|
| ggml/src/ggml-cpu/ggml-cpu-impl.h | 古いARMヘッダに合わせ、NEON x4ロードを単独ロード4回へ置換 |
| tools/cli/CMakeLists.txt、tools/llama-bench/CMakeLists.txt | GCC8のfilesystem用にstdc++fsをリンク |
| tools/server/server-context.cpp | iomanipをinclude |
| tools/server/server-schema.cpp | field_numのテンプレート型を明示 |

元benchのlink.txtには `-Wl,--whole-archive -lstdc++fs -Wl,--no-whole-archive` もありました。patchだけではこの指定を再現できず、filesystemの未解決参照が残る場合の確認点です。

## CUDA10.2

| 変更ファイル | 修正理由・内容 |
|---|---|
| ggml/src/ggml-cuda/common.cuh | 古いnvcc向けにdevice配列のconstexprを除去 |
| ggml/src/ggml-cuda/fattn-common.cuh、fattn-vec-f16.cuh、fattn-vec-f32.cuh | 未対応のbuiltin_assumeを除外 |
| ggml/src/ggml-cuda/ggml-cuda.cu（Qwen3版） | CUDA11以降のBF16 cuBLAS分岐をCUDA_VERSION >= 11000で囲む |
| CMakeLists.txt（b5050版） | arch指定を追加。[条件式の問題](../gpu.md#旧b5050版)あり |
| ggml/CMakeLists.txt（b5050版） | stdc++fsとcopy-dt-needed-entriesを追加 |

GPU版にもCPUのNEON互換処置を含みます。Qwen3版にはfattn-commonのcast除去5箇所、fattn-vec-f32のGGML_UNUSED・loop cast除去もありますが、個別の変更理由は不明です。

[BF16代替ヘッダの配置](../README.md#bf16ヘッダを配置する) は導入記事にまとめています。jetson-patchesの参照commitはcba793e345442fc9f542f3418ae4b0070bd37b06です。

## 未使用の試作

[作業場所の設定](../../README.md#作業場所を用意する) 後に実行します。[NEON guard案](llama-cpu-legacy-neon-guard.patch) はCPUベースにGCC<9条件を加える別案です。現行CPU patchとは併用しません。

```bash
cd "$JETSON_LAB/work"
git clone https://github.com/ggml-org/llama.cpp.git llama-neon-trial
cd llama-neon-trial
git checkout 62df1815bc053066761f4eac58e288f23778e164
git apply "$JETSON_LAB/llama-cpp/patches/llama-cpu-legacy-neon-guard.patch"
```

## ライセンス

[llama.cpp](../licenses/llama-LICENSE)、[旧GPU版](../licenses/llama5050gpu-LICENSE)、[jetson-patches](../licenses/jetson-patches-LICENSE) の通知を維持しています。独自追加部分の利用許諾は [LICENSE](../../LICENSE) を参照してください。
