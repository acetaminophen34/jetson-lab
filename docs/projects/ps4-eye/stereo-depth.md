# ステレオ校正、視差、深度

## 概要・背景

左右の画像を並べただけでは、安定した距離は得られません。レンズ歪み、焦点距離、左右の向きを推定し、対応点が同じ高さに並ぶように整列します。その上で視差を求め、カメラ間の基線長と焦点距離を使って距離へ変換します。

理想化した整列済みステレオでは、距離Zは焦点距離f、基線長B、視差dから`Z = f × B / d`と表せます。実コードではrectificationが生成したQ行列を使い、オフセットも含めてZを計算します。視差ゼロや対応のない画素を有効な距離として扱わないことが重要です。

## 校正ファイルの意味

[独自校正コード](../../../src/ps4-eye/ps4_calibrate.py) の出力は`~/ps4_calib/stereo_calibration.npz`です。上流同梱の単眼param_*.npyとは別物です。

| 保存値 | 意味 |
|---|---|
| K_a / K_b | 各カメラの焦点距離・主点を含む内部行列 |
| D_a / D_b | 各レンズの歪みパラメータ |
| R / T | Camera AからBへの回転と並進 |
| R1 / R2 / P1 / P2 | 保存時の整列・投影用行列 |
| Q | 視差から3次元への変換用行列 |
| image_size / square_size_m | 1280×800、格子1辺0.020m |
| rms_a / rms_b / rms_stereo | 保存した校正の再投影誤差 |

**保存NPZからの静的解析**では、RMSはA0.379786、B0.373186、stereo0.394356px、Tのノルムによる基線は約80.03mmです。今回の再測定値ではありません。25ペアが保全されていますが、校正stdoutや縦ズレ統計は未保存です。

## 前提と校正資産の復元

[撮影コード](../../../src/ps4-eye/README.md) と校正データは分けて復元します。補助スクリプトの--assets-onlyでNPZ、50枚PNG、previewだけを新規作業先へ取り出し、原文hashを照合します。

```bash
export CAMERA_ASSETS="$LAB_WORK/camera-assets"
python3 -B "$LAB_ROOT/scripts/restore-private-camera.py" \
  --private-root "$PRIVATE_ROOT" --manifest "$RECOVERY/manifest.json" \
  --dest "$CAMERA_ASSETS" --assets-only
test ! -e "$HOME/ps4_calib" || exit 1
cp -R "$CAMERA_ASSETS/ps4_calib" "$HOME/ps4_calib"
printf '%s  %s\n' e3dd00dab470d03cbddaa9af18bc5117777919291a0c6e333d322dfd24f7b9ce "$HOME/ps4_calib/stereo_calibration.npz" | sha256sum -c -
```

NPZは3,610bytesです。成功はhashと元画像の揃いで判定します。[配信の保全コード](../../../src/ps4-eye/ps4_depth_stream.py) は個人パスをplaceholderに置換しています。作業コピーでCALIBを設定するか [Path.homeの任意案](../../../patches/ps4-eye/depth-stream-home-path.patch) を適用してください。元の固定パス原文は非公開のままです。HOME変数を別用途へ付け替える必要はありません。

## 深度処理の順序と左右の向き

独自depth_streamは次を行います。

1. 左右1280×800を切り出し、640×400へ縮小する。
2. Kの先頭2行を0.5倍して縮小後の画素座標へ合わせる。
3. Bを基準へ変え、`R_ba = R.T`、`T_ba = -R.T @ T`としてstereoRectifyを再計算する。
4. remapで歪み/整列を補正し、B基準像とA対応像をグレースケールへ変換する。
5. StereoSGBM（block7、numDisparities128）で視差を計算し、固定小数表現を16で除算する。
6. 有効視差を選び、QからメートルのZを求め、色や中央領域の距離を表示する。

保存NPZのQ[3,2]は約-12.4951ですが、配信コードは左右反転後に再計算したQ[3,2]>0を要求します。元のQの符号だけで校正失敗と判断してはいけません。コード上の距離式は`Q[2,3] / (d*Q[3,2] + Q[3,3])`で、単純な色付き視差表示とは区別します。

## 校正済み深度を起動する（未検証）

RGBなど他のカメラ取得プロセスを終了した後、将来の動作確認として実施します。

```bash
python3 ~/ps4_depth_stream.py
```

`http://<Nanoのアドレス>:5001/`でcompare/overlay/depth/cameraを切り替える実装です。成功条件は映像更新、符号チェック通過、整列の妥当性、既知距離との比較です。NPZが読めるだけで距離精度が保証されるわけではありません。`ps4_depth.py`と`ps4_depth_test.py`は未校正の視差/左右順診断で、精度評価の代わりにしません。

## 必要な場合だけ再校正する

保存コードは内部コーナー9×6、1辺20mm、最低10有効ペアを要求します。元の撮影コードはホーム固定先へ保存し、校正コードも元NPZを上書きするため、単にcwdを変えるだけでは原本保護になりません。

次は**新規作業コピーだけの保存先を変更する将来手順**です。原6本・元NPZ・非公開保全画像は変更しません。

```bash
export CALIB_WORK="$LAB_WORK/recalibration"
test ! -e "$CALIB_WORK" || exit 1
mkdir -p "$CALIB_WORK/pairs"
python3 - "$HOME/ps4_calib_capture.py" "$HOME/ps4_calibrate.py" "$CALIB_WORK" <<'PYCODE'
from pathlib import Path
import sys
work = Path(sys.argv[3])
changes = [(Path(sys.argv[1]), 'OUT = Path.home() / "ps4_calib" / "pairs"',
            'OUT = Path(%r) / "pairs"' % str(work)),
           (Path(sys.argv[2]), 'BASE = Path.home() / "ps4_calib"',
            'BASE = Path(%r)' % str(work))]
for src, old, new in changes:
    text = src.read_text()
    assert text.count(old) == 1
    (work / src.name).write_text(text.replace(old, new, 1))
PYCODE
# 元の25ペアから再計算する場合だけ。新規撮影ならコピーしない。
cp "$HOME/ps4_calib/pairs/"*.png "$CALIB_WORK/pairs/"
# 新規撮影を行う場合だけ。port5002 /captureで左右を保存する。
python3 "$CALIB_WORK/ps4_calib_capture.py"
# 撮影処理終了後、または既存ペアからの再計算時:
python3 "$CALIB_WORK/ps4_calibrate.py"
```

結果はCALIB_WORKに保存されます。保存先を変えたdiffも新規記録に残します。RMS、縦ズレ、baseline、previewを確認し、既知距離で評価してから新しい校正を採用します。この再計算も撮影も未実施で、保存RMSを絶対的な合格閾値として創作しません。

## 参照資料

- [出典S5](../../../reference/sources.md)、[NPZ識別子](../../../reference/environment-versions.md)
- [検証範囲](../../../reference/validation-results.md)、[切り分け](../../troubleshooting.md)
