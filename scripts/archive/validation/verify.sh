#!/usr/bin/env bash
set -u
printf '\n== Host / OS ==\n'
uname -a
cat /etc/os-release | grep -E '^(PRETTY_NAME|VERSION_ID)='
printf '\n== L4T ==\n'
cat /etc/nv_tegra_release 2>/dev/null || echo 'L4T metadata not found'
printf '\n== Toolchains ==\n'
python3 --version
command -v nvcc >/dev/null && nvcc --version | tail -4 || echo 'nvcc missing'
printf '\n== NVIDIA packages ==\n'
dpkg-query -W -f='${binary:Package}\t${Version}\n' nvidia-l4t-core libcudnn8 tensorrt cuda-nvcc-10-2 2>/dev/null || true
printf '\n== Python imports ==\n'
python3 - <<'PY'
for name in ('numpy','cv2','tensorrt','torch','onnx','pycuda','jetson_stats'):
    try:
        m=__import__(name)
        print('{}: OK {}'.format(name, getattr(m, '__version__', 'version unknown')))
    except Exception as e:
        print('{}: unavailable ({})'.format(name, e))
PY
printf '\n== Memory / swap ==\n'
free -h
printf '\n== Disk ==\n'
df -h /
