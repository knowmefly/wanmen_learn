#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from messages import Start, Stop, Scenario, Commands, frame2numpy,Dataset
from client import Client

import argparse
import time
import cv2
import numpy as np

def detect_edge(bgr_image):
    gray_img = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2GRAY)
    processed_img = cv2.Canny(gray_img, threshold1=200, threshold2=300)    
    processed_img = cv2.GaussianBlur(processed_img, (3,3), 0 ) 
    lines = cv2.HoughLinesP(processed_img, 1, np.pi/180, 120, 20, 35)
    return processed_img, lines  

def draw_lines(img,lines,color=[255,255,255],width=3):
    for line in lines:
        coords = line[0]
        img = cv2.line(img, (coords[0], coords[1]), (coords[2], coords[3]), [255,255,255], width)
    return img

def crop_roi(img, vertices):
    return img[vertices[0][1]:vertices[1][1], vertices[0][0]:vertices[1][0]].copy()

class Model:
    def run(self,frame):
        return [1.0, 0.0, 0.0] # throttle, brake, steering

# Controls the DeepGTAV vehicle
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-l', '--host', default='localhost', help='The IP where DeepGTAV is running')
    parser.add_argument('-p', '--port', default=8000, help='The port where DeepGTAV is running')
    args = parser.parse_args()

    # Creates a new connection to DeepGTAV using the specified ip and port. 
    # If desired, a dataset path and compression level can be set to store in memory all the data received in a gziped pickle file.
    # We don't want to save a dataset in this case
    print("connecting", args.host)
    client = Client(ip=args.host, port=args.port)
    client.sendMessage(Stop())

    # We set the scenario to be in manual driving, and everything else random (time, weather and location). 
    # See deepgtav/messages.py to see what options are supported
    scenario = Scenario(weather="clear", time=[10,10],drivingMode=-1) #manual driving

#Throttle:
#0.0 to 1.0 forward acceleration
#0.0 to -1.0 backward acceleration
#Brake:
#0.0 to 1.0 braking
#Steering
#-1 to 1 left to right
#        reward = [15.0,1.0],

    start_data = Dataset(
        location = True,
        vehicles = True, peds=True,
        throttle = True,
        direction=[1.0, 1.0, 0],
        brake=True, steering=True, speed=True, yawRate=True, time=True)
    # Send the Start request to DeepGTAV. Dataset is set as default, we only receive frames at 10Hz (320, 160)
    client.sendMessage(Start(scenario=scenario, dataset=start_data))
    print("Start Message Sent", args.port)
    
    # Dummy agent
    model = Model()

    # Start listening for messages coming from DeepGTAV. We do it for 80 hours
    stoptime = time.time() + 80*3600
    while time.time() < stoptime:
        try:
            # We receive a message as a Python dictionary
            message = client.recvMessage()  
              #                "reward",message["reward"],
  
            # The frame is a numpy array that can we pass through a CNN for example     
            image = frame2numpy(message['frame'], (320,160))
            print("recv",
                "Speed",message["speed"],
                "keys",message["keys"],
                "steering",round(message["steering"],6),
                "throttle",message["throttle"],
                "brake",message["brake"],
                "location",message["location"],
                "direction",message["direction"],
                "yawRate",message["yawRate"])
            #color map

            #thresh1 = cv2.applyColorMap(image, cv2.COLORMAP_JET)
            roi_img = crop_roi(image,((0,90),(320,160)))
            thresh1,lines = detect_edge(roi_img)
            try:
                processed_img = draw_lines(roi_img,lines)
                cv2.imshow('video',processed_img)
            except Exception as e:
                print("no lines")               
            if cv2.waitKey(1) == 27:
                break
            #commands = model.run(image)
            # We send the commands predicted by the agent back to DeepGTAV to control the vehicle
            #client.sendMessage(Commands(commands[0], commands[1], commands[2]))
        except KeyboardInterrupt:
            print("stop connection")
            break
            
    # We tell DeepGTAV to stop
    client.sendMessage(Stop())
    client.close()
