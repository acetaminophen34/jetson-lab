# PS4 Eyeの独自Pythonコード

## 保全方針

取得済みの6本をすべて置いています。試作の未校正深度処理や左右順テストも除外していません。ユーザーの自作・改造コードという申告に基づく保全で、上流PS4 Eyeプロジェクトを丸ごと転載したものではありません。原ソースの技術的類似だけで全ての著作権帰属を確定せず、独自部分へ新しい利用許諾も設定していません。

5本は原文とバイト一致。`ps4_depth_stream.py`だけは固定ユーザー名入りのCALIBパスを`/home/JETSON_USER/...`へ置き換えています。これも処理の改善ではなく公開用匿名化です。置換前原本は非公開、原文hashと公開版hashを別に [出典manifest](../../reference/code-origins.json) に記録します。

## ファイル別の用途・依存・入出力

Python3.6.9、OpenCV4.1.1、NumPy1.13.3、Flask0.12.2が保存環境の基準です。pathlib/time/threading/ioは標準ライブラリです。

| コード | 用途 | 外部依存 | 実行方法（準備後、作業コピーで） | 入力 → 出力 | 技術記事 |
|---|---|---|---|---|---|
| [ps4_stream.py](ps4_stream.py) | 左右RGBの配信・RGBゲイン・snapshot | cv2、numpy、flask | `python3 ps4_stream.py` | V4L2 index0 → port5000、/stream、/settings、/snapshot | [撮影](../../docs/projects/ps4-eye/capture.md) |
| [ps4_depth.py](ps4_depth.py) | 未校正SGBMの1回診断 | cv2、numpy | `python3 ps4_depth.py` | index0、15フレーム → cwdのdepth_left/right/map/comparison.jpg | [深度](../../docs/projects/ps4-eye/stereo-depth.md) |
| [ps4_depth_test.py](ps4_depth_test.py) | 通常/左右反転の視差比較の試作 | cv2、numpy | `python3 ps4_depth_test.py` | index0 → ホームのtest_left/right/normal/swapped.jpg | [深度](../../docs/projects/ps4-eye/stereo-depth.md) |
| [ps4_calib_capture.py](ps4_calib_capture.py) | 両眼9×6コーナー検出と校正撮影 | cv2、flask | `python3 ps4_calib_capture.py` | index0、/capture POST → ~/ps4_calib/pairs/camA/camB PNG、port5002 | [校正](../../docs/projects/ps4-eye/stereo-depth.md) |
| [ps4_calibrate.py](ps4_calibrate.py) | 既存ペアから単眼/ステレオ校正 | cv2、numpy | `python3 ps4_calibrate.py` | ~/ps4_calib/pairs → NPZ、preview、RMS/基線などのstdout | [校正](../../docs/projects/ps4-eye/stereo-depth.md) |
| [ps4_depth_stream.py](ps4_depth_stream.py) | B基準rectify、視差・距離・overlay配信 | cv2、numpy、flask | `python3 ps4_depth_stream.py` | index0＋CALIB NPZ → port5001、compare/overlay/depth/camera | [深度](../../docs/projects/ps4-eye/stereo-depth.md) |

## 実行前の作業コピー

import時からカメラ取得やファイル処理を始めるコードがあります。保全原文の構文検査と、実行/importを区別してください。今回コードは実行していません。

共通変数は [再構築の入口](../../docs/getting-started.md) を使い、新しいコピーを公開repoの外へ置きます。

```bash
export CAMERA_STAGE="$LAB_WORK/camera-custom"
test ! -e "$CAMERA_STAGE" || exit 1
mkdir -p "$CAMERA_STAGE"
cp "$LAB_ROOT/src/ps4-eye/"*.py "$CAMERA_STAGE/"
cd "$CAMERA_STAGE"
# 必要な互換案を作業コピーだけへ適用。src原文へ適用しない。
git apply --check "$LAB_ROOT/patches/ps4-eye/ps4-stream-flask012.patch"
git apply --check "$LAB_ROOT/patches/ps4-eye/ps4-calib-python36.patch"
git apply --check "$LAB_ROOT/patches/ps4-eye/depth-stream-home-path.patch"
git apply "$LAB_ROOT/patches/ps4-eye/ps4-stream-flask012.patch"
git apply "$LAB_ROOT/patches/ps4-eye/ps4-calib-python36.patch"
git apply "$LAB_ROOT/patches/ps4-eye/depth-stream-home-path.patch"
```

## 原文の既知問題を残す

- Flask0.12.2はsend_fileのdownload_nameを持たないため、snapshot経路には別patchでattachment_filenameを使う案があります。
- Python3.6はPath.unlink(missing_ok=True)を持たないため、保存失敗cleanupに別patchがあります。
- CALIBの公開用placeholderは未設定のままでは読めません。3番目の任意patchはPath.homeを使う案です。

これらを保全ソースへ混ぜず [patch一覧](../../patches/README.md) で管理します。実機への適用・動作は未検証です。

## データと実行条件

標準UVC、firmwareロード、USB/V4L2の確認が先です。入力要求はYUYV3448×808、A=x48:1328、B=x1328:2608、y0:800の各1280×800。要求が実際に受理されたことは未検証です。

校正NPZと25ペアは非公開原本から [校正復元手順](../../docs/projects/ps4-eye/stereo-depth.md) に従って配置します。校正コードはホーム固定先のNPZ/previewを上書きし得るため、再計算時は同記事の別作業先手順を使います。RGB/深度を同時起動しません。Flaskは0.0.0.0で待受け、認証付きサービスとしての検証はありません。
