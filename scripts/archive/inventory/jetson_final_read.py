import os,sys,json,hashlib,base64,re,subprocess
from pathlib import Path
home=Path.home();out={'files':[],'artifacts':[],'startup_matches':[],'startup_search':[],'system_links':[],'diagnostics':[],'calibration_dataset':[]}
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for x in iter(lambda:f.read(1048576),b''):h.update(x)
 return h.hexdigest()
def copy(p,purpose):
 try:
  data=p.read_bytes()
  if len(data)>2*1024*1024:return
  out['files'].append({'path':str(p),'realpath':str(p.resolve()),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'purpose':purpose,'data':base64.b64encode(data).decode('ascii')})
 except OSError:pass
# All original stereo pairs are individually small; retain them only within 32MiB total.
base=home/'ps4_calib';images=list((base/'pairs').glob('*.png'));total=sum(x.stat().st_size for x in images)
for p in images:out['calibration_dataset'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)})
if total<=32*1024*1024:
 for p in images:copy(p,'元のステレオ校正入力画像（非公開）')
copy(base/'rectified_preview.jpg','実機校正のrectification確認画像（非公開）')
for n in ['llama5050gpu.cpp','llama-qwen3-gpu']:
 base=home/'robi-llm'/n/'build/ggml/src/ggml-cuda/CMakeFiles/ggml-cuda.dir'
 sample=next(base.glob('*.cu.o.d'),None)
 if sample:copy(sample,'BF16実使用includeパスの依存記録原文')
for p in [home/'robi-llm/cmake-3.28.6-linux-aarch64.tar.gz',home/'PS4-eye-camera-for-linux-with-python-and-OpenCV/Firmware_loader/firmware_V2.bin']:
 if p.is_file():out['artifacts'].append({'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p),'body_transferred':False})
for name in ['llama.cpp','llama5050gpu.cpp','llama-qwen3-gpu']:
 for build in ['build','build-gpu']:
  base=home/'robi-llm'/name/build/'bin'
  for target in ['llama-cli','llama-server','llama-bench','libggml-cuda.so']:
   p=base/target
   exists=p.is_file();out['artifacts'].append({'path':str(p),'exists':exists,'body_transferred':False})
   if exists:
    r=subprocess.run(['readelf','-d',str(p)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    deps=[l.strip() for l in r.stdout.decode('utf8','replace').splitlines() if any(k in l for k in ['NEEDED','RPATH','RUNPATH'])]
    out['diagnostics'].append({'path':str(p),'command':'readelf -d','exit':r.returncode,'dynamic_dependencies':deps})
# Neither execute nor load the USB camera.
for p in Path('/dev').glob('video*'):out['artifacts'].append({'path':str(p),'exists':True,'purpose':'video node listing only'})
for base in [Path('/etc/systemd/system'),home/'.config/systemd/user',Path('/lib/systemd/system'),Path('/etc/udev/rules.d'),Path('/etc/modprobe.d'),Path('/etc/modules-load.d'),Path('/etc/cron.d')]:
 out['startup_search'].append(str(base))
 if not base.exists():continue
 for p in base.rglob('*'):
  if p.is_symlink():
   out['system_links'].append({'path':str(p),'target':str(p.resolve())});continue
  try:
   if not p.is_file() or p.stat().st_size>262144:continue
   data=p.read_bytes()
   if re.search(rb'(?i)(password|passwd|token|secret|api[_-]?key|BEGIN.*PRIVATE KEY|://[^/\s]+:[^/\s]+@)',data):continue
   matches=[l.decode('utf8','replace') for l in data.splitlines() if re.search(rb'(?i)(ps4eye|ps4_|05a9|058[0ab]|uvcvideo|llama-(cli|bench|server))',l)]
   if matches:out['startup_matches'].append({'path':str(p),'sha256':sha(p),'matching_lines':matches});copy(p,'カメラ/LLM関連起動・ドライバ設定')
  except OSError:pass
for p in [Path('/etc/rc.local'),Path('/etc/modules'),home/'.bashrc',home/'.profile']:
 out['startup_search'].append(str(p))
 if not p.is_file():continue
 data=p.read_bytes()
 matches=[]
 for l in data.splitlines():
  if re.search(rb'(?i)(password|passwd|token|secret|api[_-]?key|\.ssh|\.env)',l):continue
  if re.search(rb'(ps4eye|ps4_|llama-(cli|bench|server)|uvcvideo)',l):matches.append(l.decode('utf8','replace'))
 if matches:out['startup_matches'].append({'path':str(p),'matching_lines':matches})
# Import only library metadata, prevent bytecode writes, do not open any camera.
code='import sys,cv2,numpy,flask,usb; print(sys.version); print("cv2",cv2.__version__,cv2.__file__); print("numpy",numpy.__version__); print("Flask",flask.__version__); print("PyUSB",usb.__version__); print(cv2.getBuildInformation())'
r=subprocess.run(['python3','-B','-c',code],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'))
out['diagnostics'].append({'command':'python library metadata only','exit':r.returncode,'output':(r.stdout+r.stderr).decode('utf8','replace')})
json.dump(out,sys.stdout,ensure_ascii=False)
