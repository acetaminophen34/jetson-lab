# 補助ツール

## 校正データの復元

[restore-private-camera.py](restore-private-camera.py) は既存の非公開manifestから必要なファイルを選び、新しい作業先へコピーします。Python標準ライブラリだけを使います。

```bash
python3 -B "$LAB_ROOT/tools/restore-private-camera.py" --help
```

--check-onlyは照合のみ、--assets-onlyはコードを除き校正NPZ・画像を選択します。具体例は [校正手順](../ps4-eye/calibration.md) にあります。LLM用の [ソース復元](../llama-cpp/tools/restore-llama.sh) と [CPU検証](../llama-cpp/tools/cpu-smoke.py) はプロジェクト側にまとめています。

## 過去に使用した補助・試作コード

以下は旧構成のまま残した参考用コードです。固定パスや元の配置に依存するため、リポジトリ内からそのまま実行せず、必要なら外の作業コピーで確認してください。

| コード | 用途・依存 | 元の実行方法・入出力 |
|---|---|---|
| [backup-build-camera.sh](archive/preservation/backup-build-camera.sh) | bash/git、GNU find/stat、USB/V4L2/systemctl | bashで実行。ソース・設定からpreservationとbundleを生成 |
| [export-source-changes.sh](archive/preservation/export-source-changes.sh) | bash/git/cp | bashで実行。4repoから差分と未追跡ファイルを出力 |
| [collect-extended.sh](archive/inventory/collect-extended.sh) | bash、Linux照会コマンド、Python pip | bashで実行。環境情報をinventory-extraへ出力 |
| [verify.sh](archive/validation/verify.sh) | bash/Linux/Python | bashで実行。OS・ライブラリ・資源情報をstdoutへ出力。importあり |
| [jetson_readonly_discover.py](archive/inventory/jetson_readonly_discover.py) | Python標準/git | python3 -Bで実行。既存ファイルの配置・状態をJSON出力 |
| [jetson_fetch.py](archive/inventory/jetson_fetch.py) | Python標準/git等 | 元はstdin投入。固定ファイル一覧を読みbase64付きJSON出力 |
| [jetson_final_read.py](archive/inventory/jetson_final_read.py) | Python、readelf、cv2/numpy/flask/usb | python3 -Bで実行。校正・ELF・依存をJSON出力。コピー合計32MiB上限 |
| [cpu-runner.py](archive/validation/cpu-runner.py) | Linux /proc、Python標準、CPU CLI | python3 -Bで実行。固定CLI/モデルから推論結果・RAM情報をJSON出力 |
| [check-repo.py](archive/check-repo.py) | Python/bash/git | **旧構成専用**。削除したmanifestと旧root配置が必要で、現構成の検査には使わない |

shell4本はdirname(script)/..をROOTにするため、使う場合は外部作業先のscripts/直下へコピーし、想定パスを確認します。fetchの固定ホームは公開用placeholderであり、作業コピー側で設定が必要です。cpu-runnerはモデル不一致でも早期終了0となる原案を残しています。通常のCPU確認には [cpu-smoke.py](../llama-cpp/tools/cpu-smoke.py) を使ってください。

出力には機器固有情報・画像・bundleが入ることがあります。出力先は公開repo外にし、認証情報を公開しないでください。ソース本体は配置変更だけで維持しています。
