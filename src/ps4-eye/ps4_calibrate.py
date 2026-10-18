import cv2
import numpy as np
from pathlib import Path

BASE = Path.home() / "ps4_calib"
PAIRS = BASE / "pairs"
OUTPUT = BASE / "stereo_calibration.npz"

BOARD = (9, 6)
SQUARE = 0.020  # 1マス20mm = 0.020m
SIZE = (1280, 800)

# チェッカーボードの3次元座標
obj = np.zeros((BOARD[0] * BOARD[1], 3), np.float32)
obj[:, :2] = np.mgrid[
    0:BOARD[0], 0:BOARD[1]
].T.reshape(-1, 2)
obj *= SQUARE

object_points = []
image_a = []
image_b = []

flags = (
    cv2.CALIB_CB_ADAPTIVE_THRESH |
    cv2.CALIB_CB_NORMALIZE_IMAGE
)

criteria = (
    cv2.TERM_CRITERIA_EPS +
    cv2.TERM_CRITERIA_MAX_ITER,
    50, 1e-6
)

files = sorted(PAIRS.glob("camA_*.png"))
print("Found:", len(files), "pairs", flush=True)

for file_a in files:
    file_b = PAIRS / file_a.name.replace("camA_", "camB_")

    if not file_b.exists():
        print("Missing pair:", file_b.name)
        continue

    a = cv2.imread(str(file_a), cv2.IMREAD_GRAYSCALE)
    b = cv2.imread(str(file_b), cv2.IMREAD_GRAYSCALE)

    if a is None or b is None:
        print("Read failed:", file_a.name)
        continue

    if a.shape != (SIZE[1], SIZE[0]) or b.shape != a.shape:
        print("Size mismatch:", file_a.name)
        continue

    ok_a, ca = cv2.findChessboardCorners(a, BOARD, flags)
    ok_b, cb = cv2.findChessboardCorners(b, BOARD, flags)

    if not (ok_a and ok_b):
        print("Corner detection failed:", file_a.name)
        continue

    ca = cv2.cornerSubPix(a, ca, (11, 11), (-1, -1), criteria)
    cb = cv2.cornerSubPix(b, cb, (11, 11), (-1, -1), criteria)

    object_points.append(obj.copy())
    image_a.append(ca)
    image_b.append(cb)

    print("Accepted:", file_a.name, flush=True)

if len(object_points) < 10:
    raise RuntimeError("Not enough valid pairs")

print("\nCalibrating camera A...", flush=True)

rms_a, K_a, D_a, _, _ = cv2.calibrateCamera(
    object_points, image_a, SIZE, None, None
)

print("Calibrating camera B...", flush=True)

rms_b, K_b, D_b, _, _ = cv2.calibrateCamera(
    object_points, image_b, SIZE, None, None
)

print("Stereo calibration...", flush=True)

rms_stereo, K_a, D_a, K_b, D_b, R, T, E, F = \
    cv2.stereoCalibrate(
        object_points,
        image_a, image_b,
        K_a, D_a,
        K_b, D_b,
        SIZE,
        criteria=criteria,
        flags=cv2.CALIB_FIX_INTRINSIC
    )

print("Stereo rectification...", flush=True)

R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
    K_a, D_a,
    K_b, D_b,
    SIZE,
    R, T,
    flags=cv2.CALIB_ZERO_DISPARITY,
    alpha=0
)

# 補正後、左右の対応点が同じ高さにあるか確認
vertical_errors = []

for ca, cb in zip(image_a, image_b):
    pa = cv2.undistortPoints(
        ca, K_a, D_a, R=R1, P=P1
    ).reshape(-1, 2)

    pb = cv2.undistortPoints(
        cb, K_b, D_b, R=R2, P=P2
    ).reshape(-1, 2)

    vertical_errors.extend(
        np.abs(pa[:, 1] - pb[:, 1]).tolist()
    )

baseline = float(np.linalg.norm(T))

np.savez(
    str(OUTPUT),
    K_a=K_a, D_a=D_a,
    K_b=K_b, D_b=D_b,
    R=R, T=T,
    R1=R1, R2=R2,
    P1=P1, P2=P2,
    Q=Q,
    image_size=np.array(SIZE),
    square_size_m=np.array(SQUARE),
    rms_a=np.array(rms_a),
    rms_b=np.array(rms_b),
    rms_stereo=np.array(rms_stereo)
)

# 補正結果のサンプル画像を出力
sample_a = cv2.imread(str(files[0]))
sample_b = cv2.imread(
    str(PAIRS / files[0].name.replace("camA_", "camB_"))
)

map_a1, map_a2 = cv2.initUndistortRectifyMap(
    K_a, D_a, R1, P1, SIZE, cv2.CV_32FC1
)

map_b1, map_b2 = cv2.initUndistortRectifyMap(
    K_b, D_b, R2, P2, SIZE, cv2.CV_32FC1
)

rect_a = cv2.remap(sample_a, map_a1, map_a2, cv2.INTER_LINEAR)
rect_b = cv2.remap(sample_b, map_b1, map_b2, cv2.INTER_LINEAR)

preview = cv2.hconcat([
    cv2.resize(rect_a, (640, 400)),
    cv2.resize(rect_b, (640, 400))
])

for y in range(40, 400, 40):
    cv2.line(preview, (0, y), (1279, y), (0, 255, 0), 1)

cv2.imwrite(str(BASE / "rectified_preview.jpg"), preview)

print("\n========== RESULTS ==========")
print("Valid pairs        :", len(object_points))
print("Camera A RMS       : {:.3f} px".format(rms_a))
print("Camera B RMS       : {:.3f} px".format(rms_b))
print("Stereo RMS         : {:.3f} px".format(rms_stereo))
print("Vertical error avg : {:.3f} px".format(
    np.mean(vertical_errors)))
print("Vertical error 95% : {:.3f} px".format(
    np.percentile(vertical_errors, 95)))
print("Baseline           : {:.2f} mm".format(baseline * 1000))
print("Camera A fx        : {:.2f} px".format(K_a[0, 0]))
print("Camera B fx        : {:.2f} px".format(K_b[0, 0]))
print("Translation T (m)  :", T.ravel())
print("Saved              :", OUTPUT)
print("Preview            :", BASE / "rectified_preview.jpg")
print("=============================")
