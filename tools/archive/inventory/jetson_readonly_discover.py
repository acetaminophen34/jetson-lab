import os,sys,json,hashlib,stat,subprocess,re
from pathlib import Path
home=Path.home()
def hashfile(p):
 h=hashlib.sha256()
 with open(str(p),'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()
def meta(p,sha=False):
 try:
  s=p.stat();d={'path':str(p),'realpath':str(p.resolve()),'bytes':s.st_size,'mtime_ns':s.st_mtime_ns,'mode':oct(s.st_mode&0o777)}
  if sha and p.is_file():d['sha256']=hashfile(p)
  return d
 except Exception as e:return {'path':str(p),'error':type(e).__name__}
def walk(base,depth):
 if not base.exists():return
 for root,dirs,files in os.walk(str(base)):
  rel=Path(root).relative_to(base)
  dirs[:]=[d for d in dirs if d not in ['.git','.ssh','.aws','.config','.cache','.local','node_modules','__pycache__','preservation','inventory','inventory-extra'] and not d.startswith('.')]
  if len(rel.parts)>=depth:dirs[:]=[]
  for f in files:yield Path(root)/f
out={'camera_candidates':[],'build_files':[],'binaries':[],'bf16':[],'models':[],'startup_candidates':[],'inventory':[],'git':[],'system_candidates':[]}
# Narrow camera discovery across home, avoiding LLM vendor trees/build dirs.
for p in walk(home,4):
 if not p.is_file():continue
 rel=p.relative_to(home)
 if any(x.startswith('build') for x in rel.parts) or 'llama.cpp' in rel.parts or 'llama5050gpu.cpp' in rel.parts or 'jetson-patches' in rel.parts:continue
 name=p.name.lower()
 if any(x in name for x in ['ps4','stereo','calib','depth','camera','param_']) and p.suffix.lower() in ['.py','.sh','.json','.yaml','.yml','.ini','.cfg','.conf','.npy','.npz','.xml','.txt','.jpg']:
  out['camera_candidates'].append(meta(p,True))
for n in ['ps4_depth_test.py','ps4_depth_stream.py','ps4_depth.py','ps4_stream.py','ps4_calib_capture.py','ps4_calibrate.py']:
 if not (home/n).exists():out['camera_candidates'].append(meta(home/n))
repos=[home/'robi-llm'/x for x in ['llama.cpp','llama5050gpu.cpp','llama-qwen3-gpu','jetson-patches']]
for repo in repos:
 if not repo.exists():continue
 def run(args):
  r=subprocess.run(args,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ,GIT_OPTIONAL_LOCKS='0'));return {'exit':r.returncode,'stdout':r.stdout.decode('utf8','replace'),'stderr':r.stderr.decode('utf8','replace')}
 out['git'].append({'path':str(repo),'head':run(['git','-C',str(repo),'rev-parse','HEAD']),'status':run(['git','-C',str(repo),'status','--porcelain','--untracked-files=normal'])})
 for p in walk(repo,7):
  if not p.is_file():continue
  if p.name in ['CMakeCache.txt','link.txt','flags.make','compile_commands.json']:
   # flags.make only CUDA backend, link and caches all small metadata.
   if p.name!='flags.make' or 'ggml-cuda' in str(p):out['build_files'].append(meta(p,True))
  if p.name.startswith('cuda_bf16.') or p.name in ['ggml-cpu-impl.h.bak','CMakeLists.txt.bak','server-schema.cpp.bak']:out['bf16'].append(meta(p,True))
  if p.suffix=='.so' or '.so.' in p.name or (p.parent.name=='bin' and os.access(str(p),os.X_OK)):
   try:
    with p.open('rb') as f:elf=f.read(4)==b'\x7fELF'
    if elf:out['binaries'].append(meta(p,True))
   except OSError:pass
  if len(p.relative_to(repo).parts)<=2 and p.suffix in ['.sh','.service']:
   out['startup_candidates'].append(meta(p,True))
for base in [Path('/usr/local/cuda/include'),Path('/usr/local/cuda-10.2/include'),Path('/usr/local/cuda-10.2/targets/aarch64-linux/include')]:
 for n in ['cuda_bf16.h','cuda_bf16.hpp']:out['bf16'].append(meta(base/n,True))
for base in [home/'robi-llm/models',home/'models']:
 for p in walk(base,3):
  if p.suffix.lower()=='.gguf':out['models'].append(meta(p,True))
for base in [Path('/etc/udev/rules.d'),Path('/etc/systemd/system'),home/'.config/systemd/user',Path('/etc/modprobe.d'),Path('/etc/modules-load.d')]:
 if base.exists():
  for p in base.iterdir():
   if p.is_file() and not p.is_symlink() and p.stat().st_size<262144:
    out['system_candidates'].append(meta(p,True))
for p in home.glob('*.sh'):out['startup_candidates'].append(meta(p,True))
# Hash preexisting inventory; do not copy identity/authentication configuration.
for base in [home/'jetson-environment/inventory/20261018-001021',home/'jetson-environment/inventory-extra/20261018-001917']:
 for p in base.glob('*'):
  if p.name not in ['apt-sources.list','host.txt','network-listening.txt']:out['inventory'].append(meta(p,True))
json.dump(out,sys.stdout,ensure_ascii=False)
