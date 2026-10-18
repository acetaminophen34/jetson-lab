# Nanoの基本開発環境とCUDAを確認する

[SSH接続](nano.md) の続きです。以下はすべてNano側で実行します。

記載したバージョンは実機の導入済み環境に基づきます。初期化後の再構築は未検証です。

## 1. OSとaptリポジトリを確認する

Ubuntu18.04・L4T32.7.1・aarch64を確認し、パッケージ一覧を更新します。

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

[Ubuntu Portsのbionic配布情報](https://ports.ubuntu.com/ubuntu-ports/dists/bionic/Release) と照合してください。JetPackとの互換性を保つため、Ubuntuのメジャーアップグレードは行いません。

## 2. 基本パッケージは不足分だけ入れる

Python、Git、標準GCC/CMakeを確認します。

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

不足している場合だけ導入します。`--no-upgrade` で導入済みパッケージの更新を抑えます。

```bash
sudo apt install --no-install-recommends --no-upgrade \
  build-essential git curl wget ca-certificates \
  python3 python3-pip python3-dev cmake
```

Python3.6を使うため、pipは無条件に最新版へ更新しないでください。

## 3. 使用したライブラリとバージョン

[JetPack4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461) はL4T・GPUドライバ・開発ライブラリをまとめたリリースです。実機では次の構成を使っていました。

| 区分 | 構成・過去の版 | 役割・分かっていること |
|---|---|---|
| OS/JetPack標準提供 | nvidia-l4t-core 32.7.1-20220219090432、kernel4.9.253-tegra | カーネル・Jetsonドライバ。Ubuntu18.04.6上で確認 |
| JetPack標準提供 | CUDA toolkit10.2.460-1、nvcc10.2.300 | GPU開発・実行環境。数値は別種類の版 |
| JetPack標準提供 | cuDNN8.2.1.32-1+cuda10.2 | ニューラルネットワークの演算ライブラリ |
| JetPack標準提供 | TensorRT8.2.1.8-1+cuda10.2 | 推論の最適化/runtime。Python表示8.2.1.8 |
| JetPack標準提供 | OpenCV4.1.1、libopencv/libopencv-python=4.1.1-2-gd5a58aa75 | 画像処理 |
| 後から追加したソフト/個別利用 | jetson-stats4.3.2、GCC/G++8.4.0、CMake3.28.6 | jtopとLLM向けツール |
| 後から追加した依存 | python3-usb1.0.0-1 | PS4 Eyeでusb不足を解消した作業履歴あり |
| 導入経緯不明 | build-essential、Git、標準CMake、pip、openssh-server | 導入済み |
| 導入経緯不明・稼働確認あり | docker.io20.10.7-0ubuntu5~18.04.3、nvidia-docker2 2.8.0-1 | Dockerサービス稼働済み |

GCC8・個別CMakeとカメラ固有依存は、各プロジェクトで必要になった段階で導入します。

## 4. CUDA・cuDNN・TensorRT・OpenCVを確認する

版とPython importを確認します。nvidia-jetpackが無くても、個々のライブラリが導入済みなら再インストールは不要です。

```bash
dpkg-query -W nvidia-l4t-core nvidia-jetpack cuda-toolkit-10-2 \
  libcudnn8 tensorrt libopencv libopencv-python python3-libnvinfer
/usr/local/cuda-10.2/bin/nvcc --version
python3 -c 'import cv2; print("OpenCV", cv2.__version__)'
python3 -c 'import tensorrt; print("TensorRT", tensorrt.__version__)'
```

使用環境の表示はnvcc10.2.300、OpenCV4.1.1、TensorRT8.2.1.8でした。cuDNNはdpkgの表示で確認します。

### SDKの構成要素が不足している場合だけ

[JetPack4.6.1公式導入案内](https://developer.nvidia.com/embedded/jetpack-sdk-461) に沿って、L4T32.7.1用の候補版を確認します。以下は不足時の導入例です。

```bash
apt-cache policy nvidia-jetpack cuda-toolkit-10-2 libcudnn8 tensorrt libopencv
sudo apt install --no-upgrade nvidia-jetpack=4.6.1-b110
```

4.6.1-b110が見つからない場合は、配布先を確認してください。cv2だけ無い場合はlibopencv-python、TensorRTのPythonだけ無い場合はpython3-libnvinferを確認します。

### nvccだけが見つからない場合

絶対パスのnvccが動くなら、PATHを設定します。

```bash
export PATH=/usr/local/cuda-10.2/bin:$PATH
nvcc --version
```

動作したら、同じ設定がないことを確認して~/.bashrcへ追記します。

```bash
printf '%s\n' 'export PATH=/usr/local/cuda-10.2/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

## 5. tegrastatsで状態を見る

NVIDIA標準の [tegrastats](https://docs.nvidia.com/jetson/archives/l4t-archived/l4t-3276/Tegra%20Linux%20Driver%20Package%20Development%20Guide/AppendixTegraStats.html) でRAM、CPU/GPU利用率、温度等を表示します。Ctrl+Cで表示を終了します。

```bash
sudo tegrastats --interval 1000
```

1秒ごとに状態が表示されます。

## 6. 任意：jetson-stats / jtopを使う

[jetson-stats](https://rnext.it/jetson_stats/) のjtopで、負荷や温度を一覧表示できます。実機では4.3.2を使っていました（AGPL-3.0）。

```bash
python3 -m pip show jetson-stats
jtop
```

未導入なら [4.3.2](https://pypi.org/project/jetson-stats/4.3.2/) を指定して導入します。

```bash
sudo -H python3 -m pip install jetson-stats==4.3.2
```

インストール後はSSHへ接続し直します。当時もjtop.serviceへアクセスできず、再ログイン／再起動後に使えるようになりました。

```bash
# NanoのSSHセッション
exit
```

Macで `ssh <username>@<jetson-ip>` により再接続した後、Nano側で実行します。

```bash
jtop
```

### jtop.serviceへ接続できないとき

[公式の対処](https://rnext.it/jetson_stats/troubleshooting.html) を参考に、サービス状態とログを確認します。

```bash
systemctl status jtop.service --no-pager
journalctl -u jtop.service -n 30 --no-pager
```

停止していれば `sudo systemctl restart jtop.service` で再始動します。再ログインでも直らなければ、作業を保存して `sudo reboot` を試します。

## 7. 任意：Dockerの稼働を確認する

実機ではDockerが稼働しており、containerdとNVIDIA Container Runtimeも導入されていました。

```bash
systemctl status docker --no-pager
sudo docker version
sudo docker ps
```

未導入で使いたい場合は、Ubuntuのdocker.ioを導入します。

```bash
apt-cache policy docker.io
sudo apt install --no-upgrade docker.io
sudo systemctl enable --now docker
```

GPUコンテナにはJetPack対応のNVIDIA runtimeとL4T対応イメージが必要です。[JetPack公式案内](https://developer.nvidia.com/embedded/jetpack-sdk-461) を参照してください。

## 8. 基本環境ができたらプロジェクトへ

基本環境ができたら、使うプロジェクトへ進みます。

- [llama.cpp](../llama-cpp/README.md)：GCC8.4、CMake3.28.6、固定コミットとNano用patch。
- [PS4 Eye](../ps4-eye/README.md)：Flask、PyUSB、V4L2、firmwareローダーと自作コード。

### llama.cppを使うときだけ：GCC8.4とOpenSSL開発用ヘッダ

標準GCC7.5とは別にgcc-8/g++-8を導入します。同版が入っていれば不要です。

```bash
apt-cache policy gcc-8 g++-8 libssl-dev
sudo apt install --no-install-recommends --no-upgrade \
  gcc-8=8.4.0-1ubuntu1~18.04 g++-8=8.4.0-1ubuntu1~18.04 \
  libssl-dev=1.1.1-1ubuntu2.1~18.04.23
gcc-8 --version
g++-8 --version
```

### llama.cppを使うときだけ：CMake3.28.6

[Kitware公式v3.28.6](https://github.com/Kitware/CMake/releases/tag/v3.28.6) のLinux aarch64版をNanoへ展開します。

```bash
mkdir -p ~/opt ~/Downloads
cd ~/Downloads
wget https://github.com/Kitware/CMake/releases/download/v3.28.6/cmake-3.28.6-linux-aarch64.tar.gz
echo '7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7  cmake-3.28.6-linux-aarch64.tar.gz' | sha256sum -c -
tar -xzf cmake-3.28.6-linux-aarch64.tar.gz -C ~/opt
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

以降は上記のパスでCMakeを呼び出します。システム標準のCMakeはそのまま残します。
