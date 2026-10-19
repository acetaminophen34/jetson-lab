# llama.cppの設定・対話

基本の構築・実行・ベンチマークは [README](README.md) にまとめています。以下は同じターミナルで、READMEで選んだ実行ファイルを使います。

```bash
cd "$LLAMA_BIN"
```

## 主な設定

引数はd3bd7193b（build5092）が基準です。NanoのCPU構成は62df1815bを使っています。

| オプション | 内容 | 設定例 |
|---|---|---|
| `-m` | GGUFモデルのパス | `-m "$JETSON_LAB/work/models/Qwen3-0.6B-Q4_K_M.gguf"` |
| `-ngl` | GPUへ配置するレイヤー数。0でCPU実行 | `-ngl 0` / `-ngl 99` |
| `-t` | CPUスレッド数 | `-t 4` |
| `-c` | 入力・会話履歴・出力を保持するコンテキスト長 | `-c 512` |
| `-n` | 1回の応答で生成する最大トークン数 | `-n 128` |
| `--temp` | 生成のランダム性。低いほどばらつきが小さい | `--temp 0.7` |
| `-sys` | システムプロンプト | `-sys "日本語で簡潔に回答してください。"` |
| `-p` | 初期プロンプト | `-p "自己紹介してください。"` |
| `-cnv` | 対話モード | `-cnv` |
| `--seed` | 乱数シード | `--seed 42` |

`-ngl 99` はモデルの全レイヤーをGPUへ配置するための大きめの値で、99層あるという意味ではありません。`-c` は会話を保持する枠、`-n` は回答の長さの上限です。

詳細は `./llama-cli --help` を参照します。

## 日本語で対話する

`>` に質問を入力してEnterを押します。入力待ちのCtrl+Cで終了、生成中のCtrl+Cで入力へ戻ります。CPU実行は `GPU_LAYERS=0`、GPU実行は `GPU_LAYERS=99` を使います。

```bash
LD_LIBRARY_PATH=. ./llama-cli \
  -m "$JETSON_LAB/work/models/Qwen3-0.6B-Q4_K_M.gguf" \
  -ngl "$GPU_LAYERS" -t 4 -c 1024 -n 256 --temp 0.7 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

[Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) は通常 `<think>` に思考内容を出します。`/no_think` は内容を省略させるQwen3固有の指示で、llama.cppのオプションではありません。

## モデルを変える

0.6B / 1.7Bはパラメータ数、Q4_K_M / Q5_K_M / Q8_0は量子化形式です。取得済みのGGUFへ切り替えるには、`-m` のファイル名を変更します。

```bash
LD_LIBRARY_PATH=. ./llama-cli \
  -m "$JETSON_LAB/work/models/Qwen3-1.7B-Q4_K_M.gguf" \
  -ngl "$GPU_LAYERS" -t 4 -c 512 -n 128 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

## 調整の目安

- 速度・品質：モデルサイズと量子化を選ぶ。大きいモデル・高ビット量子化ほどメモリを使い、一般に遅くなる。
- メモリ：モデルサイズと `-c` を抑える。JetsonはCPU/GPUでRAMを共有する。
- CPU/GPU負荷：`-t` と `-ngl` で調整する。
- 回答の長さ：`-n` と「3行で答えて」などの指示を使う。
- ばらつき：`--temp` を低くすると小さくなる。


## サーバーを起動したまま使う

[常駐サーバー手順](server.md)を参照してください。既存build5092に`llama-server`だけを追加し、`/completion`とメモリ内KVキャッシュを使います。実機の作業パス、バージョン固定、メモリ制約、既存CLIとの差も同ページにまとめています。
