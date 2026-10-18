# 再構築を始める

## 概要と前提

この手順は、保存したソースと設定を初期化後のNanoへ戻し、CPU推論を基本に機能を確認するための入口です。Linuxのパッケージを揃えるだけでなく、上流ソースのcommit、ローカルpatch、モデル、カメラ校正の組合せを揃えます。

**実機確認済み**なのは既存CPUバイナリの短い推論です。**静的確認済み**の手順を使ったクリーンビルドはまだ**未検証**です。OSの元イメージと同版パッケージの入手経路など、不明な点を飛ばして完全復元できるとは扱いません。

## 初期化前に揃えるもの

| 資産 | 用途 | このリポジトリへの同梱 |
|---|---|---|
| ボードに適合するOSイメージと識別情報 | L4T/カーネルの基準 | なし。元イメージ・board指定は未確定 |
| 元のpreservationバックアップ | 固定Gitソースを復元 | bundleは同梱しない |
| 非公開の追加回収領域 | 校正NPZ、25ペア、設定（コード6本はsrc） | データ本体は同梱しない |
| Qwen3 GGUF | CPU推論の重み | 本体は未転送。別途保全が必要 |
| CMake3.28.6 aarch64 archive | ビルド定義の生成 | 本体は未転送。別途保全が必要 |

版・サイズ・SHA-256の正本は [版一覧](../reference/environment-versions.md) です。これらを揃える前にNanoを消去しないでください。タイムゾーンは変更しません。

## 作業先を分ける

以下は**将来、復元先のJetsonで実行するコマンド**です。既存のソースや設定へ上書きせず、新規ディレクトリを使います。`/absolute/...` の行を実配置へ直してから、bashの同じセッションで進めます。

```bash
export LAB_ROOT=/absolute/path/jetson-lab
export BACKUP=/absolute/private/path/20261018-002830
export PRIVATE_ROOT=/absolute/private/path/jetson-rebuild-private
export RECOVERY="$PRIVATE_ROOT/followup-20261018-134602"
export LAB_WORK="$HOME/jetson-lab-work"
test -d "$LAB_ROOT/patches" || exit 1
test -d "$BACKUP/repos" || exit 1
test ! -e "$LAB_WORK" || exit 1
mkdir -p "$LAB_WORK/logs"
export RUNLOG="$LAB_WORK/logs"
```

成功条件は、公開用リポジトリ・非公開原本・新しい作業先が別々になっていることです。既存先がある場合は削除して作り直さず、`LAB_WORK` に別名を選びます。コマンドの配置先にprivate原本を指定しないでください。

## 進める順序

| 工程 | 操作先の記事 | その工程で確認すること |
|---:|---|---|
| 1 | [OSとJetPack](environment/jetpack.md) | Ubuntu/L4T/archが基準と一致する |
| 2–3 | [基本パッケージ・GCC/CMake](environment/build-tools.md) | 同版パッケージ、選択したコンパイラとCMakeが一致する |
| 4–6 | [CPUビルド](projects/llama-cpp/cpu-build.md) | 固定commit → 原patch → configure → build → ELF |
| 7–8 | [同記事のモデル・推論](projects/llama-cpp/cpu-build.md#モデルの配置と識別) | 同じGGUFのhashと短いCPU応答 |
| 9 | [PS4 Eye](projects/ps4-eye/README.md) | ドライバ → firmware → USB → コード/校正 → 撮影と深度 |
| 10 | [GPUビルド](projects/llama-cpp/gpu-build.md) | 電源対策後の任意工程。CPU経路とは分離する |

成功は工程ごとに判定します。`CMakeCache.txt` ができること、ELFが存在すること、モデルが応答することはそれぞれ別の確認です。カメラもUSB列挙と映像取得を別に判定します。

## 未完了事項と参照

CPUクリーンビルド、元benchの追加リンク指定の経緯、OS/パッケージの確保、モデル/firmwareの配布条件、カメラ動作は未完了です。[検証結果と残作業](../reference/validation-results.md) に集約しています。

- [出典S1〜S8と保全範囲](../reference/sources.md)
- [問題が起きたときの切り分け](troubleshooting.md)
