from core import EyeHandler
from core import CameraHandler
from core import voice
import time
import _thread


def eye_handler():
    d = EyeHandler("192.168.8.100", 25001)
    input()
    d.send_anim_code(b"ANGRY")
    input()
    d.send_anim_code(b"JOY")


def camera_handler():
    ch = CameraHandler(detect_eyes=True)
    while(True):
        print(ch.get_position())
        time.sleep(0.1)


def voice_handler():
    spk = voice()
    spk.connection()
    time.sleep(0.1)


_thread.start_new_thread(eye_handler, ())
_thread.start_new_thread(camera_handler, ())
_thread.start_new_thread(voice_handler, ())

input()
