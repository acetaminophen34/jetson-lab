# GCC8.4とCMake3.28.6を入れる

## 1. 基本パッケージとGCC/G++8.4.0

Nano標準PATHはGCC7.5.0・CMake3.10.2でしたが、llama.cppにはGCC/G++8.4.0とCMake3.28.6を使っていました。OSの既定コンパイラは置換せず、ビルド時にgcc-8/g++-8を指定します。

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends \
  build-essential=12.4ubuntu1 make=4.1-9.1ubuntu1 \
  git=1:2.17.1-1ubuntu0.18 libssl-dev=1.1.1-1ubuntu2.1~18.04.23 \
  gcc-8=8.4.0-1ubuntu1~18.04 g++-8=8.4.0-1ubuntu1~18.04 \
  wget ca-certificates
gcc-8 --version
g++-8 --version
```

取得先はOSのapt設定にある [Ubuntu Ports](https://ports.ubuntu.com/ubuntu-ports/) とNVIDIAのJetPack配布先です。同版が見つからなければ `apt-cache policy gcc-8 g++-8 libssl-dev` で確認します。既存環境の版は確認済みですが、現在のaptでの同版取得と上のインストールは未検証です。

## 2. CMakeのaarch64バイナリを取得する

[Kitware公式v3.28.6リリース](https://github.com/Kitware/CMake/releases/tag/v3.28.6) のaarch64版を展開します。配布のSHA256は使用したarchiveと一致しています。

```bash
mkdir -p ~/opt
cd ~/Downloads
wget https://github.com/Kitware/CMake/releases/download/v3.28.6/cmake-3.28.6-linux-aarch64.tar.gz
echo '7909cc2128ce9442c63ce674a0bfb0e4f4ce04cef667d887e15ad5670d594ba7  cmake-3.28.6-linux-aarch64.tar.gz' | sha256sum -c -
tar -xzf cmake-3.28.6-linux-aarch64.tar.gz -C ~/opt
~/opt/cmake-3.28.6-linux-aarch64/bin/cmake --version
```

CMakeはコンパイルの手順を生成するツールです。以降はこの絶対パスを使うため、PATHやシステムのCMakeを変更する必要はありません。

## 3. プロジェクトへ進む

[llama.cppのCPU構築](../llama-cpp/README.md) または [PS4 Eye](../ps4-eye/README.md) へ進みます。カメラのPython/OpenCV等はカメラの記事に導入コマンドをまとめています。
