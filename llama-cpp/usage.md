# llama.cppの使い方：Nano / TX2

`llama-cli` は文章生成・対話、`llama-bench` は性能測定に使います。引数は **d3bd7193b（build 5092）** が基準です。Nanoの[CPUビルド記事](README.md)は62df1815bですが、以下では両版にある基本引数を使います。

## 1. モデルを実行する

GGUFは `~/jetson-work/models/` に配置します。実行パスは既存の[CPU記事](README.md)・[GPU記事](gpu.md)に合わせています。

### Nano：CPU版

`-p` に質問を渡します。`-st` は1回の応答で終了する指定です。

```bash
cd ~/jetson-work/llama-cpu
LD_LIBRARY_PATH=./build-cpu/bin ./build-cpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -c 512 -n 64 -st -p "こんにちは。簡単に自己紹介してください。"
```

### TX2：CPUで実行

既存のCUDA版バイナリで、GPUオフロードを無効にします。

```bash
cd ~/jetson-work/llama-tx2
LD_LIBRARY_PATH=./build-gpu/bin ./build-gpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -c 512 -n 64 -st -p "こんにちは。簡単に自己紹介してください。"
```

### TX2：CUDAで実行

同じバイナリで `-ngl 99` を指定します。NanoのCUDA版は[別手順](gpu.md#nano)で、ここでは使用しません。

```bash
cd ~/jetson-work/llama-tx2
LD_LIBRARY_PATH=./build-gpu/bin ./build-gpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -c 512 -n 64 -st -p "こんにちは。簡単に自己紹介してください。"
```

## 2. 主な設定

以下は `llama-cli` の引数です。

| オプション | 内容 | 設定例 |
|---|---|---|
| `-m` | GGUFモデルのパス | `-m ../models/Qwen3-0.6B-Q4_K_M.gguf` |
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

詳細は使うバイナリの `--help` を参照します。

```bash
# Nano
~/jetson-work/llama-cpu/build-cpu/bin/llama-cli --help
# TX2
~/jetson-work/llama-tx2/build-gpu/bin/llama-cli --help
```

## 3. 日本語で対話する

`-cnv` で起動し、`>` が出たら質問を入力してEnterを押します。終了は入力待ちでCtrl+C。生成中のCtrl+Cは生成を止めて入力へ戻ります。

### Nano：CPU

```bash
cd ~/jetson-work/llama-cpu
LD_LIBRARY_PATH=./build-cpu/bin ./build-cpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -c 1024 -n 256 --temp 0.7 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

### TX2：CUDA

```bash
cd ~/jetson-work/llama-tx2
LD_LIBRARY_PATH=./build-gpu/bin ./build-gpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -c 1024 -n 256 --temp 0.7 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

[Qwen3](https://huggingface.co/Qwen/Qwen3-0.6B) は通常 `<think>...</think>` に思考内容を出します。`/no_think` はその内容を省略させるQwen3固有の指示で、llama.cppのオプションではありません。空のthinkタグが残ることはあります。

## 4. モデルを変更する

0.6B / 1.7Bはパラメータ数、Q4_K_M / Q5_K_M / Q8_0は量子化形式です。一般に大きいモデルや高ビットの量子化ほどメモリを使い、推論は遅くなりますが、回答品質を保ちやすくなります。

取得済みの別GGUFへ切り替えるには `-m` を変更します。TX2で1.7Bを使う例です。

```bash
cd ~/jetson-work/llama-tx2
LD_LIBRARY_PATH=./build-gpu/bin ./build-gpu/bin/llama-cli \
  -m ../models/Qwen3-1.7B-Q4_K_M.gguf \
  -ngl 99 -t 4 -c 512 -n 128 -cnv \
  -sys "あなたは日本語で簡潔に回答するアシスタントです。/no_think"
```

## 5. ベンチマーク

`llama-bench` の `-p 128` は入力128トークン、`-n 32` は生成32トークン、`-r 3` は3回反復です。CLIの `-p`（プロンプト文字列）とは意味が異なります。

### Nano：CPU

```bash
cd ~/jetson-work/llama-cpu
LD_LIBRARY_PATH=./build-cpu/bin ./build-cpu/bin/llama-bench \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -p 128 -n 32 -r 3
```

### TX2：CPU / CUDA

CPU実行は `-ngl 0`、CUDA実行は `-ngl 99` にします。

```bash
cd ~/jetson-work/llama-tx2
LD_LIBRARY_PATH=./build-gpu/bin ./build-gpu/bin/llama-bench \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 4 -p 128 -n 32 -r 3

LD_LIBRARY_PATH=./build-gpu/bin ./build-gpu/bin/llama-bench \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 99 -t 4 -p 128 -n 32 -r 3
```

`pp128` は入力処理速度、`tg32` は文章生成速度で、単位はtokens/sです。以下は**TX2のCUDA版**で測定した結果です。

| モデル | pp128 | tg32 |
|---|---:|---:|
| Qwen3-0.6B Q4_K_M | 77.88 | 20.47 |
| Qwen3-1.7B Q4_K_M | 25.25 | 9.84 |

## 6. 設定の調整

- **速度・品質**：モデルサイズと量子化を選ぶ。速度優先なら小さいモデル、品質優先なら大きいモデルや高ビット量子化を試す。
- **メモリ**：モデルサイズと `-c` を抑える。`-ngl` は配置先を変えるが、JetsonではCPU/GPUでRAMを共有する。
- **CPU/GPU負荷**：`-t` でCPUスレッド数、`-ngl` でGPUへ渡すレイヤー数を変える。
- **回答の長さ**：`-n` と「3行で答えて」などのプロンプトで調整する。
- **回答のばらつき**：`--temp` を低くすると小さく、高くすると大きくなる。
