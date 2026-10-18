import cv2
import numpy as np
import threading
import time
from flask import Flask, Response, request

app = Flask(__name__)
condition = threading.Condition()
latest = None
frame_id = 0

CALIB = "/home/JETSON_USER/ps4_calib/stereo_calibration.npz"
SIZE = (640, 400)
FULL_SIZE = (1280, 800)

# ---------------------------------------------
# Calibration: Bを基準に左右を反転
# ---------------------------------------------
c = np.load(CALIB)

K_a, D_a = c["K_a"], c["D_a"]
K_b, D_b = c["K_b"], c["D_b"]
R, T = c["R"], c["T"]

scale = SIZE[0] / FULL_SIZE[0]

def scaled_K(K):
    M = K.copy()
    M[0, :] *= scale
    M[1, :] *= scale
    return M

KA = scaled_K(K_a)
KB = scaled_K(K_b)

# 元のA→BからB→Aへ変換
R_ba = R.T
T_ba = -R.T @ T

R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
    KB, D_b,
    KA, D_a,
    SIZE,
    R_ba, T_ba,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=0
)

map_b1, map_b2 = cv2.initUndistortRectifyMap(
    KB, D_b, R1, P1, SIZE, cv2.CV_16SC2
)
map_a1, map_a2 = cv2.initUndistortRectifyMap(
    KA, D_a, R2, P2, SIZE, cv2.CV_16SC2
)

baseline = np.linalg.norm(T_ba)
focal = P1[0, 0]

print("Baseline: {:.2f} mm".format(baseline * 1000))
print("Rectified focal: {:.2f} px".format(focal))
print("Q disparity coefficient:", Q[3, 2])

if Q[3, 2] <= 0:
    raise RuntimeError("Unexpected Q sign: check camera order")

