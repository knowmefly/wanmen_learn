#https://msdn.microsoft.com/en-us/library/windows/desktop/ms646310(v=vs.85).aspx

import matplotlib_venn
import numpy as np
from numpy import ones,vstack
from numpy.linalg import lstsq
import matplotlib.pyplot as plt
from statistics import mode,mean
import cv2

from config import TOP,GAME_WIDTH, GAME_HEIGHT, WIDTH,HEIGHT
import ctypes
import time
from snapshot import grab_screen
import win32api as wapi

from controller import *
SendInput = ctypes.windll.user32.SendInput

KEY_W = 0x11
KEY_A = 0x1E
KEY_S = 0x1F
KEY_D = 0x20

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_SCANCODE = 0x0008
KEYEVENTF_UNICODE = 0x0004

INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2
# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)

LONG = ctypes.c_long
DWORD = ctypes.c_ulong
ULONG_PTR = ctypes.POINTER(DWORD)
WORD = ctypes.c_ushort

keyList = ["\b"]
for char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ 123456789,.'£$/\\":
    keyList.append(char)

class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, KEYEVENTF_SCANCODE, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, KEYEVENTF_SCANCODE | KEYEVENTF_KEYUP, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_MOVE = 0x0001

def SendInput(*inputs):
    nInputs = len(inputs)
    LPINPUT = Input * nInputs
    pInputs = LPINPUT(*inputs)
    cbSize = ctypes.c_int(ctypes.sizeof(Input))
    return ctypes.windll.user32.SendInput(nInputs, pInputs, cbSize)

def mouse_move(dx,dy):
    ii_ = Input_I()
    ii_.mi = MouseInput(dx, dy, 0, MOUSEEVENTF_MOVE, 0, None)
    x = Input(INPUT_MOUSE, ii_)
    SendInput(x)

def key_check():
    """windows just return latest status in order
    we need to reverse it to make more sense
    """
    keys = []
    for key in keyList:
        if wapi.GetAsyncKeyState(ord(key)):
            keys.append(key)            
    return sorted(keys,reverse=True)  


#个人
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
    
def mouse_left(offset):
    mouse_move(-1*offset,0)

def mouse_right(offset):
    mouse_move(offset,0)

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

        #l = l2
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
        mouse_left(30)
    elif xmid_frombottom600>WIDTH*(0.5+0.5):
        mouse_right(30)
    else:
        pass

def detect_edge(rgb_image):
    gray_img = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2GRAY)   
    #processed_img = cv2.Canny(rgb_image, threshold1=200, threshold2=300)
    #processed_img = cv2.Canny(gray_img, threshold1=130, threshold2=226)
    processed_img = cv2.Canny(gray_img, threshold1=48, threshold2=338)    
    processed_img = cv2.GaussianBlur(processed_img, (3,3), 0 )
    #vertices = np.array([[0,200],[0,0],[800,0],[800,200]], np.int32)
    #processed_img = roi(processed_img, [vertices])
    #plt.imshow(processed_img)    
    
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 120, 20, 35)
    #print(lines)
    #draw_lines(processed_img,lines)    
    return processed_img, lines

