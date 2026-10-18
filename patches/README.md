# 外部修正・試作スナップショット・改善案

外部プロジェクト全体をsrcへ入れず、固定ベースと差分でローカル改造を保全します。現行修正、未使用の試作、未適用の改善案を混ぜません。

## 外部llama.cppへの修正

| patch | 固定ベースcommit | 変更ファイル/理由・適用 |
|---|---|---|
| [llama.patch](llama.patch) | 62df1815bc053066761f4eac58e288f23778e164 | CPU現行5ファイル。NEON x4代替、stdc++fs、iomanip、型明示。[詳細](../docs/projects/llama-cpp/patches.md)、[適用](../docs/projects/llama-cpp/cpu-build.md) |
| [llama5050gpu.patch](llama5050gpu.patch) | 23106f94ea2bc3da929afb7330655fd5515d08dc | 旧GPU7ファイル。arch/リンク/constexpr/builtin/NEON。[詳細](../docs/projects/llama-cpp/patches.md)、[適用](../docs/projects/llama-cpp/gpu-build.md) |
| [llama-qwen3-gpu.patch](llama-qwen3-gpu.patch) | d3bd7193ba66c15963fd1c59448f22019a8caf6e | Qwen3 GPU6ファイル。NEON、common、fattn3箇所、CUDA_VERSIONでBF16分岐を除外。[詳細と限界](../docs/projects/llama-cpp/patches.md) |
| [llama-cpu-legacy-neon-guard.patch](llama-cpu-legacy-neon-guard.patch) | 62df1815bc053066761f4eac58e288f23778e164 | **未使用試作**。ggml/src/ggml-cpu/ggml-cpu-impl.hのガードへGCC<9条件を追加。原.bakを復元する差分で、現行CPU patchと別案 |

試作guardはaarch64でも古いGCC時に互換側へ入れる変更が残っています。実際の採用理由・動作成功は未保存で、NEON互換対応を試した可能性という解析です。現行patchと自動併用しません。

試作を参照する場合だけ、**別の新規clone**を固定ベースへ移動してから適用します。

```bash
export TRIAL_SOURCE="$LAB_WORK/llama-neon-trial"
test ! -e "$TRIAL_SOURCE" || exit 1
git clone "$BACKUP/repos/llama/repository.bundle" "$TRIAL_SOURCE"
git -C "$TRIAL_SOURCE" checkout --detach 62df1815bc053066761f4eac58e288f23778e164
git -C "$TRIAL_SOURCE" apply --check "$LAB_ROOT/patches/llama-cpu-legacy-neon-guard.patch"
git -C "$TRIAL_SOURCE" apply "$LAB_ROOT/patches/llama-cpu-legacy-neon-guard.patch"
sha256sum "$TRIAL_SOURCE/ggml/src/ggml-cpu/ggml-cpu-impl.h"
# 期待: af1c3a87c9eacc9dbd62ecaefe7d83e5bae50f4c4da5c703e9dd8a6e2066b18c
```

この再構成hashは原.bakと同じことを静的検査します。全ファイルを破棄したわけではなく、元の完全ファイルは非公開に保持し、Gitベースと差分から復元できます。他の.bak2個はベースHEADとバイト同一で、独自改造ではなく外部原文の重複と判定しました。

BF16追加ヘッダは [compat-headers](compat-headers/cuda_bf16.h) の原文を維持。toolkit実使用は.hのみ確認、.hppのtoolkit配置は未確認である点を変えません。

## 自作PS4コードへの未適用案

| patch | 対象/ベース | 理由・扱い |
|---|---|---|
| [ps4-stream-flask012.patch](ps4-eye/ps4-stream-flask012.patch) | src/ps4-eye/ps4_stream.py | send_fileのdownload_nameを旧Flaskのattachment_filenameへ。既存提案patchの原文 |
| [ps4-calib-python36.patch](ps4-eye/ps4-calib-python36.patch) | src/ps4-eye/ps4_calib_capture.py | missing_okを持たないPath.unlinkへのcleanup案。既存提案patchの原文 |
| [depth-stream-home-path.patch](ps4-eye/depth-stream-home-path.patch) | 公開用src/ps4-eye/ps4_depth_stream.py | 公開パスplaceholderをPath.homeで解決する**新しい任意案**。元ソースに混ぜない |

ベースは [code-origins.json](../reference/code-origins.json) の各公開版hashで識別します。[src README](../src/ps4-eye/README.md) のとおりrepo外の作業コピーでgit apply --check後に適用します。静的適用と構文だけを確認し、今回カメラを実行していません。

## ライセンス

llama.cpp/jetson-patches由来は既存MIT通知を維持します。ローカル追加部分や自作案へMITを新規付与していません。上流PS4 Eye原コード7本やfirmwareは、この自作コードへの適用許可と別であり転載しません。[LICENSE](../LICENSE)参照。
