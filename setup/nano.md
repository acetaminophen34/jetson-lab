# Jetson Nanoの環境準備

## 環境の構成

NanoではCPUとGPUがメモリと電源を共有します。GPUへ処理を移しても、モデルの重みや作業領域が不要になるわけではありません。

| 層 | 役割 | このプロジェクトでの位置づけ |
|---|---|---|
| JetPack | Jetson向けの開発環境一式をまとめたリリース | 再構築の目標は4.6.1 |
| L4T（Linux for Tegra） | ボード用カーネル、ドライバ、関連する基盤ソフトウェア | 実機記録はR32.7.1 |
| Ubuntu | shell、apt、Python、開発ツールなどのユーザー環境 | 実機記録は18.04.6 LTS |
| CUDA | GPUで実行するコードの開発/実行環境 | GPU版llama.cppはCUDA10.2を対象 |
| cuDNN | ニューラルネットワーク向けGPU演算ライブラリ | 導入記録はあるが、このllama経路の必須依存とは確認していない |
| TensorRT | 学習済みネットワークを最適化して推論するための環境 | 導入記録はあるが、このGGUF推論をTensorRT経由とは扱わない |

llama.cppはCUDA runtime/cuBLASを直接使う構成です。cuDNN/TensorRTが導入されていても、このGGUF推論がそれらを経由するわけではありません。

| 項目 | 使用環境 |
|---|---|
| OS / arch | Ubuntu18.04.6 LTS / aarch64 |
| L4T / kernel | R32.7.1 / 4.9.253-tegra |
| nvidia-l4t-core | 32.7.1-20220219090432 |
| BOARD表記 | t210ref（製品型番・キャリアボードは未確定） |
| メモリ / 媒体 | RAM表示約3.9G、root mmcblk0p1 ext4、29.7G |
| swap | zram4個、各495.5MiB |
| CUDA | nvcc10.2.300、toolkit package10.2.460-1 |
| cuDNN | libcudnn8=8.2.1.32-1+cuda10.2 |
| TensorRT | tensorrt=8.2.1.8-1+cuda10.2、Python8.2.1.8 |

JetPack4.6.1は再構築の目標です。元のflashイメージ、イメージhash、正確なboard指定、nvidia-jetpackメタパッケージ版は未確定のため、ボード適合性を確認してからOSを導入します。

## 1. OSを準備して確認する

```sh
uname -a
cat /etc/os-release
cat /etc/nv_tegra_release
dpkg-query -W nvidia-l4t-core nvidia-jetpack
free -m
lsblk
swapon --show
```

Ubuntu・L4T・archが表と一致することを確認します。nvidia-jetpackメタパッケージが無いだけで、CUDAが無いとは判断しません。異なる場合は、個別ライブラリの更新より先にOSイメージと対象ボードを確認します。タイムゾーンは変更しません。

## 2. 再構築に必要なものを揃える

ソース復元には既存preservationのGit bundleを使います。Qwen3のGGUFとaarch64版CMake3.28.6 archiveは別途用意し、各手順のhashで識別します。カメラのfirmwareと校正データも手元の非公開資産から使います。

同じbashセッションで、次の絶対パスを実際の配置へ直して設定してください。以降のコマンドは復元先Jetsonで実行する手順です。

```bash
export LAB_ROOT=/absolute/path/jetson-lab
export BACKUP=/absolute/private/path/20261018-002830
export PRIVATE_ROOT=/absolute/private/path/jetson-rebuild-private
export RECOVERY="$PRIVATE_ROOT/followup-20261018-134602"
export LAB_WORK="$HOME/jetson-lab-work"
test -d "$LAB_ROOT/llama-cpp/patches" || exit 1
test -d "$BACKUP/repos" || exit 1
test ! -e "$LAB_WORK" || exit 1
mkdir -p "$LAB_WORK/logs"
export RUNLOG="$LAB_WORK/logs"
```

LAB_WORKは新規作業先です。既存ディレクトリがある場合は別名を選びます。

## 3. 順に構築する

1. [基本パッケージ、GCC8.4、CMake3.28.6](packages.md)
2. [CPU版llama.cppとQwen3](../llama-cpp/cpu.md)
3. [PS4 Eyeのfirmware・撮影](../ps4-eye/README.md) と [校正・深度](../ps4-eye/calibration.md)
4. [CUDA10.2のGPU版（任意）](../llama-cpp/gpu.md)

既存CPUバイナリの推論は実機確認済みですが、初期化からのクリーンビルドは未検証です。USB列挙と画像取得も別の成功条件として扱います。

## 電源とシステム設定

ユーザー申告ではGPU起動時に電源容量不足で落ち、ACアダプタにするまではCPUだけで運用していました。電流やリセット原因の計測、電源対策後のGPU安定性は未確認です。CPU経路を先に再現してください。

LLM/PS4専用のsystemd自動起動やudev設定は確認できていません。JetPack標準のhub/tegraルールをカメラ専用とみなして上書きする必要はありません。jtopはjetson-stats4.3.2で、unitは/usr/local/bin/jtop --forceを起動する構成でしたが、推論・撮影の必須依存ではありません。クロック、nvpmodel、swapの変更も基本手順に含めません。
