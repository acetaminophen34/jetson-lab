# Jetson Lab

Jetsonで作ったプログラムと、環境を作り直すための手順をまとめています。説明・ソースコード・修正パッチをプロジェクトごとに管理します。

## 使用環境

Jetson Nano（aarch64、RAM約4GB）、Ubuntu18.04.6、L4T32.7.1、CUDA10.2。再構築の目標はJetPack4.6.1です。TX2は移植先の候補で、実機検証はしていません。

## 開発したもの

| プロジェクト | 内容 |
|---|---|
| [llama.cpp / Qwen3](llama-cpp/README.md) | 古いGCC/CUDAへの互換修正、CPU推論、GPUビルド手順。CPUで3.8 tokens/sを確認 |
| [PS4 Eye](ps4-eye/README.md) | RGB配信、左右画像の切り出し、ステレオ校正、視差・深度処理。映像取得は未検証 |
| [補助ツール](tools/README.md) | 校正データの復元、環境確認、保全・調査に使用したスクリプト |

## 環境を再構築する

[Nanoの準備](setup/nano.md) → [パッケージ・コンパイラ](setup/packages.md) → [CPU版LLM](llama-cpp/cpu.md) → [カメラ](ps4-eye/README.md) → [GPU版（任意）](llama-cpp/gpu.md)。

TX2については [適用範囲](setup/tx2.md) を確認してください。
