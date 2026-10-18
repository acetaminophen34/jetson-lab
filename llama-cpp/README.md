# llama.cppでQwen3を動かす

## 概要

NanoでQwen3-0.6BのGGUFモデルを実行します。基本はCPU版です。既存CPUバイナリで生成3.8 tokens/sを確認し、GPU版はCUDA10.2向け修正とビルド手順を用意しています。初期化後のクリーンビルドとGPU安定動作は未検証です。

## 仕組み

GGUFはモデルを格納する形式、llama.cppは推論エンジンです。ggmlのCPU/CUDAバックエンドがテンソル演算を担当します。CMakeでtargetと依存関係を生成し、GCC/G++とnvccでコンパイルします。

このCPUソースのCLIはserver-contextと共通ライブラリもリンクするため、LLAMA_BUILD_SERVER=ONが必要です。ビルド設定でserverを有効にすることと、サーバープロセスを起動することは別です。

## 構築

[環境・ツール](../setup/packages.md) を準備してから [CPUビルド](cpu.md) へ進みます。CUDAを使う場合だけ [GPUビルド](gpu.md) を選びます。

| 構成 | 固定commit | パッチ |
|---|---|---|
| CPU・基本経路 | 62df1815bc053066761f4eac58e288f23778e164 | [llama.patch](patches/llama.patch) |
| Qwen3 GPU | d3bd7193ba66c15963fd1c59448f22019a8caf6e | [llama-qwen3-gpu.patch](patches/llama-qwen3-gpu.patch) |
| 旧b5050 GPU・比較用 | 23106f94ea2bc3da929afb7330655fd5515d08dc | [llama5050gpu.patch](patches/llama5050gpu.patch) |

[修正の解説](patches/README.md) に変更ファイル・理由・BF16代替ヘッダをまとめています。未使用のNEON guard試作は現行patchと別案です。構成の異なるソース・patchを混ぜないでください。

## 実行

[CPU手順](cpu.md#モデルの配置と識別)でQwen3-0.6B-Q4_K_M.ggufを配置し、同記事の短いCPU推論を実行します。[cpu-smoke.py](tools/cpu-smoke.py) はhash確認、2スレッド、GPUなし、RAM監視と120秒制限をまとめた補助ツールです。

[restore-llama.sh](tools/restore-llama.sh) はローカルbundleから新しいソースを作るツールです。CPU/Qwen3 GPU/b5050 GPUを選択でき、ビルドやインストールは行いません。

## トラブルシューティング

古いGCCのNEON intrinsicやfilesystemリンクは [CPU手順](cpu.md#トラブルシューティング)、CUDAの言語・arch・BF16問題は [GPU手順](gpu.md) と [patch解説](patches/README.md) を確認します。

ユーザー申告ではGPU起動時に電源容量不足で落ちたため、ACアダプタへ切り替えるまではCPUのみで運用していました。電源対策後のGPU性能・安定性は未確認です。
