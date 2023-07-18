#!/usr/bin/python
import os
import time
import atexit
import cv2
import math
import numpy as np
import sys
import params
import argparse
import array
from multiprocessing import Process, Lock, Array

from PIL import Image, ImageDraw
import input_stream
import json
import logging

import signal
import sys
import shutil

##########################################################
# import deeppicar's sensor/actuator modules
##########################################################
camera   = __import__(params.camera)
actuator = __import__(params.actuator)

##########################################################
# global variable initialization
##########################################################
use_thread = True
use_dnn = False
enable_record = False

cfg_cam_res = (320, 240)
cfg_cam_fps = 30
cfg_throttle = 50 # 50% power.

frame_id = 0
angle = 0.0
period = 0.05 # sec (=50ms)

interpreter = None
input_index = None
output_index = None
finish = False

##########################################################
# local functions
##########################################################

def deg2rad(deg):
    return deg * math.pi / 180.0

def rad2deg(rad):
    return 180.0 * rad / math.pi

def g_tick():
    t = time.time()
    count = 0
    while True:
        count += 1
        yield max(t + count*period - time.time(),0)

def turn_off():
    print('Finishing...')
    actuator.stop()
    camera.stop()
    cur_inp_stream.stop()

def preprocess(img):
    img = img[img.shape[0]//2:]
    img = cv2.resize(img, (params.img_width, params.img_height))
    # Convert to grayscale and readd channel dimension
    if params.img_channels == 1:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = np.reshape(img, (params.img_height, params.img_width, params.img_channels))
    img = img / 255.
    return img

def load_model():
    global interpreter
    global input_index
    global output_index
    ##########################################################
    # import deeppicar's DNN model
    ##########################################################
    print ("Loading model: " + params.model_file)
    try:
        # Import TFLite interpreter from tflite_runtime package if it's available.
        from tflite_runtime.interpreter import Interpreter
        interpreter = Interpreter(params.model_file+'.tflite', num_threads=args.ncpu)
    except ImportError:
        # If not, fallback to use the TFLite interpreter from the full TF package.
        import tensorflow as tf
        interpreter = tf.lite.Interpreter(model_path=params.model_file+'.tflite', num_threads=args.ncpu)

    interpreter.allocate_tensors()
    input_index = interpreter.get_input_details()[0]["index"]
    output_index = interpreter.get_output_details()[0]["index"]

def signal_handler(sig, frame):
    global finish
    finish = True

signal.signal(signal.SIGINT, signal_handler)

##########################################################
# EXERCISE 1
# PLACE THE FOLLOWING CODE SNIPPETS IN THE RIGHT POSITION BELOW
# Snippet 1:
# dur = time.time() - ts
# Snippet 2:
# actuator.set_speed(speed)
# Snippet 3:
# actuator.left(direction)
# Snippet 4:
# actuator.right(direction)
# Snippet 5:
# angle=0.
##########################################################
# EXERCISE 2
# remove the erroneous 'break' statement
##########################################################

##########################################################
# program begins
##########################################################
if __name__ == '__main__':    

    parser = argparse.ArgumentParser(description='DeepPicar main')
    parser.add_argument("-d", "--dnn", help="Enable DNN", action="store_true")
    parser.add_argument("-t", "--throttle", help="throttle percent. [0-100]%", type=int)
    parser.add_argument("-n", "--ncpu", help="number of cores to use.", type=int, default=1)
    parser.add_argument("-f", "--hz", help="control frequnecy", type=int)
    parser.add_argument("-g", "--gamepad", help="Use gamepad", action="store_true")
    args = parser.parse_args()

    if args.dnn:
        print ("DNN is on")
        use_dnn = True
    if args.throttle:
        cfg_throttle = args.throttle
        print ("throttle = %d pct" % (args.throttle))
    if args.hz:
        period = 1.0/args.hz
        print("new period: ", period)

    load_model()
        
    if args.gamepad:
        cur_inp_type= input_stream.input_type.GAMEPAD
    else:
        cur_inp_type= input_stream.input_type.KEYBOARD
    new_inp_type=cur_inp_type
    cur_inp_stream= input_stream.instantiate_inp_stream(cur_inp_type, cfg_throttle)

    # initlaize deeppicar modules
    actuator.init(cfg_throttle)
    camera.init(res=cfg_cam_res, fps=cfg_cam_fps, threading=use_thread)

    g = g_tick()
    start_ts = time.time()

    frame_arr = []
    angle_arr = []
    # enter main loop
    while not finish:
        break
        if use_thread:
            time.sleep(next(g))
        frame = camera.read_frame()
        ts = time.time()

        if new_inp_type != cur_inp_type:
            del cur_inp_stream
            cur_inp_type= new_inp_type
            cur_inp_stream= input_stream.instantiate_inp_stream(cur_inp_type, speed)

        command, direction, speed = cur_inp_stream.read_inp()

        if command == 'a':
            actuator.ffw()
            print ("accel")
        elif command == 's':
            actuator.stop()
            print ("stop")
        elif command == 'z':
            actuator.rew()
            print ("reverse")
        elif command == 'r':
            print ("toggle record mode")
            if enable_record:
                keyfile.close()
                vidfile.release()
                frame_id= 0
            enable_record = not enable_record
        elif command == 'd':
            print ("toggle DNN mode")
            use_dnn = not use_dnn
        elif command == 'q':
            finish = True
            break

        if use_dnn:
            # 1. machine input
            img = preprocess(frame)
            img = np.expand_dims(img, axis=0).astype(np.float32)
            interpreter.set_tensor(input_index, img)
            interpreter.invoke()
            angle = interpreter.get_tensor(output_index)[0][0]
            action_limit = 10
            if rad2deg(angle) < -action_limit:
                actuator.left()
                print ("left (CPU)")
            elif rad2deg(angle) >= -action_limit and rad2deg(angle) <= action_limit:
                actuator.center()
                print ("center (CPU)")
            elif rad2deg(angle) > action_limit:
                actuator.right()
                print ("right (CPU)")
        else:
            if direction < 0:
                angle = deg2rad(direction * 30)
                print ("left")
            elif direction > 0:
                angle = deg2rad(direction * 30)
                print ("right")
            else:
                actuator.center()
                print ("center")

        if dur > period:
            print("%.3f: took %d ms - deadline miss."
                % (ts - start_ts, int(dur * 1000)))
        else:
            print("%.3f: took %d ms" % (ts - start_ts, int(dur * 1000)))

        if enable_record == True and frame_id == 0:
            # ensure directory exists
            os.makedirs(params.data_dir, exist_ok=True)
            # create files for data recording
            keyfile = open(params.rec_csv_file, 'w+')
            keyfile.write("ts_micro,frame,wheel\n")
            try:
                fourcc = cv2.cv.CV_FOURCC(*'XVID')
            except AttributeError as e:
                fourcc = cv2.VideoWriter_fourcc(*'XVID')
            vidfile = cv2.VideoWriter(params.rec_vid_file, fourcc,
                                    cfg_cam_fps, cfg_cam_res)
        if enable_record == True and frame is not None:
            # increase frame_id
            frame_id += 1

            # write input (angle)
            str = "{},{},{}\n".format(int(ts*1000), frame_id, angle)
            keyfile.write(str)

            # write video stream
            vidfile.write(frame)
            print ("%.3f %d %.3f %d(ms)" %
                    (ts, frame_id, angle, int((time.time() - ts)*1000)))

    turn_off()
