import argparse
import cv2
import numpy as np
import threading
import time
from camera_paths import CALIBRATION as CALIB, PROTO, MODEL
from flask import Flask, Response, request

parser = argparse.ArgumentParser(description="PS4 Camera stereo face tracking")
parser.add_argument("--camera", type=int, default=0,
                    help="V4L2 camera index (default: 0)")
args = parser.parse_args()

# ===================================
# Settings
# ===================================
SIZE = (480, 300)
DEPTH_INTERVAL = 0.35
DETECT_INTERVAL = 0.65
FACE_TIMEOUT = 1.8
DISPARITIES = 96
JPEG_QUALITY = 75


cv2.setNumThreads(2)
app = Flask(__name__)

lock = threading.Lock()
raw = None
raw_id = 0
vision = None
vision_id = 0
depth_result = None
detection = None
detection_id = 0
face_result = None
output_jpg = None
output_id = 0

# ===================================
# Stereo calibration
# ===================================
c = np.load(str(CALIB))

def scale_K(K):
    k = K.copy()
    k[0, :] *= SIZE[0] / 1280.0
    k[1, :] *= SIZE[1] / 800.0
    return k

KA = scale_K(c["K_a"])
KB = scale_K(c["K_b"])
R = c["R"].T
T = -R @ c["T"]

R1, R2, P1, P2, Q, _, _ = cv2.stereoRectify(
    KB, c["D_b"], KA, c["D_a"],
    SIZE, R, T,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=0
)

if Q[3, 2] <= 0:
    raise RuntimeError("Incorrect stereo orientation")

mb1, mb2 = cv2.initUndistortRectifyMap(
    KB, c["D_b"], R1, P1, SIZE, cv2.CV_16SC2
)
ma1, ma2 = cv2.initUndistortRectifyMap(
    KA, c["D_a"], R2, P2, SIZE, cv2.CV_16SC2
)

# ===================================
# DNN model
# ===================================
net = cv2.dnn.readNetFromCaffe(
    str(PROTO), str(MODEL)
)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

block = 5
matcher = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=DISPARITIES,
    blockSize=block,
    P1=8*block*block,
    P2=32*block*block,
    disp12MaxDiff=1,
    uniquenessRatio=8,
    speckleWindowSize=60,
    speckleRange=2
)

# ===================================
# Camera: newest frame only
# ===================================
def camera_worker():
    global raw, raw_id

    cap = cv2.VideoCapture(args.camera, cv2.CAP_V4L2)
    cap.set(cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"YUYV"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    if not cap.isOpened():
        print("ERROR: Camera not opened", flush=True)
        return

    print("Camera connected", flush=True)

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.03)
            continue

        if frame.shape[0] < 800 or frame.shape[1] < 2608:
            continue

        with lock:
            raw = (frame, time.monotonic())
            raw_id += 1

# ===================================
# Lightweight optical-flow tracking
# ===================================
def points_in_face(gray, box):
    x1, y1, x2, y2 = box.astype(int)
    mask = np.zeros(gray.shape, np.uint8)
    x1 = max(0, x1)
    y1 = max(0, y1)
    x2 = min(SIZE[0], x2)
    y2 = min(SIZE[1], y2)

    if x2 <= x1 or y2 <= y1:
        return None

    mask[y1:y2, x1:x2] = 255
    return cv2.goodFeaturesToTrack(
        gray, 60, 0.01, 5, mask=mask
    )

