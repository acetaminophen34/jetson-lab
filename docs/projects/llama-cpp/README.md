# llama.cppでQwen3を動かす

## 概要

llama.cppは、言語モデルの重みを読み、入力をトークンへ分割し、次のトークンを反復生成するC/C++の実装です。このNanoではQwen3-0.6BのGGUFを使ったCPU推論を確認しています。推論に成功したソースは、CUDA10.2向けに試した古いGPUソースとは別のcommitです。

## 背景・仕組み

GGUFにはモデルのテンソルとメタデータが入ります。モデル名のQ4_K_Mは量子化形式を示し、実行時の表示もQ4_K - Mediumでした。ファイル名だけで同一モデルを保証できないため、再構築ではSHA-256を照合します。モデル配布元/revision/ライセンスは既存資料から確定できていません。

計算の流れは、**プロンプト → トークン化 → prompt processing → 逐次生成**です。prompt processingのtoken/sと生成のtoken/sは異なる測定です。生成時には過去トークンの情報を保持するKVキャッシュも使うため、コンテキスト長を大きくすると作業メモリが増えます。

llama.cppの下層のggmlがテンソル演算を担当します。CPU版ではCPUバックエンド、GPU版ではCUDAバックエンドやcuBLASを使う構成です。GPUへ何層載せるかと、CPUのスレッド数は別の設定です。

## 対象ソースと環境

CPU経路はGCC/G++8.4.0、CMake3.28.6、Release、OpenMP有効、CUDA無効を基準にします。GPU側はCUDA C++14/10.2を使う別経路です。cuDNN/TensorRTの導入記録はありますが、このGGUF推論の必須経路とは確認していません。

固定commitと原patchの対応は [patch解説](patches.md) を正本にしています。上流の最新HEADや同名branchへ追従すると、必要な修正やモデル対応が変わるため、再構築では固定します。b5050はQwen3対応branchとは異なり、Qwen3モデルを実行できる前提にしません。

## 実装・再構築の読み順

1. [CPUビルド](cpu-build.md)：ソース復元、patch、CMake生成、コンパイル、モデル、短い推論。
2. [GPUビルド](gpu-build.md)：別commitとCUDA10.2用の処置。CPU経路へ混ぜない。
3. [patch解説](patches.md)：ソース変更の意図、実際に残る差分、理由が未確定の変更。

このHEADのCLIは単なる小さな単独プログラムではなく、CLI実装・server-context・共通ライブラリなどをリンクします。したがってCLIをビルドするために`LLAMA_BUILD_SERVER=ON`が必要ですが、サーバープロセスを起動する意味ではありません。MTMD/UIのtarget依存も、単にフラグ名だけでは判断できません。

## 動作確認と制約

**実機確認済み**：既存CPU CLIで短いQwen3推論、終了0。実測は [検証結果](../../../reference/validation-results.md) に集約しています。

**ユーザー申告**：GPU起動で電源容量不足により落ち、AC電源対策まではCPU運用。**未検証**：クリーンビルド、安定したGPU推論、サーバー運用。同じソースからバイナリを作る手順と、バイト一致する生成物を再生成できることも区別します。

## 参照資料

- [出典S2〜S4・S8](../../../reference/sources.md)
- [版・モデル識別子](../../../reference/environment-versions.md)、[問題の切り分け](../../troubleshooting.md)
