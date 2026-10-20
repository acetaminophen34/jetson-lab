#!/usr/bin/env bash
# Add llama-server to an existing, patched TX2 CUDA build. No downloads/install.
set -euo pipefail
usage() {
  cat <<'HELP'
Usage: bash llama-cpp/tools/setup-server.sh [--check] [--rebuild]
  --check    Validate the existing CUDA build only; do not change files.
  --rebuild  Build even if llama-server already exists.
Environment:
  LLAMA_SRC    Existing patched source (default: <this repo>/work/llama-cuda)
  LLAMA_BUILD  Existing CMake build (default: $LLAMA_SRC/build-gpu)
  CMAKE        CMake executable (default: cached CMAKE_COMMAND)
  BUILD_JOBS   Build parallelism (default: 1)
Requires existing build5092 CUDA 10.2 / GCC8 / TX2 arch62 environment.
JetPack, toolchains and models are not installed by this script.
HELP
}
fail() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
check=0
rebuild=0
for arg in "$@"; do
  case "$arg" in
    --check) check=1;;
    --rebuild) rebuild=1;;
    --help|-h) usage; exit 0;;
    *) usage >&2; fail "Unknown argument: $arg";;
  esac
done
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
src="${LLAMA_SRC:-$repo/work/llama-cuda}"
[[ -d "$src" ]] || fail "Source missing: $src (see llama-cpp/README.md for initial setup)"
src="$(cd "$src" && pwd -P)"
build="${LLAMA_BUILD:-$src/build-gpu}"
[[ -d "$build" ]] || fail "Existing build missing: $build"
build="$(cd "$build" && pwd -P)"
cache="$build/CMakeCache.txt"
[[ -f "$cache" ]] || fail "CMakeCache.txt missing: $cache"
command -v python3 >/dev/null || fail 'python3 is required'
command -v git >/dev/null || fail 'git is required'
cache_value() { sed -n "s/^$1:[^=]*=//p" "$cache"; }
[[ "$(git -C "$src" rev-parse HEAD)" == d3bd7193ba66c15963fd1c59448f22019a8caf6e ]] || fail 'Source commit must be build5092 (d3bd7193b)'
[[ "$(cache_value GGML_CUDA)" == ON ]] || fail 'Existing build must have GGML_CUDA=ON'
[[ "$(cache_value CMAKE_CUDA_ARCHITECTURES)" == 62 ]] || fail 'Existing build must target TX2 CUDA architecture 62'
cached_src="$(cache_value CMAKE_HOME_DIRECTORY)"
[[ -d "$cached_src" && "$(cd "$cached_src" && pwd -P)" == "$src" ]] || fail 'CMake cache belongs to a different source directory'
cmake_exe="${CMAKE:-$(cache_value CMAKE_COMMAND)}"
command -v "$cmake_exe" >/dev/null || fail "CMake executable missing: $cmake_exe (set CMAKE)"
jobs="${BUILD_JOBS:-1}"
[[ "$jobs" =~ ^[1-9][0-9]*$ ]] || fail 'BUILD_JOBS must be a positive integer'
for key in CMAKE_CXX_COMPILER CMAKE_CUDA_HOST_COMPILER; do
  compiler="$(cache_value "$key")"
  [[ -x "$compiler" ]] || fail "$key is missing or not executable: $compiler"
  compiler_version="$("$compiler" -dumpversion)"
  [[ "${compiler_version%%.*}" == 8 ]] || fail "$key must be GCC/G++8"
done
nvcc="$(cache_value CMAKE_CUDA_COMPILER)"
[[ -x "$nvcc" ]] || fail "CUDA compiler missing: $nvcc"
"$nvcc" --version | grep -Eq 'release 10\.2([, ]|$)' || fail 'CUDA compiler must be version 10.2'
# Parse include flags without evaluating shell code from CMakeCache.txt.
python3 - "$cache" "$build" <<'PY'
import pathlib, shlex, sys
cache = {}
for line in pathlib.Path(sys.argv[1]).read_text().splitlines():
    if '=' in line and ':' in line.split('=', 1)[0]:
        key, value = line.split('=', 1)
        cache[key.split(':', 1)[0]] = value
flags = shlex.split(cache.get('CMAKE_CUDA_FLAGS', ''))
includes = []
for i, flag in enumerate(flags):
    if flag == '-I' and i + 1 < len(flags):
        includes.append(flags[i + 1])
    elif flag.startswith('-I'):
        includes.append(flag[2:])
for include in includes:
    path = pathlib.Path(include)
    if not path.is_absolute():
        path = pathlib.Path(sys.argv[2]) / path
    if (path / 'cuda_bf16.h').is_file():
        break
else:
    sys.exit('ERROR: Existing CMAKE_CUDA_FLAGS must reference a directory containing cuda_bf16.h')
PY
git -C "$src" apply --reverse --check "$repo/llama-cpp/patches/llama-qwen3-gpu.patch" || fail 'Expected CUDA patch not detected; inspect existing changes without resetting/reapplying patches'
printf 'Validated source: %s\nExisting build: %s\n' "$src" "$build"
if (( check )); then
  printf 'Check complete. No configure/build/install was performed.\n'
  exit 0
fi
if [[ -x "$build/bin/llama-server" ]] && (( ! rebuild )); then
  printf 'llama-server already exists; skipping build (use --rebuild to rebuild).\n'
else
  "$cmake_exe" -S "$src" -B "$build" -DLLAMA_BUILD_SERVER=ON
  "$cmake_exe" --build "$build" --target llama-server --parallel "$jobs"
fi
[[ -x "$build/bin/llama-server" ]] || fail 'Build did not produce an executable llama-server'
LD_LIBRARY_PATH="$build/bin${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" "$build/bin/llama-server" --version
printf 'Ready: %s\nNext: follow llama-cpp/server.md for localhost HTTP checks.\n' "$build/bin/llama-server"
