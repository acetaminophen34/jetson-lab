# 固定ソースのGit履歴

既存bundle解析の抜粋。全履歴は非公開保全先に残り、bundleは本リポジトリに含めません。収集先originのURLは未保存です。

## llama 履歴

固定HEAD: `62df1815bc053066761f4eac58e288f23778e164`。HEADから到達可能なcommit数: 11632.

ブランチ（bundle由来）:

```text
refs/heads/jetson-qwen3 d3bd7193ba66c15963fd1c59448f22019a8caf6e
refs/heads/master 62df1815bc053066761f4eac58e288f23778e164
```

HEAD直近12件:

```text
62df1815bc053066761f4eac58e288f23778e164 2026-10-14T19:30:58+05:30 cuda, hip: GDN chunked kernel (#29353)
37d6d653e49aa73c947cc9631a5d499869a21cca 2026-10-14T15:20:27+02:00 skill: Update `code-review` skill for UI development (#30509)
6868a52cb337450658006ad2f9281c2eb63f1666 2026-10-14T13:16:08+02:00 ggml: fix conv_1d result layout for batched input (#28738)
3fb47677eaf0ebb569a1f94c756dcf58b8584cc0 2026-10-14T13:58:05+03:00 common : add --spec-draft-n-ubatch (#30459)
318a471a6295e53bfce7ca96ae0cf26071cbdd6e 2026-10-14T05:19:10-05:00 docs : clarify installation recommendation for Intel oneAPI Toolkit (#30407)
8c2134a8755d8a9792af513dab20282affe903e4 2026-10-14T12:36:52+03:00 ggml : add note about mul_mat_id + disable mul_mat_id_dup tests (#30501)
df18bee11e96557b07aa7b12db0976f3c7ac9165 2026-10-14T08:30:00+02:00 model: split layers evenly when no device reports free memory (#29677)
3eb101360f2666b94910b7c8e3fddbd3fd432487 2026-10-14T08:28:24+02:00 vendor : update cpp-httplib to 0.61.0 (#30494)
af0579c78a07a555d84830d01da7b61cfadbc7ef 2026-10-14T09:23:44+03:00 ggml : improve RPC tensor transfer logs (#30481)
62bacfa011cd6ba2ca30e9e891a1980b736873a9 2026-10-14T15:22:11+09:00 cuda : use SIMT implicit GEMM conv2d on AMD without WMMA (#30325)
77390baa1872e3afe4bafa3dec8ca4bcac986e41 2026-10-14T02:18:38-04:00 jinja : write floats in tojson as Python does (#30362)
c5a997624a2668248b0c86a1ff20c8b198f2320d 2026-10-13T23:17:09-07:00 opencl: use buf+offset instead of subbuffer for adreno moe expert sort (#30418)
```


## llama5050gpu 履歴

固定HEAD: `23106f94ea2bc3da929afb7330655fd5515d08dc`。HEADから到達可能なcommit数: 5050.

ブランチ（bundle由来）:

```text
refs/heads/jetson-nano-gpu 23106f94ea2bc3da929afb7330655fd5515d08dc
refs/heads/master 5cdadfc326163ed1fa66cf609fb1761f7928900c
```

HEAD直近12件:

```text
23106f94ea2bc3da929afb7330655fd5515d08dc 2025-04-04T22:09:12+08:00 gguf-split : --merge now respects --dry-run option (#12681)
94148ba330968bbfb8d9ecc67751bdc2218486cd 2025-04-04T16:00:46+02:00 sycl: allow ggml-sycl configuration and compilation using Visual Studio project/solution (#12625)
9ac4d611d05b03f961e627f4f399e4377bdb4ad3 2025-04-04T15:12:40+02:00 cmake: fix ggml-shaders-gen compiler paths containing spaces (#12747)
348888e0dc469a476f9e9eccb394893c513daab8 2025-04-04T10:24:12+02:00 docs : add XCFramework section to README.md [no ci] (#12746)
74d4f5b041ad837153b0e90fc864b8290e01d8d5 2025-04-04T00:54:35-05:00 vulkan: Hybrid waitForFences/getFenceStatus to reduce fence latency (#12630)
35e592eb30832187412360912ab8f2f5b7984df1 2025-04-04T00:53:20-05:00 vulkan: set cmake minimum and project name in vulkan-shaders (#12744)
7d7b1bafa7980603a61cb102879fe38a33f66c08 2025-04-03T22:18:17-07:00 opencl: update doc for OpenCL (#12702)
c262beddf29f3f3be5bbbf167b56029a19876956 2025-04-03T21:50:29+05:30 CUDA: Prefer vector flash decoding kernel for Gemma models (#12738)
5dd5d1ab00d074e3b7c02ca3ae12f6bf3e86336a 2025-04-03T23:32:54+08:00 vocab : use string_view::find() to avoid unnecessary looking up beyond the fragment range (#12706)
1c059995e080e37aeaacaae35850fc4c044b9dbe 2025-04-03T10:08:26-05:00 vulkan: Fix missing cmake logic for dot product extension (#12721)
2004644b7a5da6fe080e51861ab583480280f1d3 2025-04-03T13:12:39+01:00 ci : add env variable in ggml-ci and document the same in SYCL.md (#12736)
5f696e88e0eb490c8028421d3c5419df9dcf5385 2025-04-03T19:51:35+08:00 sync : minja (inclusionAI/Ling) and update tests (#12699)
```


