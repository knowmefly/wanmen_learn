#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, time, cv2
import numpy as np
import sys

from messages import Start, Stop, Scenario, Commands, frame2numpy,Dataset
from client import Client
import argparse
import time
import cv2

def get_file_idx(path):
    starting_value = 1
    while True:
        file_name = '{path}/training_data-{idx}.npy'.format(path=path, 
            idx=starting_value)
        if os.path.isfile(file_name):
            print('File exists, moving along', starting_value)
            starting_value += 1
        else:
            print('File does not exist, starting fresh!', starting_value)
            break
    return starting_value 

def main(path):
    training_data = []
    current_idx = get_file_idx(path)
    for i in list(range(4))[::-1]:
        print(i + 1)
        time.sleep(1)

    file_name = '{path}/training_data-{idx}.npy'.format(path=path,
        idx=current_idx)

    print('STARTING!!! training set saving to ',file_name)
    
    parser = argparse.ArgumentParser(description=None)
    parser.add_argument('-l', '--host', default='localhost', help='The IP where DeepGTAV is running')
    parser.add_argument('-p', '--port', default=8000, help='The port where DeepGTAV is running')
    args = parser.parse_args()

    print("connecting", args.host)
    client = Client(ip=args.host, port=args.port)
    client.sendMessage(Stop())
  
    scenario = Scenario(weather="clear", time=[10,10],drivingMode=-1) #manual driving
#        reward = [15.0,5.0],
#        direction=[1.0, 1.0, 0], peds=True,
#        vehicles = True, peds=True,
    start_data = Dataset(
        location = True,
        throttle = True,
        direction=[1234.8, 354.3, 0],
        reward = [15.0,5.0],
        brake=True, steering=True, speed=True, yawRate=True)

    client.sendMessage(Start(scenario=scenario, dataset=start_data))
    print("Start Message Sent", args.port)

    # Start listening for messages coming from DeepGTAV. We do it for 80 hours
    stoptime = time.time() + 80*3600
    file_name = '{path}/training_data-{idx}.npy'.format(path=path,
        idx=current_idx) 

    while time.time() < stoptime:
        try:
            # We receive a message as a Python dictionary
            message = client.recvMessage()
            print("rev, speed", message["speed"],message["keys"],
                message["steering"],message["throttle"],message["brake"])
                
            image = frame2numpy(message['frame'], (320,160))

            training_data.append([image,message["keys"],message["speed"],
                message["steering"],message["throttle"],
                message["brake"],message["location"],message["direction"],
                message["yawRate"],message["reward"]])

            if len(training_data) % 100 == 0:
                print(len(training_data))
                if len(training_data) == 500:
                    np.save(file_name, training_data)
                    print('SAVED')
                    training_data = []
                    current_idx += 1
                    file_name = '{path}/training_data-{idx}.npy'.format(path=path,
                        idx=current_idx)
                    print("a new training set is created", file_name)

        except (KeyboardInterrupt, Exception) as e:
            print("stop connection",e)
            break      
    # We tell DeepGTAV to stop
    client.sendMessage(Stop())
    #client.close()

if __name__ == "__main__":
    try:
       main("E:/dal/working/daldrive/data")
    except KeyboardInterrupt:
       print("stop connection")

