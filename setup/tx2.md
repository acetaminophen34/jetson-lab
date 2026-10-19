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

## 3. SSHで接続する

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

`hostname -I` で表示されたTX2のIPアドレスを指定します。

パスワードでログインしたら、以降はSSHから操作できます。ディスプレイ等を外す場合は `sudo poweroff` で終了し、電源を外してから接続を変更します。

## 4. 基本パッケージ

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

## 5. リポジトリと作業場所

Jetsonでcloneします。既にcloneしてある場合は、そのフォルダへ移動し、`export` 以降を実行します。

```bash
cd ~
git clone https://github.com/acetaminophen34/jetson-lab.git
cd jetson-lab
export JETSON_LAB="$PWD"
mkdir -p "$JETSON_LAB/work"
```

`work/` は取得したソース・モデル・作業用コードの置き場で、Git管理の対象外です。新しいSSH接続では、cloneしたフォルダで `export JETSON_LAB="$PWD"` を実行します。

## 6. インストールしたソフトを確認する

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

使用したTX2環境はCUDA10.2.300、TensorRT8.2.1、OpenCV4.1.1です。

Python3.6ではpipを無条件に最新版へ更新しません。

### CUDAのPATH

`nvcc: command not found` と出る場合は、CUDAのコマンドを探す場所を追加します。

```bash
echo 'export PATH=/usr/local/cuda-10.2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
nvcc --version
```

## 7. 負荷表示とjtop

[tegrastats](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3276/Tegra%20Linux%20Driver%20Package%20Development%20Guide/AppendixTegraStats.html) でCPU・GPU・メモリの使用状況を表示します。終了はCtrl+Cです。

```bash
sudo tegrastats --interval 1000
```

負荷表示ツール [jetson-stats](https://rnext.it/jetson_stats/) を導入します。TX2では版を指定せず導入しました。

```bash
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

## 初期設定の完了

SSHで操作でき、CUDA・OpenCV・TensorRTのバージョンが表示されれば、基本環境の準備は完了です。続けて使う機能を選びます。

- [llama.cpp：ビルド・モデル取得・推論](../llama-cpp/README.md)
- [PS4 Camera：初期化・顔追跡・CPU/GPU測距](../ps4-eye/README.md)
