# Jetson Nano / TX2の構築メモ

Nano 4GB（JetPack4.6.1）とTX2（JetPack4.6.6）の構築メモです。

| 記事 | 内容 |
|---|---|
| [Nanoの初期設定](setup/nano.md) | MacでSD作成、初回起動、SSH接続 |
| [TX2の環境構築](setup/tx2.md) | JetPack4.6.6、CUDA10.2、GCC8.4、CMake3.28.6 |
| [Nanoの基本環境](setup/packages.md) | Python、Git、CUDA、OpenCV、TensorRT、jtop |
| [llama.cpp](llama-cpp/README.md) | CPUビルド、Qwen3推論、ベンチマーク |
| [GPUビルド](llama-cpp/gpu.md) | Nano / TX2のCUDA10.2対応、TX2で生成20.47 tokens/s |
| [PS4 Eye](ps4-eye/README.md) | firmwareロード、撮影・配信、自作Python6本 |
| [校正・距離計算](ps4-eye/calibration.md) | 校正撮影、視差・深度処理 |

記事・patchは `~/Projects/jetson-lab`、ビルド作業は `~/jetson-work` に置く例です。
