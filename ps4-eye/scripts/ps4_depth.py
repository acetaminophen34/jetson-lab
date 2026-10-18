import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3448)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 808)
cap.set(cv2.CAP_PROP_FPS, 15)

if not cap.isOpened():
    raise RuntimeError("Camera open failed")

print("Camera:", cap.get(cv2.CAP_PROP_FRAME_WIDTH),
      cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

# 数フレーム取得して露出が安定するのを待つ
frame = None
for _ in range(15):
    ok, frame = cap.read()
    if not ok:
        break

cap.release()

if frame is None or not ok:
    raise RuntimeError("Frame capture failed")

# PS4 Camera: 1280x800 x 2
left = frame[0:800, 48:1328]
right = frame[0:800, 1328:2608]

# Jetson Nanoの処理負荷を減らす
left = cv2.resize(left, (640, 400))
right = cv2.resize(right, (640, 400))

# グレースケール化
gray_l = cv2.cvtColor(left, cv2.COLOR_BGR2GRAY)
gray_r = cv2.cvtColor(right, cv2.COLOR_BGR2GRAY)

# ステレオマッチング
block = 7

stereo = cv2.StereoSGBM_create(
    minDisparity=0,
    numDisparities=128,
    blockSize=block,
    P1=8 * block * block,
    P2=32 * block * block,
    disp12MaxDiff=1,
    uniquenessRatio=10,
    speckleWindowSize=100,
    speckleRange=2
)

start = time.time()
disparity = stereo.compute(gray_l, gray_r).astype(np.float32) / 16.0

print("Processing time:", round(time.time() - start, 3), "s")

# 視差が有効な場所だけ表示
valid = disparity > 0
normalized = np.clip(disparity / 128.0 * 255, 0, 255).astype(np.uint8)

depth_color = cv2.applyColorMap(normalized, cv2.COLORMAP_JET)
depth_color[~valid] = (0, 0, 0)

cv2.imwrite("depth_left.jpg", left)
cv2.imwrite("depth_right.jpg", right)
cv2.imwrite("depth_map.jpg", depth_color)
cv2.imwrite("depth_comparison.jpg", cv2.hconcat([left, depth_color]))

print("Valid disparity:", round(valid.mean() * 100, 1), "%")
print("Saved depth_map.jpg and depth_comparison.jpg")
