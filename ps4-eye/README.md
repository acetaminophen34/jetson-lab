# PS4 Eyeで撮影・配信する

## 概要

PS4 EyeをUSBステレオカメラとして使い、左右RGB配信と校正済み深度処理を行うPythonプログラムです。USB認識は実機で確認済みですが、firmwareロード後の映像取得・配信・距離精度は未検証です。

## 仕組み

USB認識 → firmware転送 → USB再列挙 → UVC/V4L2 → OpenCV取得の順に準備します。左右像を切り出し、校正・整列して視差を求めると、対応点のずれから距離を推定できます。

YUYVは2画素で色差を共有するYUV4:2:2形式です。コードはYUYVを要求しますが、取得配列はBGRとして画像変換へ渡します。実際のformatとframe.shapeの確認が必要です。転送フレームの未使用領域の意味は未特定です。

### 入力と左右の切り出し

| 項目 | 独自コードに保存された値 |
|---|---|
| 取得 | index0、CAP_V4L2、YUYV、3448×808要求 |
| RGB配信 | 30fps要求、buffer2 |
| 深度/校正撮影 | 15fps要求、配信/校正はbuffer1 |
| Camera A | frame[0:800, 48:1328] → 1280×800 |
| Camera B | frame[0:800, 1328:2608] → 1280×800 |

これらは**静的確認済みの要求値**です。実FPSやformatの測定値ではありません。上流viewerは幅1264の別切り出しで、独自校正データへ無条件に混ぜられません。実ノードがindex0でなければ、取得する各コードのindexを新しいpatchとして変更・記録します。

## 構築

[Nanoの共通変数](../setup/nano.md) を設定し、Python3.6.9、OpenCV4.1.1、NumPy1.13.3、Flask0.12.2、PyUSB1.0.0を準備します。独自6本はMatplotlibをimportしません。

上流loaderの固定commitは4180061a1afd109a9204557f256d341c5850c124です。PyUSBでcontrol transferを送り、firmwareを512byteずつ転送します。説明にはV1/V2の選択がありますが、保存loaderはfirmware_V2.bin固定であり、カメラ型番の確認が必要です。

### ドライバとライブラリ

以下は初期化後の手順です。firmwareロード以降の実機動作は未検証です。

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

### firmwareを非公開に配置

```bash
export CAMERA_UPSTREAM="$LAB_WORK/ps4-eye-upstream"
test ! -e "$CAMERA_UPSTREAM" || exit 1
git clone "$BACKUP/repos/ps4-camera/repository.bundle" "$CAMERA_UPSTREAM"
git -C "$CAMERA_UPSTREAM" checkout --detach 4180061a1afd109a9204557f256d341c5850c124
cd "$CAMERA_UPSTREAM/Firmware_loader"
printf '%s  %s\n' 141454ec1e57a5d0f400b4a345aefb37a7b8178eb9bf9abc25187c27f34a1da4 firmware_V2.bin | sha256sum -c -
```

clone先は公開repoの外です。firmwareは64,036bytesで、元bundleのblobと実機ファイルは同hashでした。hashが違えばロードせず、ベースcommit/ファイルの取り違えを確認します。

### ロードとUSB確認（未検証）

型番と使用条件が確認できた後だけ実施します。loaderは相対パスでfirmwareを読むため、上で移動したディレクトリから起動します。

```bash
sudo python3 ps4eye_init.py
lsusb
lsusb -t
v4l2-ctl --list-devices
```

保存コードは`05a9:0580`を未初期化として扱い、既に`058a`ならV1、`058b`ならV2初期化済みとして終了します。再列挙とvideoノード生成を実際に確認してください。loaderは例外を広く捕捉して成功風メッセージを表示するため、その文だけでは成功判定できません。

### V4L2のノードと設定を調べる

```bash
export PS4_VIDEO=/dev/videoX
# 列挙結果から実ノードを指定してから実行する。
v4l2-ctl -d "$PS4_VIDEO" --all
v4l2-ctl -d "$PS4_VIDEO" --list-formats-ext
v4l2-ctl -d "$PS4_VIDEO" --list-ctrls-menus
```

成功条件は映像ノード、対応format/解像度/FPSを確認できることです。まだ映像取得成功ではありません。元の露光やUSB quirks値は未収集で、固定値を創作しません。ノード番号は接続順で変わり得るため、独自コードのindex0と照合します。

### 独自コードを配置する

6本はscripts/にあります。原文のロジックは維持し、深度配信の固定ユーザー名だけ公開用placeholderにしています。作業コピーを新しく作り、必要な互換patchをそこへ適用します。

