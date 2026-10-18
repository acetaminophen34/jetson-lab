#!/usr/bin/env bash
# Jetson Nano preservation: source modifications, build metadata, PS4 camera scripts/settings.
# READ-ONLY on source projects; writes ONLY inside jetson-environment/preservation/.
# PRIVATE BACKUP: may contain proprietary code, device identifiers, camera settings, or secrets.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STAMP="$(date +%Y%m%d-%H%M%S)"
OUT="$ROOT/preservation/$STAMP"
mkdir -p "$OUT"/{repos,system,camera,manifest}
exec > >(tee "$OUT/run.log") 2>&1
printf 'Preservation start: %s\nOutput: %s\n' "$(date -Is)" "$OUT"

safe_file() {
 case "$1" in
   *.env|*.pem|*.key|*.p12|*.pfx|*id_rsa*|*id_ed25519*|*authorized_keys*|*credentials*|*token*|*secret*|*password*|*.gguf|*.pt|*.onnx|*.engine|*.jpg|*.jpeg|*.png|*.mp4|*.avi|*.mov|*.raw|*.bin|*.so|*.o|*.a|*.deb|*.zip|*.tar*|*.bak) return 1;;
 esac
 return 0
}

repos=(
 "llama|$HOME/robi-llm/llama.cpp"
 "llama5050gpu|$HOME/robi-llm/llama5050gpu.cpp"
 "jetson-patches|$HOME/robi-llm/jetson-patches"
 "ps4-camera|$HOME/PS4-eye-camera-for-linux-with-python-and-OpenCV"
)
for entry in "${repos[@]}"; do
 name="${entry%%|*}"; dir="${entry#*|}"
 [ -d "$dir/.git" ] || { printf 'Missing Git repo: %s\n' "$dir"; continue; }
 d="$OUT/repos/$name"; mkdir -p "$d/untracked"
 printf '\nRepository: %s\n' "$dir"
 printf '%s\n' "$dir" > "$d/original-path.txt"
 git -C "$dir" rev-parse HEAD > "$d/commit.txt"
 git -C "$dir" status --porcelain=v1 > "$d/status.txt"
 git -C "$dir" diff --binary HEAD > "$d/tracked-changes.patch"
 git -C "$dir" diff --stat HEAD > "$d/diff-stat.txt"
 git -C "$dir" branch --show-current > "$d/branch.txt"
 # Store remote names without their potentially credential-bearing URLs.
 git -C "$dir" remote | sort > "$d/remote-names.txt"
 # Offline repository archive captures git commit objects including local branches.
 # Repositories may be large; can disable via SKIP_GIT_BUNDLE=1.
 if [ "${SKIP_GIT_BUNDLE:-0}" != 1 ]; then
   git -C "$dir" bundle create "$d/repository.bundle" --all || rm -f "$d/repository.bundle"
 fi
 git -C "$dir" ls-files --others --exclude-standard -z | while IFS= read -r -d '' rel; do
   safe_file "$rel" || continue
   src="$dir/$rel"
   [ -f "$src" ] && [ ! -L "$src" ] || continue
   # Guard against unexpectedly large untracked artifacts.
   bytes="$(stat -c %s "$src" 2>/dev/null || echo 0)"
   [ "$bytes" -le 1048576 ] || { echo "Skipped large untracked: $src"; continue; }
   mkdir -p "$d/untracked/$(dirname "$rel")"
   cp -p -- "$src" "$d/untracked/$rel"
 done
 # Preserve exact cache variables and other textual build diagnostics if available.
 find "$dir" -maxdepth 4 -type f \( -name CMakeCache.txt -o -name compile_commands.json \) \
   -not -path '*/.git/*' -print 2>/dev/null | while IFS= read -r src; do
   rel="${src#"$dir"/}"
   mkdir -p "$d/build-metadata/$(dirname "$rel")"
   cp -p "$src" "$d/build-metadata/$rel"
 done
 # Record potential scripts, without duplicating tracked source files.
 find "$dir" -maxdepth 4 -type f \( -name '*.sh' -o -name '*.py' -o -name '*.service' -o -name '*.rules' \) \
   -not -path '*/.git/*' -not -path '*/build/*' -not -path '*/.venv/*' -print 2>/dev/null > "$d/script-paths.txt" || true
done

