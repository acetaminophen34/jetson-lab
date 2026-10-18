#!/usr/bin/env bash
# Read-only diagnostic. No sudo, no modifications, no secrets copied intentionally.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$ROOT/inventory-extra/$STAMP"
mkdir -p "$OUT"
run() { local name="$1"; shift; { printf '$'; printf ' %q' "$@"; printf '\n'; "$@"; } > "$OUT/$name" 2>&1 || true; }
run host.txt hostnamectl
run time.txt timedatectl
run network-listening.txt ss -lnt
run services-enabled.txt systemctl list-unit-files --type=service --state=enabled --no-pager
run services-running.txt systemctl list-units --type=service --state=running --no-pager
run cron-user.txt crontab -l
run python-path.txt python3 -m pip --version
run jetson-release.txt cat /etc/nv_tegra_release
run cuda-info.txt bash -c 'command -v nvcc; ls -ld /usr/local/cuda* 2>/dev/null; command -v trtexec; command -v jtop'
run mount-swap.txt bash -c 'swapon --show; findmnt -n -o SOURCE,TARGET,FSTYPE /'
run installed-manual-apt.txt apt-mark showmanual
# Paths only; no content from .ssh, .env, credentials, etc.
{
  printf 'Likely application directories (paths only)\n'
  find "$HOME" -maxdepth 3 -type d \( -name '.git' -o -name 'llama.cpp' -o -name 'robi-llm' -o -name 'yolo*' \) 2>/dev/null | sed 's@/\.git$@@' | sort -u
} > "$OUT/projects-paths.txt"
{
  printf 'Git checkouts: path, commit and dirty flag. Remote URLs omitted to avoid credentials.\n'
  while IFS= read -r dir; do
    [ -d "$dir/.git" ] || continue
    printf '\nPROJECT: %s\n' "$dir"
    git -C "$dir" rev-parse HEAD 2>/dev/null || true
    git -C "$dir" status --porcelain 2>/dev/null | head -30 || true
  done < "$OUT/projects-paths.txt"
} > "$OUT/git-status.txt"
{
  printf 'Model files (relative locations and SHA256; hashing can take a while)\n'
  for base in "$HOME/robi-llm/models" "$HOME/models"; do
    [ -d "$base" ] || continue
    find "$base" -maxdepth 3 -type f \( -iname '*.gguf' -o -iname '*.onnx' -o -iname '*.engine' -o -iname '*.pt' \) -print0 2>/dev/null \
      | while IFS= read -r -d '' f; do ls -lh "$f"; sha256sum "$f"; done
  done
} > "$OUT/models-sha256.txt"
{
  printf 'Build caches (selected safe CMake flags only)\n'
  for base in "$HOME/llama.cpp" "$HOME/robi-llm"; do
    [ -d "$base" ] || continue
    find "$base" -maxdepth 4 -name CMakeCache.txt -type f 2>/dev/null \
      | while IFS= read -r f; do
          printf '\nFILE: %s\n' "$f"
          grep -E '^(GGML_CUDA|LLAMA_CUBLAS|CMAKE_BUILD_TYPE|CMAKE_CUDA_ARCHITECTURES):' "$f" || true
        done
  done
} > "$OUT/build-flags.txt"
printf 'Saved to %s\n' "$OUT"
printf 'Review hostnames, paths, listening ports, service names, cron contents, and Git status before sharing.\n'
