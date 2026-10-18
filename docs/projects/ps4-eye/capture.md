# 撮影コード、YUYV入力、RGB配信

## 概要・仕組み

独自コードはV4L2経由でカメラから画像を読み、大きな転送フレームから左右の映像を切り出します。OpenCVのVideoCaptureが受け取る入力形式の要求と、Python処理で使う画素配列の形式を分けて考えます。

YUYVは2画素で色差を共有するYUV4:2:2の並びです。コードはFOURCCとしてYUYVを要求する一方、取得した配列をBGR画像としてcvtColorやJPEG変換へ渡します。要求が受理されたformatと実frame.shapeは、実際の取得時に確認する必要があります。転送フレームの未使用領域の意味は未特定です。

## 前提と原コードの所在

[firmware/USB](firmware.md)の工程を先に切り分けます。独自6本は [src/ps4-eye](../../../src/ps4-eye/README.md) に全て配置し、原文を保持（1本は個人パス匿名化）しています。出典・license未設定の範囲は [棚卸し](../../../reference/code-inventory.md) を参照してください。必要なのはcv2、NumPy、Flaskと標準ライブラリで、独自6本はMatplotlibをimportしていません。

| スクリプト | 役割 | 主な入力/出力 |
|---|---|---|
| [ps4_stream.py](../../../src/ps4-eye/ps4_stream.py) | RGB配信 | port5000、/stream、/settings、/snapshot |
| [ps4_depth.py](../../../src/ps4-eye/ps4_depth.py) | 未校正の視差診断 | カレント先へdepth_*.jpg |
| [ps4_depth_test.py](../../../src/ps4-eye/ps4_depth_test.py) | 左右順の比較 | ホームへtest_*.jpg |
| [ps4_calib_capture.py](../../../src/ps4-eye/ps4_calib_capture.py) | 左右同時の校正撮影 | port5002、/capture、camA/camB PNG |
| [ps4_calibrate.py](../../../src/ps4-eye/ps4_calibrate.py) | 校正パラメータ計算 | pairs → NPZ/preview |
| [ps4_depth_stream.py](../../../src/ps4-eye/ps4_depth_stream.py) | 校正済み深度配信 | NPZ → port5001、比較/深度/overlay |

これらはホーム直下に追加された独自実装で、上流repoの追跡変更patchは空でした。上流viewerの編集と同じものではありません。

## 保全コードを新しい作業先へ配置

公開用6本の用途・依存・実行方法・原文との違いは [src README](../../../src/ps4-eye/README.md) にまとめています。原文はsrcで固定し、次の新規作業コピーだけを実行/設定の対象にします。

```bash
export CAMERA_STAGE="$LAB_WORK/camera-custom"
test ! -e "$CAMERA_STAGE" || exit 1
mkdir -p "$CAMERA_STAGE"
cp "$LAB_ROOT/src/ps4-eye/"*.py "$CAMERA_STAGE/"
```

成功条件は6本の存在と公開版hash一致です。校正データは [深度の記事](stereo-depth.md) で別に復元します。原本/privateや公開srcを直接編集しません。

## 既存版とのAPI差を直す

原文には二つの互換上の問題があり、原文へ未適用の提案patchとして [patches/ps4-eye](../../../patches/README.md) にあります。

| 箇所 | 原文 | 提案する変更 | 確認範囲 |
|---|---|---|---|
| ps4_stream.pyのsend_file | download_name | Flask0.12.2のattachment_filenameへ | 関数signatureとpatch適用を静的確認。snapshot未実行 |
| ps4_calib_capture.pyの保存失敗cleanup | Path.unlink(missing_ok=True) | unlinkとFileNotFoundError捕捉へ | Python3.6のsignatureと構文確認。失敗経路未実行 |

```bash
cd "$CAMERA_STAGE"
git apply --check "$LAB_ROOT/patches/ps4-eye/ps4-stream-flask012.patch"
git apply --check "$LAB_ROOT/patches/ps4-eye/ps4-calib-python36.patch"
git apply "$LAB_ROOT/patches/ps4-eye/ps4-stream-flask012.patch"
git apply "$LAB_ROOT/patches/ps4-eye/ps4-calib-python36.patch"
```

深度配信のCALIBは公開用placeholderです。必要なら [Path.homeを使う任意patch](../../../patches/ps4-eye/depth-stream-home-path.patch) も作業コピーだけへ適用します。

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
