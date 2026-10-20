import cv2
import vpi
import numpy as np
import time
from camera_paths import CALIB_DIR, CALIBRATION

p = sorted((CALIB_DIR / "pairs").glob("camA_*.png"))[0]
a = cv2.imread(str(p))
b = cv2.imread(str(p).replace("camA_", "camB_"))

size = (480,300)
a = cv2.resize(a,size)
b = cv2.resize(b,size)

c = np.load(str(CALIBRATION))

def scale(K):
    K=K.copy()
    K[0,:]*=size[0]/1280
    K[1,:]*=size[1]/800
    return K

KA,KB=scale(c["K_a"]),scale(c["K_b"])
R=c["R"].T
T=-R@c["T"]

R1,R2,P1,P2,Q,_,_=cv2.stereoRectify(
    KB,c["D_b"],KA,c["D_a"],size,R,T,
    flags=cv2.CALIB_ZERO_DISPARITY,alpha=0
)

mb1,mb2=cv2.initUndistortRectifyMap(
    KB,c["D_b"],R1,P1,size,cv2.CV_16SC2
)
ma1,ma2=cv2.initUndistortRectifyMap(
    KA,c["D_a"],R2,P2,size,cv2.CV_16SC2
)

left=cv2.cvtColor(
    cv2.remap(b,mb1,mb2,cv2.INTER_LINEAR),
    cv2.COLOR_BGR2GRAY
)
right=cv2.cvtColor(
    cv2.remap(a,ma1,ma2,cv2.INTER_LINEAR),
    cv2.COLOR_BGR2GRAY
)

sgbm=cv2.StereoSGBM_create(
    minDisparity=0,numDisparities=64,
    blockSize=5,P1=200,P2=800,
    uniquenessRatio=8
)

cpu_times=[]
for i in range(6):
    t=time.monotonic()
    cpu=sgbm.compute(left,right).astype(np.float32)/16
    cpu_times.append((time.monotonic()-t)*1000)

gpu_times=[]
with vpi.Backend.CUDA:
    vl=vpi.asimage(left).convert(vpi.Format.Y16_ER)
    vr=vpi.asimage(right).convert(vpi.Format.Y16_ER)
    for i in range(6):
        t=time.monotonic()
        result=vpi.stereodisp(
            vl,vr,window=5,maxdisp=64,
            backend=vpi.Backend.CUDA
        )
        gpu_raw=result.cpu()
        gpu_times.append((time.monotonic()-t)*1000)

gpu=gpu_raw.view(np.int16).astype(np.float32)/32

def report(name,arr):
    valid=(arr>0)&(arr<64)
    print("{} valid pixels: {:.1f}%".format(
        name,valid.mean()*100
    ))
    if np.any(valid):
        print("{} median disparity: {:.2f} px".format(
            name,np.median(arr[valid])
        ))

print("CPU SGBM: {:.1f} ms".format(
    np.mean(cpu_times[1:])
))
print("GPU VPI: {:.1f} ms".format(
    np.mean(gpu_times[1:])
))
report("CPU",cpu)
report("GPU",gpu)

# Separate max-disparity comparison from the original experiment.
with vpi.Backend.CUDA:
    vl = vpi.asimage(left).convert(vpi.Format.Y16_ER)
    vr = vpi.asimage(right).convert(vpi.Format.Y16_ER)

    for md in (64,128):
        times = []
        for i in range(5):
            t = time.monotonic()
            result = vpi.stereodisp(
                vl,vr,window=5,maxdisp=md,
                backend=vpi.Backend.CUDA
            )
            result.cpu()
            times.append((time.monotonic()-t)*1000)

        print(md,np.mean(times[1:]))
