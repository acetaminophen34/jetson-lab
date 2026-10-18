# 出典、保全範囲、公開管理

## 資料の位置づけ

このrepoは、既存の`jetson-rebuild`、非公開回収資産、既存調査を再編集したものです。元資料を削除/上書きせず、新規Gitリポジトリへ必要な公開対象だけを入れています。調査の時系列ではなく、各技術の説明と実行手順を正本にしました。

元の公開候補41ファイルの相対名/サイズ/SHA-256を [source-index.json](source-index.json) に記録しています。これは入力資料との対応で、元の古い文章を正しい現状として再掲載するものではありません。この過去入力indexは維持し、今回のコード原本出現は [code-occurrences.json](code-occurrences.json) に追加管理しています。個人の全履歴は含めません。

## 一次資料

### S1

初回`inventory/20261018-001021`、追加`inventory-extra/20261018-001917`のOS/dpkg/pip/toolchain/storage等。Macの`jetson-rebuild-v4`コピーとNano原本の19件hash照合済み。cuDNN/TensorRT版は保存dpkg/Python記録から抽出しています。全原文は非公開。

### S2

`preservation/20261018-002830`のGit bundle、原patch、status、未追跡ヘッダと、追加回収したQwen3差分。公開する3patchは [patches/](../patches/llama.patch) にあり、固定commitとの対応は [patch解説](../docs/projects/llama-cpp/patches.md)。bundle本体と.bak原本は元保全先に残します。

### S3

CMakeCache/compile_commands/link.txt、CUDA依存ファイル、ELFの存在とhash。公開済み抽出を [設定](details/build-settings.md)、[link](details/current-build-links.md)、[生成物](details/binary-inventory.md) へ配置しました。元cacheは絶対パスを含むのでそのまま再利用しません。link.txtはコマンド定義で実行成功ログではありません。

### S4

2026-10-18の既存CPU推論。原stdout/stderr/RAM CSV/runnerは非公開`cpu-validation-20261018-140025`、公開要約は [JSON](details/cpu-inference-result.json) と [検証結果](validation-results.md)。再編集のために実行し直していません。

### S5

独自PS4スクリプト6本、校正NPZ、校正入力25ペア、preview、Python関数signature。原文は非公開`followup-20261018-134602/files/`。元コードの意味、数値配列の静的解析、保存依存版とのAPI差を記事へ反映しました。今回のユーザー指示で自作コード6本を [src](../src/ps4-eye/README.md) へ保全しました。第三者上流のコード一式とfirmwareの許諾は別であり、バイナリとともに転載しません。固定個人パスの公開用置換は [code-origins.json](code-origins.json) で区別します。

### S6

systemd/udev/modprobe/modules-loadの保存設定と一覧。jtopはAGPL記載、NVIDIAルールは配布制限表示があるため原文を新repoへ持ち込みません。記事では起動対象、検索範囲、PS4専用設定が見つからないことの限界を説明しています。

検索範囲は/etcとユーザーのsystemd、/lib/systemd、udev、modprobe、modules-load、cron.d、rc.local、modules、shell初期化の関連行。別ユーザー/コンテナ/未保存セッションまで不存在とは判定しません。全shell履歴や認証設定は公開しません。

### S7

4repoの既存bundle履歴解析。[Git履歴抜粋](details/git-history.md) に固定refと直近履歴を保存。llama CPUはHEADまで11632、b5050は5050、jetson-patchesは48、カメラは14commit。参照repo READMEの成功/速度を実機測定へ取り込みません。元originのURLは名前だけで、認証付きURLを収集していません。

### S8

ユーザーによる「GPU起動時に電源容量不足で落ち、ACアダプタにするまではCPU運用だった」という説明。原因の実測や対策完了とは区別します。

## 元資料からの統合先

