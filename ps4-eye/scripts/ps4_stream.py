import cv2
import numpy as np
import threading
import time
import io
from flask import Flask, Response, request, jsonify, send_file

app = Flask(__name__)
lock = threading.Lock()

settings = {"r": 1.0, "g": 1.0, "b": 1.0}
latest_jpeg = None
running = True

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>PS4 Camera - Jetson Nano</title>
<style>
body {
    background: #15191f;
    color: #eee;
    font-family: system-ui, sans-serif;
    margin: 24px;
}
main { max-width: 1300px; margin: auto; }
h2 { font-weight: 600; }
img {
    display: block;
    width: 100%;
    height: auto;
    background: #000;
    border-radius: 8px;
}
.panel {
    margin-top: 22px;
    padding: 20px;
    background: #242a32;
    border-radius: 10px;
}
.control {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 14px 0;
}
.control label { width: 55px; }
.control input { flex: 1; }
.control output { width: 50px; text-align: right; }
button, a.button {
    display: inline-block;
    padding: 9px 15px;
    background: #43566b;
    border: 0;
    border-radius: 6px;
    color: #fff;
    text-decoration: none;
    cursor: pointer;
}
small { color: #aaa; }
</style>
</head>
<body>
<main>
<h2>PS4 Camera / Jetson Nano</h2>
<img src="/stream" alt="Stereo camera stream">

<div class="panel">
<h3>RGBゲイン調整</h3>
<small>1.00が無補正。緑が強い場合はGを下げて調整します。</small>

<div class="control">
<label>Red</label>
<input id="r" type="range" min="0.3" max="2.5" step="0.05" value="1">
<output id="rv">1.00</output>
</div>
<div class="control">
<label>Green</label>
<input id="g" type="range" min="0.3" max="2.5" step="0.05" value="1">
<output id="gv">1.00</output>
</div>
<div class="control">
<label>Blue</label>
<input id="b" type="range" min="0.3" max="2.5" step="0.05" value="1">
<output id="bv">1.00</output>
</div>

<button onclick="resetGains()">リセット</button>
<a class="button" href="/snapshot" target="_blank">静止画を保存</a>
</div>
</main>

<script>
let pending = null;

function values() {
    return {
        r: Number(document.getElementById("r").value),
        g: Number(document.getElementById("g").value),
        b: Number(document.getElementById("b").value)
    };
}

function update() {
    const v = values();

    for (const k of ["r", "g", "b"]) {
        document.getElementById(k + "v").textContent = v[k].toFixed(2);
    }

    clearTimeout(pending);
    pending = setTimeout(() => {
        fetch("/settings", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(v)
        });
    }, 100);
}

function resetGains() {
    for (const k of ["r", "g", "b"]) {
        document.getElementById(k).value = 1;
    }
    update();
}

for (const k of ["r", "g", "b"]) {
    document.getElementById(k).addEventListener("input", update);
}
</script>
</body>
</html>
"""

def capture_loop():
    global latest_jpeg, running

    cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

    if not cap.isOpened():
        print("ERROR: /dev/video0 を開けません")
        running = False
        return

    cap.set(cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"YUYV"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
    cap.set(cv2.CAP_PROP_FPS, 30)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    print("Camera:", cap.get(cv2.CAP_PROP_FRAME_WIDTH),
          "x", cap.get(cv2.CAP_PROP_FRAME_HEIGHT), flush=True)

    while running:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1)
            continue

        # PS4 Cameraの左右映像を切り出す
        if frame.shape[1] < 2608 or frame.shape[0] < 800:
            print("Unexpected frame shape:", frame.shape)
            time.sleep(1)
            continue

        left = frame[0:800, 48:1328]
        right = frame[0:800, 1328:2608]

        stereo = cv2.hconcat([left, right])

        # 180度回転すると左右の表示順も入れ替わる
        with lock:
            r = settings["r"]
            g = settings["g"]
            b = settings["b"]

        if r != 1.0 or g != 1.0 or b != 1.0:
            gains = np.array([b, g, r], dtype=np.float32)
            stereo = np.clip(
                stereo.astype(np.float32) * gains,
                0, 255
            ).astype(np.uint8)

        ok, buffer = cv2.imencode(
            ".jpg", stereo,
            [cv2.IMWRITE_JPEG_QUALITY, 90]
        )
        if ok:
            with lock:
                latest_jpeg = buffer.tobytes()

    cap.release()

@app.route("/")
def index():
    return HTML

@app.route("/settings", methods=["POST"])
def set_settings():
    data = request.get_json(silent=True) or {}
    with lock:
        for k in ("r", "g", "b"):
            if k in data:
                try:
                    value = float(data[k])
                    if np.isfinite(value):
                        settings[k] = max(0.3, min(2.5, value))
                except (ValueError, TypeError):
                    pass
        return jsonify(settings.copy())

@app.route("/stream")
def stream():
    def frames():
        while running:
            with lock:
                jpg = latest_jpeg
            if jpg is not None:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" +
                       jpg + b"\r\n")
            time.sleep(0.05)

    return Response(
        frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/snapshot")
def snapshot():
    with lock:
        jpg = latest_jpeg
    if jpg is None:
        return "No image available", 503

    return send_file(
        io.BytesIO(jpg),
        mimetype="image/jpeg",
        as_attachment=True,
        attachment_filename="ps4_stereo.jpg"
    )

if __name__ == "__main__":
    worker = threading.Thread(target=capture_loop, daemon=True)
    worker.start()

    app.run(
        host="0.0.0.0",
        port=5000,
        threaded=True,
        use_reloader=False
    )
