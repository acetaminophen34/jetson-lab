# ステレオ校正と距離計算

[撮影コードの配置](README.md#5-自作コードを配置する) を先に済ませます。校正済みの絶対距離精度は未検証です。

## 1. 既存の校正データを使う

手元の `ps4_calib` をホームへコピーします。校正はカメラ個体・解像度・切り出し設定に依存します。

```bash
cp -R ~/Downloads/ps4_calib ~/ps4_calib
ls ~/ps4_calib/stereo_calibration.npz
ls ~/ps4_calib/pairs/
```

既存の校正画像はcamA_*.pngとcamB_*.pngの25ペアです。

## 2. 新しく校正する

既存データがある場合だけ退避します。退避先に同名フォルダがないことを確認してください。

```bash
mv ~/ps4_calib ~/ps4_calib.previous
```

内部コーナー9×6、格子1辺20mmのパターンを使います。撮影画面 `http://<jetson-ip>:5002/` で位置・傾きを変えて10組以上保存します。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_calib_capture.py
```

Ctrl+Cで撮影を終了し、計算します。

```bash
python3 ps4_calibrate.py
```

入力は `~/ps4_calib/pairs/`、出力は `stereo_calibration.npz` と `rectified_preview.jpg` です。保存NPZのRMSはA0.379786、B0.373186、stereo0.394356px、基線長は約80.03mmでした。

## 3. 深度配信

RGB配信・校正撮影を終了してから起動します。`~/ps4_calib/stereo_calibration.npz` を読み、`http://<jetson-ip>:5001/` へ配信します。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_depth_stream.py
```

## 距離計算の仕組み

1. 左右1280×800を640×400へ縮小し、内部行列Kの先頭2行を0.5倍する。
2. B基準へ `R_ba = R.T`、`T_ba = -R.T @ T` と変換して整列する。
3. StereoSGBM（block7、numDisparities128）で視差を計算し、固定小数値を16で除算する。
4. 有効画素で `Z = Q[2,3] / (d*Q[3,2] + Q[3,3])` を計算する。

NPZのK/Dは内部行列・歪み、R/Tは左右の配置、Qは視差から3次元への変換です。保存Q[3,2]は約-12.4951ですが、配信ではB基準へ再計算したQ[3,2]>0を使います。

## 相対視差の試作

相対視差と左右順を調べる試作です。一つずつ実行します。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_depth.py
python3 ps4_depth_test.py
```

depth.pyは作業先へdepth_*.jpg、depth_test.pyはホームへtest_*.jpgを保存します。