# ---------------------------------------------
# Stereo matching
# ---------------------------------------------
block = 7
matcher = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=128,
    blockSize=block,
    P1=8 * block * block,
    P2=32 * block * block,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=80,
    speckleRange=2
)

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
    margin:0;height:100%;
    background:#101216;color:#eee;
    font-family:system-ui,sans-serif;
}
main{
    height:100dvh;padding:12px;
    display:flex;flex-direction:column;gap:10px;
}
header{
    display:flex;align-items:center;
    justify-content:space-between;
    flex-wrap:wrap;gap:8px;
}
h1{margin:0;font-size:17px}
.controls{display:flex;gap:6px;flex-wrap:wrap}
button{
    border:1px solid #3a424c;
    border-radius:7px;
    padding:8px 13px;
    color:#eee;background:#252b33;
    cursor:pointer;
}
button.active{background:#e1eafa;color:#111}
.viewport{
    flex:1;min-height:0;
    background:#080a0d;
    display:flex;justify-content:center;
    align-items:center;border-radius:9px;
    overflow:hidden;
}
.viewport img{
    display:block;width:100%;height:100%;
    object-fit:contain;
}
</style>
</head>
<body>
<main>
<header>
<h1>PS4 Stereo Vision</h1>
<div class="controls">
<button class="active" data-mode="compare"
 onclick="setMode('compare')">比較</button>
<button data-mode="overlay"
 onclick="setMode('overlay')">オーバーレイ</button>
<button data-mode="depth"
 onclick="setMode('depth')">深度</button>
<button data-mode="camera"
 onclick="setMode('camera')">カメラ</button>
</div>
</header>
<div class="viewport">
<img id="video" src="/stream?mode=compare">
</div>
</main>
<script>
function setMode(mode){
    document.querySelectorAll("button[data-mode]")
      .forEach(b=>b.classList.toggle(
        "active",b.dataset.mode===mode));
    document.getElementById("video").src=
        "/stream?mode="+mode+"&t="+Date.now();
}
</script>
</body>
</html>
"""

def label(img, text):
    cv2.putText(
        img, text, (12, 28),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.75, (255, 255, 255), 2
    )

def capture_loop():
    global latest, frame_id

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("Camera open failed", flush=True)
        return

    cap.set(cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"YUYV"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    print("Camera:", cap.get(cv2.CAP_PROP_FRAME_WIDTH),
          "x", cap.get(cv2.CAP_PROP_FRAME_HEIGHT),
          flush=True)

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1)
            continue

        if frame.shape[0] < 800 or frame.shape[1] < 2608:
            continue

        a = cv2.resize(
            frame[:800, 48:1328], SIZE,
            interpolation=cv2.INTER_AREA
        )
        b = cv2.resize(
            frame[:800, 1328:2608], SIZE,
            interpolation=cv2.INTER_AREA
        )

        # B基準でレンズ歪み・左右の傾きを補正
        right_base = cv2.remap(
            b, map_b1, map_b2, cv2.INTER_LINEAR
        )
        left_match = cv2.remap(
            a, map_a1, map_a2, cv2.INTER_LINEAR
        )

        gray1 = cv2.cvtColor(right_base, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(left_match, cv2.COLOR_BGR2GRAY)

        disp = matcher.compute(
            gray1, gray2
        ).astype(np.float32) / 16.0

        valid = (disp > 0) & (disp < 128)

        # Q行列を用いて視差からZ方向の距離（m）を求める
        denominator = disp * Q[3, 2] + Q[3, 3]

        z = np.full(disp.shape, np.nan, dtype=np.float32)
        np.divide(
            Q[2, 3], denominator,
            out=z,
            where=valid & (np.abs(denominator) > 1e-6)
        )

        valid &= np.isfinite(z) & (z > 0.15) & (z < 5.0)

        # 画面中央80x80ピクセルの距離を代表値とする
        cx, cy = SIZE[0] // 2, SIZE[1] // 2
        x1, x2 = cx - 40, cx + 40
        y1, y2 = cy - 40, cy + 40

        region_valid = valid[y1:y2, x1:x2]
        region_z = z[y1:y2, x1:x2]
        samples = region_z[region_valid]

        # 有効な画素が一定数ある場合のみ距離を表示
        if samples.size >= 100:
            distance_cm = float(np.median(samples)) * 100
            dist_text = "{:.1f} cm".format(distance_cm)
        else:
            dist_text = "N/A"

        norm = np.clip(
            disp / 128 * 255, 0, 255
        ).astype(np.uint8)

        depth = cv2.applyColorMap(
            norm, cv2.COLORMAP_JET
        )
        depth[~valid] = 0

        mixed = cv2.addWeighted(
            right_base, 0.55,
            depth, 0.45, 0
        )

        overlay = right_base.copy()
        overlay[valid] = mixed[valid]

        # 測距範囲の枠
        cv2.rectangle(
            overlay,
            (x1, y1), (x2, y2),
            (255, 255, 255), 2
        )
        cv2.drawMarker(
            overlay, (cx, cy),
            (255, 255, 255),
            cv2.MARKER_CROSS, 16, 1
        )

        # 距離を黒背景に白文字で表示
        cv2.rectangle(
            overlay, (8, 42), (225, 83),
            (0, 0, 0), -1
        )
        cv2.putText(
            overlay, dist_text,
            (16, 72),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.95, (255, 255, 255), 2
        )

        # 比較：上にオーバーレイ、下に2枚
        overlay_big = cv2.resize(overlay, (960, 600))
        cam_small = cv2.resize(right_base, (480, 300))
        depth_small = cv2.resize(depth, (480, 300))

        label(overlay_big, "overlay")
        label(cam_small, "camera")
        label(depth_small, "disparity")

        compare = cv2.vconcat([
            overlay_big,
            cv2.hconcat([cam_small, depth_small])
        ])

        with condition:
            latest = {
                "compare": compare,
                "overlay": overlay,
                "depth": depth,
                "camera": right_base
            }
            frame_id += 1
            condition.notify_all()

    cap.release()

@app.route("/")
def index():
    return HTML

@app.route("/stream")
def stream():
    mode = request.args.get("mode", "compare")
    if mode not in ("compare", "overlay", "depth", "camera"):
        mode = "compare"

    def generate():
        last = -1

        while True:
            with condition:
                ready = condition.wait_for(
                    lambda: latest is not None and frame_id != last,
                    timeout=5
                )
                if not ready:
                    continue

                img = latest[mode]
                last = frame_id

            ok, jpg = cv2.imencode(
                ".jpg", img,
                [cv2.IMWRITE_JPEG_QUALITY, 85]
            )

            if ok:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + jpg.tobytes()
                    + b"\r\n"
                )

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    threading.Thread(
        target=capture_loop,
        daemon=True
    ).start()

    app.run(
        host="0.0.0.0",
        port=5001,
        threaded=True,
        use_reloader=False
    )
