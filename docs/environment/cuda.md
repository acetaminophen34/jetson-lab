# CUDA10.2と生成コードの対象

## 概要・仕組み

CUDAを使うC++プロジェクトには、GPUのドライバ、nvccコンパイラ、runtime、GPU向けライブラリが関係します。`nvcc --version`だけでドライバやリンク結果まで同じと判定することはできません。

nvccはGPU向けのdevice codeとCPU側のhost codeを扱います。この環境ではhost compilerをG++8.4.0へ明示し、CUDA側はC++14で生成する設定が残っています。CPU用C++17のコードと、CUDA側のC++14は同じプロジェクト内でも別の指定です。

## 環境と前提条件

nvccの実表示は10.2.300、CUDA toolkitのdpkg版は10.2.460-1です。別の構成要素の版なので、数字が異なることを破損とは判断しません。CPU専用経路ではCUDAもBF16代替ヘッダもビルド要件にしません。

GPU側は`libcudart.so.10.2`、`libcublas.so.10`、`libcuda.so.1`への直接依存を保存ELFから確認しています。検索cacheに見つかった全CUDAライブラリを、実際にリンクしたとは扱いません。

## アーキテクチャ指定を確認する

`CMAKE_CUDA_ARCHITECTURES`は生成するGPUコードの対象です。CMakeCacheは設定の保存値、compile_commandsは生成コマンドの記録で、両方を見る必要があります。

| 構成 | cache値 | 生成コマンド | 判定 |
|---|---|---|---|
| 新しいllama.cpp/build-gpu | 53 | compute_53 / sm_53 | 設定は一致、新規ビルド成功は未確認 |
| llama5050gpu.cpp/build | 53 | compute_50 / sm_50 と compute_61 / sm_61 | 原patchの条件式による上書きが説明になる |
| llama-qwen3-gpu/build | 53 | compute_53 / sm_53 | 設定は一致、既存bench/.soは存在 |

b5050の`if(NOT DEFINED ${CMAKE_CUDA_ARCHITECTURES})`は、変数名ではなく展開した値を存在確認へ渡します。そのためcache53でも通常変数を50/61へ変更する解析が成り立ちます。原patchはこの状態のまま保存しており、修正案を混ぜていません。

## 再構築時の確認方法

```sh
/usr/local/cuda-10.2/bin/nvcc --version
readlink -f /usr/local/cuda
# GPU configureを実施した後の確認例。ここではビルドを開始しない。
rg 'CMAKE_CUDA_(ARCHITECTURES|STANDARD|HOST_COMPILER)' "$GPU_BUILD/CMakeCache.txt"
rg -- '--generate-code' "$GPU_BUILD/compile_commands.json"
```

`rg`が未導入なら`grep -E`へ読み替えられます。成功条件は、選んだ構成の記録と生成対象が説明できることです。失敗時はPATH、host compiler、別構成のpatch、CMake条件式を確認します。

## BF16の互換処置

古いCUDAヘッダに合わせる処置として`cuda_bf16.h`を追加しています。ただし実体は`nv_bfloat16`を`half`へ置き換える代替です。BF16とFP16は同じ16bitでも数値の表現が違い、正しいBF16演算を実装したわけではありません。用途と配置は [patch解説](../projects/llama-cpp/patches.md) と [GPU手順](../projects/llama-cpp/gpu-build.md) を正本にしています。

## 動作確認・制約

この資料のGPU経路は設定/既存ファイルの確認までです。GPU起動時に落ちたという説明はユーザー申告で、安定したGPU推論や速度を保証しません。TX2向けarchも未確認なのでNano値を流用しません。

## 参照資料

- [出典S2・S3](../../reference/sources.md)、[ビルドメタデータ](../../reference/details/build-settings.md)、[リンクとBF16依存記録](../../reference/details/current-build-links.md)
