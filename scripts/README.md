# 環境構築・保全・検証スクリプト

## 現在の管理用コード

| コード | 用途・依存 | 実行方法 | 入力 → 出力 | 記事 |
|---|---|---|---|---|
| [restore-llama.sh](restore-llama.sh) | bash/git、固定commitと原patchを新規ツリーへ戻す | `bash scripts/restore-llama.sh cpu BACKUP WORK`（GPU profileも選択可） | 元bundle/patch → repo外の新規ソース。buildしない | [CPU](../docs/projects/llama-cpp/cpu-build.md)、[GPU](../docs/projects/llama-cpp/gpu-build.md) |
| [cpu-smoke.py](cpu-smoke.py) | Linux /proc、Python標準ライブラリ、既存CLI | `python3 -B scripts/cpu-smoke.py --exe CLI --model GGUF --out NEW_DIR` | CLI/既存モデル → 120秒上限の短いCPU推論、result/stdout/stderr | [CPU](../docs/projects/llama-cpp/cpu-build.md) |
| [restore-private-camera.py](restore-private-camera.py) | Python標準ライブラリ、hashで復元 | `python3 -B scripts/restore-private-camera.py --help` | 非公開manifest/原本 → 新規作業コピー。--check-onlyはコピーしない。--assets-onlyはコード6本を除く | [撮影](../docs/projects/ps4-eye/capture.md)、[校正](../docs/projects/ps4-eye/stereo-depth.md) |
| [check-repo.py](check-repo.py) | Python/bash/git、公開対象・リンク・hashの検査 | `python3 -B scripts/check-repo.py` | 作業ツリー/index/全commit tree/出典manifest → PASS/FAIL。実機操作しない | [出典・管理](../reference/sources.md) |

既存4本の原文はGitの初回commit 5c63dd1に残っています。src統合に必要な検査/データ復元機能は管理用コードとして更新し、原文保存版のarchivedコードとは区別します。

## 取得済みの保全・調査コード（全8本）

使わないコードも原案として残しています。整形や相対パスの修正はしていません。**repo内からそのまま実行しないでください。** 元のディレクトリ構成や固定ファイル一覧を想定し、出力に非公開情報・画像・bundleを含めるものがあります。

| 原文/公開コピー | 用途・依存 | 元の実行方法 | 入力 → 出力 | 注意・記事 |
|---|---|---|---|---|
| [backup-build-camera.sh](archive/preservation/backup-build-camera.sh) | bash/git/GNU find/stat、lsusb/v4l2/systemctl等 | 元scripts直下で`bash backup-build-camera.sh` | source/config → preservation日時別ディレクトリ、既定でbundleも生成 | ソース読取り＋出力作成。秘密情報は原稿で要レビュー。[出典](../reference/sources.md) |
| [export-source-changes.sh](archive/preservation/export-source-changes.sh) | bash/git/cp | `bash export-source-changes.sh` | 4repo → source-backup日時別diff/untracked | 原文の除外条件を維持。[patch](../docs/projects/llama-cpp/patches.md) |
| [collect-extended.sh](archive/inventory/collect-extended.sh) | bash、Linux照会コマンド、Python pip | `bash collect-extended.sh` | host/toolchain/model等 → inventory-extra日時別ログ/hash | OSを設定変更しないがログは非公開。[環境](../docs/environment/jetpack.md) |
| [verify.sh](archive/validation/verify.sh) | bash、Linux、Python環境 | `bash verify.sh` | OS/ライブラリ/資源 → stdout | importを行う。単なる構文検査ではない。[版](../reference/environment-versions.md) |
| [jetson_readonly_discover.py](archive/inventory/jetson_readonly_discover.py) | Python標準、git | 対象Nanoで`python3 -B jetson_readonly_discover.py > discovery.json` | 配置された既存ファイル → path/size/hash/状態JSON | モデルhashは重い。端末/ファイルへ原文保存し公開しない。[棚卸し](../reference/code-inventory.md) |
| [jetson_fetch.py](archive/inventory/jetson_fetch.py) | Python標準、git/照会ツール | 元はstdin投入、stdoutをMacへ保存 | 固定REQUESTS402件/関連履歴 → base64付きJSON | 固定ホームは公開用placeholderに置換済み。最新の一般収集器ではない。[棚卸し](../reference/code-inventory.md) |
| [jetson_final_read.py](archive/inventory/jetson_final_read.py) | Python標準、readelf、cv2/numpy/flask/usb | `python3 -B jetson_final_read.py > final.json` | 校正/設定/ELF/依存 → JSON | 原文の合計32MiBコピー上限を維持。実際の校正画像保全は別工程だった。[出典](../reference/sources.md) |
| [cpu-runner.py](archive/validation/cpu-runner.py) | Linux /proc、Python標準、既存CPU CLI | `python3 -B cpu-runner.py > result.json` | 固定モデル/CLI → 推論とRAM/速度JSON | 実際の成功時ラッパー原文。model不一致の早期終了0等も改変せず保存。[実測](../reference/validation-results.md) |

元shell4本は`dirname(script)/..`をROOTとします。この分類配置で直接起動すると想定と異なる場所へ書くことがあります。将来参照実行する場合は、コードを外部の専用作業先の`scripts/`直下へコピーし、想定パス/除外条件をレビューしてから行います。コードは動作するように無言で修正していません。これらの実行を今回の保全作業で行ってはいません。

固定ホームを匿名化したfetch版は、そのまま元機で実行できる版ではありません。原文は非公開で保全され、公開版を実行するなら作業コピー側でパスを設定する必要があります。

## 出典とライセンス

コピーした8本のうち7本は原文バイトと一致、fetch1本のみ固定ホーム790箇所を置換。カメラも含めた原文/公開版hashと原本パスは [code-origins.json](../reference/code-origins.json)、実際の絶対パスは非公開レビュー記録にあります。調査補助コードを特定の人が独立に書いたと断定せず、プロジェクト作業コードとして保全しています。新しい包括ライセンスは設定していません。
