# llama.cppの使い方

モデルの配置は [導入記事](README.md#モデルを用意する) を参照してください。`llama-cli` は文章生成・対話、`llama-bench` は性能測定に使います。

## 1. 実行ファイルのあるフォルダへ移動する

**Nano CPU：**

```bash
cd ~/jetson-work/llama-cpu/build-cpu/bin
```

**TX2 CUDA：**

```bash
cd ~/jetson-work/llama-tx2/build-gpu/bin
```

以下はこのディレクトリから実行します。CPUは `-ngl 0`、TX2のGPU実行は `-ngl 99` です。TX2のCUDA版でも `-ngl 0` でCPU実行できます。

## 2. 文章を生成する

CPUで1回だけ回答させる例です。`-st` は1回の応答で終了します。

```bash
LD_LIBRARY_PATH=. ./llama-cli \
  -m ~/jetson-work/models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -c 512 -n 64 -st -p "こんにちは。簡単に自己紹介してください。"
```

TX2で使ったGPU推論コマンドです。

```bash
LD_LIBRARY_PATH=. ./llama-cli \
  -m ~/jetson-work/models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -c 512 -n 64 \
  -p "こんにちは。簡単に自己紹介してください。"
```

## 3. 主な設定

引数はd3bd7193b（build5092）が基準です。NanoのCPU構成は62df1815bを使っています。

| オプション | 内容 | 設定例 |
|---|---|---|
| `-m` | GGUFモデルのパス | `-m ~/jetson-work/models/Qwen3-0.6B-Q4_K_M.gguf` |
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

## 4. 日本語で対話する

`>` に質問を入力してEnterを押します。入力待ちのCtrl+Cで終了、生成中のCtrl+Cで入力へ戻ります。TX2のGPU実行では `-ngl 99` に変えます。

```bash
LD_LIBRARY_PATH=. ./llama-cli \
  -m ~/jetson-work/models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -c 1024 -n 256 --temp 0.7 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

[Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) は通常 `<think>` に思考内容を出します。`/no_think` は内容を省略させるQwen3固有の指示で、llama.cppのオプションではありません。

## 5. モデルを変える

0.6B / 1.7Bはパラメータ数、Q4_K_M / Q5_K_M / Q8_0は量子化形式です。取得済みのGGUFへ切り替えるには、`-m` のファイル名を変更します。

```bash
LD_LIBRARY_PATH=. ./llama-cli \
  -m ~/jetson-work/models/Qwen3-1.7B-Q4_K_M.gguf \
  -ngl 99 -t 4 -c 512 -n 128 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

## 6. ベンチマーク

`-p 128` は入力128トークン、`-n 32` は生成32トークン、`-r 3` は3回反復です。CLIの `-p`（質問文）とは意味が異なります。

```bash
LD_LIBRARY_PATH=. ./llama-bench \
  -m ~/jetson-work/models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -p 128 -n 32 -r 3
```

CPUは `-ngl 0`、スレッド数をまとめて測る場合は `-t 1,2,4` に変更します。pp128は入力処理、tg32は文章生成の速度（tokens/s）です。

### Nano CPU：以前から使用していたモデル

| スレッド | pp128 | tg32 |
|---:|---:|---:|
| 1 | 3.85 | 1.98 |
| 2 | 7.63 | 3.85 |
| 4 | 13.65 | 5.62 |

### TX2 CUDA：Unsloth版

| モデル | pp128 | tg32 |
|---|---:|---:|
| Qwen3-0.6B Q4_K_M | 77.88 ± 0.59 | 20.47 ± 0.09 |
| Qwen3-1.7B Q4_K_M | 25.25 | 9.84 |

0.6Bでは全29レイヤーをGPUへオフロードしました。

```text
Device 0: NVIDIA Tegra X2, compute capability 6.2
offloaded 29/29 layers to GPU
CUDA0 model buffer size = 372.65 MiB
```

### Nanoの短いプロンプト測定

上のベンチマークとは別に、62df1815bを使って短い質問への応答速度を測りました。CPUは2スレッド、会話を保持する枠は512トークン、回答の上限は32トークンです。

```bash
cd ~/jetson-work/llama-cpu
CUDA_VISIBLE_DEVICES='' OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 \
  LD_LIBRARY_PATH=./build-cpu/bin \
  ./build-cpu/bin/llama-cli -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  --device none --n-gpu-layers 0 --no-kv-offload \
  --threads 2 --threads-batch 2 --ctx-size 512 \
  --batch-size 32 --ubatch-size 32 --n-predict 32 --single-turn \
  --reasoning off --no-warmup --perf --seed 1 --temp 0 --simple-io \
  -p 'Reply with exactly: CPU test OK.' < /dev/null
```

| 応答 / 終了コード | Prompt / Generation | 時間 / 最大RSS |
|---|---|---|
| CPU test OK. / 0 | 7.4 / 3.8 tokens/s | 7.326秒 / 約583MiB |

`no usable GPU found` 警告は出ましたが、CPU推論は成功しました。

## 7. 調整の目安

- 速度・品質：モデルサイズと量子化を選ぶ。大きいモデル・高ビット量子化ほどメモリを使い、一般に遅くなる。
- メモリ：モデルサイズと `-c` を抑える。JetsonはCPU/GPUでRAMを共有する。
- CPU/GPU負荷：`-t` と `-ngl` で調整する。
- 回答の長さ：`-n` と「3行で答えて」などの指示を使う。
- ばらつき：`--temp` を低くすると小さくなる。
