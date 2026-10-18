# トラブルシューティング

## 切り分けの考え方

復元は「版を確認する」「生成する」「起動する」「結果を評価する」の順で進めます。最後の症状だけから先の設定を変更すると、元環境との違いを追えなくなります。まず最初のエラーと終了コードを残し、既存ソース/バックアップの修正や削除は避けます。

以下は保存資料に基づく確認順です。解決を実機で実証していない項目は、その場で成功済みとは扱いません。

| 症状 | 最初に確認するもの | 対応先 |
|---|---|---|
| aptで同版が無い | apt-cache policy、元dpkgの版、配布元 | [ツール準備](environment/build-tools.md)。最新へ自動置換しない |
| 古いGCC/CMakeが選ばれる | PATHではなくconfigureの絶対パス、cache | [ツール準備](environment/build-tools.md) |
| git applyが失敗する | ベースcommit、対象patch、二重適用、作業先 | [patch](projects/llama-cpp/patches.md)。元repoをresetしない |
| NEON x4ロードでコンパイルエラー | CPU原patch、ヘッダとGCC版 | [patch](projects/llama-cpp/patches.md) |
| filesystemの未解決参照 | stdc++fs、リンク順、原bench末尾whole-archive | [CPUビルド](projects/llama-cpp/cpu-build.md)。元の追加経緯は未確定 |
| CLIがtarget一覧に無い | このHEADのLLAMA_BUILD_SERVER/TOOLS条件 | [CPUビルド](projects/llama-cpp/cpu-build.md) |
| CUDA17やbuiltin/BF16のエラー | CUDA C++14、host compiler、正しいGPU用patch/include | [GPUビルド](projects/llama-cpp/gpu-build.md) |
| cache53だが生成コード50/61 | b5050の条件式、compile_commands | [CUDA](environment/cuda.md) |
| CPU実行時no usable GPU found | GPUなし指定、実際の終了値と応答 | [CPU検証](../reference/validation-results.md)。この警告だけで失敗にしない |
| GPU起動時に装置が落ちる | ユーザー申告の電源問題、電源対策状況 | [ハードウェア](hardware.md)。負荷試験を繰り返さない |
| USBに見えるがvideoが無い | 初期ID0580か、firmware後の再列挙、module | [firmware](projects/ps4-eye/firmware.md) |
| loaderが成功表示だが撮れない | bare except、USB ID、V4L2、driver | [firmware](projects/ps4-eye/firmware.md)。表示だけで成功判定しない |
| フレームが無い/範囲不足 | 実ノードとindex0、FOURCC、frame.shape、同時使用 | [撮影](projects/ps4-eye/capture.md) |
| snapshotで引数エラー | Flask0.12のattachment_filename | [互換修正](projects/ps4-eye/capture.md) |
| 撮影保存失敗時に別の例外 | Python3.6のPath.unlinkにmissing_ok無し | [互換修正](projects/ps4-eye/capture.md) |
| 距離の符号/整列がおかしい | 左右順、B基準変換、再計算Q、縮小K | [深度](projects/ps4-eye/stereo-depth.md) |

## 記録する項目

新しい検証では、対象機種/版、commitとpatch、実行argv、終了値、最初のエラー、ファイルhash、負荷条件を残します。RAMはプロセスRSSと装置全体のMemAvailableを区別し、性能はpromptと生成の速度を分けます。カメラは要求FPSと実測FPSを分けます。

原ログにパスや認証情報が混じる可能性があるため、原文は非公開へ保存し、公開記事には説明と確認済みの値を抽出します。新事実は [検証結果](../reference/validation-results.md) と該当記事へ反映します。

## 参照資料

- [出典と公開範囲](../reference/sources.md)
- [再構築の入口](getting-started.md)
