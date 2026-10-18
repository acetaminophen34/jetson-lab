# TX2の環境構築

L4T R32.7.6が導入済みのTX2へSDKを追加しました。OSの書き込みは行っていません。

| 項目 | 使用環境 |
|---|---|
| 機種 / RAM | Jetson TX2 / 8GB |
| JetPack / L4T | 4.6.6-b24 / R32.7.6 |
| Ubuntu | 18.04.6 LTS |
| CPU | Denver 2×2 + Cortex-A57×4 |
| GPU | Pascal、Compute Capability 6.2 |
| CUDA | 10.2 |
| GCC/G++ / CMake | 8.4.0 / 3.28.6 |

## 1. JetPackを追加する

[NVIDIA公式JetPack4.6.6](https://developer.nvidia.com/jetpack-sdk-466) のSDKを導入します。導入後、JetPack4.6.6、CUDA Toolkit10.2、cuBLAS、cuDNNが入りました。

```bash
sudo apt update
sudo apt install nvidia-jetpack=4.6.6-b24
```

## 2. 電源モード

初期状態はMAXP_CORE_ARM（モード3）で一部CPUコアがOFFでした。MAXN（モード0）へ変更するとオンラインになりました。

```bash
sudo nvpmodel -q
sudo nvpmodel -m 0
```

次へ：[共通のSSH設定・開発ツール](packages.md)。
