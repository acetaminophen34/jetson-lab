# Nano 4GBの初期設定

Jetson Nano 4GB Developer Kit / JetPack4.6.1。初回はディスプレイ・キーボード・マウスを接続します。

## 1. Mac：SDイメージを取得する

32GB以上のUHS-1 microSDを用意し、[NVIDIA公式](https://developer.nvidia.com/embedded/jetpack-sdk-461) のNano用イメージを取得します。

```bash
mkdir -p ~/Downloads
cd ~/Downloads
curl -fL --retry 3 -o jetson-nano-jp461-sd-card-image.zip \
  https://developer.nvidia.com/embedded/l4t/r32_release_v7.1/jp_4.6.1_b110_sd_card/jeston_nano/jetson-nano-jp461-sd-card-image.zip
```

ダウンロードしたZIPを展開できるか確認します。最後にエラーがなければEtcherへ進みます。

```bash
cd ~/Downloads
unzip -t jetson-nano-jp461-sd-card-image.zip
```

## 2. Mac：Etcherで書き込む

[balenaEtcher](https://etcher.balena.io/) をインストールし、microSDを接続します。

1. **Flash from file**：取得したZIPを選ぶ。
2. **Select target**：microSDの製品名・容量を確認する。**選んだドライブは全消去されるため、書き込み先を間違えないこと。**
3. **Flash!**：書き込み・検証が終わったら取り出す。Macが「読み取れない」と表示しても初期化しない。

ドライブの確認には次を使えます。[NVIDIAの手順](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit) も参照してください。

```bash
diskutil list external
```

## 3. Nano：起動する

電源を外した状態でmicroSD、ディスプレイ、USBキーボード・マウス、LANを接続してから給電します。Micro-USBは5V・2A以上、DCジャックは適合する5V・4A電源を使い、J48設定を [ユーザーガイド](https://developer.download.nvidia.com/embedded/L4T/r32-3-1_Release_v1.0/Jetson_Nano_Developer_Kit_User_Guide.pdf) で確認してください。ジャンパー変更は電源を外して行います。

## 4. Nano：Ubuntuの初回設定

画面の案内に従い、ユーザー名・パスワード・ホスト名を設定します。APP（Ubuntuを保存する領域）は、通常は提示される最大容量を選びます。

```bash
whoami
hostname
lsblk
df -h /
free -h
```

有線LANまたはWi-FiでMacと同じネットワークへ接続します。

## 5. CUDAなどが入っていない場合

CUDAやOpenCVが入っていない場合は、[JetPack4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461) の開発用ソフトを追加します。既に入っていれば次へ進みます。

```bash
sudo apt update
sudo apt install --no-upgrade nvidia-jetpack=4.6.1-b110
```

## 6. SSHで接続する

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

## 7. 基本パッケージ

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

## 8. リポジトリと作業場所

Jetsonでcloneします。既にcloneしてある場合は、そのフォルダへ移動し、`export` 以降を実行します。

```bash
cd ~
git clone https://github.com/acetaminophen34/jetson-lab.git
cd jetson-lab
export JETSON_LAB="$PWD"
mkdir -p "$JETSON_LAB/work"
```

`work/` は取得したソース・モデル・作業用コードの置き場で、Git管理の対象外です。新しいSSH接続では、cloneしたフォルダで `export JETSON_LAB="$PWD"` を実行します。

## 9. インストールしたソフトを確認する

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

## 10. 負荷表示とjtop

[tegrastats](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3276/Tegra%20Linux%20Driver%20Package%20Development%20Guide/AppendixTegraStats.html) でCPU・GPU・メモリの使用状況を表示します。終了はCtrl+Cです。

```bash
sudo tegrastats --interval 1000
```

負荷表示ツール [jetson-stats](https://rnext.it/jetson_stats/) を導入します。Nanoでは4.3.2を使用しました。

```bash
sudo -H python3 -m pip install jetson-stats==4.3.2
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

## 初期設定の完了

SSHで操作でき、CUDA・OpenCV・TensorRTのバージョンが表示されれば、基本環境の準備は完了です。続けて使う機能を選びます。

- [llama.cpp：ビルド・モデル取得・推論](../llama-cpp/README.md)
- [PS4 Camera：初期化・顔追跡・CPU/GPU測距](../ps4-eye/README.md)
