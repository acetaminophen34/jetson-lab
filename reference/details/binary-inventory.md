# LLM生成物の実在・ハッシュ

ELFマジック、ファイルサイズ、SHA-256を読み取り確認。実行していません。symlinkの別名を含め42パス。ファイルの存在は過去のビルド全体成功・現在ソースとの一致・推論成功を証明しません。

| パス | 実体 | bytes | SHA-256 |
|---|---|---:|---|
| `~/robi-llm/llama.cpp/build-gpu/bin/libggml-base.so` | `~/robi-llm/llama.cpp/build-gpu/bin/libggml-base.so.0.26.0` | 803864 | `6ac36ec1faaea30ed98b40ceef6d0a1e7a360e5ea67bd44f4f228a9ebb080d67` |
| `~/robi-llm/llama.cpp/build-gpu/bin/libggml-base.so.0.26.0` | `~/robi-llm/llama.cpp/build-gpu/bin/libggml-base.so.0.26.0` | 803864 | `6ac36ec1faaea30ed98b40ceef6d0a1e7a360e5ea67bd44f4f228a9ebb080d67` |
| `~/robi-llm/llama.cpp/build-gpu/bin/libggml-base.so.0` | `~/robi-llm/llama.cpp/build-gpu/bin/libggml-base.so.0.26.0` | 803864 | `6ac36ec1faaea30ed98b40ceef6d0a1e7a360e5ea67bd44f4f228a9ebb080d67` |
| `~/robi-llm/llama.cpp/build/bin/libggml-base.so` | `~/robi-llm/llama.cpp/build/bin/libggml-base.so.0.26.0` | 803864 | `6ac36ec1faaea30ed98b40ceef6d0a1e7a360e5ea67bd44f4f228a9ebb080d67` |
| `~/robi-llm/llama.cpp/build/bin/llama-cli` | `~/robi-llm/llama.cpp/build/bin/llama-cli` | 1249008 | `db710ff78b0f69636620b609acd1ab35ed84b2d1bbeaf9f28a03698b98ae21d0` |
| `~/robi-llm/llama.cpp/build/bin/libggml-cpu.so` | `~/robi-llm/llama.cpp/build/bin/libggml-cpu.so.0.26.0` | 995864 | `8a5b3372ff0c9b0f3eec4fd0ad1b821d5c1296d233e3c1d4e07e1014373e3195` |
| `~/robi-llm/llama.cpp/build/bin/libllama-common.so` | `~/robi-llm/llama.cpp/build/bin/libllama-common.so.0.6.0` | 5019600 | `fbd7bb1920772fad327329a804876d40c6346db4a76dc6f73459fb2a6c02cf40` |
| `~/robi-llm/llama.cpp/build/bin/llama-minicpmv-cli` | `~/robi-llm/llama.cpp/build/bin/llama-minicpmv-cli` | 14376 | `0565a594f4ea699c912ddfbf687033500984f18c12bf64c7df013446d68bb2ea` |
| `~/robi-llm/llama.cpp/build/bin/libllama.so.0.6.0` | `~/robi-llm/llama.cpp/build/bin/libllama.so.0.6.0` | 4504416 | `e4aabac2ffd4a693ce20f0a8a1cc7da858bf05d2993d21ae3a7c075a5a3afaf5` |
| `~/robi-llm/llama.cpp/build/bin/libllama-common.so.0.6.0` | `~/robi-llm/llama.cpp/build/bin/libllama-common.so.0.6.0` | 5019600 | `fbd7bb1920772fad327329a804876d40c6346db4a76dc6f73459fb2a6c02cf40` |
| `~/robi-llm/llama.cpp/build/bin/libmtmd.so.0` | `~/robi-llm/llama.cpp/build/bin/libmtmd.so.0.6.0` | 1686592 | `a80d36ff476dfdc858515d339846f5e257634f3f5d80fe11ff6adc18197d8185` |
| `~/robi-llm/llama.cpp/build/bin/libllama.so` | `~/robi-llm/llama.cpp/build/bin/libllama.so.0.6.0` | 4504416 | `e4aabac2ffd4a693ce20f0a8a1cc7da858bf05d2993d21ae3a7c075a5a3afaf5` |
| `~/robi-llm/llama.cpp/build/bin/llama-llava-cli` | `~/robi-llm/llama.cpp/build/bin/llama-llava-cli` | 14376 | `0565a594f4ea699c912ddfbf687033500984f18c12bf64c7df013446d68bb2ea` |
| `~/robi-llm/llama.cpp/build/bin/libmtmd.so.0.6.0` | `~/robi-llm/llama.cpp/build/bin/libmtmd.so.0.6.0` | 1686592 | `a80d36ff476dfdc858515d339846f5e257634f3f5d80fe11ff6adc18197d8185` |
| `~/robi-llm/llama.cpp/build/bin/libmtmd.so` | `~/robi-llm/llama.cpp/build/bin/libmtmd.so.0.6.0` | 1686592 | `a80d36ff476dfdc858515d339846f5e257634f3f5d80fe11ff6adc18197d8185` |
| `~/robi-llm/llama.cpp/build/bin/libggml.so.0.26.0` | `~/robi-llm/llama.cpp/build/bin/libggml.so.0.26.0` | 53048 | `88e61e534f6d06c47c01d50fb5eab5f767dbb557c308193a7397c58d70178bb3` |
| `~/robi-llm/llama.cpp/build/bin/llama-gemma3-cli` | `~/robi-llm/llama.cpp/build/bin/llama-gemma3-cli` | 14376 | `0565a594f4ea699c912ddfbf687033500984f18c12bf64c7df013446d68bb2ea` |
| `~/robi-llm/llama.cpp/build/bin/libggml.so.0` | `~/robi-llm/llama.cpp/build/bin/libggml.so.0.26.0` | 53048 | `88e61e534f6d06c47c01d50fb5eab5f767dbb557c308193a7397c58d70178bb3` |
| `~/robi-llm/llama.cpp/build/bin/libllama.so.0` | `~/robi-llm/llama.cpp/build/bin/libllama.so.0.6.0` | 4504416 | `e4aabac2ffd4a693ce20f0a8a1cc7da858bf05d2993d21ae3a7c075a5a3afaf5` |
| `~/robi-llm/llama.cpp/build/bin/libllama-cli-impl.so` | `~/robi-llm/llama.cpp/build/bin/libllama-cli-impl.so` | 211072 | `184ba495237318bbc2790aa76b8afe9dfa5f8731a50842bd9e04b7e7c2216420` |
| `~/robi-llm/llama.cpp/build/bin/libllama-server-impl.so` | `~/robi-llm/llama.cpp/build/bin/libllama-server-impl.so` | 6493960 | `a8d3e2f19277163c032c704ccf89146e03dcec453b8e606815427c61afda498c` |
| `~/robi-llm/llama.cpp/build/bin/llama-bench` | `~/robi-llm/llama.cpp/build/bin/llama-bench` | 562784 | `98b0dca2db65c519602a09d8f4f63856b6bf6f19789f1beb31146fe01d1cc3da` |
| `~/robi-llm/llama.cpp/build/bin/libllama-bench-impl.so` | `~/robi-llm/llama.cpp/build/bin/libllama-bench-impl.so` | 431144 | `82760e21983b5f5df549adfb26e7bb2f417c5ac0bc39e88a7ac3e337f887de1b` |
| `~/robi-llm/llama.cpp/build/bin/libggml-cpu.so.0.26.0` | `~/robi-llm/llama.cpp/build/bin/libggml-cpu.so.0.26.0` | 995864 | `8a5b3372ff0c9b0f3eec4fd0ad1b821d5c1296d233e3c1d4e07e1014373e3195` |
| `~/robi-llm/llama.cpp/build/bin/libllama-common.so.0` | `~/robi-llm/llama.cpp/build/bin/libllama-common.so.0.6.0` | 5019600 | `fbd7bb1920772fad327329a804876d40c6346db4a76dc6f73459fb2a6c02cf40` |
| `~/robi-llm/llama.cpp/build/bin/libggml-base.so.0.26.0` | `~/robi-llm/llama.cpp/build/bin/libggml-base.so.0.26.0` | 803864 | `6ac36ec1faaea30ed98b40ceef6d0a1e7a360e5ea67bd44f4f228a9ebb080d67` |
| `~/robi-llm/llama.cpp/build/bin/libggml-base.so.0` | `~/robi-llm/llama.cpp/build/bin/libggml-base.so.0.26.0` | 803864 | `6ac36ec1faaea30ed98b40ceef6d0a1e7a360e5ea67bd44f4f228a9ebb080d67` |
| `~/robi-llm/llama.cpp/build/bin/llama-qwen2vl-cli` | `~/robi-llm/llama.cpp/build/bin/llama-qwen2vl-cli` | 14376 | `0565a594f4ea699c912ddfbf687033500984f18c12bf64c7df013446d68bb2ea` |
| `~/robi-llm/llama.cpp/build/bin/libggml.so` | `~/robi-llm/llama.cpp/build/bin/libggml.so.0.26.0` | 53048 | `88e61e534f6d06c47c01d50fb5eab5f767dbb557c308193a7397c58d70178bb3` |
| `~/robi-llm/llama.cpp/build/bin/libggml-cpu.so.0` | `~/robi-llm/llama.cpp/build/bin/libggml-cpu.so.0.26.0` | 995864 | `8a5b3372ff0c9b0f3eec4fd0ad1b821d5c1296d233e3c1d4e07e1014373e3195` |
| `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-base.so` | `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-base.so` | 603544 | `3a352e9ba1cd63cfd3106db1f6b74c2bd66afbfb69389f6501eb4358cb740ae7` |
| `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-cpu.so` | `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-cpu.so` | 537576 | `6807aecd17448a988c19bb599033ba8089b3928d63686bb246a994fa7cee6e91` |
| `~/robi-llm/llama5050gpu.cpp/build/bin/libllama.so` | `~/robi-llm/llama5050gpu.cpp/build/bin/libllama.so` | 1720248 | `aa95f4be2aa7315c917ff0854f3793cc9d999866f3ab1d783ccab5ef92bb7180` |
| `~/robi-llm/llama5050gpu.cpp/build/bin/llama-bench` | `~/robi-llm/llama5050gpu.cpp/build/bin/llama-bench` | 427600 | `088b101842d2292a64745473ba88f0a55375c735192347779c92330251927942` |
| `~/robi-llm/llama5050gpu.cpp/build/bin/libggml.so` | `~/robi-llm/llama5050gpu.cpp/build/bin/libggml.so` | 217008 | `4963d831bc44c8f73767258781d007bcd47401cb9b5c9e63e081d1bfba205fa4` |
| `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-cuda.so` | `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-cuda.so` | 98862856 | `13af90e7668f8f2f0c2078892f4de23e8fd6dde2637f94e0c43bbbfe862302c9` |
| `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-base.so` | `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-base.so` | 603544 | `c3c536299faeda6513edd4b7dfe504a27988c7fac6902093fd683614250aa47c` |
| `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-cpu.so` | `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-cpu.so` | 553056 | `8c437fa0356dc76c2e548f1aa1dce93c04182d51195270e876b62f5916fab54c` |
| `~/robi-llm/llama-qwen3-gpu/build/bin/libllama.so` | `~/robi-llm/llama-qwen3-gpu/build/bin/libllama.so` | 1736568 | `21eb10d45d357724e7ad2a456ecabcf16a47c2f0805571e782aaf2445b36e1a0` |
| `~/robi-llm/llama-qwen3-gpu/build/bin/llama-bench` | `~/robi-llm/llama-qwen3-gpu/build/bin/llama-bench` | 427600 | `265ce269461e9061a3e77cb65bfb477388240615d8ef1aa99466890b64ac18f0` |
| `~/robi-llm/llama-qwen3-gpu/build/bin/libggml.so` | `~/robi-llm/llama-qwen3-gpu/build/bin/libggml.so` | 217008 | `a716fe644ecd7ff47efb032774f7d747217e059f42838781795cbd64195c2b54` |
| `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-cuda.so` | `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-cuda.so` | 52478824 | `cce93a8974a1ab69b899f81429d1e7a399864d7f22d4c9c4911af450f350d8b1` |

