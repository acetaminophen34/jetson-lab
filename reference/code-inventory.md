# ソースコードの棚卸しと公開対象

この一覧をコード配置前に作成し、原文・出典・機密情報を確認しました。対象は取得済みのjetson-rebuild-private、旧jetson-rebuild、Downloadsのjetson-rebuild-v4、初回preservationコピーです。外部repo全体や未取得のNanoファイルを「自作」と推測して追加しません。

## 公開対象として確認した取得済みソース

ユーザーが自作・改造コードの保全を指示した範囲として扱います。独自コードや調査補助コードに新しい包括ライセンスを設定せず、第三者由来部分をユーザー独占著作と断定しません。鍵・トークン・認証付きURLは検出されず、固定ユーザー名パスだけ2ファイルで公開用置換が必要です。

| 公開先 | 原文bytes | 原文SHA-256 | 公開時の扱い |
|---|---:|---|---|
| `src/ps4-eye/ps4_calib_capture.py` | 6732 | `d66fe414bc0357005860308a865d3c0d02a68fb45473bd82fcce77f55b18b80a` | 原文のまま |
| `src/ps4-eye/ps4_calibrate.py` | 4732 | `5bfbb7333a28dbce9b57385b1d46aa423161f8db5d04149660589152e679bbe1` | 原文のまま |
| `src/ps4-eye/ps4_depth.py` | 1962 | `b4dcc1e2c630c975dd9189cb580b06f253ce5c11123e9ce300e41787e56a3095` | 原文のまま |
| `src/ps4-eye/ps4_depth_stream.py` | 9094 | `da7abafbd7ff8eb017d08c628968fa13f75f652cb43c07c791378dd27642740f` | 固定ホームパスのみ匿名化。原文は非公開保持 |
| `src/ps4-eye/ps4_depth_test.py` | 1669 | `ae0bcdbdd4d5b1e49dd2a5a53c114472937caf5ae371a2e977d63673e7c6d598` | 原文のまま |
| `src/ps4-eye/ps4_stream.py` | 6157 | `4fbcf9f34bdb07f48f5c7835ec35ee1f808af430bbf0c67b6980e07d22e9f806` | 原文のまま |
| `scripts/archive/preservation/backup-build-camera.sh` | 6561 | `70dea5385e694a447d99ae47d31997f88767623ead4402f050b057f2bf85aa74` | 原文のまま |
| `scripts/archive/inventory/collect-extended.sh` | 2673 | `98801e4d3daa18fc97759765f26561dd9376633408a386bedc349b5110d87146` | 原文のまま |
| `scripts/archive/preservation/export-source-changes.sh` | 1672 | `de9106a40d15a3ad29bb6ec966ead938d5771ad54fa66af2368335d8716aff4c` | 原文のまま |
| `scripts/archive/validation/verify.sh` | 909 | `7da3c9f682c6d7da82548de3869b6a9a46ca2dddbbf9a2e0194bd3cd3fe5bb15` | 原文のまま |
| `scripts/archive/inventory/jetson_fetch.py` | 179591 | `660e1ebbabf532ddd8720a37626a663b5d9ff0faa6d6d53b299a3bdfb4a3bd25` | 固定ホームパスのみ匿名化。原文は非公開保持 |
| `scripts/archive/inventory/jetson_final_read.py` | 4620 | `11d2ae30a514c36f4bc1856184c067ca43fc351e5deb72be704eac42c609bff5` | 原文のまま |
| `scripts/archive/inventory/jetson_readonly_discover.py` | 4386 | `b912865bd5bd6c0ab6b723aa5f9f6d05c30a1c0deb1d2a74caee8af3f48c5f27` | 原文のまま |
| `scripts/archive/validation/cpu-runner.py` | 3449 | `49fa9726a324b77db87ef3cdab83074ae11d9f5767dcd12b010358970594766c` | 原文のまま |

既存scripts/の4本も管理対象に含め、既存Git commitを原文の出典として記録します。新たに見つかったggml-cpu-impl.h.bakのGCC<9ガード案は、現行CPU patchとは別の試作patchとして復元可能に保全します。

## 第三者修正と原案

- 既存LLMの原patch3種類とBF16ヘッダ2個は、対象commitとMIT通知を維持。
- PS4 EyeのFlask0.12/Python3.6互換案2件は原コードへ混ぜずpatchへ配置。
- 深度配信の公開用パスplaceholderをPath.homeへ変える案は、原文とは別の任意patchとして記録。

