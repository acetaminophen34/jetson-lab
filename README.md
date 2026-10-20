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

既存の推論環境が標準の`work/llama-cuda`以外にある場合は、[サーバー手順の参照先設定](llama-cpp/server.md#参照先を設定する)を環境に合わせて変更してください。

## 既存CUDA環境にサーバーを追加する

構築済みのTX2向けllama.cppがある場合は、clone先で次を実行します。

```bash
bash llama-cpp/tools/setup-server.sh --check
bash llama-cpp/tools/setup-server.sh
```

既存環境の検査とllama-serverだけの追加ビルドを行います。初回のCUDA環境構築は含みません。標準の`work/llama-cuda`以外を参照する設定や実行オプションは[サーバー導入手順](llama-cpp/server.md#スクリプトで追加する)を参照してください。
