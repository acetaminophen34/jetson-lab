# Nanoでllama.cppとQwen3を動かす

[llama.cpp](https://github.com/ggml-org/llama.cpp) でQwen3-0.6BをCPU実行します。クリーンビルドは未検証です。

ビルド後の操作は [使い方：Nano / TX2](usage.md) を参照してください。

## 1. GCC8.4とCMake3.28.6を入れる

[基本環境](../setup/packages.md) の準備後、GCC8とOpenSSL開発用ヘッダを入れます。システム標準のGCC/CMakeは残します。

```bash
apt-cache policy gcc-8 g++-8 libssl-dev
sudo apt install --no-install-recommends --no-upgrade \
  gcc-8=8.4.0-1ubuntu1~18.04 g++-8=8.4.0-1ubuntu1~18.04 \
  libssl-dev=1.1.1-1ubuntu2.1~18.04.23
gcc-8 --version
g++-8 --version
```

[Kitware公式](https://github.com/Kitware/CMake/releases/tag/v3.28.6) のLinux aarch64版を展開します。

```bash
mkdir -p ~/opt ~/Downloads
cd ~/Downloads
wget https://github.com/Kitware/CMake/releases/download/v3.28.6/cmake-3.28.6-linux-aarch64.tar.gz
echo '7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7  cmake-3.28.6-linux-aarch64.tar.gz' | sha256sum -c -
tar -xzf cmake-3.28.6-linux-aarch64.tar.gz -C ~/opt
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

## 2. ソース取得とpatch適用

使用コミットへ切り替え、[Nano用patch](patches/llama.patch) を適用します。[変更理由](patches/README.md) はNEON互換、stdc++fsリンク、include・型指定の補完です。

```bash
mkdir -p ~/jetson-work
cd ~/jetson-work
git clone https://github.com/ggml-org/llama.cpp.git llama-cpu
cd llama-cpu
git checkout 62df1815bc053066761f4eac58e288f23778e164
git apply --check ~/Projects/jetson-lab/llama-cpp/patches/llama.patch
git apply ~/Projects/jetson-lab/llama-cpp/patches/llama.patch
```

## 3. CPU版をビルドする

CUDAを無効化してGCC8を指定します。このコミットのCLIビルドにはSERVER=ONが必要です。

```bash
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake -S . -B build-cpu \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_C_COMPILER=/usr/bin/gcc-8 -DCMAKE_CXX_COMPILER=/usr/bin/g++-8 \
  -DGGML_CUDA=OFF -DGGML_NATIVE=OFF -DGGML_BLAS=OFF -DGGML_OPENMP=ON \
  -DLLAMA_BUILD_SERVER=ON -DLLAMA_BUILD_TOOLS=ON \
  -DLLAMA_OPENSSL=ON -DOPENSSL_NO_ASM=ON \
  -DLLAMA_BUILD_MTMD=OFF -DLLAMA_BUILD_UI=OFF -DLLAMA_USE_PREBUILT_UI=OFF
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --build build-cpu \
  --target llama-cli llama-bench --parallel 1
```

実行ファイルと共有ライブラリは `build-cpu/bin/` に生成されます。PREBUILT_UI=OFFは外部UI資産を取得しないための指定です。

## 4. モデルを配置する

使用モデルは `Qwen3-0.6B-Q4_K_M.gguf`（484220000bytes）です。同一ファイルの公開URLは不明なので、手元のファイルを配置します。

```bash
mkdir -p ~/jetson-work/models
cp ~/Downloads/Qwen3-0.6B-Q4_K_M.gguf ~/jetson-work/models/
cd ~/jetson-work/models
echo '7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d  Qwen3-0.6B-Q4_K_M.gguf' | sha256sum -c -
```

新規取得なら [Unsloth版](https://huggingface.co/unsloth/Qwen3-0.6B-GGUF) もあります。**上のモデルとは別ファイルで動作未検証**です（Apache-2.0）。以下は元モデルを配置していない場合の取得例です。

```bash
mkdir -p ~/jetson-work/models
cd ~/jetson-work/models
wget -O Qwen3-0.6B-Q4_K_M.gguf \
  https://huggingface.co/unsloth/Qwen3-0.6B-GGUF/resolve/50968a4468ef4233ed78cd7c3de230dd1d61a56b/Qwen3-0.6B-Q4_K_M.gguf
echo 'ac2d97712095a558e31573f62f466a3f9d93990898b0ec79d7c974c1780d524a  Qwen3-0.6B-Q4_K_M.gguf' | sha256sum -c -
```

## 5. CPUで推論する

通常はGPUオフロードなし・4スレッドで使っていました。運用時のモデル保存先は `~/robi-llm/models/` です。

```bash
cd ~/jetson-work/llama-cpu
LD_LIBRARY_PATH=./build-cpu/bin ./build-cpu/bin/llama-cli \
  -m ../models/Qwen3-0.6B-Q4_K_M.gguf -ngl 0 -t 4
```

## 6. ベンチマーク

prompt128・生成32トークン、3回反復の測定条件です。

```bash
./build-cpu/bin/llama-bench -m ../models/Qwen3-0.6B-Q4_K_M.gguf \
  -ngl 0 -t 1,2,4 -p 128 -n 32 -r 3
```

| スレッド | Prompt t/s | Generation t/s |
|---:|---:|---:|
| 1 | 3.85 | 1.98 |
| 2 | 7.63 | 3.85 |
| 4 | 13.65 | 5.62 |

### 短いプロンプトでの別測定

2スレッド、ctx512、生成上限32での実行条件です。

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

いずれも元モデルでの測定値です。`no usable GPU found` 警告は出ましたが、CPU推論は成功しました。

## GPU版

[CUDA10.2用のビルド手順](gpu.md) は別ツリーで行います。GPU起動時に電源容量不足で落ちたため、ACアダプタへ切り替えるまではCPUのみで運用していました。
