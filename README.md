# Jetson Nanoの構築メモ

Jetson Nano 4GB Developer Kit / JetPack4.6.1で、llama.cppとPS4 Eyeを使うためのメモです。

| 記事 | 内容 |
|---|---|
| [初期設定](setup/nano.md) | MacでSD作成、初回起動、SSH接続 |
| [基本環境](setup/packages.md) | Python、Git、CUDA、OpenCV、TensorRT、jtop |
| [llama.cpp](llama-cpp/README.md) | CPUビルド、Qwen3推論、ベンチマーク |
| [GPUビルド](llama-cpp/gpu.md) | CUDA10.2対応 |
| [PS4 Eye](ps4-eye/README.md) | firmwareロード、撮影・配信、自作Python6本 |
| [校正・距離計算](ps4-eye/calibration.md) | 校正撮影、視差・深度処理 |

記事・patchは `~/Projects/jetson-lab`、ビルド作業は `~/jetson-work` に置く例です。
