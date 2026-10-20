# Jetson Nano / TX2の構築メモ

Jetson Nano 4GB（JetPack4.6.1）とTX2 8GB（JetPack4.6.6）で使った環境、llama.cpp、PS4 Cameraのコードと手順をまとめています。

## まず読むページ

- **Nanoを初期設定する** → [SDカード作成からSSH・基本ツールまで](setup/nano.md)
- **TX2を初期設定する** → [JetPack導入からSSH・基本ツールまで](setup/tx2.md)
- **Qwen3を動かす** → [llama.cppのビルド・モデル取得・推論・ベンチマーク](llama-cpp/README.md)
- **Qwen3をHTTPで使う** → [llama-serverの追加・起動](llama-cpp/server.md)
- **カメラで顔追跡・距離表示をする** → [PS4 Cameraの初期化・CPU/GPU実行](ps4-eye/README.md)

初期設定は使う機種のページを1つ選び、その後は使いたい機能のREADMEを上から進めます。

## ファイルの配置

説明・コード・修正パッチは、プロジェクトごとにまとめています。

```text
jetson-lab/
├── setup/                 Nano・TX2の初期設定
├── llama-cpp/
│   ├── README.md          ビルドから推論・性能測定まで
│   ├── server.md          HTTPサーバーの導入・起動
│   ├── usage.md           対話・生成オプションの設定
│   ├── patches/           GCC8・CUDA10.2向け修正とBF16代替ヘッダ
│   └── tools/             サーバー追加・復元・検証用スクリプト
├── ps4-eye/
│   ├── README.md          初期化から顔追跡・距離表示まで
│   ├── scripts/           カメラのPythonコード
│   ├── tools/             ライブラリ確認・データ配置の準備スクリプト
│   ├── calibration/       保存済みの校正データ
│   └── calibration.md     新しいカメラの校正手順
├── work/                  取得したソース・モデル・ビルド結果
└── tools/                 旧調査・保全用ツール
```

カメラの主なコードは次の3本です。校正用・旧試作コードも [scripts/](ps4-eye/scripts/) に残しています。

- [stereo_vision.py](ps4-eye/scripts/stereo_vision.py)：CPU版の顔追跡・距離表示
- [stereo_vision_gpu.py](ps4-eye/scripts/stereo_vision_gpu.py)：VPI CUDAで視差を計算するGPU版
- [benchmark_stereo.py](ps4-eye/scripts/benchmark_stereo.py)：保存した校正画像でCPU/GPUを比較

## 作業場所を用意する

cloneと作業場所の設定は、初期設定の各ページに含めています。`work/` は手順の実行時に作られ、Gitには入りません。

| 作成される場所 | 内容 |
|---|---|
| `work/llama-cpu/build-cpu/bin/` | CPU版のllama.cpp実行ファイル |
| `work/llama-cuda/build-gpu/bin/` | CUDA版のllama.cpp実行ファイル |
| `work/models/` | Qwen3などのGGUFモデル |
| `work/ps4eye/` | カメラのファームウェアローダー |
| `work/ps4-eye/calibration/` | カメラ実行時に読み込む校正データ |
| `work/ps4-eye/models/` | 顔検出モデル |

llama.cppの取得したソースは、それぞれ `work/llama-cpu/` と `work/llama-cuda/` にあります。

## 既存CUDA環境にサーバーを追加する

構築済みのTX2向けllama.cppがある場合は、clone先で実行します。

```bash
bash llama-cpp/tools/setup-server.sh --check
bash llama-cpp/tools/setup-server.sh
```

既存環境を検査し、llama-serverだけを追加ビルドします。標準の `work/llama-cuda` 以外を使う場合の指定方法は [サーバー導入手順](llama-cpp/server.md#スクリプトで追加する) にあります。

## 以前の調査資料

手元のMacの `jetson-rebuild`・`jetson-rebuild-private` は、リポジトリ外の `~/Projects/.archive/jetson/` に退避しています。現在の構築手順はこのリポジトリにまとめています。
