# Jetson Nano 4GB：SDカードからSSH接続まで

対象は **Jetson Nano 4GB Developer KitとJetPack4.6.1** です。Nano 2GB、Orin Nano、TX2、eMMC搭載モジュールや他社キャリア用の手順とは分けてください。

実際の初回設定はディスプレイ・キーボード・マウスを接続して行いました。以下はその方法に沿った一般向け手順で、当時の操作履歴がない部分は推奨手順として示します。今回は書き込み・インストール・実機の再検証を行っていません。

## 1. 用意するもの

Mac、カードリーダー、microSD（公式最小目安32GB UHS-1）、HDMI/DisplayPortディスプレイ、USBキーボード・マウス、適合電源を用意します。ネットワークはまず有線LANを使うと簡単です。Wi-Fiを使う場合は対応する無線LAN機器を別途用意します。

## 2. Mac：JetPack4.6.1のイメージを取得する

[JetPack4.6.1公式ページ](https://developer.nvidia.com/embedded/jetpack-sdk-461) の **Jetson Nano Developer Kit** 向けSDイメージをブラウザで保存します。Macのターミナルからなら、次の公式URLで取得できます（URL内のjeston_nanoは配布元の表記のままです）。

```bash
mkdir -p ~/Downloads
cd ~/Downloads
curl -fL --retry 3 -o jetson-nano-jp461-sd-card-image.zip \
  https://developer.nvidia.com/embedded/l4t/r32_release_v7.1/jp_4.6.1_b110_sd_card/jeston_nano/jetson-nano-jp461-sd-card-image.zip
```

### Mac：チェックサムとZIPを確認する

SHA256を計算し、配布元など信頼できる経路で得た**同じZIPの期待値**があれば照合します。この記事ではNVIDIA公式の期待SHA256を確認できていないため、値や「一致済み」という結果は掲載しません。

```bash
cd ~/Downloads
shasum -a 256 jetson-nano-jp461-sd-card-image.zip
unzip -t jetson-nano-jp461-sd-card-image.zip
```

`unzip -t` がエラーなしならZIP内部の整合性を確認できますが、SHA256の表示だけでは配布元との同一性・真正性を確認したことにはなりません。元実機に書き込んだイメージのhashも不明です。

## 3. Mac：balenaEtcherでmicroSDへ書く

[balenaEtcher公式サイト](https://etcher.balena.io/) からMacに合う版を取得し、インストールします。書き込みの一般的な流れは [NVIDIA公式ガイド](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit) にもあります。今回のEtcher操作は推奨手順で、当時使ったアプリの版は不明です。

1. microSDをMacへ接続し、Etcherで **Flash from file** → 取得したZIPを選ぶ。
2. **Select target** でmicroSDの製品名と容量を確認する。**対象ドライブは全消去されるため、Mac内蔵ディスクや別のバックアップドライブを選ばない。**
3. **Flash!** を実行し、Macの管理者認証が求められたら入力する。
4. 書き込み・検証の完了を待ち、安全に取り出す。Macが「読み取れない」と表示しても初期化しない。

迷う場合は不要な外付けドライブを外し、挿入前後の一覧でmicroSDを特定します。このコマンド自体は書き込みを行いません。

```bash
diskutil list external
```

## 4. Nano：周辺機器を接続して起動する

電源を外した状態で、microSDをNanoモジュール側のスロットへ挿し、ディスプレイ、USBキーボード・マウス、LANを接続してから給電します。USB Type-Aは周辺機器用で、MacのUSBポートからの給電だけで安定動作するとは考えないでください。

4GB開発キットのMicro-USB給電は5V・2Aを満たす良質な電源とケーブルが基本です。DCジャックを使う場合は適合する5V・4A電源とJ48設定を [4GB開発キットのユーザーガイド](https://developer.download.nvidia.com/embedded/L4T/r32-3-1_Release_v1.0/Jetson_Nano_Developer_Kit_User_Guide.pdf) で確認し、ジャンパー変更は電源を外して行います。Nano 2GBのUSB-C給電方法とは異なります。

過去のGPU起動では電源容量不足で落ちたとのユーザー申告があります。GPUやUSBカメラを使う前に電源条件を整え、この初期設定ではクロック最大化・nvpmodel変更・GPU負荷試験は行いません。

## 5. Nanoの画面：Ubuntuの初回設定を完了する

画面の案内でライセンスを確認し、言語・キーボード、ユーザー名・パスワード・コンピューター名を設定します。**実際に使用したユーザー名はa62ss**ですが、読者は自分の名前を選び、実パスワードを記事やGitへ保存しないでください。ホスト名・言語等の当時の選択値は不明で、タイムゾーンを変更する操作は本手順に含めません。

APPはUbuntuのルート領域です。特別な用途がなければ初回画面で提示される最大容量を選び、デスクトップが起動したら空き容量を確認します（当時その選択をしたかは不明です）。

```bash
whoami
hostname
lsblk
df -h /
free -h
```

過去の実測はrootがmmcblk0p1、媒体表示29.7G、RAM約3.9G、zram4個×495.5MiBでした。これは観測値であり、全読者に同じ媒体容量やswap設定を要求するものではありません。

### Nanoの画面：ネットワークを接続する

有線LANを接続するか、GUIのネットワーク設定で対応Wi-Fiを設定し、Macと同じLANに参加させます。IPと経路が表示され、ブラウザでWebページを開けることを確認します。

```bash
hostname -I
ip route
```

`hostname -I` が複数のIPを返す場合、Macから到達できる有線LAN/Wi-Fi側のIPを選びます。Dockerブリッジ等のIPと取り違えないでください。

## 6. Nano：SSHサーバーを有効にする

Nanoのターミナルで実行します。過去のinventoryにはopenssh-server導入済みの記録がありますが、初期化後に無ければ次のパッケージ導入だけを先に行います。

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

Macのターミナルで、初回設定のユーザー名とNanoのIPを指定します。次の `<username>` と `<jetson-ip>` は置換用の記号です。

```text
ssh <username>@<jetson-ip>
```

**実機で使用した接続例：**

```bash
ssh a62ss@192.168.100.6
```

192.168.100.6は現在の実機例で、固定の初期アドレスではありません。DHCPや接続先ネットワークにより変わります。パスワード認証を使っており、入力中に文字が表示されないのは正常です。

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

ユーザー名が自分のもの、archがaarch64なら接続確認は完了です。以降の [基本パッケージ・CUDA確認](packages.md) は、このSSH接続から行えます。

### ディスプレイなしの運用へ移る

SSH接続を確認できたら、画面・キーボード・マウスは常時接続しなくても構いません。接続を外して再起動を確認する場合は、Nanoを正常終了し、電源を外して周辺機器を外し、LANと適合電源を残して再度起動します。

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
| Permission denied | 初回設定のユーザー名とパスワードを確認。実パスワードを共有しない |
| 初期化後にホスト鍵変更警告 | 再初期化した同じ機器かを確認して鍵指紋を照合。警告を無条件に無視しない |

次へ：[基本開発環境、CUDA、jtop、Docker](packages.md)。
