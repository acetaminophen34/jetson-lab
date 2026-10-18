#!/usr/bin/env python3
"""A bounded CPU-only inference check; future use on a prepared Jetson, not a benchmark suite."""
import argparse
import datetime
import hashlib
import json
import os
import resource
import re
import subprocess
import threading
import time
from pathlib import Path

MODEL_SHA256 = '7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def memory():
    result = {}
    for line in Path('/proc/meminfo').read_text().splitlines():
        key, value = line.split(':', 1)
        if key in {'MemTotal', 'MemAvailable', 'SwapFree', 'SwapTotal'}:
            result[key + '_kib'] = int(value.split()[0])
    return result


def no_core():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--exe', required=True, type=Path)
    parser.add_argument('--model', required=True, type=Path)
    parser.add_argument('--out', required=True, type=Path)
    args = parser.parse_args()
    exe, model, out = args.exe.resolve(), args.model.resolve(), args.out.resolve()
    repo = Path(__file__).resolve().parents[1]
    if repo == out or repo in out.parents or out.exists():
        parser.error('Output must be a new directory outside this repository')
    if not exe.is_file() or not os.access(str(exe), os.X_OK) or not model.is_file():
        parser.error('Executable or model missing')
    if not Path('/proc/meminfo').exists():
        parser.error('This monitor requires Linux /proc')
    model_hash = sha(model)
    if model_hash != MODEL_SHA256:
        parser.error('Model SHA-256 mismatch; inference was not started')
    before = memory()
    if before['MemAvailable_kib'] < 1048576:
        parser.error('MemAvailable < 1GiB; inference was not started')
    argv = [str(exe), '-m', str(model), '--device', 'none', '--n-gpu-layers', '0',
            '--no-kv-offload', '--threads', '2', '--threads-batch', '2', '--ctx-size', '512',
            '--batch-size', '32', '--ubatch-size', '32', '--n-predict', '32', '--single-turn',
            '--reasoning', 'off', '--no-warmup', '--perf', '--seed', '1', '--temp', '0',
            '--simple-io', '-p', 'Reply with exactly: CPU test OK.']
    env = {k: v for k, v in os.environ.items() if not k.startswith(('LLAMA_ARG_', 'MTMD_'))}
    env.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', OPENBLAS_NUM_THREADS='2',
               LD_LIBRARY_PATH=str(exe.parent), PYTHONDONTWRITEBYTECODE='1')
    out.mkdir(parents=True, mode=0o700, exist_ok=False)
    result = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'argv': argv, 'model_sha256': model_hash, 'exe_sha256': sha(exe),
              'ram_before': before, 'samples': [], 'timeout_seconds': 120, 'timed_out': False}
    streams = {}
    start = time.monotonic()
    child = subprocess.Popen(argv, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, env=env, preexec_fn=no_core)

    def drain(name, stream):
        streams[name] = stream.read().decode('utf8', 'replace')

    readers = [threading.Thread(target=drain, args=(name, stream))
               for name, stream in [('stdout', child.stdout), ('stderr', child.stderr)]]
    for reader in readers:
        reader.start()
    cuda = set()
    try:
        while child.poll() is None:
            sample = {'elapsed_seconds': round(time.monotonic() - start, 3), 'system': memory()}
            try:
                for line in Path('/proc/{}/status'.format(child.pid)).read_text().splitlines():
                    if line.startswith(('VmRSS:', 'VmHWM:', 'Threads:')):
                        key, value = line.split(':', 1)
                        sample[key] = int(value.split()[0])
                for line in Path('/proc/{}/maps'.format(child.pid)).read_text().splitlines():
                    if any(v in line for v in ['libcuda.', 'libcudart.', 'libcublas', 'libggml-cuda']):
                        cuda.add(line.split()[-1])
            except OSError:
                pass
            result['samples'].append(sample)
            if time.monotonic() - start > 120:
                result['timed_out'] = True
                break
            time.sleep(0.25)
    finally:
        if child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()
        child.wait()
        for reader in readers:
            reader.join()
        usage = resource.getrusage(resource.RUSAGE_CHILDREN)
        result.update(returncode=child.returncode, wall_seconds=time.monotonic() - start,
                      ram_after=memory(), max_rss_kib=usage.ru_maxrss,
                      user_cpu_seconds=usage.ru_utime, system_cpu_seconds=usage.ru_stime,
                      loaded_cuda_libraries=sorted(cuda))
        result['expected_response_present'] = any(
            line.strip() == 'CPU test OK.' for line in streams.get('stdout', '').splitlines())
        speed = re.search(r'Prompt:\s*([0-9.]+) t/s.*Generation:\s*([0-9.]+) t/s', streams.get('stdout', ''))
        if speed:
            result['prompt_tokens_per_second'] = float(speed.group(1))
            result['generation_tokens_per_second'] = float(speed.group(2))
        for name in ['stdout', 'stderr']:
            (out / (name + '.txt')).write_text(streams.get(name, ''))
        (out / 'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print('exit={}, wall={:.3f}s, maxRSS={}KiB'.format(child.returncode, result['wall_seconds'], usage.ru_maxrss))
    if result['timed_out'] or cuda or not result['expected_response_present']:
        raise SystemExit(1)
    raise SystemExit(child.returncode if child.returncode >= 0 else 1)


if __name__ == '__main__':
    main()
