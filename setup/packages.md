# Nanoの基本開発環境とCUDAを確認する

[Nanoの初回設定・SSH接続](nano.md) の続きです。**このページのコマンドはNano側**で実行します。MacからSSHで入力しても、処理されるのはNanoです。

既存inventoryで確認した版・状態と、初期化後に同様の環境へ進むための推奨コマンドを併記します。今回これらのインストールや動作確認を実機でやり直したわけではありません。

## 1. OSとaptリポジトリを確認する

Ubuntu18.04・L4T32.7.1・aarch64を確認してから、パッケージ一覧を更新します。`apt update` は一覧の更新であり、導入済みパッケージを一括更新する操作ではありません。

```bash
cat /etc/os-release
cat /etc/nv_tegra_release
uname -m
sudo apt update
```

[Ubuntu18.04は標準サポート終了済み](https://ubuntu.com/18-04)です。404やRelease fileエラー時は下記で配布先とbionic指定を確認し、NVIDIAのr32.7/t210向け設定を別OS向けへ変えないでください。

```bash
grep -RhE '^[[:space:]]*deb ' /etc/apt/sources.list /etc/apt/sources.list.d/
apt-cache policy
```

[Ubuntu Portsのbionic配布情報](https://ports.ubuntu.com/ubuntu-ports/dists/bionic/Release) は確認できます。「古いOSだから」と全URLをold-releasesへ一括置換したり、署名検証を無効にしたりせず、実際に失敗した配布先を確認します。JetPack互換性を維持するため、ここではdo-release-upgradeや無差別なapt upgradeを行いません。

## 2. 基本パッケージは不足分だけ入れる

Python、Git、標準GCC/CMakeが使えるか先に確認します。以下の版は過去の実機表示で、初回イメージの状態やapt候補版と必ず同じとは限りません。

```bash
python3 --version
python3 -m pip --version
git --version
gcc --version
g++ --version
cmake --version
```

| ツール | 過去の確認版 |
|---|---|
| Python / pip | 3.6.9 / 9.0.1 |
| Git | 2.17.1（dpkg: 1:2.17.1-1ubuntu0.18） |
| 標準GCC/G++ | 7.5.0 |
| 標準CMake | 3.10.2（dpkg: 3.10.2-1ubuntu2.18.04.2） |
| build-essential / make | 12.4ubuntu1 / 4.1-9.1ubuntu1 |

必要なものが無い場合に使う導入例です。`--no-upgrade` は既にある対象パッケージの更新を抑え、`--reinstall` は指定しません。使えるものを再インストールする必要はありません。

```bash
sudo apt install --no-install-recommends --no-upgrade \
  build-essential git curl wget ca-certificates \
  python3 python3-pip python3-dev cmake
```

取得先はUbuntu PortsとOSに設定されたNVIDIA配布先です。Python3.6を使うため、pipやPython一式を無条件に最新版へ置換しません。

## 3. JetPackの構成要素と導入履歴を区別する

[JetPack4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461) はL4T・GPUドライバ・開発ライブラリをまとめたリリースです。下表の「標準提供」はそのリリースの構成要素という意味で、各パッケージが実機の最初の起動時から入っていたという証明ではありません。

| 区分 | 構成・過去の版 | 役割・分かっていること |
|---|---|---|
| OS/JetPack標準提供 | nvidia-l4t-core 32.7.1-20220219090432、kernel4.9.253-tegra | カーネル・Jetsonドライバ。Ubuntu18.04.6上で確認 |
| JetPack標準提供 | CUDA toolkit10.2.460-1、nvcc10.2.300 | GPU開発・実行環境。数値は別種類の版 |
| JetPack標準提供 | cuDNN8.2.1.32-1+cuda10.2 | ニューラルネットワークの演算ライブラリ |
| JetPack標準提供 | TensorRT8.2.1.8-1+cuda10.2 | 推論の最適化/runtime。Python表示8.2.1.8 |
| JetPack標準提供 | OpenCV4.1.1、libopencv/libopencv-python=4.1.1-2-gd5a58aa75 | 画像処理。実機での独自ビルド歴は不明 |
| 後から追加したソフト/個別利用 | jetson-stats4.3.2、GCC/G++8.4.0、CMake3.28.6 | jtopとLLM向けツール。導入コマンド全履歴は不明 |
| 後から追加した依存 | python3-usb1.0.0-1 | PS4 Eyeでusb不足を解消した作業履歴あり |
| 導入経緯不明 | build-essential、Git、標準CMake、pip、openssh-server | inventoryでは導入済み。最初からか後追加かは判別できない |
| 導入経緯不明・稼働確認あり | docker.io20.10.7-0ubuntu5~18.04.3、nvidia-docker2 2.8.0-1 | Dockerサービスはactive/running。導入方法は未確定 |

apt-markのmanual表示だけで「ユーザーが後から追加した」とは判断しません。GCC8・個別CMakeとカメラ固有依存は、基本環境ができてから必要なプロジェクトだけで使います。

## 4. CUDA・cuDNN・TensorRT・OpenCVを確認する

既に入っているSDKは入れ直さず、版とPython importを確認します。nvidia-jetpackはまとめ用メタパッケージなので、それだけが無くても各構成要素が導入済みのことがあります。

```bash
dpkg-query -W nvidia-l4t-core nvidia-jetpack cuda-toolkit-10-2 \
  libcudnn8 tensorrt libopencv libopencv-python python3-libnvinfer
/usr/local/cuda-10.2/bin/nvcc --version
python3 -c 'import cv2; print("OpenCV", cv2.__version__)'
python3 -c 'import tensorrt; print("TensorRT", tensorrt.__version__)'
```

期待する表示はnvcc10.2.300、OpenCV4.1.1、TensorRT8.2.1.8です。cuDNNには同名のPython importを要求せず、dpkgで確認します。OpenCV/TensorRTのimport成功だけではGPU演算の実行テストにはなりません。

### SDKの構成要素が不足している場合だけ

L4T32.7.1用の配布先であることと候補版を確認し、[JetPack4.6.1公式導入案内](https://developer.nvidia.com/embedded/jetpack-sdk-461) に沿って不足SDKを導入します。次は4.6.1メタパッケージを使う推奨例で、現在のapt依存解決と実機導入は未検証です。

```bash
apt-cache policy nvidia-jetpack cuda-toolkit-10-2 libcudnn8 tensorrt libopencv
sudo apt install --no-upgrade nvidia-jetpack=4.6.1-b110
```

現時点の4.6.1-b110のapt提供可否は未確定です。配布が無い、または異なるL4T/SDK版へ変更される場合は進めず、提供元と依存を確認します。cv2だけ無い場合はJetPackのlibopencv-python、TensorRTのPythonだけ無い場合はpython3-libnvinferを確認し、pipの別ビルドやPC向けCUDA installerで置き換えません。

### nvccだけが見つからない場合

絶対パスのnvccが動けば、CUDA未導入ではなくPATHの問題です。その場合だけ次の設定を現在のシェルで試します。

```bash
export PATH=/usr/local/cuda-10.2/bin:$PATH
nvcc --version
```

有効なら、まだ同じ設定がないことを確認してbashの設定へ1回だけ追記します。LD_LIBRARY_PATHは初期設定で一律変更せず、実際のリンクエラーがある場合に対象ライブラリを調べます。

```bash
printf '%s\n' 'export PATH=/usr/local/cuda-10.2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## 5. tegrastatsで状態を見る

NVIDIA標準の [tegrastats](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3276/Tegra%20Linux%20Driver%20Package%20Development%20Guide/AppendixTegraStats.html) でRAM、CPU/GPU利用率、温度等を表示します。リンクはL4T32.7系の共通ツール説明で、OSの更新を指示するものではありません。Ctrl+Cで表示を終了します。

```bash
sudo tegrastats --interval 1000
```

1秒ごとに値が出れば利用できます。コマンドが無い場合はL4Tツールの配置を確認し、クロックや電源モードを変更して解決しようとはしません。

## 6. 任意：jetson-stats / jtopを使う

[jetson-stats公式](https://rnext.it/jetson_stats/) のjtopは状態表示ツールで、実機では4.3.2とjtop.serviceの稼働が確認されています（AGPL-3.0）。既に動く場合は再導入せず、まず版を確認します。

```bash
python3 -m pip show jetson-stats
jtop
```

**未導入の場合だけ**、過去環境に合わせた [PyPIの4.3.2](https://pypi.org/project/jetson-stats/4.3.2/) を指定します。新規導入は未検証で、最新版への一括更新は行いません。

```bash
sudo -H python3 -m pip install jetson-stats==4.3.2
```

インストール後はSSHからログアウトしてMacから接続し直し、jtopを起動します。公式案内にも再ログインまたは再起動が必要とあり、**過去にもjtop.serviceへアクセスできず、再ログイン／再起動後に使えた経緯があります**（ユーザーの作業履歴）。

```bash
# NanoのSSHセッション
exit
```

Macで `ssh <username>@<jetson-ip>` により再接続した後、Nano側で実行します。

```bash
jtop
```

### jtop.serviceへ接続できないとき

[公式の対処](https://rnext.it/jetson_stats/troubleshooting.html) と同様に、サービス状態とログを確認します。ここでの再起動・サービス再始動は読者が行うための手順で、今回実機では実行していません。

```bash
systemctl status jtop.service --no-pager
journalctl -u jtop.service -n 30 --no-pager
```

停止している場合だけ `sudo systemctl restart jtop.service` を試します。再ログイン後も使えず、実行中の作業を終了できる場合は `sudo reboot` で再起動し、Macから再接続します。常時sudoで起動することや、jtopのクロック/ファン制御を初期設定の代わりにはしません。

## 7. 任意：Dockerの稼働を確認する

実機ではDockerサービスがactive/runningで、containerdとNVIDIA Container Runtimeも導入されていました。これはサービスの稼働確認で、全コンテナやGPUコンテナの動作保証ではありません。

```bash
systemctl status docker --no-pager
sudo docker version
sudo docker ps
```

Dockerを使わなければ追加導入は不要です。未導入で必要な場合だけ、OSのdocker.io候補を確認して導入します（下記は推奨例・未検証）。inventoryの同名dockerパッケージをDocker Engineとして選ばず、ここではUbuntuのdocker.ioを使います。

```bash
apt-cache policy docker.io
sudo apt install --no-upgrade docker.io
sudo systemctl enable --now docker
```

GPUコンテナにはJetPack対応のNVIDIA runtimeとL4T対応イメージも必要です。[JetPack公式案内](https://developer.nvidia.com/embedded/jetpack-sdk-461) を参照し、PC向けDocker/NVIDIA driver手順を混ぜないでください。一般ユーザーをdockerグループへ追加する手順は必須にせず、上の例はsudoで確認します。

## 8. 基本環境ができたらプロジェクトへ

SSHでログインでき、Python/Git/標準コンパイラ、nvcc、必要なPython importが使えれば基本環境は準備できています。CUDA演算、LLM推論、カメラ撮影の実行確認は、各プロジェクトの手順で行います。

- [llama.cpp](../llama-cpp/README.md)：GCC8.4、CMake3.28.6、固定コミットとNano用patch。
- [PS4 Eye](../ps4-eye/README.md)：Flask、PyUSB、V4L2、firmwareローダーと自作コード。

### llama.cppを使うときだけ：GCC8.4とOpenSSL開発用ヘッダ

標準GCC7.5を置き換えず、別コマンドのgcc-8/g++-8を入れます。過去の版は以下のとおりで、既に同版が使えればこの導入は不要です。

```bash
apt-cache policy gcc-8 g++-8 libssl-dev
sudo apt install --no-install-recommends --no-upgrade \
  gcc-8=8.4.0-1ubuntu1~18.04 g++-8=8.4.0-1ubuntu1~18.04 \
  libssl-dev=1.1.1-1ubuntu2.1~18.04.23
gcc-8 --version
g++-8 --version
```

### llama.cppを使うときだけ：CMake3.28.6

Nano側で [Kitware公式v3.28.6](https://github.com/Kitware/CMake/releases/tag/v3.28.6) の**Linux aarch64版**を取得します。Mac用バイナリとは異なります。以下のarchiveは過去環境のものと公開checksumが一致しています。

```bash
mkdir -p ~/opt ~/Downloads
cd ~/Downloads
wget https://github.com/Kitware/CMake/releases/download/v3.28.6/cmake-3.28.6-linux-aarch64.tar.gz
echo '7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7  cmake-3.28.6-linux-aarch64.tar.gz' | sha256sum -c -
tar -xzf cmake-3.28.6-linux-aarch64.tar.gz -C ~/opt
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

既に同じ場所の3.28.6が使えれば再展開は不要です。以降は各記事の絶対パス指定を使い、システムのCMakeやupdate-alternativesを変更しません。固定版が配布先に無い場合は別版へ自動置換せず、apt候補または元の配布物を確認します。
