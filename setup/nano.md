# Jetson Nano 4GB：SDカードからSSH接続まで

対象：Jetson Nano 4GB Developer Kit、JetPack4.6.1。

初回設定はディスプレイ・キーボード・マウスを接続して行い、その後MacからSSHで操作しました。

## 1. 用意するもの

Mac、カードリーダー、32GB以上のUHS-1 microSD、HDMI/DisplayPortディスプレイ、USBキーボード・マウス、電源、LANケーブルを用意します。Wi-Fiを使う場合は対応する無線LAN機器も必要です。

## 2. Mac：JetPack4.6.1のイメージを取得する

[JetPack4.6.1公式ページ](https://developer.nvidia.com/embedded/jetpack-sdk-461) の **Jetson Nano Developer Kit** 向けSDイメージをブラウザで保存します。ターミナルから取得する場合は次のコマンドを使います。

```bash
mkdir -p ~/Downloads
cd ~/Downloads
curl -fL --retry 3 -o jetson-nano-jp461-sd-card-image.zip \
  https://developer.nvidia.com/embedded/l4t/r32_release_v7.1/jp_4.6.1_b110_sd_card/jeston_nano/jetson-nano-jp461-sd-card-image.zip
```

### Mac：チェックサムとZIPを確認する

SHA256とZIPの破損を確認します。公式のSHA256期待値は未確認です。

```bash
cd ~/Downloads
shasum -a 256 jetson-nano-jp461-sd-card-image.zip
unzip -t jetson-nano-jp461-sd-card-image.zip
```

`unzip -t` がエラーなく終了すれば、ZIP内部の整合性は確認できています。SHA256は信頼できる配布元の値と照合してください。

## 3. Mac：balenaEtcherでmicroSDへ書く

[balenaEtcher公式サイト](https://etcher.balena.io/) からMacに合う版を取得し、インストールします。[NVIDIA公式ガイド](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit) に沿って書き込みます。

1. microSDをMacへ接続し、Etcherで **Flash from file** → 取得したZIPを選ぶ。
2. **Select target** でmicroSDの製品名と容量を確認する。**対象ドライブは全消去されるため、Mac内蔵ディスクや別のバックアップドライブを選ばない。**
3. **Flash!** を実行し、Macの管理者認証が求められたら入力する。
4. 書き込み・検証の完了を待ち、安全に取り出す。Macが「読み取れない」と表示しても初期化しない。

対象が分からない場合は、microSDの挿入前後で次の一覧を比較します。

```bash
diskutil list external
```

## 4. Nano：周辺機器を接続して起動する

電源を外した状態で、microSDをNanoモジュール側のスロットへ挿し、ディスプレイ、USBキーボード・マウス、LANを接続してから給電します。キーボード・マウスはUSB Type-Aへ接続します。

Micro-USB給電には5V・2A以上の電源を使います。DCジャックを使う場合は適合する5V・4A電源とJ48設定を [4GB開発キットのユーザーガイド](https://developer.download.nvidia.com/embedded/L4T/r32-3-1_Release_v1.0/Jetson_Nano_Developer_Kit_User_Guide.pdf) で確認し、ジャンパー変更は電源を外して行います。

GPU起動時に電源容量不足で落ちたため、ACアダプタへ切り替えるまではCPUのみで運用していました。

## 5. Nanoの画面：Ubuntuの初回設定を完了する

画面の案内に従ってUbuntuの初期設定を済ませます。ここではユーザー名を `a62ss` として説明します。

APPパーティションは、通常は提示される最大容量を選びます。デスクトップが起動したら、ストレージとメモリを確認します。

```bash
whoami
hostname
lsblk
df -h /
free -h
```

使用した実機では、rootがmmcblk0p1、媒体29.7G、RAM約3.9G、zram4個×495.5MiBでした。

### Nanoの画面：ネットワークを接続する

有線LANまたはWi-FiでMacと同じネットワークへ接続し、NanoのIPアドレスを確認します。

```bash
hostname -I
ip route
```

IPが複数ある場合は、有線LANまたはWi-Fiのアドレスを使います。

## 6. Nano：SSHサーバーを有効にする

openssh-serverの有無を確認します。

```bash
dpkg-query -W openssh-server
```

**未導入の場合だけ：**

```bash
sudo apt update
sudo apt install --no-upgrade openssh-server
```

SSHを起動時にも有効にし、現在のIPを表示します。`status` がactive (running)ならサーバーが動いています（表示を閉じるときはq）。

```bash
sudo systemctl enable --now ssh
sudo systemctl status ssh
hostname -I
```

## 7. Mac：SSHでログインする

Macのターミナルで、ユーザー名とNanoのIPを指定します。

```text
ssh <username>@<jetson-ip>
```

**実機で使用した接続例：**

```bash
ssh a62ss@192.168.100.6
```

192.168.100.6は実機の例です。自分のNanoで確認したIPに置き換え、Ubuntuで設定したパスワードを入力します。

初回のホスト鍵確認では、必要に応じてNano側で公開鍵の指紋を表示し、Macの表示と照合してから承認します。

```bash
# Nano側：MacでED25519鍵が提示された場合
ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

ログイン後、Macから開いたSSHターミナルでNanoのユーザー名と機種を確認します。

```bash
whoami
hostname
uname -m
```

接続できたら、以降の [基本パッケージ・CUDA確認](packages.md) はSSHから進めます。

### ディスプレイなしの運用へ移る

SSHで接続できたらNanoを終了し、電源を外してディスプレイ・キーボード・マウスを外します。LANと電源をつなぎ直して起動すれば、以降はMacから操作できます。

```bash
# Nano側
sudo poweroff
```

Macから同じ形式のsshで再接続します。接続できなければルーターのDHCP一覧、または一時的にNanoの画面を使って新しいIPを確認します。

## 接続できないとき

| 症状 | 確認すること |
|---|---|
| Connection refused | Nano側でsystemctl status ssh。サービス未導入・停止やIPの取り違えを確認 |
| タイムアウト | 同じLANか、IP、LANケーブル、Wi-Fiの端末間通信制限を確認。ファイアウォールを使う場合はLAN内のSSHを許可 |
| Permission denied | 初回設定のユーザー名とパスワードを確認 |
| 初期化後にホスト鍵変更警告 | 再初期化した同じ機器かを確認して鍵指紋を照合。警告を無条件に無視しない |

次へ：[基本開発環境、CUDA、jtop、Docker](packages.md)。