## 除外・留保するもの

第三者カメラrepoの追跡ソース7本（trash.pyを含む）とjetson-patchesの置換ファイル一式は、外部コードの原本です。独自コードとの差分があると確認できないものを一括転載しません。HEADと同一の.bak2個は第三者原文の重複で、非公開原本とhashを残します。試作変更が残る.bak1個は省略せず独立patch化します。

firmware、GGUF、画像、校正バイナリ、Git bundle、build生成物、認証設定は公開コードへ入れません。重複したコードは全原本出現を棚卸しに記録し、公開コピーを1個に統合します。用途が古い・試作であることを理由には除外しません。

公開版/原文のhash、出典パスの公開表記と対応、除外した各コードの判定は配置後のcode-origins.jsonとcode-occurrences.jsonに記録します。実際の絶対パスは非公開レビューmanifestに保持します。

## 配置後の結果

取得済み自作/作業ソース14本を新規保全しました。12本は原文とバイト一致、2本は固定ホームだけを公開用置換しています。既存管理helper4本はGit原文を維持し、今回必要なsrc連携変更を管理コードとして行います。試作.bak1個はベース＋patchで原文と同じ完全ファイルを復元できます。

元の絶対パスと原文の固定コピーは非公開`publication-review-20261018-144121/`に保存。公開manifestの$PRIVATE/$V4/$PRESERVATION/$OLD_DOCS/$JETSON_HOMEは対応する保全rootの表記です。実際のアカウント名を履歴へ漏らさないため、公開JSONにはroot別名だけを載せます。

[code-occurrences.json](code-occurrences.json) は4つの既存rootにあるコード実体65出現を全て分類しています。重複版、第三者原文、空patchも個別行で確認でき、独自原案を用途だけで省略していません。[code-origins.json](code-origins.json) は各公開コード/patchの原文・公開版hashと変換/復元方法です。

### 個別の除外・不足

- 上流カメラPython7本は保存commitの追跡原文。trash.pyもコメント断片の上流原文であり、独自試作だと推測して転載しない。
- jetson-patchesの置換ソース一式は第三者参照ファイル。追加ヘッダ2個と既存の必要原patchは継続保全し、それ以外の丸ごとコピーをしない。
- server-schema.cpp.bakとcli/CMakeLists.txt.bakはCPUベースHEADとバイト同一。原本・hashを非公開/棚卸しに保持し、独自変更はない。
- 空のps4-camera/jetson-patches差分は変更byteが無い。元の空ファイルを保全し公開実装として増やさない。
- Nanoのbackup-build-camera.sh別版は既存調査に6567bytes/hashのみあり、今回のDownloads版6561bytesとは違う。未取得本文をDownloads版で代用しない。
- 画像、NPZ/NPY、firmware、GGUF、bundle、ELF、buildメタデータ、認証設定はソース保全とは別。実体は原保全先に維持し公開追加しない。
- 旧報告の「JPEG10枚回収」を再確認すると、manifest内のカメラ画像は8枚＋校正preview1枚。left_fixed.jpg/right_fixed.jpgの取得実体は確認できないため、本一覧では未回収とする。既存の履歴的報告を根拠に生成・追加しない。

今回新たなSSH/機器操作/ビルド/推論/撮影は行っていません。既存private/backup/元ソースは変更・削除していません。GitHubへのpushは未実施です。

## 今回の静的検証結果

- 棚卸しした原本65出現（内容46種類）のサイズとSHA256は作業前後で一致。
- 新規取得済みコード14本は12本が原文完全一致、2本は記録したホームパス置換のみ。非公開固定コピーも原本と一致。
- PS4 Eyeの任意patch3個は一時コピーに適用可能で、適用後もPython3.6構文として解析可能。import/撮影は実行していない。
- 試作NEON patchから復元した完全ファイルは原.bakのSHA256と一致。
- 校正データ復元helperはcheck-onlyで52資産と25組を照合。従来のコード込み選択58資産も照合し、コピーはしていない。
- 公開検査は相対リンク、Python/シェル構文、原patch/コードhash、秘密情報パターン、Git indexと全commit treeを対象とする。ライセンスは新規付与せず、上流通知と帰属未確定範囲を維持。

詳細な原本照合結果と実パスmanifestは、非公開レビュー領域のverification.jsonに保持しています。これらは静的検証であり、今回新しく実機動作を確認したものではありません。
