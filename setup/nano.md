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

ZIPの破損を確認します。公式SHA256の期待値は不明です。

```bash
cd ~/Downloads
shasum -a 256 jetson-nano-jp461-sd-card-image.zip
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

画面の案内に従い、ユーザー名・パスワード・ホスト名を設定します。APPパーティションは通常、提示される最大容量を選びます。

```bash
whoami
hostname
lsblk
df -h /
free -h
```

有線LANまたはWi-FiでMacと同じネットワークへ接続します。

## 5. SDKが不足している場合

[JetPack4.6.1](https://developer.nvidia.com/embedded/jetpack-sdk-461) のパッケージを追加します。既にCUDA・OpenCV等が入っていれば不要です。

```bash
apt-cache policy nvidia-jetpack cuda-toolkit-10-2 libcudnn8 tensorrt libopencv
sudo apt install --no-upgrade nvidia-jetpack=4.6.1-b110
```

次へ：[共通のSSH設定・開発ツール](packages.md)。
