# Jetson Nano / TX2の構築メモ

Jetson Nano 4GB（JetPack4.6.1）とTX2 8GB（JetPack4.6.6）で使った環境とプログラムです。

| 使いたいもの | 手順 |
|---|---|
| OS・SSH・基本ツール | [環境構築](setup/README.md) |
| Qwen3の文章生成 | [llama.cppのCPU/CUDAビルド・実行・ベンチマーク](llama-cpp/README.md) |
| カメラの顔追跡・距離表示 | [PS4 Cameraの初期化・CPU/GPU実行](ps4-eye/README.md) |

各機能のREADMEは、上から順に実行できます。追加の設定や新しいカメラの校正だけを補足記事に分けています。

## 作業場所を用意する

初めて使う場合は [環境構築](setup/README.md#3-リポジトリと作業場所) から進めます。取得したソースやモデルは、clone先の `work/` にまとめます。
