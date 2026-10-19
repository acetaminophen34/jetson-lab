# PS4 Cameraで顔追跡・距離表示をする

[stereo_vision.py](scripts/stereo_vision.py) で左右の映像から距離を計算し、顔を追跡してブラウザへ配信します。Nanoで使っていた最新版です。TX2へ移す場合も同じコードと、同じカメラの校正データを使います。

[作業場所の設定](../README.md#作業場所を用意する) を済ませ、以下はJetson側の同じターミナルで実行します。

## 1. 必要なライブラリを入れる

Nanoで使用した環境はPython3.6.9、OpenCV4.1.1、NumPy1.13.3、Flask0.12.2、PyUSB1.0.0です。JetPackのOpenCVと、配信・USB操作に必要なパッケージを使います。

```bash
sudo apt update
sudo apt install --no-install-recommends \
  libopencv python3-numpy python3-flask python3-usb \
  v4l-utils libusb-1.0-0-dev
python3 -c 'import cv2,numpy,flask,usb; print(cv2.__version__,numpy.__version__,flask.__version__,usb.__version__)'
```

## 2. カメラを初期化する

### Nanoで使ったローダーを取得する

[sieuwe1のローダー](https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV) を取得し、カメラへファームウェアを読み込ませます。ファームウェアは配布元に同梱されており、このリポジトリには含めていません。

```bash
mkdir -p "$JETSON_LAB/work"
cd "$JETSON_LAB/work"
git clone https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV.git ps4-eye-upstream
cd ps4-eye-upstream
git checkout 4180061a1afd109a9204557f256d341c5850c124
sudo modprobe uvcvideo
cd Firmware_loader
sudo python3 ps4eye_init.py
lsusb
```

### TX2に用意したローダーを使う

TX2では [ps4eye/ps4eye](https://github.com/ps4eye/ps4eye) のローダーと、[psxdev/luke_firmwares](https://github.com/psxdev/luke_firmwares) の `101_85C8E0_64036.bin` を使って初期化しました。既存の `~/ps4eye/python/` には、ローダーが読む名前 `firmware.bin` で配置します。

```bash
cd ~/ps4eye/python
sudo modprobe uvcvideo
sudo python3 ps4eye_init.py
lsusb
```

TX2ではUSB IDが初期化前の `05a9:0580` から `05a9:058a` へ変わっています。次に、映像入力に使うデバイスを特定します。

## 3. 映像入力のデバイスを特定する

カメラ名と `/dev/videoN` の対応を表示します。

```bash
v4l2-ctl --list-devices
ls -l /dev/video*
```

一覧に出たデバイスの対応形式を調べます。次は `/dev/video0` の例です。PS4 CameraではYUYVと下表の解像度を探します。

```bash
v4l2-ctl -d /dev/video0 --list-formats-ext
```

| 解像度 | 対応FPS |
|---|---:|
| 3448×808 | 60 |
| 1748×408 | 120 |
| 898×200 | 240 |

Nanoでは `/dev/video0` を使いました。TX2の `/dev/video0` はBG10（10-bit Bayer）を表示したため、番号を決め打ちせず、一覧の他のデバイスも同じコマンドで調べます。

## 4. 校正データを配置する

同じカメラをNanoからTX2へ移す場合は、登録済みの校正データをコピーします。

```bash
mkdir -p ~/ps4_calib
cp -i "$JETSON_LAB/ps4-eye/calibration/stereo_calibration.npz" \
  ~/ps4_calib/stereo_calibration.npz
```

別のカメラを使う場合や、解像度・切り出し・レンズ配置を変えた場合は [校正手順](calibration.md) へ進みます。

## 5. 顔検出モデルを取得する

OpenCV公式リポジトリの [ネットワーク定義](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector) と [学習済みモデル](https://github.com/opencv/opencv_3rdparty/tree/dnn_samples_face_detector_20170830) を取得します。コードが読むファイル名に合わせて `~/models/` へ保存します。モデル本体はGitへ追加しません。

```bash
mkdir -p ~/models
wget -O ~/models/deploy.prototxt \
  https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
wget -O ~/models/res10.caffemodel \
  https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
```

## 6. 起動する

作業用のコピーを作って起動します。校正データと顔検出モデルは、上の配置先から自動で読み込みます。

```bash
mkdir -p "$JETSON_LAB/work/ps4-eye-custom"
cp "$JETSON_LAB/ps4-eye/scripts/stereo_vision.py" "$JETSON_LAB/work/ps4-eye-custom/"
```

コードの入力は `cv2.VideoCapture(0, cv2.CAP_V4L2)`、つまり `/dev/video0` です。手順3で別の番号が見つかった場合は、起動前に作業用コピーのこの `0` をその番号へ合わせます。カメラを使うスクリプトは1本ずつ起動します。

```bash
cd "$JETSON_LAB/work/ps4-eye-custom"
python3 stereo_vision.py
```

MacのSafariなどで `http://<jetson-ip>:5001/` を開きます。上段は顔枠と距離を重ねた映像、下段は補正後の映像と視差の色表示です。終了はCtrl+Cです。

- `FACE: … cm`：顔中央の距離。`FACE: N/A` は距離を計算できる画素が不足、`FACE: NONE` は追跡対象なし。
- `FPS`：表示画像の更新速度。`ms`：撮影から表示画像の生成までの時間で、ブラウザへの通信時間は含まない。
- 映像だけを読むURLは `http://<jetson-ip>:5001/stream`。FlaskがMJPEG形式で配信します。

配信にログイン機能はないため、信頼できるLAN内で使います。

## 処理の流れと設定

1. **映像取得・切り出し**：V4L2でYUYV入力を取得し、OpenCVが返すBGR画像からA・Bを切り出して480×300へ縮小します。
2. **歪み補正・平行化**：校正値から補正マップを作り、左右の対応点が同じ高さになるよう変換します。画面と顔追跡の基準はCamera Bです。
3. **視差・距離**：StereoSGBMでBとAのずれを求め、校正から計算したQ行列で距離へ変換します。色表示はCOLORMAP_JETです。
4. **顔検出・追跡**：OpenCV DNNをCPUで実行し、300×300の入力から顔を検出します。検出の合間はLucas–Kanade光学フローで顔の特徴点を追跡します。複数の候補では、それまでの追跡位置に近い顔を優先します。
5. **距離表示**：顔枠の縦横それぞれ30〜70%の領域にある有効な距離を集め、10画素以上あれば中央値をcm表示します。
6. **配信**：撮影、補正・追跡、顔検出、深度計算、表示画像の生成を5つのスレッドに分けます。共有するのは最新の画像・結果で、処理待ちの画像をためずに遅れを抑えます。JPEGは更新ごとに一度生成し、Flaskから配信します。

| 設定 | コードの値 |
|---|---|
| 入力 | YUYV、3448×808、15fps要求、取得バッファ1 |
| Camera A | `frame[:800, 48:1328]`（1280×800） |
| Camera B | `frame[:800, 1328:2608]`（1280×800） |
| 処理解像度 / OpenCV内部スレッド | 480×300 / 2 |
| StereoSGBM | 視差数96、blockSize=5、uniquenessRatio=8 |
| 深度計算 / 顔検出の実行間隔 | 最短0.35秒 / 0.65秒 |
| 顔検出の信頼度 / 追跡解除 | 0.65以上 / 最後に顔を検出してから1.8秒 |
| 光学フロー | 特徴点最大60、探索窓17×17、ピラミッドmaxLevel=2 |
| 有効距離 / 距離表示に使う結果の鮮度 | 0.15m超〜5m未満 / 1.5秒未満 |
| JPEG品質 / 配信ポート | 75 / 5001 |

## 校正と旧スクリプト

校正画像の撮影・校正値の計算は [calibration.md](calibration.md) にまとめています。旧コードも残していますが、顔追跡と距離表示は `stereo_vision.py` を使います。

| コード | 用途 |
|---|---|
| [ps4_calib_capture.py](scripts/ps4_calib_capture.py) / [ps4_calibrate.py](scripts/ps4_calibrate.py) | 校正画像の撮影 / 校正データの計算 |
| [ps4_stream.py](scripts/ps4_stream.py) | カラー映像の配信・画像保存 |
| [ps4_depth_stream.py](scripts/ps4_depth_stream.py) | 旧版の深度配信 |
| [ps4_depth.py](scripts/ps4_depth.py) / [ps4_depth_test.py](scripts/ps4_depth_test.py) | 相対視差表示 / 左右順比較の試作 |