def vision_worker():
    global vision, vision_id, face_result

    previous_gray = None
    points = None
    box = None
    face_seen = 0
    used_detection = -1
    processed_raw = -1

    while True:
        with lock:
            item = raw
            seq = raw_id
            det = detection
            det_seq = detection_id

        if item is None or seq == processed_raw:
            time.sleep(0.006)
            continue

        processed_raw = seq
        frame, captured_at = item

        a = cv2.resize(
            frame[:800, 48:1328], SIZE,
            interpolation=cv2.INTER_AREA
        )
        b = cv2.resize(
            frame[:800, 1328:2608], SIZE,
            interpolation=cv2.INTER_AREA
        )

        base = cv2.remap(
            b, mb1, mb2, cv2.INTER_LINEAR
        )
        gray = cv2.cvtColor(
            base, cv2.COLOR_BGR2GRAY
        )

        now = time.monotonic()

        # 新しいDNN検出結果を適用
        if det is not None and det_seq != used_detection:
            new_box, det_time = det

            if now - det_time < 1.2:
                if box is not None:
                    old_c = (box[:2]+box[2:])/2
                    new_c = (new_box[:2]+new_box[2:])/2
                    if np.linalg.norm(old_c-new_c) < 110:
                        box = box*0.25 + new_box*0.75
                    else:
                        box = new_box.copy()
                else:
                    box = new_box.copy()

                points = points_in_face(gray, box)
                face_seen = now

            used_detection = det_seq

        # DNNの検出と検出の間は光学フロー
        elif (box is not None and
              points is not None and
              previous_gray is not None):

            next_pts, status, _ = cv2.calcOpticalFlowPyrLK(
                previous_gray, gray, points, None,
                winSize=(17, 17),
                maxLevel=2
            )

            if next_pts is not None and status is not None:
                good_old = points[status.ravel()==1]
                good_new = next_pts[status.ravel()==1]

                if len(good_new) >= 6:
                    shifts = (good_new-good_old).reshape(-1,2)
                    dx, dy = np.median(shifts, axis=0)

                    if abs(dx)<30 and abs(dy)<30:
                        box += np.array([dx,dy,dx,dy],
                                        dtype=np.float32)

                    points = good_new.reshape(-1,1,2)

                    if len(points)<12:
                        points = points_in_face(gray,box)
                else:
                    points = None

        if box is not None:
            box[0::2] = np.clip(box[0::2], 0, SIZE[0])
            box[1::2] = np.clip(box[1::2], 0, SIZE[1])

        if now-face_seen > FACE_TIMEOUT:
            box = None
            points = None

        previous_gray = gray

        with lock:
            vision = (base, a, captured_at)
            vision_id += 1
            face_result = None if box is None else box.copy()

# ===================================
# DNN detection, independent thread
# ===================================
def detection_worker():
    global detection, detection_id

    last_run = 0

    while True:
        if time.monotonic()-last_run < DETECT_INTERVAL:
            time.sleep(0.03)
            continue

        with lock:
            item = vision

        if item is None:
            time.sleep(0.03)
            continue

        base = item[0]
        last_run = time.monotonic()

        blob = cv2.dnn.blobFromImage(
            base, 1.0, (300,300),
            (104.0,177.0,123.0),
            swapRB=False, crop=False
        )

        net.setInput(blob)
        result = net.forward()

        candidates = []
        for i in range(result.shape[2]):
            confidence = float(result[0,0,i,2])
            if confidence < 0.65:
                continue

            coords = result[0,0,i,3:7] * [
                SIZE[0],SIZE[1],SIZE[0],SIZE[1]
            ]
            x1,y1,x2,y2 = coords

            x1 = max(0,min(SIZE[0]-1,x1))
            y1 = max(0,min(SIZE[1]-1,y1))
            x2 = max(x1+1,min(SIZE[0],x2))
            y2 = max(y1+1,min(SIZE[1],y2))

            candidates.append((
                np.array([x1,y1,x2,y2],np.float32),
                confidence
            ))

        if candidates:
            # 既存の追跡位置に近い顔を優先
            with lock:
                previous = face_result

            def score(item):
                face, conf = item
                value = conf
                if previous is not None:
                    pc = (previous[:2]+previous[2:])/2
                    nc = (face[:2]+face[2:])/2
                    value -= 0.004*np.linalg.norm(pc-nc)
                return value

            selected = max(candidates,key=score)[0]

            with lock:
                detection = (selected,time.monotonic())
                detection_id += 1

