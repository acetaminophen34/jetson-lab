import cv2
import numpy as np
from camera_paths import DATA

OUT = DATA
OUT.mkdir(parents=True, exist_ok=True)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
cap.set(cv2.CAP_PROP_FPS, 15)

if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

frame = None
for i in range(15):
    ok, image = cap.read()
    if ok:
        frame = image

cap.release()

if frame is None or frame.shape[1] < 2608:
    raise RuntimeError("Invalid camera frame")

left = cv2.resize(frame[:800, 48:1328], (640, 400))
right = cv2.resize(frame[:800, 1328:2608], (640, 400))

cv2.imwrite(str(OUT / "test_left.jpg"), left)
cv2.imwrite(str(OUT / "test_right.jpg"), right)

def test(a, b, name):
    gray_a = cv2.cvtColor(a, cv2.COLOR_BGR2GRAY)
    gray_b = cv2.cvtColor(b, cv2.COLOR_BGR2GRAY)

    stereo = cv2.StereoSGBM_create(
        minDisparity=0,
        numDisparities=128,
        blockSize=7,
        P1=8 * 3 * 7**2,
        P2=32 * 3 * 7**2,
        disp12MaxDiff=1,
        uniquenessRatio=10,
        speckleWindowSize=100,
        speckleRange=2
    )

    disp = stereo.compute(gray_a, gray_b).astype(np.float32) / 16

    valid = (disp > 0) & (disp < 128)
    print(name, "Valid:", round(valid.mean() * 100, 1), "%")

    normalized = np.clip(disp / 128 * 255, 0, 255).astype(np.uint8)
    color = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
    color[~valid] = 0

    comparison = cv2.hconcat([a, color])
    cv2.imwrite(str(OUT / ("test_" + name + ".jpg")), comparison)

test(left, right, "normal")
test(right, left, "swapped")

print("Saved images in", OUT)