## 明示した対象の有無

- `~/robi-llm/llama.cpp/build/bin/llama-cli`: 実体あり
- `~/robi-llm/llama.cpp/build/bin/llama-server`: 実体なし
- `~/robi-llm/llama.cpp/build/bin/llama-bench`: 実体あり
- `~/robi-llm/llama.cpp/build/bin/libggml-cuda.so`: 実体なし
- `~/robi-llm/llama.cpp/build-gpu/bin/llama-cli`: 実体なし
- `~/robi-llm/llama.cpp/build-gpu/bin/llama-server`: 実体なし
- `~/robi-llm/llama.cpp/build-gpu/bin/llama-bench`: 実体なし
- `~/robi-llm/llama.cpp/build-gpu/bin/libggml-cuda.so`: 実体なし
- `~/robi-llm/llama5050gpu.cpp/build/bin/llama-cli`: 実体なし
- `~/robi-llm/llama5050gpu.cpp/build/bin/llama-server`: 実体なし
- `~/robi-llm/llama5050gpu.cpp/build/bin/llama-bench`: 実体あり
- `~/robi-llm/llama5050gpu.cpp/build/bin/libggml-cuda.so`: 実体あり
- `~/robi-llm/llama5050gpu.cpp/build-gpu/bin/llama-cli`: 実体なし
- `~/robi-llm/llama5050gpu.cpp/build-gpu/bin/llama-server`: 実体なし
- `~/robi-llm/llama5050gpu.cpp/build-gpu/bin/llama-bench`: 実体なし
- `~/robi-llm/llama5050gpu.cpp/build-gpu/bin/libggml-cuda.so`: 実体なし
- `~/robi-llm/llama-qwen3-gpu/build/bin/llama-cli`: 実体なし
- `~/robi-llm/llama-qwen3-gpu/build/bin/llama-server`: 実体なし
- `~/robi-llm/llama-qwen3-gpu/build/bin/llama-bench`: 実体あり
- `~/robi-llm/llama-qwen3-gpu/build/bin/libggml-cuda.so`: 実体あり
- `~/robi-llm/llama-qwen3-gpu/build-gpu/bin/llama-cli`: 実体なし
- `~/robi-llm/llama-qwen3-gpu/build-gpu/bin/llama-server`: 実体なし
- `~/robi-llm/llama-qwen3-gpu/build-gpu/bin/llama-bench`: 実体なし
- `~/robi-llm/llama-qwen3-gpu/build-gpu/bin/libggml-cuda.so`: 実体なし