# ===================================
# Depth processing, low frequency
# ===================================
def depth_worker():
    global depth_result
    import vpi

    last_run = 0.0
    last_frame_time = -1.0
    error_count = 0

    print("VPI CUDA stereo starting (maxdisp=128)", flush=True)

    while True:
        if time.monotonic() - last_run < DEPTH_INTERVAL:
            time.sleep(0.01)
            continue

        with lock:
            item = vision

        if item is None:
            time.sleep(0.02)
            continue

        base, a, captured_at = item

        if captured_at == last_frame_time:
            time.sleep(0.01)
            continue

        last_frame_time = captured_at
        last_run = time.monotonic()

        try:
            t0 = time.monotonic()

            match = cv2.remap(
                a, ma1, ma2, cv2.INTER_LINEAR
            )

            left = cv2.cvtColor(
                base, cv2.COLOR_BGR2GRAY
            )
            right = cv2.cvtColor(
                match, cv2.COLOR_BGR2GRAY
            )

            with vpi.Backend.CUDA:
                vl = vpi.asimage(left).convert(
                    vpi.Format.Y16_ER
                )
                vr = vpi.asimage(right).convert(
                    vpi.Format.Y16_ER
                )

                result = vpi.stereodisp(
                    vl, vr,
                    window=5,
                    maxdisp=128,
                    backend=vpi.Backend.CUDA
                )

                raw_disp = result.cpu()

            disp = (
                raw_disp.view(np.int16)
                .astype(np.float32) / 32.0
            )

            valid = (
                (disp > 0) &
                (disp < 128) &
                np.isfinite(disp)
            )

            denom = disp * Q[3, 2] + Q[3, 3]
            z = np.full(
                disp.shape, np.nan, dtype=np.float32
            )

            usable = valid & (np.abs(denom) > 1e-6)

            np.divide(
                Q[2, 3], denom,
                out=z,
                where=usable
            )

            valid = (
                usable &
                np.isfinite(z) &
                (z > 0.15) &
                (z < 5.0)
            )

            color = cv2.applyColorMap(
                np.clip(
                    disp / 128.0 * 255.0,
                    0, 255
                ).astype(np.uint8),
                cv2.COLORMAP_JET
            )
            color[~valid] = 0

            with lock:
                depth_result = (
                    color, z, valid, time.monotonic()
                )

            elapsed = (time.monotonic() - t0) * 1000

            if not hasattr(depth_worker, "count"):
                depth_worker.count = 0
            depth_worker.count += 1

            if depth_worker.count % 10 == 0:
                print(
                    "VPI CUDA depth: {:.1f} ms".format(elapsed),
                    flush=True
                )

            error_count = 0

        except Exception as e:
            error_count += 1
            if error_count <= 3:
                print(
                    "VPI CUDA depth error:", repr(e),
                    flush=True
                )
            time.sleep(0.1)

