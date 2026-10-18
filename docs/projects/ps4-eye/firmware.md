# firmwareをロードし、映像デバイスを確認する

## 概要・背景

USBに見えるデバイスが、そのまま映像取得可能なカメラとは限りません。保存loaderは初期状態のUSBデバイスへfirmwareを送り、再起動後の別product IDを待つ仕組みです。その後にV4L2のvideoノードを確認します。

上流loaderはPythonのPyUSBでUSB control transferを送り、firmwareを512byteずつ転送します。READMEにはV1/V2の選択説明がありますが、保存コードは選択入力を持たず`firmware_V2.bin`固定です。実機型番は追加確認が必要です。

## 環境と前提

[再構築の共通変数](../../getting-started.md)、元カメラbundle、非公開のfirmwareを用意します。ライセンス未確認のfirmwareをこのrepoへ追加してはいけません。モジュールはJetPack/L4Tに合う標準カーネルのものを使い、独自UVCドライバを作った証拠はありません。

## ドライバとライブラリ

以下は初期化後の将来手順です。今回はロードやインストールを実行していません。

```bash
uname -r
modinfo uvcvideo
apt-cache policy libopencv python3-numpy python3-flask python3-usb v4l-utils libusb-1.0-0-dev
sudo apt-get install --no-install-recommends \
  libopencv=4.1.1-2-gd5a58aa75 python3-numpy=1:1.13.3-2ubuntu1 \
  python3-flask=0.12.2-3ubuntu0.1 python3-usb=1.0.0-1 \
  v4l-utils=1.14.2-1 libusb-1.0-0-dev=2:1.0.21-2
sudo modprobe uvcvideo
python3 -B -c 'import cv2,numpy,flask,usb; print(cv2.__version__,numpy.__version__,flask.__version__,usb.__version__); print(cv2.getBuildInformation())'
```

成功条件は対応モジュールと依存版の一致、cv2でV4L2がYESであることです。元のkernel configはUVC=m、現在cv2のbuild情報はV4L2/FFmpegがYES、GStreamer1.14.5でした。失敗時はカーネルとmoduleの対応、同版パッケージの提供元、Python ABIを確認します。最新pipへの置換で解決したことにはしません。

## firmwareを非公開に配置

```bash
export CAMERA_UPSTREAM="$LAB_WORK/ps4-eye-upstream"
test ! -e "$CAMERA_UPSTREAM" || exit 1
git clone "$BACKUP/repos/ps4-camera/repository.bundle" "$CAMERA_UPSTREAM"
git -C "$CAMERA_UPSTREAM" checkout --detach 4180061a1afd109a9204557f256d341c5850c124
cd "$CAMERA_UPSTREAM/Firmware_loader"
printf '%s  %s\n' 141454ec1e57a5d0f400b4a345aefb37a7b8178eb9bf9abc25187c27f34a1da4 firmware_V2.bin | sha256sum -c -
```

clone先は公開repoの外です。firmwareは64,036bytesで、元bundleのblobと実機ファイルは同hashでした。hashが違えばロードせず、ベースcommit/ファイルの取り違えを確認します。

## ロードとUSB確認（未検証）

型番と使用条件が確認できた後だけ実施します。loaderは相対パスでfirmwareを読むため、上で移動したディレクトリから起動します。

```bash
sudo python3 ps4eye_init.py
lsusb
lsusb -t
v4l2-ctl --list-devices
```

保存コードは`05a9:0580`を未初期化として扱い、既に`058a`ならV1、`058b`ならV2初期化済みとして終了します。再列挙とvideoノード生成を実際に確認してください。loaderは例外を広く捕捉して成功風メッセージを表示するため、その文だけでは成功判定できません。

## V4L2のノードと設定を調べる

```bash
export PS4_VIDEO=/dev/videoX
# 列挙結果から実ノードを指定してから実行する。
v4l2-ctl -d "$PS4_VIDEO" --all
v4l2-ctl -d "$PS4_VIDEO" --list-formats-ext
v4l2-ctl -d "$PS4_VIDEO" --list-ctrls-menus
```

成功条件は映像ノード、対応format/解像度/FPSを確認できることです。まだ映像取得成功ではありません。元の露光やUSB quirks値は未収集で、固定値を創作しません。ノード番号は接続順で変わり得るため、独自コードのindex0と照合します。

## 未検証事項と設定の扱い

今回の編集は既存資料だけを使っています。USB認識の過去記録をfirmwareロード/撮影の成功と読み替えません。PS4自動ロード設定は見つかっておらず、一般NVIDIA udevルールの転載や無条件上書きは行いません。撮影側の次の工程は [撮影と配信](capture.md) です。

## 参照資料

- [出典S5・S6](../../../reference/sources.md)、[版・firmware識別子](../../../reference/environment-versions.md)
- 上流loaderの保存commitは [Git履歴](../../../reference/details/git-history.md) に記録
