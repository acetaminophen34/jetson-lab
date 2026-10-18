# PS4 Eyeで撮影・配信する

firmwareロード、OpenCVでの画像取得・保存、Safariへの配信、人物と背景の相対視差表示まで動作しました。

## 1. ライブラリを入れる

Python3.6.9、OpenCV4.1.1、NumPy1.13.3、Flask0.12.2、PyUSB1.0.0を使います。

```bash
sudo apt-get install --no-install-recommends \
  libopencv=4.1.1-2-gd5a58aa75 python3-numpy=1:1.13.3-2ubuntu1 \
  python3-flask=0.12.2-3ubuntu0.1 python3-usb=1.0.0-1 \
  v4l-utils=1.14.2-1 libusb-1.0-0-dev=2:1.0.21-2
python3 -c 'import cv2,numpy,flask,usb; print(cv2.__version__,numpy.__version__,flask.__version__,usb.__version__)'
```

## 2. ローダーを取得する

[sieuwe1のプロジェクト](https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV) を使います。firmwareは同梱されていますが、配布ライセンスは不明のためこのrepoへは含めません。

```bash
mkdir -p ~/jetson-work
cd ~/jetson-work
git clone https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV.git ps4-eye-upstream
cd ps4-eye-upstream
git checkout 4180061a1afd109a9204557f256d341c5850c124
cd Firmware_loader
echo '141454ec1e57a5d0f400b4a345aefb37a7b8178eb9bf9abc25187c27f34a1da4  firmware_V2.bin' | sha256sum -c -
```

## 3. firmwareをロードする

Firmware_loader内で実行します。動作時はUSB IDが05a9:0580から05a9:058aへ変わりました。

```bash
sudo modprobe uvcvideo
cd ~/jetson-work/ps4-eye-upstream/Firmware_loader
sudo python3 ps4eye_init.py
```

保存ローダーはfirmware_V2.bin固定ですが、058aはV1扱いのIDです。使うカメラとfirmwareの適合を確認してください。

## 4. USB・V4L2を確認する

動作時は `/dev/video0` と次のYUYV対応モードが認識されました。

```bash
lsusb
lsusb -t
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video0 --list-formats-ext
v4l2-ctl -d /dev/video0 --all
v4l2-ctl -d /dev/video0 --list-ctrls-menus
```

| 解像度 | 対応FPS |
|---|---:|
| 3448×808 | 60 |
| 1748×408 | 120 |
| 898×200 | 240 |

## 5. 自作コードを配置する

6本を作業先へコピーします。互換patchはFlaskのsnapshot引数、Python3.6のunlink、校正ファイルのホームパスを修正する互換案です（未検証）。

```bash
mkdir ~/jetson-work/ps4-eye-custom
cp ~/Projects/jetson-lab/ps4-eye/scripts/*.py ~/jetson-work/ps4-eye-custom/
cd ~/jetson-work/ps4-eye-custom
git apply ~/Projects/jetson-lab/ps4-eye/patches/ps4-stream-flask012.patch
git apply ~/Projects/jetson-lab/ps4-eye/patches/ps4-calib-python36.patch
git apply ~/Projects/jetson-lab/ps4-eye/patches/depth-stream-home-path.patch
```

| コード | 用途 |
|---|---|
| [ps4_stream.py](scripts/ps4_stream.py) | RGB配信、ゲイン調整、snapshot |
| [ps4_calib_capture.py](scripts/ps4_calib_capture.py) | 左右校正画像を保存 |
| [ps4_calibrate.py](scripts/ps4_calibrate.py) | 画像から校正NPZを計算 |
| [ps4_depth_stream.py](scripts/ps4_depth_stream.py) | 校正済み深度配信 |
| [ps4_depth.py](scripts/ps4_depth.py) | 試作：未校正の視差表示 |
| [ps4_depth_test.py](scripts/ps4_depth_test.py) | 試作：左右順の比較 |

## 6. RGB配信

起動後、MacのSafariで `http://<jetson-ip>:5000/` を開きます。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_stream.py
```

| 設定 | 値 |
|---|---|
| 入力 | index0、CAP_V4L2、YUYV、3448×808 |
| RGB | 30fps要求、buffer2、ゲイン初期値各1.0 |
| 校正撮影・深度 | 15fps要求、配信/校正はbuffer1 |
| Camera A | frame[0:800, 48:1328] → 1280×800 |
| Camera B | frame[0:800, 1328:2608] → 1280×800 |

左右の切り出し・向き・色表示を修正して配信できました。終了はCtrl+C。別のカメラ取得コードとは同時起動しません。配信は認証なしの0.0.0.0待受です。

## 7. 校正・深度処理

[校正・距離計算](calibration.md) へ進みます。

## 起きたエラー

| エラー | 対処 |
|---|---|
| No module named usb | python3-usbを導入（上のapt installに含む） |
| COLORMAP_TURBOが使えない | COLORMAP_JETへ変更。深度コードに反映済み |