# ===================================
# Display / single JPEG per update
# ===================================
def display_worker():
    global output_jpg, output_id

    previous = -1
    last_time = time.monotonic()
    fps = 0.0

    while True:
        with lock:
            item = vision
            seq = vision_id
            face = None if face_result is None \
                else face_result.copy()
            dr = depth_result

        if item is None or seq==previous:
            time.sleep(0.008)
            continue

        previous = seq
        base, _, captured_at = item
        overlay = base.copy()

        if dr is not None:
            depth,z,valid,depth_time = dr

            # 深度計算結果が古すぎる場合は距離を使わない
            depth_fresh = time.monotonic()-depth_time < 1.5

            mixed = cv2.addWeighted(
                base,0.55,depth,0.45,0
            )
            overlay[valid] = mixed[valid]
        else:
            depth = np.zeros_like(base)
            depth_fresh = False

        label = "FACE: NONE"

        if face is not None:
            x1,y1,x2,y2 = face.astype(int)
            x1 = max(0,min(SIZE[0]-1,x1))
            y1 = max(0,min(SIZE[1]-1,y1))
            x2 = max(x1+1,min(SIZE[0],x2))
            y2 = max(y1+1,min(SIZE[1],y2))

            label = "FACE: N/A"

            bw = x2-x1
            bh = y2-y1

            mx1 = x1+int(bw*0.3)
            mx2 = x1+int(bw*0.7)
            my1 = y1+int(bh*0.3)
            my2 = y1+int(bh*0.7)

            if dr is not None and depth_fresh:
                samples = z[my1:my2,mx1:mx2][
                    valid[my1:my2,mx1:mx2]
                ]
                if samples.size >= 10:
                    label = "FACE: {:.1f} cm".format(
                        np.median(samples)*100
                    )

            cv2.rectangle(
                overlay,(x1,y1),(x2,y2),
                (0,255,0),2
            )

        now = time.monotonic()
        dt = now-last_time
        last_time = now
        if dt>0:
            instant = 1/dt
            fps = instant if fps==0 else fps*0.85+instant*0.15

        age_ms = (now-captured_at)*1000

        cv2.rectangle(
            overlay,(5,5),(245,44),(0,0,0),-1
        )
        cv2.putText(
            overlay,label,(10,31),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,(255,255,255),2
        )
        cv2.putText(
            overlay,
            "{:.1f} FPS | {:.0f} ms".format(fps,age_ms),
            (10,SIZE[1]-12),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.47,(255,255,255),1
        )

        top = cv2.resize(overlay,(720,450))
        cam = cv2.resize(base,(360,225))
        dep = cv2.resize(depth,(360,225))

        compare = cv2.vconcat([
            top,cv2.hconcat([cam,dep])
        ])

        ok,jpg = cv2.imencode(
            ".jpg",compare,
            [cv2.IMWRITE_JPEG_QUALITY,JPEG_QUALITY]
        )
        if ok:
            with lock:
                output_jpg = jpg.tobytes()
                output_id += 1

# ===================================
# Browser
# ===================================
HTML = """
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PS4 Stereo Vision</title>
<style>
*{box-sizing:border-box}
html,body{
 margin:0;height:100%;background:#101216;
 color:#eee;font-family:system-ui,sans-serif
}
main{
 height:100dvh;padding:10px;
 display:flex;flex-direction:column;gap:8px
}
header{
 display:flex;align-items:center;
 justify-content:space-between;flex-wrap:wrap;gap:8px
}
h1{font-size:17px;margin:0}
.viewport{
 flex:1;min-height:0;background:#080a0d;
 display:flex;align-items:center;justify-content:center;
 border-radius:8px;overflow:hidden
}
img{width:100%;height:100%;object-fit:contain}
</style>
</head>
<body>
<main>
<header><h1>PS4 Stereo Vision</h1></header>
<div class="viewport"><img src="/stream"></div>
</main>
</body>
</html>
"""

@app.route("/")
def index():
    return HTML

@app.route("/stream")
def stream():
    def generate():
        last = -1
        while True:
            with lock:
                jpg = output_jpg
                seq = output_id

            if jpg is None or seq==last:
                time.sleep(0.01)
                continue

            last = seq
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n"
                b"Cache-Control: no-cache\r\n\r\n"
                +jpg+b"\r\n"
            )

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace;boundary=frame",
        headers={"Cache-Control":"no-store"}
    )

if __name__=="__main__":
    print("Starting low-latency stereo face tracking",flush=True)

    for worker in (
        camera_worker,
        vision_worker,
        detection_worker,
        depth_worker,
        display_worker
    ):
        threading.Thread(
            target=worker,daemon=True
        ).start()

    app.run(
        host="0.0.0.0",
        port=5001,
        threaded=True,
        use_reloader=False
    )