def find_main_lanes(img, lines, color=[0, 255, 255], thickness=3):

    # if this fails, go with some default line
    try:
        ys = []  
        for i in lines:
            for ii in i:
                ys += [ii[1],ii[3]]
        min_y = min(ys)
        max_y = HEIGHT
        mid_y = 200
        new_lines = []
        line_dict = {}
        
        #yellow_lines = find_yellow_lane_BGR(img)
        # yellow_lane is the most important thing
        # 筛两次，把主要的方向筛出来，然后选择相应的线作为lane
        #yellow_lane = np.mean(yellow_edge_line,axis=0)
        #yellow_slope = (yellow_lane[3]-yellow_lane[1])/(yellow_lane[2]-yellow_lane[0])
        # use arctan to find the angle
        # case 1: if we have good yellow lane:
        #     find other lanes with 1.1 angle +_15
        #     find the nearst three lane (how to measure the distance?)
        #
        
        for idx,i in enumerate(lines):
            for xyxy in i:
                # These four lines:
                # modified from http://stackoverflow.com/questions/21565994/method-to-return-the-equation-of-a-straight-line-given-two-points
                # Used to calculate the definition of a line, given two sets of coords.
                x_coords = (xyxy[0],xyxy[2])
                y_coords = (xyxy[1],xyxy[3])
                A = vstack([x_coords,ones(len(x_coords))]).T
                #print(A,y_coords)
                m, b = lstsq(A, y_coords, rcond= -1)[0]
                #print(m)
                if m == 0:
                    break
                # Calculating our new, and improved, xs
                x1 = (min_y-b) / m
                x2 = (max_y-b) / m

                line_dict[idx] = [m,b,[int(x1), min_y, int(x2), max_y]]
                new_lines.append([int(x1), min_y, int(x2), max_y])

        final_lanes = {}

        
        for idx in line_dict:
            final_lanes_copy = final_lanes.copy()
            m = line_dict[idx][0]
            b = line_dict[idx][1]
            line = line_dict[idx][2]
            
            if len(final_lanes) == 0:
                final_lanes[m] = [ [m,b,line] ]
                
            else:
                found_copy = False

                for other_ms in final_lanes_copy:
                    if not found_copy:
                        if abs(other_ms*1.2) > abs(m) > abs(other_ms*0.8):
                            if abs(final_lanes_copy[other_ms][0][1]*1.2) > abs(b) > abs(final_lanes_copy[other_ms][0][1]*0.8):
                                final_lanes[other_ms].append([m,b,line])
                                found_copy = True
                                break
                        else:
                            final_lanes[m] = [ [m,b,line] ]

        line_counter = {}

        for lanes in final_lanes:
            line_counter[lanes] = len(final_lanes[lanes])

        top_lanes = sorted(line_counter.items(), key=lambda item: item[1])[::-1][:2]
        #print('78')
        #print(top_lanes)
        lane1_id = top_lanes[0][0]
        lane2_id = top_lanes[1][0]
        #lane3_id = top_lanes[2][0]
        
        def average_lane(lane_data):
            x1s = []
            y1s = []
            x2s = []
            y2s = []
            for data in lane_data:
                x1s.append(data[2][0])
                y1s.append(data[2][1])
                x2s.append(data[2][2])
                y2s.append(data[2][3])
            return [int(mean(x1s)), int(mean(y1s)), int(mean(x2s)), int(mean(y2s))]

        l1 = average_lane(final_lanes[lane1_id])
        l2 = average_lane(final_lanes[lane2_id])
        #l3 = average_lane(final_lanes[lane3_id])

        return l1,l2
    except Exception as e:
        print(str(e))
if __name__ == '__main__':

    while(True):
        paused = False
        if not paused:
            screen = grab_screen(region=(0,TOP,GAME_WIDTH,GAME_HEIGHT))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            processed_img = cv2.Canny(screen, threshold1 = 200, threshold2 = 300)
            processed_img = cv2.GaussianBlur(processed_img, (3,3), 0)
            lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 120, 20, 35)

        # if cv2.waitKey(0) & 0xFF == ord('q'):
        #     cv2.destroyAllWindows()
        #     break
            #l1 = find_main_lanes(processed_img, lines, 1)
        try:
            l1, l2 = find_main_lanes(processed_img, lines, 1)
            if abs(l1[2]-400) > abs(l2[2]-400):
                l = l2
            else:
                l = l1
        except Exception as e:
            print('Error in find main lines', str(e))
            
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
        walking_turn_200(paused = False)
        

    # while True:
    #     keys = key_check()
    #     if 'T' in keys:
    #         break
    #     else:
    #         time.sleep(2)
    #     last_time = time.time()

    #     for i in list(range(4))[::-1]:
    #         print(i +1)
    #         time.sleep(1)
    #     paused = False
    #     mode_choice = 0
        # for i in range(3):
        #     mouse_move(30,0)
        #     time.sleep(1)
       # for i in range(10):
       #      PressKey(KEY_W)
       #      ReleaseKey(KEY_W)
       #      time.sleep(0.1)
       # for i in range(5):
       #      PressKey(KEY_A)
       #      ReleaseKey(KEY_A)
       #      time.sleep(0.1)