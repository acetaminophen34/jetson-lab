import os,sys,json,hashlib,subprocess,time,threading,resource,datetime
from pathlib import Path
home=Path.home();exe=home/'robi-llm/llama.cpp/build/bin/llama-cli';model=home/'robi-llm/models/Qwen3-0.6B-Q4_K_M.gguf'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def memory():
 d={}
 for line in Path('/proc/meminfo').read_text().splitlines():
  k,v=line.split(':',1)
  if k in ['MemTotal','MemAvailable','MemFree','SwapTotal','SwapFree']:d[k+'_kib']=int(v.split()[0])
 return d
argv=[str(exe),'-m',str(model),'--device','none','--n-gpu-layers','0','--no-kv-offload','--threads','2','--threads-batch','2','--ctx-size','512','--batch-size','32','--ubatch-size','32','--n-predict','32','--single-turn','--reasoning','off','--no-warmup','--perf','--seed','1','--temp','0','--simple-io','-p','Reply with exactly: CPU test OK.']
out={'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'argv':argv,'model_sha256':sha(model),'model_bytes':model.stat().st_size,'exe_sha256':sha(exe),'ram_before':memory(),'timeout_seconds':120,'samples':[],'loaded_cuda_libraries':[]}
if out['model_sha256']!='7af3fdf842f87b24672f8a7f1dd50404043f0bfb71093ff91c31d2b49df4631d' or out['ram_before']['MemAvailable_kib']<1048576:
 out['not_executed_reason']='model hash mismatch or MemAvailable < 1GiB';json.dump(out,sys.stdout);sys.exit(0)
env={k:v for k,v in os.environ.items() if not k.startswith(('LLAMA_ARG_','MTMD_'))}
env.update(CUDA_VISIBLE_DEVICES='',OMP_NUM_THREADS='2',OPENBLAS_NUM_THREADS='2',PYTHONDONTWRITEBYTECODE='1',LD_LIBRARY_PATH=str(exe.parent))
out['explicit_environment']={k:env[k] for k in ['CUDA_VISIBLE_DEVICES','OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','LD_LIBRARY_PATH']}
def no_core():resource.setrlimit(resource.RLIMIT_CORE,(0,0))
t0=time.monotonic();proc=subprocess.Popen(argv,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,preexec_fn=no_core)
streams={}
def drain(name,stream):streams[name]=stream.read().decode('utf8','replace')
threads=[threading.Thread(target=drain,args=(name,stream)) for name,stream in [('stdout',proc.stdout),('stderr',proc.stderr)]]
for t in threads:t.start()
out['timed_out']=False;loaded=set()
while proc.poll() is None:
 sample={'elapsed_seconds':round(time.monotonic()-t0,3),'system':memory()}
 try:
  status=Path('/proc/'+str(proc.pid)+'/status').read_text()
  for l in status.splitlines():
   if l.startswith(('VmRSS:','VmHWM:','VmSize:','Threads:')):
    k,v=l.split(':',1);sample[k]=int(v.split()[0])
  for l in Path('/proc/'+str(proc.pid)+'/maps').read_text().splitlines():
   if any(k in l for k in ['libcuda.','libcudart.','libcublas','libggml-cuda']):loaded.add(l.split()[-1])
 except OSError:pass
 out['samples'].append(sample)
 if time.monotonic()-t0>120:
  out['timed_out']=True;proc.terminate()
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:proc.kill()
  break
 time.sleep(0.25)
proc.wait()
for t in threads:t.join()
u=resource.getrusage(resource.RUSAGE_CHILDREN)
out.update(returncode=proc.returncode,wall_seconds=time.monotonic()-t0,stdout=streams.get('stdout',''),stderr=streams.get('stderr',''),ram_after=memory(),max_rss_kib=u.ru_maxrss,user_cpu_seconds=u.ru_utime,system_cpu_seconds=u.ru_stime,loaded_cuda_libraries=sorted(loaded),finished_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
json.dump(out,sys.stdout,ensure_ascii=False)
