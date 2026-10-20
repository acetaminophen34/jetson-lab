"""Mock existing CUDA build; no real compiler, network or model is used."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().with_name('setup-server.sh')


class SetupServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='setup server ')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.src = self.root / 'source'
        self.build = self.src / 'build-gpu'
        (self.build / 'bin').mkdir(parents=True)
        tools = self.root / 'tools'
        tools.mkdir()
        self.calls = self.root / 'calls'
        self.write_exe(tools / 'git', '''case "$*" in
  *rev-parse*) echo "${MOCK_COMMIT:-d3bd7193ba66c15963fd1c59448f22019a8caf6e}";;
  *apply*) exit "${MOCK_PATCH_EXIT:-0}";;
  *) exit 99;;
esac
''')
        self.write_exe(tools / 'g++', 'echo 8.4.0\n')
        self.write_exe(tools / 'nvcc', 'echo "Cuda compilation tools, release 10.2, V10.2.89"\n')
        self.write_exe(tools / 'cmake', '''printf '%s\\n' "$*" >> "$MOCK_CALLS"
if [[ "$1" == --build ]]; then
  printf '#!/bin/sh\\necho "version: 5092"\\n' > "$MOCK_BUILD/bin/llama-server"
  chmod +x "$MOCK_BUILD/bin/llama-server"
fi
''')
        compat = self.root / 'compat headers'
        compat.mkdir()
        (compat / 'cuda_bf16.h').touch()
        self.cache = self.build / 'CMakeCache.txt'
        self.cache.write_text('''GGML_CUDA:BOOL=ON
CMAKE_CUDA_ARCHITECTURES:STRING=62
CMAKE_HOME_DIRECTORY:INTERNAL={src}
CMAKE_COMMAND:INTERNAL={tools}/cmake
CMAKE_CXX_COMPILER:FILEPATH={tools}/g++
CMAKE_CUDA_HOST_COMPILER:FILEPATH={tools}/g++
CMAKE_CUDA_COMPILER:FILEPATH={tools}/nvcc
CMAKE_CUDA_FLAGS:STRING=-I"{compat}"
'''.format(src=self.src, tools=tools, compat=compat))
        self.original = self.cache.read_bytes()
        self.env = dict(os.environ, PATH=str(tools) + ':' + os.environ['PATH'],
                        LLAMA_SRC=str(self.src), LLAMA_BUILD=str(self.build),
                        MOCK_CALLS=str(self.calls), MOCK_BUILD=str(self.build))
        for key in ('CMAKE', 'BUILD_JOBS'):
            self.env.pop(key, None)

    def write_exe(self, path, content):
        path.write_text('#!/usr/bin/env bash\nset -eu\n' + content)
        path.chmod(0o700)

    def run_setup(self, *args, success=True):
        result = subprocess.run(['bash', str(SCRIPT)] + list(args), env=self.env,
                                cwd=str(self.root), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertEqual(result.returncode == 0, success, result.stderr.decode())
        return result

    def test_check_is_read_only(self):
        self.run_setup('--check')
        self.assertFalse(self.calls.exists())
        self.assertEqual(self.cache.read_bytes(), self.original)
        self.assertFalse((self.build / 'bin/llama-server').exists())

    def test_build_repeat_and_rebuild(self):
        self.run_setup()
        self.assertEqual(len(self.calls.read_text().splitlines()), 2)
        self.assertIn('--target llama-server --parallel 1', self.calls.read_text())
        self.run_setup()
        self.assertEqual(len(self.calls.read_text().splitlines()), 2)
        self.env['BUILD_JOBS'] = '2'
        self.run_setup('--rebuild')
        self.assertEqual(len(self.calls.read_text().splitlines()), 4)
        self.assertIn('--parallel 2', self.calls.read_text())

    def test_wrong_commit_and_patch_fail_before_build(self):
        for key, value in (('MOCK_COMMIT', 'wrong'), ('MOCK_PATCH_EXIT', '1')):
            self.env[key] = value
            self.run_setup(success=False)
            del self.env[key]
        self.assertFalse(self.calls.exists())

    def test_invalid_cache_fails_before_build(self):
        for old, new in (('GGML_CUDA:BOOL=ON', 'GGML_CUDA:BOOL=OFF'),
                         ('STRING=62', 'STRING=53'),
                         (str(self.src), '/wrong/source'),
                         ('cuda_bf16.h', 'not-used')):
            self.cache.write_bytes(self.original)
            if old == 'cuda_bf16.h':
                for header in self.root.glob('compat*/*.h'):
                    header.unlink()
            else:
                self.cache.write_text(self.original.decode().replace(old, new))
            self.run_setup(success=False)
        self.assertFalse(self.calls.exists())

    def test_invalid_jobs_and_arguments(self):
        self.env['BUILD_JOBS'] = '0'
        self.run_setup(success=False)
        self.env['BUILD_JOBS'] = '1'
        self.run_setup('--unknown', success=False)
        self.assertFalse(self.calls.exists())

    def test_missing_source_and_help(self):
        self.env['LLAMA_SRC'] = str(self.root / 'missing')
        self.run_setup(success=False)
        self.run_setup('--help')


if __name__ == '__main__':
    unittest.main()
