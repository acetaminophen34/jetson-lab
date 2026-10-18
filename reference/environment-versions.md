# 環境の版・ファイル識別子

このページは版とhashの正本です。初回/追加調査、保存CMake、過去の実機照会を統合した値で、新たな実機調査は行っていません。各手順では必要な値だけを引用します。

## 基盤とツール

| 項目 | 確認値 | 根拠/区分 |
|---|---|---|
| 再構築目標 | JetPack4.6.1 | 指定目標。元イメージとメタパッケージは未確定 |
| OS | Ubuntu18.04.6 LTS、aarch64 | 実機記録 |
| カーネル/L4T | 4.9.253-tegra、R32.7.1、t210ref | 実機記録 |
| nvidia-l4t-core | 32.7.1-20220219090432 | dpkg |
| 標準GCC/CMake | 7.5.0 / 3.10.2 | 標準PATHの実機記録 |
| プロジェクトGCC/G++ | 8.4.0、dpkg8.4.0-1ubuntu1~18.04 | dpkgと実バイナリ確認 |
| プロジェクトCMake | 3.28.6 aarch64 | cacheと実バイナリ確認 |
| nvcc / CUDA toolkit package | 10.2.300 / 10.2.460-1 | 別種類の版を区別する |
| cuDNN | libcudnn8=8.2.1.32-1+cuda10.2 | dpkg、llamaの利用証明ではない |
| TensorRT | tensorrt=8.2.1.8-1+cuda10.2、Python8.2.1.8 | dpkgとPython記録 |
| OpenMP | 4.5、libgomp/pthread | CMake記録 |
| OpenSSL開発package | 1.1.1-1ubuntu2.1~18.04.23 | dpkg。HTTPS有効化は別条件 |
| build-essential / make / git | 12.4ubuntu1 / 4.1-9.1ubuntu1 / 1:2.17.1-1ubuntu0.18 | dpkg |
| メモリ/媒体 | RAM表示3.9G、root mmcblk0p1 ext4、29.7G | 観測時点の表示 |
| swap | zram4個×495.5MiB | 観測時点 |
| タイムゾーン | America/New_York（EDT,-0400） | 変更しない |

## Python・カメラ関連

| 項目 | 確認値 |
|---|---|
| Python / pip | 3.6.9 / 9.0.1 |
| OpenCV | 4.1.1、libopencv=4.1.1-2-gd5a58aa75 |
| cv2配置 | /usr/lib/python3.6/dist-packages/cv2/python-3.6配下のaarch64拡張 |
| cv2ビルド機能 | V4L2 YES、FFmpeg YES、GStreamer1.14.5、/usrへ導入 |
| NumPy | 1.13.3、python3-numpy=1:1.13.3-2ubuntu1 |
| Flask | 0.12.2、python3-flask=0.12.2-3ubuntu0.1 |
| PyUSB | 1.0.0、python3-usb=1.0.0-1 |
| v4l-utils | 1.14.2-1 |
| libusb runtime/dev | 2:1.0.21-2 |
| 旧viewer向けMatplotlib / SciPy | 2.1.1 / 0.19.1（独自6本の全てに必要という意味ではない） |
| jetson-stats | 4.3.2（既存pip記録） |

OpenCVをこの実機で独自ビルドした証拠は未保存です。build情報のコンパイラ版はライブラリが作られた時の値で、LLMのGCC8.4とは別です。

## 再配置するファイル

| 資産 | bytes | SHA-256 |
|---|---:|---|
| Qwen3-0.6B-Q4_K_M.gguf | 484220000 | 7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d |
| CMake3.28.6 aarch64 archive | 53907530 | 7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7 |
| firmware_V2.bin | 64036 | 141454ec1e57a5d0f400b4a345aefb37a7b8178eb9bf9abc25187c27f34a1da4 |
| stereo_calibration.npz | 3610 | e3dd00dab470d03cbddaa9af18bc5117777919291a0c6e333d322dfd24f7b9ce |
| CUDA代替cuda_bf16.h | 144 | bfe47be09ef61153bea805be2c8121e47cd400686ac40a396e373679ebbe8490 |
| 既存CPU llama-cli | 1249008 | db710ff78b0f69636620b609acd1ab35ed84b2d1bbeaf9f28a03698b98ae21d0 |

モデル/CMake archive本体は過去の回収対象に含めておらず、初期化前の別途保全が必要です。firmwareは元bundle、校正と画像は非公開保全先にあります。各assetの利用/再配布許諾までhashが証明するわけではありません。

## 詳細資料

- [CMake設定抽出](details/build-settings.md)、[linkとBF16依存記録](details/current-build-links.md)
- [既存生成物とELF依存](details/binary-inventory.md)
- [初回67件の指紋](details/backup-inventory.md)、[回収/実行証跡の指紋](details/recovery-manifest.md)
- [出典](sources.md)