# Camera hardware, device nodes and relevant installed packages.
(ls -l /dev/video* /dev/media* 2>&1 || true) > "$OUT/camera/devices.txt"
(lsusb 2>&1 || true) > "$OUT/camera/usb-devices.txt"
(v4l2-ctl --list-devices 2>&1 || true) > "$OUT/camera/v4l2-devices.txt"
(v4l2-ctl --all --device=/dev/video0 2>&1 || true) > "$OUT/camera/video0-properties.txt"
(dpkg-query -W 'v4l-utils' 'libusb*' 'uvc*' 'gstreamer1.0*' 'python3-opencv' 2>&1 || true) > "$OUT/camera/camera-packages.txt"
(lsmod 2>&1 || true) > "$OUT/camera/kernel-modules.txt"
# Identify GStreamer/openCV/python command and relevant video handling in user scripts.
for dir in "$HOME/PS4-eye-camera-for-linux-with-python-and-OpenCV" "$HOME/robi-llm"; do
 [ -d "$dir" ] || continue
 grep -RInE --include='*.py' --include='*.sh' --include='*.cpp' --include='*.md' \
   --exclude-dir=.git --exclude-dir=build --exclude-dir=.venv \
   'v4l2|/dev/video|VideoCapture|gst-launch|GStreamer|firmware|pyusb|usb.core' "$dir" 2>/dev/null \
   | head -n 300 > "$OUT/camera/$(basename "$dir")-references.txt" || true
done
# Firmware file names and SHA256 only; actual firmware may have redistribution restrictions.
if [ -d "$HOME/PS4-eye-camera-for-linux-with-python-and-OpenCV" ]; then
 find "$HOME/PS4-eye-camera-for-linux-with-python-and-OpenCV" -maxdepth 5 -type f \
   \( -iname '*firmware*' -o -iname '*.bin' -o -iname '*.fw' \) -print0 \
   | xargs -0 -r sha256sum > "$OUT/camera/firmware-hashes.txt"
fi

# Relevant local configs. Do not auto-collect /etc/NetworkManager, SSH keys, or wireless secrets.
for dir in "$HOME/.config/systemd/user" /etc/systemd/system /etc/udev/rules.d; do
 [ -d "$dir" ] || continue
 find "$dir" -maxdepth 2 -type f \( -name '*.service' -o -name '*.timer' -o -name '*.rules' \) -print 2>/dev/null \
   > "$OUT/system/$(echo "$dir" | tr '/' '_')-files.txt"
done
(systemctl --user list-unit-files --type=service --no-pager 2>&1 || true) > "$OUT/system/user-services.txt"
(systemctl list-unit-files --type=service --no-pager 2>&1 || true) > "$OUT/system/system-services.txt"
# Include only candidate rules/service files matching project/camera keywords; inspect before sharing.
for dir in "$HOME/.config/systemd/user" /etc/systemd/system /etc/udev/rules.d; do
 [ -d "$dir" ] || continue
 find "$dir" -maxdepth 2 -type f \( -name '*.service' -o -name '*.rules' \) -print0 2>/dev/null |
 while IFS= read -r -d '' src; do
   if [[ "$src" =~ ([Pp][Ss]4|camera|video|uvc|rob[i]|llama|jetson) ]] || grep -qiE 'PS4|camera|video|uvc|rob[i]|llama|jetson' "$src" 2>/dev/null; then
     name="$(echo "$src" | sed 's#^/##;s#/#__#g')"
     cp -p "$src" "$OUT/system/$name" 2>/dev/null || true
   fi
 done
done

# User's top-level scripts: generate manifest only; add desired paths manually after inspection.
find "$HOME" -maxdepth 2 -type f \( -name '*.sh' -o -name '*.py' -o -name '*.service' \) \
  -not -path '*/.cache/*' -not -path '*/.local/*' -print 2>/dev/null > "$OUT/manifest/home-script-paths.txt" || true
(date -Is; uname -a; cat /etc/nv_tegra_release 2>/dev/null || true) > "$OUT/manifest/host-version.txt"
# List all included files to support future verification.
find "$OUT" -type f -printf '%P\n' | sort > "$OUT/manifest/archive-files.txt"
printf '\nSaved to %s\n' "$OUT"
printf 'KEEP THIS BACKUP PRIVATE. Review paths, patches, configs and caches for secrets before uploading.\n'
