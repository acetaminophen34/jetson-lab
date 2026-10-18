# PS4 EyeをNanoのステレオカメラにする

## 1. PS4 Eyeカメラの概要

左右2台の映像を使い、RGB配信とステレオ深度処理を行います。**2026年10月15日にはfirmwareロード、OpenCVでの画像取得・保存、MacのSafariへのリアルタイム配信、StereoSGBMによる人物と背景の相対視差表示に成功していました。**

これはユーザーが過去のChatGPT会話から復元した当時の成功履歴です。現在の機器状態では再検証していません。保存コードと設定から整理した以下の構築手順や互換patchを、当時実行した完全なコマンド列と同一とは扱いません。校正済みの絶対距離精度は未確認です。

## 2. Linuxで動かす仕組み

USB初期状態のカメラへfirmwareを送り、再列挙後にLinux標準のuvcvideo/V4L2で映像を読みます。独自カーネルドライバを入れた記録はなく、GitHubから取得するのはPythonのfirmwareローダーです。

[上流プロジェクト](https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV) のローダーはPyUSBで512byteずつ転送します。READMEはV1/V2を説明していますが、使用コミットの実装はfirmware_V2.bin固定なのでカメラ型番を確認してください。

## 3. 必要なソフトを入れる

JetPack4.6.1のOpenCV4.1.1と、Python3.6.9・NumPy1.13.3・Flask0.12.2・PyUSB1.0.0を使います。以下の同版インストールは未検証で、同版が無ければapt-cache policyで提供元を確認してください。

```bash
sudo apt-get install --no-install-recommends \
  libopencv=4.1.1-2-gd5a58aa75 python3-numpy=1:1.13.3-2ubuntu1 \
  python3-flask=0.12.2-3ubuntu0.1 python3-usb=1.0.0-1 \
  v4l-utils=1.14.2-1 libusb-1.0-0-dev=2:1.0.21-2
python3 -c 'import cv2,numpy,flask,usb; print(cv2.__version__,numpy.__version__,flask.__version__,usb.__version__)'
```

