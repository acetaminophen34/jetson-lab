#!/usr/bin/env bash
# Restore a recorded commit and its original patch into a new, external worktree.
set -euo pipefail
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 cpu|qwen3-gpu|b5050-gpu BACKUP_DIR EXISTING_WORK_DIR" >&2
  exit 2
fi
root="$(cd "$(dirname "$0")/.." && pwd -P)"
backup="$2"
work="$(cd "$3" && pwd -P)"
case "$work/" in "$root/"*) echo 'Work directory must be outside this repository' >&2; exit 2;; esac
case "$1" in
  cpu) bundle="$backup/repos/llama/repository.bundle"; name=llama-cpu; commit=62df1815bc053066761f4eac58e288f23778e164; patch=llama.patch;;
  qwen3-gpu) bundle="$backup/repos/llama/repository.bundle"; name=llama-qwen3-gpu; commit=d3bd7193ba66c15963fd1c59448f22019a8caf6e; patch=llama-qwen3-gpu.patch;;
  b5050-gpu) bundle="$backup/repos/llama5050gpu/repository.bundle"; name=llama-b5050-gpu; commit=23106f94ea2bc3da929afb7330655fd5515d08dc; patch=llama5050gpu.patch;;
  *) echo 'Unknown profile' >&2; exit 2;;
esac
dest="$work/$name"
[[ -f "$bundle" && ! -e "$dest" ]] || { echo 'Bundle missing or destination already exists' >&2; exit 2; }
git clone --no-hardlinks "$bundle" "$dest"
git -C "$dest" checkout --detach "$commit"
git -C "$dest" apply --check "$root/patches/$patch"
git -C "$dest" apply "$root/patches/$patch"
if [[ "$1" == b5050-gpu ]]; then
  cp "$root/patches/compat-headers/cuda_bf16.h" "$dest/"
  cp "$root/patches/compat-headers/cuda_bf16.hpp" "$dest/"
fi
git -C "$dest" rev-parse HEAD
git -C "$dest" diff --stat
printf 'Restored source only: %s\nNo configure/build/install/runtime operation was performed.\n' "$dest"
