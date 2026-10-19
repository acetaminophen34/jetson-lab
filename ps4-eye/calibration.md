# PS4 Cameraの校正データを用意する

[stereo_vision.py](scripts/stereo_vision.py) は `~/ps4_calib/stereo_calibration.npz` から、レンズの歪みと左右カメラの位置関係を読み込みます。[作業場所の設定](../README.md#作業場所を用意する) を済ませてから進めます。

## 同じカメラをNanoからTX2へ移す

登録済みの [stereo_calibration.npz](calibration/stereo_calibration.npz) は、Nanoで使用したPS4 Cameraの校正結果です。**校正データはカメラ個体に依存します。** 同じカメラをTX2へ移す場合は、このデータを再利用できます。

```bash
mkdir -p ~/ps4_calib
cp -i "$JETSON_LAB/ps4-eye/calibration/stereo_calibration.npz" \
  ~/ps4_calib/stereo_calibration.npz
```

配置したら [READMEの顔検出モデル取得・起動手順](README.md#5-顔検出モデルを取得する) へ進みます。別のPS4 Cameraを使う場合、または解像度・画像の切り出し・レンズ配置を変えた場合は再校正します。

## 別のカメラで校正する

### 1. 校正用コードを配置する

画像取得に使うデバイスは [READMEの手順](README.md#3-映像入力のデバイスを特定する) で特定します。撮影コードも入力番号は0なので、別の番号なら作業用コピーの `cv2.VideoCapture(0, cv2.CAP_V4L2)` を合わせます。

```bash
mkdir -p "$JETSON_LAB/work/ps4-eye-custom"
cp "$JETSON_LAB/ps4-eye/scripts/ps4_calib_capture.py" \
  "$JETSON_LAB/ps4-eye/scripts/ps4_calibrate.py" \
  "$JETSON_LAB/work/ps4-eye-custom/"
git -C "$JETSON_LAB" apply --directory=work/ps4-eye-custom \
  "$JETSON_LAB/ps4-eye/patches/ps4-calib-python36.patch"
```

パッチは、Python3.6で使えない `unlink(missing_ok=True)` を置き換えます。既存データを残して撮り直す場合は、先に `~/ps4_calib` を別名へ移してください。

### 2. 左右の校正画像を撮る

内側の交点が横9個・縦6個、1マス20mmのチェッカーボードを使います。他のカメラスクリプトを終了してから撮影を始めます。

```bash
cd "$JETSON_LAB/work/ps4-eye-custom"
python3 ps4_calib_capture.py
```

ブラウザで `http://<jetson-ip>:5002/` を開き、位置・距離・傾きを変えて左右の画像を10組以上保存します。保存先は `~/ps4_calib/pairs/`、ファイル名は `camA_*.png` と `camB_*.png` です。

### 3. 校正値を計算する

Ctrl+Cで撮影を終了してから実行します。

```bash
python3 ps4_calibrate.py
```

`~/ps4_calib/stereo_calibration.npz` と `~/ps4_calib/rectified_preview.jpg` ができます。プレビューの左右で、同じ点が水平線上に並ぶかを見ます。Nanoの校正ではRMS誤差がA0.379786px、B0.373186px、左右一組で0.394356px、カメラ間隔の計算値は約80.03mmでした。

計算を終えたら [stereo_vision.pyを起動](README.md#6-起動する) します。

## 最新版での校正値の使い方

- `K_a`・`K_b`：1280×800での内部行列。最新版は処理解像度480×300に合わせ、各行を480/1280、300/800倍します。
- `D_a`・`D_b`：各レンズの歪み係数。歪み補正に使います。
- `R`・`T`：左右カメラの回転・位置関係。Camera B基準に `R.T`、`-R.T @ T` へ変換し、`stereoRectify` で平行化とQ行列を計算し直します。NPZに保存されたQをそのまま使う方式ではありません。

StereoSGBMはBを基準、Aを比較画像として視差を計算します。結果を16で割って画素単位の視差 `d` に戻し、次の式で距離を求めます。

```text
Z = Q[2,3] / (d * Q[3,2] + Q[3,3])
```

校正時のマス寸法は0.020mなので、Zの単位はmです。最新版は0.15m超〜5m未満を有効とし、顔中央の有効画素の中央値を100倍してcm表示します。
