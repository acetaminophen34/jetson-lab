# PS4 Cameraで顔追跡・距離表示をする

左右の映像から距離を求め、顔の追跡結果とともにブラウザへ配信します。Nano/TX2で同じプログラムを使い、起動時にカメラ番号だけを選びます。

| プログラム | 視差計算 | 顔検出・追跡 |
|---|---|---|
| [stereo_vision.py](scripts/stereo_vision.py) | CPU：OpenCV StereoSGBM | OpenCV DNN CPU・Lucas–Kanade光学フロー |
| [stereo_vision_gpu.py](scripts/stereo_vision_gpu.py) | GPU：NVIDIA VPI CUDA | CPU版と同じ |

## 1. 環境と必要なパッケージ

Nano 4GBはJetPack4.6.1、TX2 8GBはJetPack4.6.6 / L4T R32.7.6、Ubuntu18.04.6を使用しました。Python3、OpenCV4.1.1、CUDA10.2の環境で進めます。

Jetson上でcloneした `jetson-lab` の直下で実行します。[setup-camera.sh](tools/setup-camera.sh) が不足パッケージの導入、顔検出モデル・校正データの配置、作業用コードへのパッチ適用をまとめて行います。

```bash
export JETSON_LAB="$PWD"
bash ps4-eye/tools/setup-camera.sh
```

GPU版も使う場合は、代わりに `--gpu` を付けます。JetPack4系のVPI Pythonパッケージも準備します。

```bash
bash ps4-eye/tools/setup-camera.sh --gpu
```

確認だけなら `--check` を使います。不足があれば対象を表示し、終了コード1で終了します。

```bash
bash ps4-eye/tools/setup-camera.sh --check
# VPIも確認する場合
bash ps4-eye/tools/setup-camera.sh --check --gpu
```

### 準備するもの

| 用途 | パッケージ・配置先 |
|---|---|
| 映像取得・画像処理 | JetPackの `libopencv`・`libopencv-python`、`python3-numpy` |
| ブラウザ配信 | `python3-flask` |
| ファームウェアローダー・デバイス確認 | `python3-usb`、`v4l-utils` |
| ソース・モデル取得 | `git`、`wget` |
| GPU視差計算（`--gpu`） | `libnvvpi1`、`python3-vpi1` |
| 作業用コード | `work/ps4-eye-custom/` |
| 校正データ | `~/ps4_calib/stereo_calibration.npz` |
| 顔検出モデル | `~/models/deploy.prototxt`、`~/models/res10.caffemodel` |

NanoではPython3.6.9、NumPy1.13.3、Flask0.12.2、PyUSB1.0.0を使用しました。インストール済みのパッケージと既存ファイルは保持します。校正データの初回配置は、登録済みデータと同じカメラを使う前提です。

### 適用するパッチ

最新版の `stereo_vision.py` と `stereo_vision_gpu.py` に追加パッチは不要です。以下は校正撮影・旧コードの作業用コピーだけに適用します。適用済みならスキップし、元の `scripts/` は変更しません。

| パッチ | 対象 | 修正内容 |
|---|---|---|
| [ps4-calib-python36.patch](patches/ps4-calib-python36.patch) | `ps4_calib_capture.py` | Python3.6で使えない `unlink(missing_ok=True)` を置き換える |
| [ps4-stream-flask012.patch](patches/ps4-stream-flask012.patch) | `ps4_stream.py` | 画像保存時の引数をFlask0.12の `attachment_filename` に合わせる |
| [depth-stream-home-path.patch](patches/depth-stream-home-path.patch) | `ps4_depth_stream.py` | 校正データの固定ユーザーパスをホームディレクトリ基準にする |

パッチを適用できない変更済みファイルがある場合は、その場で停止します。ファームウェア初期化と撮影は、このスクリプトでは実行しません。

## 2. カメラを初期化する

