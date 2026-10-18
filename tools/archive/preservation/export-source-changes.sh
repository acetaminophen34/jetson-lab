#!/usr/bin/env bash
# Archive local Git modifications in a PRIVATE, local-only directory.
# NEVER upload without reviewing: patches may contain proprietary code or secrets.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$ROOT/source-backup/$STAMP"
mkdir -p "$OUT"
for spec in 'llama|robi-llm/llama.cpp' 'llama5050gpu|robi-llm/llama5050gpu.cpp' 'jetson-patches|robi-llm/jetson-patches' 'ps4-camera|PS4-eye-camera-for-linux-with-python-and-OpenCV'; do
  name="${spec%%|*}"
  rel="${spec#*|}"
  dir="$HOME/$rel"
  [ -d "$dir/.git" ] || { printf 'Skip: %s\n' "$dir"; continue; }
  target="$OUT/$name"
  mkdir -p "$target/untracked"
  git -C "$dir" rev-parse HEAD > "$target/commit.txt"
  git -C "$dir" status --porcelain > "$target/status.txt"
  git -C "$dir" diff --binary HEAD -- > "$target/working-tree.patch"
  # Untracked files are NOT committed or modified. Copy only below the source directories.
  # We intentionally exclude PS4 sample captures; collect paths for them in status.txt.
  if [ "$name" != 'ps4-camera' ]; then
    git -C "$dir" ls-files --others --exclude-standard -z |
    while IFS= read -r -d '' relpath; do
      case "$relpath" in
        *.env|*.pem|*.key|*id_rsa*|*.gguf|*.pt|*.onnx|*.engine|*.bak) continue;;
      esac
      [ -f "$dir/$relpath" ] && [ ! -L "$dir/$relpath" ] || continue
      mkdir -p "$target/untracked/$(dirname "$relpath")"
      cp -p -- "$dir/$relpath" "$target/untracked/$relpath"
    done
  fi
  printf 'Saved %s\n' "$target"
done
printf '\nLocal backup: %s\nReview all content for secrets before sharing. Keep a PRIVATE backup; patches can include credentials.\n' "$OUT"
