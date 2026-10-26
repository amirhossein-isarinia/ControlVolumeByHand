import cv2
import time
import math
import os
import shutil
import subprocess
from collections import deque

import numpy as np
import vlc
import HandTrackingModule as htm

# اجرا از هر مسیری کار کند: پوشه‌ی برنامه را مبنا قرار می‌دهیم
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)


# ---------- کنترل صدای سیستم (لینوکس) ----------
def set_system_volume(percent):
    percent = int(max(0, min(100, percent)))
    if shutil.which("pactl"):  # PulseAudio / PipeWire
        subprocess.run(
            ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{percent}%"],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    elif shutil.which("amixer"):  # ALSA
        subprocess.run(
            ["amixer", "sset", "Master", f"{percent}%"],
            check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
    else:
        print("pactl یا amixer پیدا نشد؛ صدای سیستم تغییر نمی‌کند.")


# ---------- تنظیمات وبکم ----------
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)

pTime = 0
fpsQueue = deque(maxlen=10)

detector = htm.handDetector(detectionCon=0.7)

volPer = 50
set_system_volume(volPer)

# ---------- موزیک ----------
music_folder = os.path.join(BASE_DIR, "music")
playlist = sorted(
    os.path.join(music_folder, f)
    for f in os.listdir(music_folder)
    if f.lower().endswith(".mp3")
)
if not playlist:
    print("فولدر موزیک خالی است!")
    raise SystemExit

player = vlc.MediaPlayer()
current_index = 0
player.set_media(vlc.Media(playlist[current_index]))
player.play()

# ---------- تغییر آهنگ ----------
lastSongChange = 0
songChangeCooldown = 1.0
prevHandX = None
prevHandY = None

# ---------- کنترل ولوم با حرکت دایره‌ای ----------
index_history = deque(maxlen=20)
last_angle = None
angle_accumulator = 0
angle_threshold = math.radians(50)


def getColor(vol):
    if vol < 50:
        r = int(np.interp(vol, [0, 50], [0, 255]))
        g = 255
    else:
        r = 255
        g = int(np.interp(vol, [50, 100], [255, 0]))
    b = 0
    return (b, g, r)


while True:
    success, img = cap.read()
    if not success:
        print("وبکم باز نشد یا تصویری نمی‌آید.")
        break

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if len(lmList) != 0:
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        # ---------- کنترل آهنگ با حرکت چپ/راست ----------
        handX = cx
        currentTime = time.time()
        if prevHandX is not None:
            if (handX - prevHandX) > 75 and (currentTime - lastSongChange) > songChangeCooldown:
                current_index = (current_index + 1) % len(playlist)
                player.set_media(vlc.Media(playlist[current_index]))
                player.play()
                print("🎵 Next Song")
                lastSongChange = currentTime
            elif (prevHandX - handX) > 75 and (currentTime - lastSongChange) > songChangeCooldown:
                current_index = (current_index - 1) % len(playlist)
                player.set_media(vlc.Media(playlist[current_index]))
                player.play()
                print("🎵 Previous Song")
                lastSongChange = currentTime
        prevHandX = handX

        # ---------- کنترل پلی/پاز با حرکت بالا/پایین ----------
        handY = cy
        if prevHandY is not None:
            if (prevHandY - handY) > 100 and (currentTime - lastSongChange) > songChangeCooldown:
                player.pause()
                print("⏸ Pause")
                lastSongChange = currentTime
            elif (handY - prevHandY) > 100 and (currentTime - lastSongChange) > songChangeCooldown:
                player.play()
                print("▶️ Play")
                lastSongChange = currentTime
        prevHandY = handY

        # ---------- کنترل صدا با چرخش انگشت سبابه ----------
        index_x, index_y = x2, y2
        index_history.append((index_x, index_y))

        if len(index_history) >= 5:
            pts = np.array(index_history)
            center_x, center_y = np.mean(pts[:, 0]), np.mean(pts[:, 1])

            dx = index_x - center_x
            dy = index_y - center_y
            angle = math.atan2(dy, dx)

            if last_angle is not None:
                dAngle = angle - last_angle
                if dAngle > math.pi:
                    dAngle -= 2 * math.pi
                elif dAngle < -math.pi:
                    dAngle += 2 * math.pi

                angle_accumulator += dAngle

                if angle_accumulator > angle_threshold:
                    volPer = min(100, volPer + 5)
                    set_system_volume(volPer)
                    print("🔊 Volume Up:", volPer)
                    angle_accumulator = 0
                elif angle_accumulator < -angle_threshold:
                    volPer = max(0, volPer - 5)
                    set_system_volume(volPer)
                    print("🔉 Volume Down:", volPer)
                    angle_accumulator = 0

            last_angle = angle
            cv2.circle(img, (int(center_x), int(center_y)), 40, (255, 255, 0), 2)

    # ---------- نوار ولوم ----------
    volBar = np.interp(volPer, [0, 100], [400, 150])
    color = getColor(volPer)
    cv2.rectangle(img, (50, 150), (85, 400), (200, 200, 200), 3)
    cv2.rectangle(img, (50, int(volBar)), (85, 400), color, cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_PLAIN, 2, color, 3)

    # ---------- FPS ----------
    cTime = time.time()
    fps = 1 / (cTime - pTime) if cTime != pTime else 0
    fpsQueue.append(fps)
    avgFps = sum(fpsQueue) / len(fpsQueue)
    pTime = cTime
    cv2.putText(img, f'FPS: {int(avgFps)}', (40, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)

    # ---------- پخش خودکار آهنگ بعدی ----------
    if player.get_state() == vlc.State.Ended:
        current_index = (current_index + 1) % len(playlist)
        player.set_media(vlc.Media(playlist[current_index]))
        player.play()
        print("🎵 Auto Next Song:", playlist[current_index])

    cv2.imshow("Volume & Song Control", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

player.stop()
cap.release()
cv2.destroyAllWindows()









# نحوه اجرا کردن برنامه در ترمینال
# cd "$HOME/drive D/ControlVolumeByHand"  رفتن به لوکیشن پروژه 
# source .venv/bin/activate   فعالسازی محیط مجازی
# python VolumeHandControl.py   ران کردن خود برنامه