[ps4eye/ps4eyeのローダー](https://github.com/ps4eye/ps4eye) を取得し、TX2で使用した [ファームウェア](https://github.com/psxdev/luke_firmwares/blob/master/101_85C8E0_64036.bin) を、ローダーが読む `firmware.bin` の名前で置きます。ファームウェア本体はこのリポジトリには含めていません。

```bash
cd "$JETSON_LAB/work"
git clone https://github.com/ps4eye/ps4eye.git
cd ps4eye/python
wget -O firmware.bin \
  https://raw.githubusercontent.com/psxdev/luke_firmwares/master/101_85C8E0_64036.bin
```

カメラを接続して実行します。TX2で用意済みの `~/ps4eye/python/` を使う場合は、そこへ移動して同じ初期化コマンドを実行します。

```bash
sudo modprobe uvcvideo
sudo python3 ps4eye_init.py
lsusb
v4l2-ctl --list-devices
```

初期化するとUSB IDが `05a9:0580` から `05a9:058a` へ変わります。Nanoで以前使ったローダーは [sieuwe1版](https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV/tree/4180061a1afd109a9204557f256d341c5850c124/Firmware_loader) です。

## 3. カメラ番号を選ぶ

使用時はNanoが `/dev/video0`、TX2が `/dev/video1` でした。TX2の `/dev/video0` はOV5693（BG10形式）です。接続状態で番号が変わるため、一覧からYUYV形式のPS4 Cameraを選びます。

```bash
v4l2-ctl --list-devices
```

次の設定は、使うカメラ番号のどちらか一方だけを実行します。

```bash
# Nanoで使用した番号
CAMERA=0
```

```bash
# TX2で使用した番号
CAMERA=1
```

```bash
v4l2-ctl -d "/dev/video$CAMERA" --list-formats-ext
```

| 対応するYUYV入力 | FPS |
|---|---:|
| 3448×808 | 60 |
| 1748×408 | 120 |
| 898×200 | 240 |

プログラムでは3448×808、15fpsを要求します。

## 4. 校正データと顔検出モデルを配置する

手順1で次の場所へ配置されます。既存ファイルがあれば上書きしません。

```text
~/ps4_calib/stereo_calibration.npz
~/models/deploy.prototxt
~/models/res10.caffemodel
```

[登録済みの校正データ](calibration/stereo_calibration.npz) はNanoで使用したカメラのものです。同じカメラをTX2へ移す場合は再利用できます。別のカメラや、解像度・切り出し・レンズ配置を変える場合は [再校正](calibration.md) します。

顔検出モデルの配布元はOpenCV公式の [ネットワーク定義](https://github.com/opencv/opencv/tree/master/samples/dnn/face_detector) と [学習済みモデル](https://github.com/opencv/opencv_3rdparty/tree/dnn_samples_face_detector_20170830) です。取得URLは準備スクリプトに記載しています。

## 5. CPU版を起動する

カメラを使うプログラムは1本ずつ実行します。ソースを書き換えず、`--camera` で番号を渡します。

```bash
python3 "$JETSON_LAB/work/ps4-eye-custom/stereo_vision.py" --camera "$CAMERA"
```

MacのSafariなどで `http://<jetson-ip>:5001/` を開きます。上段は顔枠と距離、下段は補正後の映像と視差の色表示です。終了はCtrl+Cです。

- `FACE: … cm`：顔中央の有効な距離の中央値。
- `FACE: N/A`：距離に使える画素が不足。`FACE: NONE`：追跡対象なし。
- `FPS`：表示画像の更新速度。`ms`：撮影から表示画像を生成するまでの時間。
- `/stream`：MJPEG映像だけを読むURL。

配信にログイン機能はないため、信頼できるLAN内で使います。

## 6. GPU版を起動する

手順1を `--gpu` 付きで実行しておきます。

CPU版を終了してから起動します。配信URLは同じです。

```bash
python3 "$JETSON_LAB/work/ps4-eye-custom/stereo_vision_gpu.py" --camera "$CAMERA"
```

GPU版は `vpi.stereodisp()` をCUDAで実行し、`window=5`・`maxdisp=128` を使います。顔検出・追跡・距離表示はCPU版と共通で、顔検出をTensorRTへ変更する処理はありません。

## 7. CPU/GPUの性能を比較する

[benchmark_stereo.py](scripts/benchmark_stereo.py) は、`~/ps4_calib/pairs/` の最初の `camA_*.png`・`camB_*.png` を使います。同じカメラの校正NPZと、手元に保存した校正画像を配置して実行します。

```bash
python3 "$JETSON_LAB/ps4-eye/scripts/benchmark_stereo.py"
```

Nano 4GB / JetPack4.6.1、480×300、視差数64での結果です。6回のうち初回を除く5回の平均で、GPU側は結果のCPU転送まで含みます。VPI形式への入力変換は計測外です。

| 処理 | 時間 | 有効視差の画素率 | 視差の中央値 |
|---|---:|---:|---:|
| CPU StereoSGBM | 126.9ms | 62.5% | 41.50px |
| GPU VPI CUDA | 64.9ms | 75.1% | 41.12px |

続けて最大視差64・128を比較します。別の実行では、初回を除く4回の平均が64pxで47.1ms、128pxで40.8msでした。

## 動作実績と主な設定

NanoではCPU版とVPI CUDAの視差計算、TX2ではCPU/GPU版の映像配信・顔追跡・距離表示を使用しました。NanoではUSB給電時に高負荷で停止したため、GPU実行には適合するAC電源を用意します。

| 設定 | 値 |
|---|---|
| 入力 | YUYV、3448×808、15fps要求、バッファ1 |
| Camera A / B | `frame[:800, 48:1328]` / `frame[:800, 1328:2608]`、各1280×800 |
| 処理解像度 / OpenCV内部スレッド | 480×300 / 2 |
| CPUの視差 / GPUの視差 | StereoSGBM：96、blockSize=5 / VPI CUDA：128、window=5 |
| 深度計算 / 顔検出の間隔 | 最短0.35秒 / 0.65秒 |
| 顔検出 / 追跡解除 | 信頼度0.65以上 / 最後の顔検出から1.8秒 |
| 光学フロー | 特徴点最大60、探索窓17×17、maxLevel=2 |
| 距離表示 | 0.15m超〜5m未満、顔中央の縦横30〜70%から10画素以上の中央値 |
| JPEG品質 / ポート | 75 / 5001 |

撮影、補正・追跡、顔検出、深度計算、表示画像の生成を5つのスレッドに分け、最新の画像・結果だけを共有して遅れを抑えます。GPU版は同じ撮影画像の重複処理を避け、深度を10回計算するごとに処理時間を表示します。

## 校正とその他のコード

新しいカメラの [校正手順](calibration.md) と、以前の [カラー配信](scripts/ps4_stream.py)・[深度配信](scripts/ps4_depth_stream.py)・[視差の試作](scripts/ps4_depth.py)・[左右順比較](scripts/ps4_depth_test.py) も残しています。

顔検出のTensorRT変換は、`clip: 1` のパースエラー、その行を除いたコピーでもConcat・Reshape・Softmaxの互換性エラーで失敗したため、OpenCV DNN CPUを使用しています。