## ELFの直接依存（readelfによる読み取り）


`~/robi-llm/llama.cpp/build/bin/llama-cli`

```text
0x0000000000000001 (NEEDED)             Shared library: [libllama-cli-impl.so]
0x0000000000000001 (NEEDED)             Shared library: [libpthread.so.0]
0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
0x0000000000000001 (NEEDED)             Shared library: [ld-linux-aarch64.so.1]
0x000000000000001d (RUNPATH)            Library runpath: [~/robi-llm/llama.cpp/build/bin:]
```

`~/robi-llm/llama.cpp/build/bin/llama-bench`

```text
0x0000000000000001 (NEEDED)             Shared library: [libllama-bench-impl.so]
0x0000000000000001 (NEEDED)             Shared library: [libllama.so.0]
0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
0x0000000000000001 (NEEDED)             Shared library: [ld-linux-aarch64.so.1]
0x000000000000001d (RUNPATH)            Library runpath: [~/robi-llm/llama.cpp/build/bin:]
```

`~/robi-llm/llama5050gpu.cpp/build/bin/llama-bench`

```text
0x0000000000000001 (NEEDED)             Shared library: [libllama.so]
0x0000000000000001 (NEEDED)             Shared library: [libpthread.so.0]
0x0000000000000001 (NEEDED)             Shared library: [libggml.so]
0x0000000000000001 (NEEDED)             Shared library: [libggml-base.so]
0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libm.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
0x0000000000000001 (NEEDED)             Shared library: [ld-linux-aarch64.so.1]
0x000000000000001d (RUNPATH)            Library runpath: [~/robi-llm/llama5050gpu.cpp/build/bin:]
```

