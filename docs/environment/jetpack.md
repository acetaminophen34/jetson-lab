# JetPack・L4T・Ubuntuと推論ライブラリ

## 概要

Jetsonの環境は「UbuntuとCUDAを入れたもの」だけでは表せません。ボードを動かすカーネル/ドライバ、Linuxのユーザー環境、GPU開発ライブラリ、アプリケーションを分けて考えると、何を同じ版へ戻す必要があるか判断できます。

## 背景・仕組み

| 層 | 役割 | このプロジェクトでの位置づけ |
|---|---|---|
| JetPack | Jetson向けの開発環境一式をまとめたリリース | 再構築の目標は4.6.1 |
| L4T（Linux for Tegra） | ボード用カーネル、ドライバ、関連する基盤ソフトウェア | 実機記録はR32.7.1 |
| Ubuntu | shell、apt、Python、開発ツールなどのユーザー環境 | 実機記録は18.04.6 LTS |
| CUDA | GPUで実行するコードの開発/実行環境 | GPU版llama.cppはCUDA10.2を対象 |
| cuDNN | ニューラルネットワーク向けGPU演算ライブラリ | 導入記録はあるが、このllama経路の必須依存とは確認していない |
| TensorRT | 学習済みネットワークを最適化して推論するための環境 | 導入記録はあるが、このGGUF推論をTensorRT経由とは扱わない |

llama.cppのCUDAバックエンドは保存ELFでCUDA runtime・cuBLASなどへの依存を確認しています。cuDNNやTensorRTが装置に存在することから、それらがllama.cppで使われたとは推定しません。

## 環境と前提条件

**実機の記録**はL4T32.7.1、Ubuntu18.04.6、nvcc10.2.300です。cuDNNはdpkgで8.2.1.32-1+cuda10.2、TensorRTは8.2.1.8-1+cuda10.2を確認しています。ライブラリ、Pythonモジュール、メタパッケージは版の表し方が違うため、正確な識別子は [版一覧](../../reference/environment-versions.md) に分けています。

JetPack4.6.1は再構築の指定目標です。元のflashイメージ、イメージhash、正確なboard指定、`nvidia-jetpack`メタパッケージの版は未確定です。既存資料のL4T値だけでこれらまで確定したとは扱いません。

## OS準備・確認

OSを導入する前にボードと媒体を確定します。この資料には未確定の値を埋めた破壊的flashコマンドを置きません。適合イメージを用意した後、次を読み取ります。

```sh
uname -a
cat /etc/os-release
cat /etc/nv_tegra_release
dpkg-query -W nvidia-l4t-core nvidia-jetpack
```

成功条件は、arch/Ubuntu/L4Tが基準と一致することです。`nvidia-jetpack`が見つからないだけで、カーネルやCUDAが無いとは判定しません。失敗時はイメージと対象ボードを確認し、個別パッケージを無理に更新して合わせないでください。

## 設定を戻す範囲

systemdは起動順序とプロセス管理、udevはデバイス検出時の権限などを扱います。保存されたNVIDIAのhub/tegraルールは、そのままPS4 Eye専用設定ではありません。jtopの保存unitは`/usr/local/bin/jtop --force`を起動し、失敗時に再起動する構成でした。LLM/PS4専用自動起動は検索範囲で見つかっていません。

NVIDIAの配布制限表示を含むルールやAGPL表記のjtop unitは、この公開repoへ転載していません。初期化後のJetPack提供設定と非公開原文を比較し、独自変更だと確認できた部分だけを検討します。サービス一覧のenabled表示は、稼働確認と同義ではありません。

## 動作確認・未検証事項

OS情報と導入ライブラリは保存記録で確認済みです。初期化から同じ環境へ戻す作業そのもの、依存パッケージの現在の入手可否は未検証です。元のタイムゾーン観測はAmerica/New_Yorkで、変更手順は設けません。

## 参照資料

- [出典S1・S6](../../reference/sources.md)：初回/追加環境調査、system設定
- [CUDA](cuda.md)、[ビルドツール](build-tools.md)
