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

## 2. Python・pip・jtop

Pythonを用意し、jetson-statsを導入します。使用したjetson-statsの版は不明です。

```bash
sudo apt install python3 python3-pip python3-dev
```

```bash
sudo -H python3 -m pip install jetson-stats
```

再ログインして起動します。TX2で動作しました。

```bash
jtop
```

## 3. CUDAのPATH

nvccは存在していましたが、PATHが通っていなかったため追加しました。

```bash
echo 'export PATH=/usr/local/cuda-10.2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
nvcc --version
```

## 4. GCC/G++8.4.0

gcc-8/g++-8を導入します。実機でG++8.4.0を確認しました。

```bash
sudo apt install gcc-8 g++-8 git wget libssl-dev
```

```bash
g++-8 --version
```

## 5. CMake3.28.6

[Kitware公式](https://github.com/Kitware/CMake/releases/tag/v3.28.6) のLinux aarch64版を展開します。

```bash
mkdir -p ~/opt ~/Downloads
cd ~/Downloads

wget https://github.com/Kitware/CMake/releases/download/v3.28.6/cmake-3.28.6-linux-aarch64.tar.gz

tar -xzf cmake-3.28.6-linux-aarch64.tar.gz -C ~/opt
```

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

## 6. 電源モード

初期状態はMAXP_CORE_ARM（モード3）で一部CPUコアがOFFでした。MAXN（モード0）へ変更するとオンラインになりました。

```bash
sudo nvpmodel -q
sudo nvpmodel -m 0
```

次へ：[TX2のllama.cpp GPUビルド・推論](../llama-cpp/gpu.md#tx2)。