```bash
export CAMERA_STAGE="$LAB_WORK/camera-custom"
test ! -e "$CAMERA_STAGE" || exit 1
mkdir -p "$CAMERA_STAGE"
cp "$LAB_ROOT/ps4-eye/scripts/"*.py "$CAMERA_STAGE/"
cd "$CAMERA_STAGE"
# 必要な互換案を作業コピーだけへ適用。リポジトリ内の原文へ適用しない。
git apply --check "$LAB_ROOT/ps4-eye/patches/ps4-stream-flask012.patch"
git apply --check "$LAB_ROOT/ps4-eye/patches/ps4-calib-python36.patch"
git apply --check "$LAB_ROOT/ps4-eye/patches/depth-stream-home-path.patch"
git apply "$LAB_ROOT/ps4-eye/patches/ps4-stream-flask012.patch"
git apply "$LAB_ROOT/ps4-eye/patches/ps4-calib-python36.patch"
git apply "$LAB_ROOT/ps4-eye/patches/depth-stream-home-path.patch"
```

互換patchは、Flask0.12.2のsend_file引数をdownload_nameからattachment_filenameへ変更する案、Python3.6で未対応のPath.unlink(missing_ok=True)を置き換える案、CALIBをPath.homeから解決する案です。静的な適用・構文確認のみで、実機適用は未検証です。コード原文に混ぜず [patches](patches/ps4-stream-flask012.patch) として置いています。

[校正データの配置](calibration.md#前提と校正資産の復元) を済ませてから実行します。

## 実行

### コードの用途

| コード | 用途 | 外部依存 | 実行方法（準備後、作業コピーで） | 入力 → 出力 | 技術記事 |
|---|---|---|---|---|---|
| [ps4_stream.py](scripts/ps4_stream.py) | 左右RGBの配信・RGBゲイン・snapshot | cv2、numpy、flask | `python3 ps4_stream.py` | V4L2 index0 → port5000、/stream、/settings、/snapshot | [撮影](README.md) |
| [ps4_depth.py](scripts/ps4_depth.py) | 未校正SGBMの1回診断 | cv2、numpy | `python3 ps4_depth.py` | index0、15フレーム → cwdのdepth_left/right/map/comparison.jpg | [深度](calibration.md) |
| [ps4_depth_test.py](scripts/ps4_depth_test.py) | 通常/左右反転の視差比較の試作 | cv2、numpy | `python3 ps4_depth_test.py` | index0 → ホームのtest_left/right/normal/swapped.jpg | [深度](calibration.md) |
| [ps4_calib_capture.py](scripts/ps4_calib_capture.py) | 両眼9×6コーナー検出と校正撮影 | cv2、flask | `python3 ps4_calib_capture.py` | index0、/capture POST → ~/ps4_calib/pairs/camA/camB PNG、port5002 | [校正](calibration.md) |
| [ps4_calibrate.py](scripts/ps4_calibrate.py) | 既存ペアから単眼/ステレオ校正 | cv2、numpy | `python3 ps4_calibrate.py` | ~/ps4_calib/pairs → NPZ、preview、RMS/基線などのstdout | [校正](calibration.md) |
| [ps4_depth_stream.py](scripts/ps4_depth_stream.py) | B基準rectify、視差・距離・overlay配信 | cv2、numpy、flask | `python3 ps4_depth_stream.py` | index0＋CALIB NPZ → port5001、compare/overlay/depth/camera | [深度](calibration.md) |

配信・校正が主な実装です。ps4_depth.pyとps4_depth_test.pyは未校正の診断・試作で、距離精度の評価には使いません。

### RGB配信を起動する

既存ファイルが無い場合だけホームへ作業コピーを配置します。各コードはホームの校正ファイルや出力先を使うため、単にcwdを変えても保存先は変わりません。

```bash
for name in ps4_stream.py ps4_depth.py ps4_depth_test.py \
            ps4_depth_stream.py ps4_calib_capture.py ps4_calibrate.py; do
  test ! -e "$HOME/$name" || exit 1
  cp "$CAMERA_STAGE/$name" "$HOME/$name"
done
python3 ~/ps4_stream.py
```

ブラウザで `http://<Nanoのアドレス>:5000/` を開きます。RGBゲインは初期値各1.0で、永続設定は未確認です。Flaskは0.0.0.0で待受け、認証は実装されていません。

確認するのはisOpened/readの成功、切り出しに十分なframe.shape、左右の正しい像、/streamの更新、/snapshotです。RGB確認後にそのプロセスを終了し、[校正と深度](calibration.md)へ進みます。複数の取得スクリプトを同時起動しません。

## トラブルシューティング

| 症状 | 確認するもの |
|---|---|
| USBに見えるがvideoが無い | 未初期化ID0580か、firmware後の再列挙、uvcvideo |
| loader成功表示でも撮れない | 広い例外捕捉があるため、実際のUSB ID・driver・V4L2を確認 |
| read失敗・範囲不足 | /dev/videoの実ノード、index0、format、frame.shape、別プロセスとの競合 |
| snapshotの引数エラー | Flask0.12用patchの適用 |
| 校正画像の保存失敗時に例外 | Python3.6用cleanup patchの適用 |
| 深度の符号や整列が不正 | [左右順・Q・縮小K](calibration.md#深度処理の順序と左右の向き) |

最後の実機記録は05a9:0580、USB5000M、vendor-specific interface、driver欄空、videoノードなしです。PS4専用udev/systemd設定や独自UVCドライバは確認できておらず、まず手動で工程を切り分けます。firmwareや校正画像はこのrepoには同梱していません。
