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

有線LANまたはWi-FiでMacと同じネットワークへ接続し、NanoのIPを確認します。

```bash
hostname -I
ip route
```

## 5. Nano：SSHを有効にする

openssh-serverが入っているか確認し、無い場合だけ導入します。

```bash
dpkg-query -W openssh-server
```

```bash
sudo apt update
sudo apt install --no-upgrade openssh-server
```

SSHを起動し、active (running)になっていることを確認します。

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
hostname -I
```

## 6. Mac：SSHで接続する

初回設定のユーザー名と、Nanoで確認したIPを指定します。

```text
ssh <username>@<jetson-ip>
```

実機の例です。192.168.100.6は固定の初期アドレスではありません。

```bash
ssh a62ss@192.168.100.6
```

Ubuntuのパスワードでログインしたら、[基本環境](packages.md) の設定へ進みます。

## 7. ディスプレイなしで使う

SSH接続を確認したらNanoを終了し、電源を外してディスプレイ・キーボード・マウスを外します。LANと電源を接続して起動し、Macから再接続します。

```bash
# Nano側
sudo poweroff
```
