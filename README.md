# jetson-lab

Jetson Nanoで、小さな言語モデルとUSBステレオカメラを扱うための技術ノートです。JetPackの構成、古いCUDAに合わせたC++の修正、画像取得と深度計算のつながりを説明し、同じソース・設定から環境を組み直す手順をまとめています。

**CPU版llama.cppでQwen3-0.6Bの推論を確認済みです。** GPUは電源上の制約があり、カメラはUSB認識まで確認しています。新規ビルドや撮影まで検証済みの教材ではありません。到達点と未検証範囲を各記事に示しています。

## 読み方

初めて読む場合は [環境の全体像](docs/environment/jetpack.md) → [llama.cpp](docs/projects/llama-cpp/README.md) または [PS4 Eye](docs/projects/ps4-eye/README.md) と進むと、コマンドの意味を理解しやすくなります。

環境を組み直す場合は **[再構築の入口](docs/getting-started.md)** から始めてください。OS準備 → 基本パッケージ → コンパイラ/CMake → ソース・patch → CPUビルド → モデル・推論 → カメラ → 任意のGPU、の順で各記事を案内します。

## 目次

| 分野 | 記事 |
|---|---|
| ハードウェア | [Nanoのメモリ・電源とTX2の扱い](docs/hardware.md) |
| 基本環境 | [JetPack / L4T / Ubuntu / cuDNN / TensorRT](docs/environment/jetpack.md)、[CUDAとアーキテクチャ](docs/environment/cuda.md)、[GCCとCMakeの準備](docs/environment/build-tools.md) |
| 言語モデル | [仕組みと構成](docs/projects/llama-cpp/README.md)、[CPUビルド・モデル・推論](docs/projects/llama-cpp/cpu-build.md)、[GPUビルド](docs/projects/llama-cpp/gpu-build.md)、[patchの内容と理由](docs/projects/llama-cpp/patches.md) |
| カメラ | [PS4 Eyeの全体像](docs/projects/ps4-eye/README.md)、[firmwareとUSB](docs/projects/ps4-eye/firmware.md)、[撮影コードと配信](docs/projects/ps4-eye/capture.md)、[校正・視差・深度](docs/projects/ps4-eye/stereo-depth.md) |
| 問題の切り分け | [トラブルシューティング](docs/troubleshooting.md) |
| 参照 | [版と識別子](reference/environment-versions.md)、[検証結果](reference/validation-results.md)、[出典・非公開資産・ライセンス](reference/sources.md) |

## 記述の読み分け

| 表記 | 意味 |
|---|---|
| **実機確認済み** | 保存された実機の観測・実行結果。対象と条件を限定する |
| **静的確認済み** | ソース、設定、patch、保存データから確認。実行成功を意味しない |
| **未検証** | 未実行の復元・新規ビルド・計測や、資料だけでは確定できない事項 |
| **ユーザー申告** | 利用者の説明。電圧などを計測した結果とは区別する |

背景の一般的な技術説明と、このNanoで観測した値も区別します。各記事末尾に根拠となる参照資料を示します。詳しいログやSHA-256は `reference/details/` に置き、通常の読み進め方から分離しています。

## リポジトリの範囲

公開用の文書、3種類の原patch、互換ヘッダ、補助スクリプトだけを管理します。元の `jetson-rebuild` と非公開保全先は別に残しています。モデル、firmware、独自カメラ原コード、校正バイナリ、撮影画像、巨大bundle、認証情報は含みません。

編集時は `python3 -B scripts/check-repo.py` でリンク・shell構文・公開対象を検査します。新しい確認結果は技術記事を直し、根拠を [検証結果](reference/validation-results.md) へ追加します。調査日記を記事の末尾へ積み重ねません。

全体への新規ライセンス付与は行っていません。[LICENSE](LICENSE) で権利の適用範囲を確認してください。この整理ではSSH接続・実機操作・追加取得を行わず、ローカルの独立Gitリポジトリとしてコミットしています。GitHubへのpushは公開内容確認後の工程です。
