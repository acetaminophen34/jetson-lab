# Jetson Nano / TX2の構築メモ

Jetson Nano 4GB（JetPack4.6.1）とTX2 8GB（JetPack4.6.6）で使った環境とプログラムです。

| 使いたいもの | 手順 |
|---|---|
| Nanoの初期設定 | [SDカード作成 → 初回起動 → SSH → 基本ツール](setup/nano.md) |
| TX2の初期設定 | [JetPack導入 → SSH → 基本ツール](setup/tx2.md) |
| Qwen3の文章生成 | [llama.cppのCPU/CUDAビルド・実行・ベンチマーク](llama-cpp/README.md) |
| Qwen3を起動したままHTTPで使う | [既存TX2 CUDA環境へのllama-server追加ビルド・起動確認](llama-cpp/server.md) |
| カメラの顔追跡・距離表示 | [PS4 Cameraの初期化・CPU/GPU実行](ps4-eye/README.md) |

各機能のREADMEは、上から順に実行できます。追加の設定や新しいカメラの校正だけを補足記事に分けています。

## 作業場所を用意する

初期設定の各ページにcloneと作業場所の設定を含めています。取得したソースやモデルは、clone先の `work/` にまとめます。

TX2の既存推論環境が`/home/a62ss/jetson-work/llama-tx2`にある場合は、[サーバー手順の実機パス](llama-cpp/server.md#作業ディレクトリの違い)を使います。`work/llama-cuda`は新規構築時の配置例です。
