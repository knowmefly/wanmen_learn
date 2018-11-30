import ctypes
from wheel import *
import time
from directkeys import find_main_lanes 
from snapshot import grab_screen
from directkeys import PressKey,ReleaseKey
from config import TOP,GAME_WIDTH, GAME_HEIGHT, WIDTH,HEIGHT
import cv2
import numpy as np

KEY_W = 0x11
KEY_A = 0x1E
KEY_S = 0x1F
KEY_D = 0x20




def walking_along_straight_line(l,paused = False):
    # if not paused:
    #     screen = grab_screen(region=(0,TOP,GAME_WIDTH,GAME_HEIGHT))
    #     screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
    #     processed_img = cv2.Canny(screen, threshold1 = 200, threshold2 = 300)
    #     processed_img = cv2.GaussianBlur(processed_img, (3,3), 0)
    #     lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 120, 20, 35)
    # try:
    #     l1,l2 = find_main_lanes(processed_img,lines,3)
    #     [l1,l2] = sorted([l1,l2],key=lambda line:line[2])

    #     l = l2
    #     #print(l)
    # except Exception as e:
    #     print('Error' ,str(e))

    print('nearest point line =',l[2])
    x1 = l[0]
    y1 = l[1]
    x2 = l[2]
    y2 = l[3]

    x_mid = x2+(x1-x2)*(y2-50)/(y2-y1)
    delta_x = (x2-x_mid)

    if abs(l[2]-400)>400:
        straight()
    elif abs(l[2]-400)>200:
        straight()
    elif l[2]-400<-20:
        forward_left()
    elif l[2]-400>20:
        forward_right()
    else:
        straight()
def walking_turn_200(paused = False):
    if not paused:
        screen = grab_screen(region=(0,TOP,GAME_WIDTH,GAME_HEIGHT))
        screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
        processed_img = cv2.Canny(screen, threshold1 = 200, threshold2 = 300)
        processed_img = cv2.GaussianBlur(processed_img, (3,3), 0)
        lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 120, 20, 35)
    try:
        l1,l2 = find_main_lanes(processed_img,lines,3)
        [l1,l2] = sorted([l1,l2],key=lambda line:line[2])

        l = l2
        #print(l)
    except Exception as e:
        print('Error' ,str(e))


    l_list = [l1,l2]
    xtop1_frombottom200 = l_list[0][0]
    xtop2_frombottom200 = l_list[1][0]
    xbott1_frombottom000 = l_list[0][2]
    xbott2_frombottom000 = l_list[1][2]

    xtop1_frombottom600 = xbott1_frombottom000+3*(xtop1_frombottom200-xbott1_frombottom000)
    xtop2_frombottom600 = xbott2_frombottom000+3*(xtop2_frombottom200-xbott2_frombottom000)

    xmid_frombottom600 = 1/2*(xtop1_frombottom600+xtop2_frombottom600)
    if xmid_frombottom600<WIDTH*(0.5-0.5):
        mouse_left(10)
    elif xmid_frombottom600>WIDTH*(0.5+0.5):
        mouse_right(10)
    else:
        pass
