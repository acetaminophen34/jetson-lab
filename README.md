# Jetson Nanoの構築メモ

Jetson Nanoでllama.cppとPS4 Eyeを使うためのメモです。短い説明と、ターミナルへ入力するコマンドを順番に載せています。

| 対象 | 内容 |
|---|---|
| [Nanoの準備](setup/nano.md) | JetPack4.6.1、Ubuntu18.04、CUDA10.2 |
| [GCC・CMake](setup/packages.md) | GCC/G++8.4.0、CMake3.28.6の導入 |
| [llama.cpp](llama-cpp/README.md) | ソース取得、Nano用patch、CPUビルド、Qwen3推論 |
| [GPU版](llama-cpp/gpu.md) | CUDA10.2用patchと追加ビルド手順 |
| [PS4 Eye](ps4-eye/README.md) | firmwareロード、RGB配信、自作Python6本 |
| [校正・距離計算](ps4-eye/calibration.md) | 校正撮影、NPZ、視差から深度を求める処理 |

実機はNano（aarch64、RAM約4GB）です。過去会話から復元した履歴では、10月14日にQwen3のCPUベンチマークで4スレッド5.62 t/s、10月15日にPS4 Eyeの撮影・Safari配信・相対視差表示に成功していました。後日の2スレッド3.8 tokens/sは別測定です。

カメラは現在再検証しておらず、校正済み絶対距離精度は未確認です。クリーンビルド・GPU安定動作・[TX2への適用](setup/tx2.md)も未検証です。

作業用の例は `~/jetson-work`、この記事とpatchは `~/Projects/jetson-lab` に置きます。別の場所を使う場合はコマンド内のパスを読み替えてください。掲載した取得・構築コマンドは既存設定から整理した未検証の手順であり、過去の端末履歴をそのまま再録したものではありません。
