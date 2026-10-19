import argparse
import cv2
import time
import threading
from pathlib import Path
from flask import Flask, Response, jsonify

parser = argparse.ArgumentParser(description="PS4 Camera calibration capture")
parser.add_argument("--camera", type=int, default=0,
                    help="V4L2 camera index (default: 0)")
args = parser.parse_args()

app = Flask(__name__)

OUT = Path.home() / "ps4_calib" / "pairs"
OUT.mkdir(parents=True, exist_ok=True)

BOARD = (9, 6)  # 内側の交点
lock = threading.Lock()
latest = None
count = len(list(OUT.glob("camA_*.png")))

HTML = """
<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PS4 Stereo Calibration</title>
<style>
* {box-sizing:border-box}
body {
  background:#11151b;
  color:#eee;
  font-family:system-ui,sans-serif;
  margin:0;
}
main {
  width:min(1100px,100%);
  margin:auto;
  padding:18px;
}
header {
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:12px;
  flex-wrap:wrap;
}
h2 {font-size:20px;margin:0}
.counter {font-size:19px;color:#a7c5ec}
img {
  width:100%;
  display:block;
  border-radius:9px;
  background:#000;
  margin:16px 0;
}
button {
  width:100%;
  padding:17px;
  border:0;
  border-radius:9px;
  background:#c5ddfa;
  color:#152334;
  font-size:19px;
  font-weight:600;
  cursor:pointer;
}
button:disabled {opacity:0.45;cursor:wait}
#status {
  min-height:55px;
  margin-top:16px;
  font-size:16px;
  line-height:1.6;
}
.ok {color:#8ce3b0}
.fail {color:#f5aa99}
</style>
</head>
<body>
<main>
<header>
  <h2>Stereo Calibration</h2>
  <div class="counter" id="counter">0 / 25</div>
</header>

<img src="/stream" alt="Stereo live preview">

<button id="capture" onclick="capture()">撮影・角検出・保存</button>
<div id="status">チェッカーボードを左右両方に写してください。</div>
</main>

<script>
async function refreshCount() {
  const r = await fetch("/count");
  const d = await r.json();
  document.getElementById("counter").textContent = d.count + " / 25";
}
async function capture() {
  const button = document.getElementById("capture");
  const status = document.getElementById("status");
  button.disabled = true;
  status.textContent = "左右のコーナーを検出しています…";
  status.className = "";

  try {
    const r = await fetch("/capture", {method:"POST"});
    const d = await r.json();
    status.className = d.ok ? "ok" : "fail";
    status.textContent = d.message;
    refreshCount();
  } catch (e) {
    status.className = "fail";
    status.textContent = "通信エラー: " + e;
  } finally {
    button.disabled = false;
  }
}
refreshCount();
</script>
</body>
</html>
"""

def camera_worker():
    global latest

    cap = cv2.VideoCapture(args.camera, cv2.CAP_V4L2)
    if not cap.isOpened():
        print("ERROR: Cannot open /dev/video0", flush=True)
        return

    cap.set(cv2.CAP_PROP_FOURCC,
            cv2.VideoWriter_fourcc(*"YUYV"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
    cap.set(cv2.CAP_PROP_FPS, 15)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

    print("Camera resolution:",
          cap.get(cv2.CAP_PROP_FRAME_WIDTH),
          cap.get(cv2.CAP_PROP_FRAME_HEIGHT), flush=True)

    while True:
        ok, frame = cap.read()
        if not ok:
            time.sleep(0.1)
            continue

        if frame.shape[0] < 800 or frame.shape[1] < 2608:
            continue

        # 元の1280x800画像を保持
        a = frame[:800, 48:1328].copy()
        b = frame[:800, 1328:2608].copy()

        with lock:
            latest = (a, b, time.monotonic())

    cap.release()

@app.route("/")
def index():
    return HTML

@app.route("/count")
def get_count():
    with lock:
        return jsonify(count=count)

@app.route("/capture", methods=["POST"])
def capture():
    global count

    with lock:
        pair = latest
        if pair is None:
            return jsonify(ok=False, message="カメラ画像がありません")
        a, b, timestamp = pair
        a, b = a.copy(), b.copy()

    if time.monotonic() - timestamp > 3:
        return jsonify(ok=False, message="カメラ映像が更新されていません")

    # 両眼とも9x6交点が認識できた場合のみ保存
    flags = (
        cv2.CALIB_CB_ADAPTIVE_THRESH |
        cv2.CALIB_CB_NORMALIZE_IMAGE
    )

    found_a, corners_a = cv2.findChessboardCorners(
        cv2.cvtColor(a, cv2.COLOR_BGR2GRAY), BOARD, flags
    )
    found_b, corners_b = cv2.findChessboardCorners(
        cv2.cvtColor(b, cv2.COLOR_BGR2GRAY), BOARD, flags
    )

    if not (found_a and found_b):
        return jsonify(
            ok=False,
            message="検出失敗：Cam A={} / Cam B={}。"
                    "ボード全体が写る距離・角度にしてください。"
                    .format("OK" if found_a else "NG",
                            "OK" if found_b else "NG")
        )

    with lock:
        count += 1
        index = count

    pa = OUT / ("camA_{:03d}.png".format(index))
    pb = OUT / ("camB_{:03d}.png".format(index))

    saved_a = cv2.imwrite(str(pa), a)
    saved_b = cv2.imwrite(str(pb), b)

    if not (saved_a and saved_b):
        with lock:
            count -= 1
        pa.unlink(missing_ok=True)
        pb.unlink(missing_ok=True)
        return jsonify(ok=False, message="保存に失敗しました")

    return jsonify(
        ok=True,
        message="保存成功：ペア {}（左右とも54コーナー検出）".format(index)
    )

@app.route("/stream")
def stream():
    def generate():
        while True:
            with lock:
                pair = latest

            if pair is None:
                time.sleep(0.1)
                continue

            a, b, _ = pair
            preview = cv2.hconcat([
                cv2.resize(a, (640, 400)),
                cv2.resize(b, (640, 400))
            ])

            cv2.putText(preview, "CAM A", (15, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (255, 255, 255), 2)
            cv2.putText(preview, "CAM B", (655, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                        (255, 255, 255), 2)

            ok, jpg = cv2.imencode(
                ".jpg", preview,
                [cv2.IMWRITE_JPEG_QUALITY, 80]
            )
            if ok:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" +
                       jpg.tobytes() + b"\r\n")
            time.sleep(0.1)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

if __name__ == "__main__":
    threading.Thread(
        target=camera_worker, daemon=True
    ).start()

    print("Images saved in:", OUT, flush=True)
    app.run(
        host="0.0.0.0",
        port=5002,
        threaded=True,
        use_reloader=False
    )