| 元の主な内容 | 新しい正本 |
|---|---|
| 基本環境・Nano/TX2・system | hardware、environment、版一覧 |
| LLM履歴・ビルド修正・再構築 | llama-cppの4記事とGit/ビルド参照 |
| カメラ解析・復元手順 | ps4-eyeの4記事 |
| 調査報告・追加更新・検証 | 検証結果へ統合。古い「未収集」表現は現在の回収状態へ更新 |
| 長いcache/link/hash一覧 | reference/detailsに隔離 |
| 独自原コード・試作・旧補助スクリプト | src/scripts/patchesへ用途別に保全。原文/匿名化/復元差分をhashで区別 |
| 画像・校正実体・外部原文の重複 | 既存非公開保全先に維持 |

初回67件の [指紋一覧](details/backup-inventory.md)、追加回収/実行証跡の [指紋一覧](details/recovery-manifest.md) も参照できます。これらは画像やfirmwareの実体ではありません。

## ライセンスと公開内容

- 第三者MIT通知は`licenses/`に元バイトのまま保存。由来範囲は [LICENSE](../LICENSE) を参照。
- 独自文書・スクリプト・修正追加部分へ包括ライセンスを勝手に付与していません。所有者の判断前は再配布許諾未設定です。
- 自作カメラコードは保全指示に基づきsrcへ置き、第三者の上流プロジェクト一式は含めません。firmware、モデル、校正値バイナリ、画像、鍵/トークン/認証設定、巨大bundle、build本体をGitへ入れません。
- 自作コードは公開repoにありますが、firmware/校正/画像は非公開資産です。撮影まで公開repoだけで完結すると誤認させません。

## 継続編集とGitHub

```sh
python3 -B scripts/check-repo.py
git diff --check
git diff --stat
git diff --cached
```

技術記事の意味・成功条件と参照値を先にレビューし、証跡は必要なものだけを抽出します。check-repoは相対リンク/anchor、shell構文、許可ファイル種別、サイズ、秘密情報の典型パターンを検査します。原patchと詳細抽出の末尾空白はバイト保全のため.gitattributesで通常の空白整形から除外し、別途hashで確認します。Git履歴内の全treeも対象にするため、誤って非公開物をコミットしてから削除する運用はしません。自動検査だけで秘密が無いことを万能に証明するものではありません。

この編集ではlocal mainへ初回commitを作成し、remote設定とpushはしていません。GitHubの公開先・ライセンス・差分を所有者が確認した後に、公開リポジトリjetson-labへremoteを設定してpushするのが次の工程です。

## この編集で行った検査

- 元入力44ファイル（旧repo41件と主要非公開manifest/結果）の編集前後SHA-256一致。
- 新repoの相対リンク/anchor、Python3.6相当の構文、文書中shell40ブロック、補助shellの構文を確認。
- 3原patchを既存ローカルGitオブジェクトへ適用チェック。ビルドは実行していない。
- 復元helperのrepo内出力/既存先拒否、hash不一致時の拒否を確認。
- カメラはcheck-onlyで58資産と25ペアのhash/対応を検査し、実体コピーを行っていない。
- 公開allowlist、250KB上限、典型的秘密文字列、staged treeと全commit treeを検査。原patch/第三者通知はasset-manifestで原バイトを照合。

## 理解を補う公式資料

以下は一次収集事実の根拠と区別した参照先です。この編集ではオンラインの再取得/最新版調査をしていません。

- [NVIDIA JetPack](https://developer.nvidia.com/embedded/jetpack)、[Jetson Linux文書](https://docs.nvidia.com/jetson/)
- [CMake 3.28コマンド文書](https://cmake.org/cmake/help/v3.28/manual/cmake.1.html)
- [llama.cpp](https://github.com/ggml-org/llama.cpp)、[Jetson向け参照patch](https://github.com/kreier/llama.cpp-jetson)
- [PS4 Eye上流コード](https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV)、[OpenCV文書](https://docs.opencv.org/)、[PyUSB](https://github.com/pyusb/pyusb)

## コード一体管理への更新

[棚卸し](code-inventory.md) で取得済みコード65出現を全分類し、自作/作業ソース14本、試作スナップショット1件、既存互換案2件を追加しました。原本絶対パスと原文固定コピーはpublication-reviewの非公開記録に保存。公開版で固定ホーム2ファイルだけを匿名化しています。新しいライセンス付与やGitHub pushは行っていません。
