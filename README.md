# Jetson Nano / TX2の構築メモ

Nano 4GB（JetPack4.6.1）とTX2（JetPack4.6.6）でllama.cppとPS4 Eyeを使うためのメモです。

| 順序 | 記事 | 内容 |
|---|---|---|
| 1 | [Nanoの初期設定](setup/nano.md) / [TX2の初期設定](setup/tx2.md) | OS・JetPack、機種固有の設定 |
| 2 | [共通パッケージ・開発ツール](setup/packages.md) | SSH、Python、CUDA、jtop、GCC/CMake |
| 3 | [llama.cppのCPUビルド](llama-cpp/README.md) / [CUDAビルド](llama-cpp/gpu.md) | ソース取得とpatch適用、ビルド |
| 4 | [モデル取得](llama-cpp/README.md#モデルを用意する) | Qwen3 GGUFの配置 |
| 5 | [使い方](llama-cpp/usage.md) | 推論・対話・設定・ベンチマーク |

カメラ：[PS4 Eyeの撮影・配信](ps4-eye/README.md) → [校正・距離計算](ps4-eye/calibration.md)。

以降のコマンドでは、Jetson上の `~/Projects/jetson-lab` にこのリポジトリがあるものとします。ソースやモデルは `~/jetson-work` に置きます。

初期設定と共通パッケージの導入後、Jetson側で取得してください。

```bash
mkdir -p ~/Projects
cd ~/Projects
git clone https://github.com/acetaminophen34/jetson-lab.git
```
