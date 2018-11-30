import numpy as np
from config import DELTA_TIME_CONTROL
from getkeys import query_mouse_position
import time
def straight():
    PressKey(KEY_W)
    time.sleep(DELTA_TIME_CONTROL)
    ReleaseKey(KEY_W)
    ReleaseKey(KEY_A)
    ReleaseKey(KEY_S)
    ReleaseKey(KEY_D)

def left():
    PressKey(KEY_A)
    time.sleep(DELTA_TIME_CONTROL)
    ReleaseKey(KEY_A)
    ReleaseKey(KEY_S)
    ReleaseKey(KEY_D)
def right():
    PressKey(KEY_D)
    time.sleep(DELTA_TIME_CONTROL)
    ReleaseKey(KEY_A)
    ReleaseKey(KEY_S)
    ReleaseKey(KEY_D)
def forward_left():
    PressKey(KEY_A)
    PressKey(KEY_W)
    time.sleep(DELTA_TIME_CONTROL)
    ReleaseKey(KEY_W)
    ReleaseKey(KEY_A)
    ReleaseKey(KEY_S)
    ReleaseKey(KEY_D)
    time.sleep(0.1)
def forward_right():
    PressKey(KEY_W)
    PressKey(KEY_D)
    time.sleep(DELTA_TIME_CONTROL)
    ReleaseKey(KEY_W)
    ReleaseKey(KEY_A)
    ReleaseKey(KEY_S)
    ReleaseKey(KEY_D)

def mouse_left():
	mouse_move(-1*offset,0)

def mouse_right():
	mouse_move(offset,0)