import numpy as np
import cv2
import os
import sys
import glob
import random
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter
import time
import threading
import serial

modelpath = 'detect.tflite'
lblpath = 'labelmap.txt'
min_conf = 0.50

interpreter = Interpreter(model_path=modelpath)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

float_input = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

with open(lblpath, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

object_names = [
    "close_left",
    "close_right",
    "face",
    "not_yawn",
    "yawn"
]

# Countdown function
def count_seconds(seconds):
    global yawn_detected
    global yawn_start_time
    global yawn_duration

    yawn_detected = True
    yawn_start_time = time.time()

    for i in range(1, seconds):
        print(f"Remaining: {i} seconds")
        time.sleep(1)
        if not yawn_detected:
            yawn_duration = time.time() - yawn_start_time
            print(f"Yawn duration: {yawn_duration} seconds")
            return
    sendYawn("5")
    print("Yawn Detected")
    
    yawn_detected = False


def sendYawn(x):
    ser = serial.Serial('COM4', 9600, timeout=1)
    ser.reset_input_buffer()
    count=0
    while count < 2:
        ser.write(b"5\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(1)
        count+=1
        
        




def eyes_count_seconds(seconds):
    global eyes_detected
    global eyes_start_time
    global eyes_duration

    eyes_detected = True
    eyes_start_time = time.time()

    for i in range(1, seconds):
        print(f"Remaining: {i} seconds")
        time.sleep(1)
        if not eyes_detected:
            eyes_duration = time.time() - eyes_start_time
            print(f"eyes detected duration: {eyes_duration} seconds")
            return
    print("Close Detected")
    eyes_detected = False

# Function to handle yawn detection
def handle_yawn_detection():
    global yawn_detected

    yawn_detected = True
    print("Starting countdown...")
    count_seconds(3)  # Change the countdown time as needed

    # Reset yawn detection state
    yawn_detected = False

def handle_eyes_detection():
    global eyes_detected

    eyes_detected = True
    print("Starting countdown...")
    eyes_count_seconds(3)  # Change the countdown time as needed

    # Reset yawn detection state
    eyes_detected = False


eyes_detected = False  # Initialize eyes_detected variable
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame from camera. Exiting...")
        break

    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    imH, imW, _ = frame.shape
    image_resized = cv2.resize(image_rgb, (width, height))
    input_data = np.expand_dims(image_resized, axis=0)
    # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
    if float_input:
        input_data = (np.float32(input_data) - input_mean) / input_std

    # Perform the actual detection by running the model with the image as input
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()

    boxes = interpreter.get_tensor(output_details[1]['index'])[0]  # Bounding box coordinates of detected objects
    classes = interpreter.get_tensor(output_details[3]['index'])[0]  # Class index of detected objects
    scores = interpreter.get_tensor(output_details[0]['index'])[0]  # Confidence of detected objects

    detections = []

    for i in range(len(scores)):
        if ((scores[i] > min_conf) and (scores[i] <= 1.0)):
            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1, (boxes[i][0] * imH)))
            xmin = int(max(1, (boxes[i][1] * imW)))
            ymax = int(min(imH, (boxes[i][2] * imH)))
            xmax = int(min(imW, (boxes[i][3] * imW)))
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
            # Draw label
            object_name = object_names[int(classes[i])]  # Look up object name from "labels" array using class index

            if object_name == 'yawn' and not yawn_detected:
                threading.Thread(target=handle_yawn_detection).start()
            elif object_name == 'not_yawn':
                yawn_detected = False

            #elif object_name == 'close_left' and 'close_right' in object_names and not eyes_detected:
            #   threading.Thread(target=handle_eyes_detection).start()




            label = '%s: %d%%' % (object_name, int(scores[i] * 100))  # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)  # Get font size
            label_ymin = max(ymin, labelSize[1] + 10)  # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10),
                          (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255),
                          cv2.FILLED)  # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0),
                        2)  # Draw label text
            detections.append([object_name, scores[i], xmin, ymin, xmax, ymax])

    cv2.imshow('output', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()