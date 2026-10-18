# ステレオ校正と距離計算

[カメラ初期化・コード配置](README.md) の続きです。過去会話から復元した2026年10月15日の履歴では、撮影とStereoSGBMによる人物・背景の相対視差表示に成功していました。現在は再検証しておらず、以下の再校正・校正済み深度配信手順と絶対距離精度は未検証です。

## 1. 既存の校正データを使う場合

校正値はカメラ個体、左右順、解像度、切り出し設定に依存し、一般配布のファイルではありません。手元の `ps4_calib` フォルダをDownloadsに用意し、初期化後のホームに同名フォルダが無い状態でコピーします。

```bash
cp -R ~/Downloads/ps4_calib ~/ps4_calib
ls ~/ps4_calib/stereo_calibration.npz
ls ~/ps4_calib/pairs/
```

保存NPZは3610bytes、SHA256は `e3dd00dab470d03cbddaa9af18bc5117777919291a0c6e333d322dfd24f7b9ce` です。保存画像はcamA_*.pngとcamB_*.pngの25ペアで、NPZとともにGitへは含めていません。

## 2. 新しく校正する場合

既存の `~/ps4_calib` がある場合は、再計算で上書きしないよう別名に退避します。以下のmvは既存フォルダがある場合だけ行い、退避先も未使用の名前にしてください。

```bash
mv ~/ps4_calib ~/ps4_calib.previous
```

内部コーナー9×6、格子1辺20mmのパターンを使います。撮影画面を開き、両眼で検出できる位置・傾きを変えて10組以上保存します。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_calib_capture.py
```

`http://<Nanoのアドレス>:5002/` の撮影操作はPOST /captureで、左右PNGを `~/ps4_calib/pairs` に保存します。撮影をCtrl+Cで終了してから校正計算します。

```bash
python3 ps4_calibrate.py
```

出力は `~/ps4_calib/stereo_calibration.npz` と `rectified_preview.jpg` です。stdoutのRMS、基線長とpreviewの整列を確認し、既知距離でも評価して採用します。

## 3. 校正ファイルの意味

| 値 | 意味 |
|---|---|
| K_a / K_b、D_a / D_b | 各カメラの内部行列とレンズ歪み |
| R / T | Camera AからBへの回転と並進 |
| R1 / R2 / P1 / P2 | 整列・投影用行列 |
| Q | 視差から3次元への変換行列 |
| image_size / square_size_m | 1280×800、格子1辺0.020m |

保存NPZのRMSはA0.379786、B0.373186、stereo0.394356px、Tのノルムによる基線は約80.03mmです。これらは保存値の解析で、今回の再計算結果や一律の合格閾値ではありません。上流viewer用param_*.npyとは別物です。

## 4. 深度配信を起動する

RGBや校正撮影を終了してから起動します。[ホームパス修正patch](patches/depth-stream-home-path.patch) を適用した作業コピーなら、現在ユーザーの `~/ps4_calib/stereo_calibration.npz` を読みます。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_depth_stream.py
```

ブラウザで `http://<Nanoのアドレス>:5001/` を開き、compare/overlay/depth/cameraを切り替えます。映像更新、左右整列、符号チェック、既知距離との比較が確認点です。

## 距離計算の仕組み

左右像を整列し、対応点の横ずれ（視差d）を求めます。理想化した距離は `Z = f × B / d`（焦点距離f、基線長B）ですが、実コードはQ行列のオフセットも使います。

1. 左右1280×800を640×400へ縮小し、Kの先頭2行を0.5倍する。
2. Bを基準に `R_ba = R.T`、`T_ba = -R.T @ T` としてstereoRectifyを再計算する。
3. remapで整列し、グレースケール像にStereoSGBM（block7、numDisparities128）を使う。
4. 固定小数視差を16で除算し、有効画素で `Z = Q[2,3] / (d*Q[3,2] + Q[3,3])` を求める。

保存Q[3,2]は約-12.4951ですが、配信コードはB基準へ再計算したQ[3,2]>0を要求します。元Qの符号だけで校正失敗と判断せず、左右順と再計算を確認してください。視差0や対応の無い画素は有効距離にしません。

## 試作コードで左右順を調べる

未校正の診断用であり、距離精度の評価用ではありません。一つずつ実行します。

```bash
cd ~/jetson-work/ps4-eye-custom
python3 ps4_depth.py
python3 ps4_depth_test.py
```

depth.pyはcwdのdepth_*.jpg、depth_test.pyはホームのtest_*.jpgへ書きます。整列が崩れる場合は切り出し範囲、NPZのimage_size、縮小K、左右順を確認します。
