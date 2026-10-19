# Nano / TX2の環境構築

最初に機種に合うOSを用意します。[NanoのSDカード作成・初回起動](nano.md)、[TX2のJetPack導入](tx2.md) は機種別です。それ以降はこのページの順で進めます。Macと書かれた操作以外はJetson側で実行します。

## 1. SSHで接続する

SSH接続に必要なソフトを入れます。インストール済みなら、そのまま次へ進めます。

```bash
sudo apt update
sudo apt install --no-upgrade openssh-server
```

SSHを有効にし、接続先IPを表示します。

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
hostname -I
```

**Mac側**でユーザー名とIPを指定します。

```text
ssh <username>@<jetson-ip>
```

Nanoで使った例です。192.168.100.6は固定の初期アドレスではありません。

```bash
ssh a62ss@192.168.100.6
```

パスワードでログインしたら、以降はSSHから操作できます。ディスプレイ等を外す場合は `sudo poweroff` で終了し、電源を外してから接続を変更します。

## 2. 基本パッケージ

不足するパッケージを導入します。Ubuntu18.04のメジャーアップグレードは行いません。

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

Ubuntu18.04の配布名はbionicです。別のUbuntu向け配布先へ変更しないでください。

## 3. リポジトリと作業場所

Jetsonでcloneします。既にcloneしてある場合は、そのフォルダへ移動し、`export` 以降を実行します。

```bash
cd ~
git clone https://github.com/acetaminophen34/jetson-lab.git
cd jetson-lab
export JETSON_LAB="$PWD"
mkdir -p "$JETSON_LAB/work"
```

`work/` は取得したソース・モデル・作業用コードの置き場で、Git管理の対象外です。新しいSSH接続では、cloneしたフォルダで `export JETSON_LAB="$PWD"` を実行します。

## 4. インストールしたソフトを確認する

```bash
python3 --version
python3 -m pip --version
git --version
gcc --version
g++ --version
cmake --version
```

```bash
dpkg-query -W nvidia-l4t-core nvidia-jetpack cuda-toolkit-10-2 \
  libcudnn8 tensorrt libopencv libopencv-python python3-libnvinfer
/usr/local/cuda-10.2/bin/nvcc --version
python3 -c 'import cv2; print("OpenCV", cv2.__version__)'
python3 -c 'import tensorrt; print("TensorRT", tensorrt.__version__)'
```

| 構成 | Nano | TX2 |
|---|---|---|
| Ubuntu / L4T | 18.04.6 / R32.7.1 | 18.04.6 / R32.7.6 |
| JetPack | 4.6.1 | 4.6.6-b24 |
| CUDA | toolkit10.2.460-1 / nvcc10.2.300 | 10.2 |
| 個別開発ツール | GCC/G++8.4.0、CMake3.28.6 | GCC/G++8.4.0、CMake3.28.6 |

Nanoで使用した標準ツール・ライブラリの版です。

| ソフト | バージョン |
|---|---|
| Python / pip | 3.6.9 / 9.0.1 |
| Git | 2.17.1（1:2.17.1-1ubuntu0.18） |
| 標準GCC/G++ / CMake | 7.5.0 / 3.10.2（3.10.2-1ubuntu2.18.04.2） |
| build-essential / make | 12.4ubuntu1 / 4.1-9.1ubuntu1 |
| L4T package / kernel | 32.7.1-20220219090432 / 4.9.253-tegra |
| cuDNN | 8.2.1.32-1+cuda10.2 |
| TensorRT | 8.2.1.8-1+cuda10.2、Python8.2.1.8 |
| OpenCV | 4.1.1、libopencv/libopencv-python=4.1.1-2-gd5a58aa75 |

Python3.6ではpipを無条件に最新版へ更新しません。

### CUDAのPATH

`nvcc: command not found` と出る場合は、CUDAのコマンドを探す場所を追加します。

```bash
echo 'export PATH=/usr/local/cuda-10.2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
nvcc --version
```

## 5. 負荷表示とjtop

[tegrastats](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3276/Tegra%20Linux%20Driver%20Package%20Development%20Guide/AppendixTegraStats.html) でCPU・GPU・メモリの使用状況を表示します。終了はCtrl+Cです。

```bash
sudo tegrastats --interval 1000
```

未導入なら [jetson-stats](https://rnext.it/jetson_stats/) を入れます。Nanoは4.3.2、TX2では版を指定せず導入しました。

```bash
# Nano
sudo -H python3 -m pip install jetson-stats==4.3.2
```

```bash
# TX2
sudo -H python3 -m pip install jetson-stats
```

再ログインして起動します。jtop.serviceへアクセスできない問題は、再ログイン／再起動で解消しました。

```bash
jtop
```

直らない場合は [サービス状態とログ](https://rnext.it/jetson_stats/troubleshooting.html) を見ます。

```bash
systemctl status jtop.service --no-pager
journalctl -u jtop.service -n 30 --no-pager
```

次は [llama.cppの構築・実行](../llama-cpp/README.md)、または [PS4 Camera](../ps4-eye/README.md) へ進みます。