## jetson-patches 履歴

固定HEAD: `cba793e345442fc9f542f3418ae4b0070bd37b06`。HEADから到達可能なcommit数: 48.

ブランチ（bundle由来）:

```text
refs/heads/main cba793e345442fc9f542f3418ae4b0070bd37b06
```

HEAD直近12件:

```text
cba793e345442fc9f542f3418ae4b0070bd37b06 2026-02-24T00:11:39+07:00 Add LFM2.5-1.2B-Thinking section to README
15ba3a7a08957049eb06cb91c75b0d46c9f519a9 2026-02-24T00:07:40+07:00 Can we compile for Liquid?
a944a1785adc7f58c5d6677bfbe574de60139cff 2025-05-06T15:53:27+07:00 two processes concurrently
678a3cb1205881443ba2f8df02d7bf50ec628289 2025-04-21T09:34:47+07:00 include small images above bigger subsections for readability
bff1a3edc25e968cb624566fb1f2e9ee8c7960b8 2025-04-21T09:28:27+07:00 prerequisites
c2930671aea08dc62685662e0a7917bd73e00d75 2025-04-21T09:07:44+07:00 include small logos for better readability
f3778c7928a85fbb0d796d718e1f35596014b300 2025-04-21T08:35:17+07:00 include Gemma 3 logo
603909b12be2c88e5dce64b19e9097e80d05b549 2025-04-20T21:58:58+07:00 Merge branch 'main' of https://github.com/kreier/llama.cpp-jetson
86415f438ad7b1702cadc3024ea1689618bdcb04 2025-04-20T21:58:53+07:00 updated graph, include comparison CPU
1c3e9e5bc9e1b0547fa78882f4d7ba1a71407362 2025-04-20T21:16:01+07:00 improve wording of a few instructions
0920d107dcd175568dba85ee017c41b9f0ad746a 2025-04-20T20:23:55+07:00 fix installation, include image
5c1c292f8ba2856b0b50765dbf13bc028fee6658 2025-04-20T16:56:39+07:00 faster memory access with GPU
```


## ps4-camera 履歴

固定HEAD: `4180061a1afd109a9204557f256d341c5850c124`。HEADから到達可能なcommit数: 14.

ブランチ（bundle由来）:

```text
refs/heads/main 4180061a1afd109a9204557f256d341c5850c124
```

HEAD直近12件:

```text
4180061a1afd109a9204557f256d341c5850c124 2022-07-17T17:26:05+02:00 Merge pull request #3 from sniff122/main
780c8a558158b3133bdfeaaa0269414fe70a9a94 2022-07-17T15:27:44+01:00 Mention about the use of the PS5 camera adapter
bdec556dd9148f54c78ed08faef9849677a70719 2021-02-19T20:12:39+01:00 Added section for video settings
a1c2d755fc7b98d0b66e5b52ee9f89dde5fdf778 2021-01-06T18:28:25+01:00 Added better specs
358ac8395f72ad10bc739a1d0a5a3b836b1bc09a 2020-12-11T22:06:32+00:00 added links
c1b2113dca7ce6360335cb2756c79883107b5b03 2020-11-25T21:31:43+01:00 added demo gif to readme
84ad96c55629170731013cd5135d8a8ad1360d36 2020-11-25T21:30:15+01:00 added demo
27e4b835a488757f063ad5aa3122557596832877 2020-11-25T21:09:54+01:00 imrpoved depth
13a3c45f4a8acc2cbbbb4506ef0a5fc921196b3d 2020-11-19T01:16:51+01:00 Merge branch 'main' of https://github.com/sieuwe1/PS4-eye-camera-for-linux-with-python-and-OpenCV into main
a7e6d078a8f49eac6abf1ae9f4bd40fc2d782304 2020-11-19T01:16:20+01:00 improved depth
19e52c697c377ba0439dcd80620d95f0071e16d3 2020-11-04T16:53:46+01:00 added warning
ea9b620fe1d2b6d29b697b9b199b217f9b774386 2020-11-04T16:49:14+01:00 added first version
```