OpenCVは [JetPackの配布版](https://developer.nvidia.com/embedded/jetpack-sdk-461)、他は [Ubuntu Ports](https://ports.ubuntu.com/ubuntu-ports/) を含むOSのapt設定から取得します。保存環境のcv2はV4L2/FFmpegがYES、GStreamer1.14.5でした。独自6本にはMatplotlibは不要です。

当時は `No module named 'usb'` でローダーが止まり、python3-usb不足を解消して先へ進みました。対処するパッケージは次のとおりです（当時のaptコマンド文字列そのものは未確認）。

```bash
sudo apt-get install python3-usb
```

## 4. GitHubからローダーとfirmwareを取得する

[使用コミット](https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV/commit/4180061a1afd109a9204557f256d341c5850c124) のFirmware_loaderに、ローダーとfirmwareが同梱されています。配布の存在と元firmwareとのhash一致は確認していますが、配布ライセンスは未確認なので公開repoへ転載しません。

```bash
mkdir -p ~/jetson-work
cd ~/jetson-work
git clone https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV.git ps4-eye-upstream
cd ps4-eye-upstream
git checkout 4180061a1afd109a9204557f256d341c5850c124
cd Firmware_loader
echo '141454ec1e57a5d0f400b4a345aefb37a7b8178eb9bf9abc25187c27f34a1da4  firmware_V2.bin' | sha256sum -c -
```

firmwareの [直接配布URL](https://raw.githubusercontent.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV/4180061a1afd109a9204557f256d341c5850c124/Firmware_loader/firmware_V2.bin) もあります。上のcloneで取得できるため、別途wgetする必要はありません。

## 5. カメラを初期化する

当時は `sudo python3 ps4eye_init.py` でfirmwareロードに成功し、USB IDが `05a9:0580` から `05a9:058a` へ変化しました。ローダーは相対パスでfirmwareを読むため、Firmware_loader内で起動します。

```bash
sudo modprobe uvcvideo
cd ~/jetson-work/ps4-eye-upstream/Firmware_loader
sudo python3 ps4eye_init.py
```

保存ローダーの判定では058aをV1、058bをV2初期化済みと扱います。一方、保存コードはfirmware_V2.bin固定であり、当時ロードしたファイルとの対応や型番は未確定です。058aへの遷移という履歴を優先し、型番やfirmwareの組合せを推測で確定しません。再実行時は適合を確認し、成功メッセージだけでなくUSB IDも確認してください。

## 6. USBとV4L2を確認する

当時は `/dev/video0` を認識し、次のYUYV対応モードを確認しました。これは列挙された対応モードで、撮影・配信での実測FPSではありません。

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

後日の環境調査では0580、5000M、driver空、videoノードなしの状態でした。これはその時点の状態で、10月15日の初期化・撮影成功を否定するものではありません。現在は再初期化・再撮影していません。専用udev/systemd設定や露光・USB quirksの固定値は未確認です。

## 7. 自作Pythonコードを配置する

自作6本を新しい作業先へコピーします。コードをそのまま残すため、Python3.6/Flask0.12互換案とホームパス修正案は作業コピーだけへ適用します（patch適用は静的確認済み、実機動作は未検証）。

```bash
mkdir ~/jetson-work/ps4-eye-custom
cp ~/Projects/jetson-lab/ps4-eye/scripts/*.py ~/jetson-work/ps4-eye-custom/
cd ~/jetson-work/ps4-eye-custom
git apply ~/Projects/jetson-lab/ps4-eye/patches/ps4-stream-flask012.patch
git apply ~/Projects/jetson-lab/ps4-eye/patches/ps4-calib-python36.patch
git apply ~/Projects/jetson-lab/ps4-eye/patches/depth-stream-home-path.patch
```

| コード | 役割・入出力 |
|---|---|
| [ps4_stream.py](scripts/ps4_stream.py) | RGB配信、ゲイン、snapshot。port5000 |
| [ps4_calib_capture.py](scripts/ps4_calib_capture.py) | 左右校正撮影。port5002、~/ps4_calib/pairsへPNG |
| [ps4_calibrate.py](scripts/ps4_calibrate.py) | pairsからNPZとpreviewを計算 |
| [ps4_depth_stream.py](scripts/ps4_depth_stream.py) | NPZを使った深度配信。port5001 |
| [ps4_depth.py](scripts/ps4_depth.py) | 試作：未校正SGBM診断、cwdへdepth_*.jpg |
| [ps4_depth_test.py](scripts/ps4_depth_test.py) | 試作：左右順を比較、ホームへtest_*.jpg |

外部依存はcv2・NumPy・Flaskで、校正撮影コードはcv2とFlaskを使います。import時からカメラ取得等が始まるコードなので、単なる構文確認のためにimportしないでください。

## 8. 左右RGBを配信する

当時はOpenCVで画像取得・保存に成功し、左右画像の切り出し、向きと色表示を修正してMacのSafariへリアルタイム配信できました。以下は現在保存している配信コードの起動方法で、同じ状態の再確認はしていません。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_stream.py
```

ブラウザで `http://<Nanoのアドレス>:5000/` を開きます。RGBゲイン初期値は各1.0で、/stream、/settings、/snapshotを持ちます。

| 設定 | 現在保存しているコードの要求値 |
|---|---|
| 入力 | index0、CAP_V4L2、YUYV、3448×808 |
| RGB | 30fps、buffer2 |
| 校正撮影・深度 | 15fps、配信/校正はbuffer1 |
| Camera A | frame[0:800, 48:1328]、1280×800 |
| Camera B | frame[0:800, 1328:2608]、1280×800 |

YUYVは2画素で色差を共有するYUV4:2:2形式です。OpenCVから受け取った配列はBGRとして処理するため、実際のformat・frame.shapeと左右像を確認します。要求FPSを実測値とは扱いません。上流viewerの幅1264切り出しは、この独自コードと別設定です。

Flaskは0.0.0.0待受で認証はありません。フレーム更新とsnapshotを確認したらCtrl+Cで終了し、他の取得コードを同時起動せず次へ進みます。

## 9. ステレオ校正と距離計算

当時はStereoSGBMで人物と背景の相対視差を表示できました。`COLORMAP_TURBO` が使えなかったため `COLORMAP_JET` へ変更しており、保存されている深度コードもJETを使っています。これは相対的な奥行き表示の成功で、校正済みの絶対距離精度の確認ではありません。

[校正・距離計算](calibration.md) に、現在保存しているコードの実行方法、校正ファイルの配置と深度処理をまとめています。

## 10. よくあるトラブル

| 症状 | 確認・対処 |
|---|---|
| No module named usb | 当時はpython3-usb不足。sudo apt-get install python3-usbで解消 |
| COLORMAP_TURBOが使えない | 当時はCOLORMAP_JETへ変更。保存コードもJETを使用 |
| USBに見えるがvideoが無い | 0580のままか、再列挙したか、uvcvideoを確認 |
| read失敗・左右像が欠ける | 実ノードとindex0、format、frame.shape、他プロセスの使用を確認 |
| snapshotで引数エラー | Flask0.12はdownload_nameでなくattachment_filename。上の互換patchを使う |
| 校正保存失敗時に別の例外 | Python3.6のPath.unlinkにmissing_okが無い。cleanup互換patchを使う |
| 距離が負・整列がずれる | [左右順、Q、縮小K](calibration.md#距離計算の仕組み) を確認 |

usb不足とCOLORMAP_TURBOの問題は当時の履歴にあるエラーです。Flask/Python互換案は保存コードとAPIから分かったもので、当時同じエラーが起きたと確認したものではありません。
