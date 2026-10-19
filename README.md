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

## 作業場所を用意する

初期設定と共通パッケージの導入後、Jetson側で好きな場所へcloneします。次はホームディレクトリへ置く例です。

```bash
cd ~
git clone https://github.com/acetaminophen34/jetson-lab.git
cd jetson-lab
export JETSON_LAB="$PWD"
mkdir -p "$JETSON_LAB/work"
```

既にcloneしてある場合は、そのフォルダで次を実行します。

```bash
export JETSON_LAB="$PWD"
mkdir -p "$JETSON_LAB/work"
```

`JETSON_LAB` はclone先の場所です。同じターミナルで各記事のコマンドを続けて実行してください。新しいSSH接続では、cloneしたフォルダへ移動してもう一度設定します。

ソース・モデル・作業用コードは `work/` に保存します。このフォルダはGit管理の対象外です。GCC/CMakeの導入は [共通開発ツール](setup/packages.md) を参照してください。
