#!/usr/bin/env bash
# Prepare dependencies and working copies; never initialize or open the camera.
set -euo pipefail

usage() {
  cat <<'HELP'
Usage: bash ps4-eye/tools/setup-camera.sh [--check] [--gpu]
  --check  Check dependencies and files without changing anything.
  --gpu    Include NVIDIA VPI Python dependencies and checks.
Run on Jetson with JetPack 4.x. Existing files are preserved.
HELP
}
check=0
gpu=0
for arg in "$@"; do
  case "$arg" in
    --check) check=1 ;;
    --gpu) gpu=1 ;;
    --help|-h) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
  esac
done
repo="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)"
work="$repo/work/ps4-eye-custom"
packages=(git wget libopencv libopencv-python python3-numpy python3-flask python3-usb v4l-utils)
if (( gpu )); then packages+=(libnvvpi1 python3-vpi1); fi

if (( ! check )); then
  missing=()
  for package in "${packages[@]}"; do
    if [[ "$(dpkg-query -W -f='${Status}' "$package" 2>/dev/null || true)" != 'install ok installed' ]]; then
      missing+=("$package")
    fi
  done
  if (( ${#missing[@]} )); then
    sudo apt update
    sudo apt install --no-install-recommends --no-upgrade "${missing[@]}"
  fi

  mkdir -p "$work" "$HOME/models" "$HOME/ps4_calib"
  for source in "$repo/ps4-eye/scripts/"*.py; do
    destination="$work/$(basename "$source")"
    if [[ ! -e "$destination" ]]; then cp "$source" "$destination"; fi
  done
  for patch in ps4-stream-flask012.patch ps4-calib-python36.patch depth-stream-home-path.patch; do
    patch_file="$repo/ps4-eye/patches/$patch"
    if git -C "$repo" apply --reverse --check --directory=work/ps4-eye-custom "$patch_file" 2>/dev/null; then
      printf 'Already applied: %s\n' "$patch"
    else
      git -C "$repo" apply --check --directory=work/ps4-eye-custom "$patch_file"
      git -C "$repo" apply --directory=work/ps4-eye-custom "$patch_file"
      printf 'Applied: %s\n' "$patch"
    fi
  done

  if [[ ! -e "$HOME/ps4_calib/stereo_calibration.npz" ]]; then
    cp "$repo/ps4-eye/calibration/stereo_calibration.npz" "$HOME/ps4_calib/"
  fi
  download() {
    local destination="$1" url="$2" temporary
    if [[ -e "$destination" ]]; then return; fi
    temporary="$(mktemp "${destination}.XXXXXX")"
    if wget -O "$temporary" "$url" && [[ -s "$temporary" ]]; then
      mv "$temporary" "$destination"
    else
      rm -f "$temporary"
      printf 'Download failed: %s\n' "$url" >&2
      return 1
    fi
  }
  download "$HOME/models/deploy.prototxt" \
    https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
  download "$HOME/models/res10.caffemodel" \
    https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel
fi

# Checks are read-only and do not import the camera scripts or load the models.
failed=0
for package in "${packages[@]}"; do
  if dpkg-query -W -f='${Status}\n' "$package" 2>/dev/null | grep -qx 'install ok installed'; then
    printf 'OK package: %s\n' "$package"
  else
    printf 'MISSING package: %s\n' "$package" >&2
    failed=1
  fi
done
if ! python3 - "$gpu" <<'PY'
import importlib
import sys
modules = ['cv2', 'numpy', 'flask', 'usb']
if sys.argv[1] == '1':
    modules.append('vpi')
failed = False
for name in modules:
    try:
        module = importlib.import_module(name)
        print('OK import: {} {}'.format(name, getattr(module, '__version__', '')))
    except Exception as exc:
        print('FAILED import: {}: {}'.format(name, exc), file=sys.stderr)
        failed = True
sys.exit(1 if failed else 0)
PY
then failed=1; fi
for file in "$HOME/ps4_calib/stereo_calibration.npz" \
            "$HOME/models/deploy.prototxt" "$HOME/models/res10.caffemodel" \
            "$work/stereo_vision.py" "$work/stereo_vision_gpu.py"; do
  if [[ -s "$file" ]]; then
    printf 'OK file: %s\n' "$file"
  else
    printf 'MISSING/EMPTY file: %s\n' "$file" >&2
    failed=1
  fi
done
for patch in ps4-stream-flask012.patch ps4-calib-python36.patch depth-stream-home-path.patch; do
  if git -C "$repo" apply --reverse --check --directory=work/ps4-eye-custom "$repo/ps4-eye/patches/$patch" 2>/dev/null; then
    printf 'OK patch: %s\n' "$patch"
  else
    printf 'NOT APPLIED patch: %s\n' "$patch" >&2
    failed=1
  fi
done
if (( failed )); then exit 1; fi
printf '\nReady: %s\nChoose the camera device, initialize firmware, then run stereo_vision.py or stereo_vision_gpu.py with --camera.\n' "$work"
