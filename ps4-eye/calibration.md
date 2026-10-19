# PS4 Cameraの校正データを用意する

CPU/GPU版は `~/ps4_calib/stereo_calibration.npz` から、レンズの歪みと左右カメラの位置関係を読み込みます。[作業場所の設定](../README.md#作業場所を用意する) を済ませてから進めます。

同じカメラの登録済み校正データを使う場合は、[READMEの配置・起動手順](README.md#4-校正データと顔検出モデルを配置する) だけで実行できます。このページは別のカメラで撮り直す場合の手順です。

## 別のカメラで校正する

### 1. 校正用コードを配置する

画像取得に使うデバイスは [READMEの手順](README.md#3-カメラ番号を選ぶ) で特定します。撮影時もREADMEで選んだ `CAMERA` の番号を `--camera` で渡します。

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
python3 ps4_calib_capture.py --camera "$CAMERA"
```

ブラウザで `http://<jetson-ip>:5002/` を開き、位置・距離・傾きを変えて左右の画像を10組以上保存します。保存先は `~/ps4_calib/pairs/`、ファイル名は `camA_*.png` と `camB_*.png` です。

### 3. 校正値を計算する

Ctrl+Cで撮影を終了してから実行します。

```bash
python3 ps4_calibrate.py
```

`~/ps4_calib/stereo_calibration.npz` と `~/ps4_calib/rectified_preview.jpg` ができます。プレビューの左右で、同じ点が水平線上に並ぶかを見ます。Nanoの校正ではRMS誤差がA0.379786px、B0.373186px、左右一組で0.394356px、カメラ間隔の計算値は約80.03mmでした。

計算を終えたら [CPU/GPU版を起動](README.md#5-cpu版を起動する) します。

## 最新版での校正値の使い方

- `K_a`・`K_b`：1280×800での内部行列。最新版は処理解像度480×300に合わせ、各行を480/1280、300/800倍します。
- `D_a`・`D_b`：各レンズの歪み係数。歪み補正に使います。
- `R`・`T`：左右カメラの回転・位置関係。Camera B基準に `R.T`、`-R.T @ T` へ変換し、`stereoRectify` で平行化とQ行列を計算し直します。NPZに保存されたQをそのまま使う方式ではありません。

CPU/GPU版ともCamera Bを基準、Aを比較画像にして視差を求めます。視差の画素単位への変換は各プログラム内で行い、共通の式 `Z = Q[2,3] / (d * Q[3,2] + Q[3,3])` で距離へ変換します。校正時のマス寸法は0.020mなので、Zの単位はmです。
