# 撮影コード、YUYV入力、RGB配信

## 概要・仕組み

独自コードはV4L2経由でカメラから画像を読み、大きな転送フレームから左右の映像を切り出します。OpenCVのVideoCaptureが受け取る入力形式の要求と、Python処理で使う画素配列の形式を分けて考えます。

YUYVは2画素で色差を共有するYUV4:2:2の並びです。コードはFOURCCとしてYUYVを要求する一方、取得した配列をBGR画像としてcvtColorやJPEG変換へ渡します。要求が受理されたformatと実frame.shapeは、実際の取得時に確認する必要があります。転送フレームの未使用領域の意味は未特定です。

## 前提と原コードの所在

[firmware/USB](firmware.md)の工程を先に切り分けます。独自6本は非公開保全先のmanifestで管理し、包括的ライセンス未確認のため公開repoへコピーしません。必要なのはcv2、NumPy、Flaskと標準ライブラリで、独自6本はMatplotlibをimportしていません。

| スクリプト | 役割 | 主な入力/出力 |
|---|---|---|
| ps4_stream.py | RGB配信 | port5000、/stream、/settings、/snapshot |
| ps4_depth.py | 未校正の視差診断 | カレント先へdepth_*.jpg |
| ps4_depth_test.py | 左右順の比較 | ホームへtest_*.jpg |
| ps4_calib_capture.py | 左右同時の校正撮影 | port5002、/capture、camA/camB PNG |
| ps4_calibrate.py | 校正パラメータ計算 | pairs → NPZ/preview |
| ps4_depth_stream.py | 校正済み深度配信 | NPZ → port5001、比較/深度/overlay |

これらはホーム直下に追加された独自実装で、上流repoの追跡変更patchは空でした。上流viewerの編集と同じものではありません。

## 原コードを新しい作業先へ復元

補助スクリプトは非公開manifestからカメラ6本、校正NPZ、25ペア、previewを選び、hashを確認して新規先へ配置します。元パスを知らなくてもsaved_asを根拠にします。公開repo内への出力や既存先への上書きは拒否します。

```bash
export CAMERA_STAGE="$LAB_WORK/camera-custom"
python3 -B "$LAB_ROOT/scripts/restore-private-camera.py" \
  --private-root "$PRIVATE_ROOT" --manifest "$RECOVERY/manifest.json" \
  --dest "$CAMERA_STAGE"
```

成功条件はスクリプト6本・NPZ・50枚が揃いhashが一致することです。失敗時は非公開資産の配置、manifestのroot、欠落ファイルを確認し、代わりの画像/校正値を生成しません。

## 既存版とのAPI差を直す

原文には二つの互換上の問題があり、別の提案patchとして非公開保全先にあります。

| 箇所 | 原文 | 提案する変更 | 確認範囲 |
|---|---|---|---|
| ps4_stream.pyのsend_file | download_name | Flask0.12.2のattachment_filenameへ | 関数signatureとpatch適用を静的確認。snapshot未実行 |
| ps4_calib_capture.pyの保存失敗cleanup | Path.unlink(missing_ok=True) | unlinkとFileNotFoundError捕捉へ | Python3.6のsignatureと構文確認。失敗経路未実行 |

```bash
cd "$CAMERA_STAGE"
git apply --check "$RECOVERY/proposed-compatibility/ps4_stream.py.patch"
git apply --check "$RECOVERY/proposed-compatibility/ps4_calib_capture.py.patch"
git apply "$RECOVERY/proposed-compatibility/ps4_stream.py.patch"
git apply "$RECOVERY/proposed-compatibility/ps4_calib_capture.py.patch"
```

変更は復元した作業コピーだけへ適用します。この提案を過去に実機へ適用して動いたという事実はありません。依存版を上げたことにして原文の問題を隠しません。

## 入力と左右の切り出し

| 項目 | 独自コードに保存された値 |
|---|---|
| 取得 | index0、CAP_V4L2、YUYV、3448×808要求 |
| RGB配信 | 30fps要求、buffer2 |
| 深度/校正撮影 | 15fps要求、配信/校正はbuffer1 |
| Camera A | frame[0:800, 48:1328] → 1280×800 |
| Camera B | frame[0:800, 1328:2608] → 1280×800 |

これらは**静的確認済みの要求値**です。実FPSやformatの測定値ではありません。上流viewerは幅1264の別切り出しで、独自校正データへ無条件に混ぜられません。実ノードがindex0でなければ、取得する各コードのindexを新しいpatchとして変更・記録します。

## ホームへ配置してRGBを確認する（未検証）

初期化後、既存ファイルがない場合だけ配置します。校正データの配置は [ステレオ深度](stereo-depth.md) を先に確認します。

```bash
for name in ps4_stream.py ps4_depth.py ps4_depth_test.py \
            ps4_depth_stream.py ps4_calib_capture.py ps4_calibrate.py; do
  test ! -e "$HOME/$name" || exit 1
  cp "$CAMERA_STAGE/$name" "$HOME/$name"
done
python3 ~/ps4_stream.py
```

ブラウザで`http://<Nanoのアドレス>:5000/`を開く将来の手順です。ソース上は0.0.0.0待受で、認証付きサービスとしての実装ではありません。RGBゲインの初期値は各1.0で、永続設定は確認できていません。

成功条件はisOpened/read成功、切り出し範囲を満たすframe.shape、正しい左右像、/streamの更新、互換処置後の/snapshotです。カメラを使う別プロセスを同時に起動せず、RGB確認後に実行端末で終了して次へ進みます。今回の編集では何も起動/停止していません。

## 参照資料・未検証事項

- [出典S5](../../../reference/sources.md)：6本の原文、signature、独自設定
- [検証結果](../../../reference/validation-results.md)：撮影・配信は未検証
- 次へ：[校正と深度](stereo-depth.md)
