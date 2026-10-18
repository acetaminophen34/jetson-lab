# NanoのOSとJetPackを用意する

## 1. JetPack4.6.1を選ぶ

[JetPack4.6.1公式ページ](https://developer.nvidia.com/embedded/jetpack-sdk-461) から、ボードに合うイメージを選びます。JetPackはOS・ドライバ・GPUライブラリの組合せで、以下の版を基準にします。

| 構成 | 役割・使用版 |
|---|---|
| L4T | Jetson用カーネルとドライバ。R32.7.1、kernel4.9.253-tegra |
| Ubuntu | Linuxのユーザー環境。18.04.6 LTS、aarch64 |
| CUDA | GPUのコンパイラ/runtime。nvcc10.2.300、cuda-toolkit-10-2=10.2.460-1 |
| cuDNN | ニューラルネットワーク演算。libcudnn8=8.2.1.32-1+cuda10.2 |
| TensorRT | 推論の最適化/runtime。tensorrt=8.2.1.8-1+cuda10.2 |

llama.cppのGPU経路はCUDA runtimeとcuBLASを使い、cuDNN/TensorRT経由ではありません。nvccの表示版とtoolkitパッケージ版は別の識別子です。

## 2. OSイメージを入手する

次は公式ページが案内するNano開発キット用4.6.1 SDイメージの取得例です。ダウンロードURLの応答は確認しましたが、元環境で使ったイメージとの一致は未確認です。Nano 2GB、eMMC搭載モジュール、別キャリアでは適合イメージ・flash方法を選び直してください。

```bash
mkdir -p ~/Downloads
cd ~/Downloads
wget https://developer.nvidia.com/embedded/l4t/r32_release_v7.1/jp_4.6.1_b110_sd_card/jeston_nano/jetson-nano-jp461-sd-card-image.zip
```

書き込みは [Nano公式ガイド](https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-devkit) に従います。元のボード型番・flash指定が未確定のため、媒体を上書きするコマンドはここには載せていません。

## 3. 起動後に版を確認する

L4T32.7.1・Ubuntu18.04系になっていることを確認します。タイムゾーンは変更しません。

```bash
cat /etc/os-release
cat /etc/nv_tegra_release
uname -m
dpkg-query -W nvidia-l4t-core cuda-toolkit-10-2 libcudnn8 tensorrt
```

使用環境のnvidia-l4t-coreは32.7.1-20220219090432でした。CUDAなどが無い場合は、[JetPack4.6.1の導入案内](https://developer.nvidia.com/embedded/jetpack-sdk-461) のSDK Manager/パッケージ手順を使い、4.6.1向けの版を選びます。PC向けCUDA installerや最新JetPackへの置換は行いません。

## 4. 開発ツールを入れる

次は [GCC・CMakeの導入](packages.md) です。記事とコードは `~/Projects/jetson-lab` に配置し、新しい作業先を作ります。

```bash
mkdir -p ~/jetson-work
```

NanoのRAM表示は約3.9G、root媒体29.7G、swapはzram4個×495.5MiBでした。GPU起動時に電源容量不足で落ちたとのユーザー申告があるため、まずCPU版を使います。GPUはAC電源対策後の安定性が未確認です。
