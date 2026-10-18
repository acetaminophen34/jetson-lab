# 基本パッケージとGCC/CMake

## 概要・背景

CMakeはビルドの依存関係やコマンドを生成し、makeは生成された手順を実行します。GCC/G++は実際にC/C++をコンパイル・リンクします。「CMakeの版を変える」と「コンパイラを変える」は異なる操作です。

標準PATHではGCC7.5.0、CMake3.10.2でした。一方、LLMのcacheには`/usr/bin/gcc-8`、`/usr/bin/g++-8`と個別配置CMake3.28.6が残り、実バイナリでもGCC/G++8.4.0を確認しています。OS全体の既定ツールを置換せず、プロジェクトのconfigureで使う実行ファイルを明示します。

## 前提条件

[再構築の入口](nano.md) の共通変数を設定し、OSの一致を確認してから進めます。以下は初期化後の導入手順です。同版を取得できない場合は、配布元または保全debを確認して停止します。

## 基本パッケージ

```bash
apt-cache policy build-essential git make libssl-dev gcc-8 g++-8
sudo apt-get install --no-install-recommends \
  build-essential=12.4ubuntu1 git=1:2.17.1-1ubuntu0.18 make=4.1-9.1ubuntu1 \
  libssl-dev=1.1.1-1ubuntu2.1~18.04.23 \
  gcc-8=8.4.0-1ubuntu1~18.04 g++-8=8.4.0-1ubuntu1~18.04
/usr/bin/gcc-8 --version
/usr/bin/g++-8 --version
```

apt upgradeや最新pipへの一括置換は手順に含めません。OS同梱のGCCを入れ替えるためのupdate-alternatives操作も不要です。失敗時は最初のaptエラーと利用可能な版を確認し、異なる版へ自動的に進めません。

## CMakeをプロジェクト用に展開

元archiveはaarch64版CMake3.28.6です。本体はこのrepoに無いので、別途保全した同一物を指定します。

```bash
export CMAKE_ARCHIVE=/absolute/private/path/cmake-3.28.6-linux-aarch64.tar.gz
printf '%s  %s\n' 7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7 "$CMAKE_ARCHIVE" | sha256sum -c -
test ! -e "$LAB_WORK/cmake-3.28.6-linux-aarch64" || exit 1
tar -xzf "$CMAKE_ARCHIVE" -C "$LAB_WORK"
export LAB_CMAKE="$LAB_WORK/cmake-3.28.6-linux-aarch64/bin/cmake"
"$LAB_CMAKE" --version
```

成功条件はarchiveのhash一致とCMake3.28.6、GCC/G++8.4.0です。既定PATHの値が古いままでも、明示したコマンドが正しければプロジェクト用ツールを使えます。別archや別archiveを同じ名前で代用しません。

## 修正との関係

GCC8向けのfilesystemリンク、ARM NEONの代替、古いコンパイラでの型指定を [patch解説](../llama-cpp/patches/README.md) で扱います。OpenSSL1.1.1はcacheに見つかっていますが、固定CPUソースのHTTPS有効化条件は別です。ローカルモデルを読むだけの動作と、HTTPSでダウンロードできることを混同しません。

## 確認とトラブルシューティング

元ツールの版は実機で確認済み、上の新規インストールと新規展開からのビルドは未検証です。

## Python・カメラ用ライブラリ

カメラのパッケージ導入コマンドは [PS4 Eyeの構築](../ps4-eye/README.md#構築) にまとめています。

| 項目 | 使用版・機能 |
|---|---|
| Python / pip | 3.6.9 / 9.0.1 |
| OpenCV | 4.1.1、libopencv=4.1.1-2-gd5a58aa75 |
| cv2 | /usr/lib/python3.6/dist-packages/cv2/python-3.6配下のaarch64拡張 |
| OpenCVの機能 | V4L2 YES、FFmpeg YES、GStreamer1.14.5 |
| NumPy / Flask / PyUSB | 1.13.3 / 0.12.2 / 1.0.0 |
| v4l-utils / libusb | 1.14.2-1 / 2:1.0.21-2 |
| 上流viewer用Matplotlib / SciPy | 2.1.1 / 0.19.1（独自6本には必須ではない） |
| OpenMP | 4.5、libgomp/pthread |

OpenCVをこの実機で独自ビルドしたかは不明です。OpenCVのbuild情報にあるコンパイラ版と、llama.cppに指定するGCC8.4は別です。