`~/robi-llm/llama5050gpu.cpp/build/bin/libggml-cuda.so`

```text
0x0000000000000001 (NEEDED)             Shared library: [libggml-base.so]
0x0000000000000001 (NEEDED)             Shared library: [libcudart.so.10.2]
0x0000000000000001 (NEEDED)             Shared library: [libcublas.so.10]
0x0000000000000001 (NEEDED)             Shared library: [libcuda.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libm.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
0x0000000000000001 (NEEDED)             Shared library: [ld-linux-aarch64.so.1]
0x000000000000001d (RUNPATH)            Library runpath: [~/robi-llm/llama5050gpu.cpp/build/bin:]
```

`~/robi-llm/llama-qwen3-gpu/build/bin/llama-bench`

```text
0x0000000000000001 (NEEDED)             Shared library: [libllama.so]
0x0000000000000001 (NEEDED)             Shared library: [libpthread.so.0]
0x0000000000000001 (NEEDED)             Shared library: [libggml.so]
0x0000000000000001 (NEEDED)             Shared library: [libggml-base.so]
0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libm.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
0x0000000000000001 (NEEDED)             Shared library: [ld-linux-aarch64.so.1]
0x000000000000001d (RUNPATH)            Library runpath: [~/robi-llm/llama-qwen3-gpu/build/bin:]
```

`~/robi-llm/llama-qwen3-gpu/build/bin/libggml-cuda.so`

```text
0x0000000000000001 (NEEDED)             Shared library: [libggml-base.so]
0x0000000000000001 (NEEDED)             Shared library: [libcudart.so.10.2]
0x0000000000000001 (NEEDED)             Shared library: [libcublas.so.10]
0x0000000000000001 (NEEDED)             Shared library: [libcuda.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libstdc++.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libm.so.6]
0x0000000000000001 (NEEDED)             Shared library: [libgcc_s.so.1]
0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
0x0000000000000001 (NEEDED)             Shared library: [ld-linux-aarch64.so.1]
0x000000000000001d (RUNPATH)            Library runpath: [~/robi-llm/llama-qwen3-gpu/build/bin:]
```
