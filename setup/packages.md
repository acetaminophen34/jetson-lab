# Nanoの基本環境

以下はNano側で実行します。使用環境はUbuntu18.04.6、L4T32.7.1、aarch64です。

## 1. パッケージを用意する

一覧を更新し、不足する基本パッケージを入れます。JetPackとの互換性を保つため、Ubuntuのメジャーアップグレードは行いません。

```bash
cat /etc/os-release
cat /etc/nv_tegra_release
uname -m
sudo apt update
```

```bash
sudo apt install --no-install-recommends --no-upgrade \
  build-essential git curl wget ca-certificates \
  python3 python3-pip python3-dev cmake
```

[Ubuntu18.04は標準サポート終了済み](https://ubuntu.com/18-04)です。aptが404等で止まる場合は、Ubuntu側のbionic指定とNVIDIA側のr32.7/t210設定を確認します。

```bash
grep -RhE '^[[:space:]]*deb ' /etc/apt/sources.list /etc/apt/sources.list.d/
apt-cache policy
```

## 2. 使用したバージョン

```bash
python3 --version
python3 -m pip --version
git --version
gcc --version
g++ --version
cmake --version
```

| ソフト | 使用版 |
|---|---|
| Python / pip | 3.6.9 / 9.0.1 |
| Git | 2.17.1（dpkg: 1:2.17.1-1ubuntu0.18） |
| 標準GCC/G++ | 7.5.0 |
| 標準CMake | 3.10.2（dpkg: 3.10.2-1ubuntu2.18.04.2） |
| build-essential / make | 12.4ubuntu1 / 4.1-9.1ubuntu1 |
| L4T / kernel | 32.7.1-20220219090432 / 4.9.253-tegra |
| CUDA toolkit / nvcc | 10.2.460-1 / 10.2.300 |
| cuDNN | 8.2.1.32-1+cuda10.2 |
| TensorRT | 8.2.1.8-1+cuda10.2、Python8.2.1.8 |
| OpenCV | 4.1.1、libopencv/libopencv-python=4.1.1-2-gd5a58aa75 |

Python3.6を使うため、pipは無条件に最新版へ更新しません。

## 3. CUDA・OpenCV・TensorRTを確認する

既に入っていれば再導入は不要です。

```bash
dpkg-query -W nvidia-l4t-core nvidia-jetpack cuda-toolkit-10-2 \
  libcudnn8 tensorrt libopencv libopencv-python python3-libnvinfer
/usr/local/cuda-10.2/bin/nvcc --version
python3 -c 'import cv2; print("OpenCV", cv2.__version__)'
python3 -c 'import tensorrt; print("TensorRT", tensorrt.__version__)'
```

SDKが不足している場合だけ、[JetPack4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461) のパッケージを導入します（新規導入は未検証）。指定版が無ければ配布先を確認してください。

```bash
apt-cache policy nvidia-jetpack cuda-toolkit-10-2 libcudnn8 tensorrt libopencv
sudo apt install --no-upgrade nvidia-jetpack=4.6.1-b110
```

絶対パスのnvccは動くのに `nvcc` が見つからない場合、PATHを設定します。

```bash
export PATH=/usr/local/cuda-10.2/bin:$PATH
nvcc --version
```

継続して使うなら、同じ設定がないことを確認して追記します。

```bash
printf '%s\n' 'export PATH=/usr/local/cuda-10.2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## 4. 負荷を表示する

[tegrastats](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3276/Tegra%20Linux%20Driver%20Package%20Development%20Guide/AppendixTegraStats.html) を起動します。終了はCtrl+Cです。

```bash
sudo tegrastats --interval 1000
```

## 5. jtopを使う

[jetson-stats](https://rnext.it/jetson_stats/) は4.3.2を使用しました。未導入の場合だけ入れます。

```bash
sudo -H python3 -m pip install jetson-stats==4.3.2
```

SSHへ接続し直して起動します。

```bash
jtop
```

jtop.serviceへアクセスできない問題は、再ログイン／再起動で解消しました。直らない場合は [サービス状態とログ](https://rnext.it/jetson_stats/troubleshooting.html) を確認します。

```bash
systemctl status jtop.service --no-pager
journalctl -u jtop.service -n 30 --no-pager
```

## 次へ

- [llama.cpp](../llama-cpp/README.md)：GCC8.4・CMake3.28.6の導入から。
- [PS4 Eye](../ps4-eye/README.md)：カメラ用ライブラリとfirmwareロード。
