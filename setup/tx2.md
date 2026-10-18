# TX2の環境構築

UbuntuとL4T R32.7.6が入っているTX2に、CUDAなどの開発用ソフトを追加する手順です。

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

[JetPack4.6.6](https://developer.nvidia.com/jetpack-sdk-466) を入れると、CUDA10.2とGPU計算用ライブラリが導入されます。

```bash
sudo apt update
sudo apt install nvidia-jetpack=4.6.6-b24
```

## 2. 電源モード

全CPUコアを使うため、電源モードをMAXN（モード0）へ変更します。元のMAXP_CORE_ARM（モード3）では一部のコアが停止していました。

```bash
sudo nvpmodel -q
sudo nvpmodel -m 0
```

次へ：[共通のSSH設定・開発ツール](packages.md)。
