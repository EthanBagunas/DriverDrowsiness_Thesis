import numpy as np
import cv2
import cvzone
import os
import sys
import glob
import random
import importlib.util
from tensorflow.lite.python.interpreter import Interpreter
from cvzone.PlotModule import LivePlot
from cvzone.FaceMeshModule import FaceMeshDetector
import time
import threading
import serial

ser = serial.Serial('COM4', 9600, timeout=1)

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
detected_labels = {cls: False for cls in object_names}

yawn_detected = False

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
    sendYawn()
    print("Yawn Detected")
    yawn_detected = False



# Function to handle yawn detection

def sendClose():
    ser.reset_input_buffer()
    count=0
    while count < 2:
        ser.write(b"1\n")
        time.sleep(1)
        count+=1


def sendYawn():
    ser.reset_input_buffer()
    count=0
    while count < 2:
        ser.write(b"0\n")
        time.sleep(1)
        count+=1

def handle_yawn_detection():
    global yawn_detected

    yawn_detected = True
    print("Starting countdown...")
    count_seconds(3)  # Change the countdown time as needed

    # Reset yawn detection state
    yawn_detected = False






colorBox = (0, 0, 255)



cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow backend

#cap = cv2.VideoCapture('lexis.mp4')



detector = FaceMeshDetector(maxFaces=1)
plotY = LivePlot(640,360,[20,50])
RplotY = LivePlot(640,360,[20,50])

RidList = [359,255,339,254,253,252,256,388,387,386,385,384,463]
idList = [22, 23, 24, 26, 110, 157, 158, 159, 160, 161, 130, 243]
ratioList = []
RratioList = []
blinkCounter = 0
RblinkCounter = 0
counter = 0
Rcounter = 0
color = (255, 0, 255)
Rcolor = (255, 0, 255)

closed_eye_timer = 0
closed_eye_duration = 3  # in seconds
eyes_closed = False




mask = cv2.imread('mask.png')

while True:
    ret, frame = cap.read()
    imgRegion = cv2.bitwise_and(frame, mask)

    if not ret:
        print("Failed to capture frame from camera. Exiting...")
        break

    #ComputerVisionCode
    imgRegion, faces = detector.findFaceMesh(imgRegion, draw=False)

    if faces:
        colorBox = (0, 255, 0)
        face = faces[0]
        for id, rid in zip(idList, RidList):
            cv2.circle(frame, face[id], 5, (color), cv2.FILLED)
            cv2.circle(frame, face[rid], 5, (Rcolor), cv2.FILLED)

        # left
        leftUp = face[159]
        leftDown = face[23]
        leftleft = face[130]
        leftright = face[243]
        lengthVer, _ = detector.findDistance(leftUp, leftDown)
        lengthHor, _ = detector.findDistance(leftleft, leftright)
        #cv2.line(frame, leftUp, leftDown, (0, 200, 0), 3)
        #cv2.line(frame, leftleft, leftright, (0, 200, 0), 3)

        # right
        rightUp = face[386]
        rightDown = face[253]
        rightleft = face[359]
        rightright = face[463]
        RlengthVer, _ = detector.findDistance(rightUp, rightDown)
        RlengthHor, _ = detector.findDistance(rightleft, rightright)
        #cv2.line(frame, rightUp, rightDown, (0, 200, 0), 3)
        #cv2.line(frame, rightleft, rightright, (0, 200, 0), 3)

        Lratio = (lengthVer / lengthHor) * 100
        Rratio = (RlengthVer / RlengthHor) * 100
        ratioList.append(Lratio)
        RratioList.append(Rratio)

        if len(RratioList) > 3:
            RratioList.pop(0)
        RratioAvg = sum(RratioList) / len(RratioList)
        if RratioAvg < 35 and Rcounter == 0:
            RblinkCounter += 1
            Rcolor = (0, 200, 0)
            Rcounter = 1
        if Rcounter != 0:
            Rcounter += 1
            if Rcounter > 10:
                Rcounter = 0
                Rcolor = (255, 0, 255)

        if len(ratioList) > 3:
            ratioList.pop(0)
        ratioAvg = sum(ratioList) / len(ratioList)

        if ratioAvg < 35 and counter == 0:
            blinkCounter += 1
            color = (0, 200, 0)
            counter = 1
        if counter != 0:
            counter += 1
            if counter > 10:
                counter = 0
                color = (255, 0, 255)

        if ratioAvg < 35 and RratioAvg < 35:
            closed_eye_timer += 1
            if closed_eye_timer >= closed_eye_duration * 25 and not eyes_closed:  # 25 frames per second
                sendClose()
                print("Both eyes closed")
                eyes_closed = True
        else:
            closed_eye_timer = 0
            eyes_closed = False

    else:
     colorBox = (0,0,255)

    #TensorFlow
    image_rgb = cv2.cvtColor(imgRegion, cv2.COLOR_BGR2RGB)
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
            object_name = object_names[int(classes[i])]  # Look up object name from "labels" array using class index

            if object_name in ['close_left', 'close_right']:
                continue  # Skip processing close_left and close_right

            # Get bounding box coordinates and draw box
            # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
            ymin = int(max(1, (boxes[i][0] * imH)))
            xmin = int(max(1, (boxes[i][1] * imW)))
            ymax = int(min(imH, (boxes[i][2] * imH)))
            xmax = int(min(imW, (boxes[i][3] * imW)))
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)
            # Draw label

            if object_name == 'yawn' and not yawn_detected:
                threading.Thread(target=handle_yawn_detection).start()
            elif object_name == 'not_yawn':
                yawn_detected = False
            elif object_name == 'face':
                colorBox = (0, 255, 0)
            else:
                colorBox = (0, 0, 255)  # Change colorBox to blue when object detected is not a face

            label = '%s: %d%%' % (object_name, int(scores[i] * 100))  # Example: 'person: 72%'
            labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)  # Get font size
            label_ymin = max(ymin, labelSize[1] + 10)  # Make sure not to draw label too close to top of window
            cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10),
                          (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255),
                          cv2.FILLED)  # Draw white box to put label text in
            cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0),
                        2)  # Draw label text
            detections.append([object_name, scores[i], xmin, ymin, xmax, ymax])

    cv2.rectangle(frame, (430, 320), (255, 90), colorBox, 3)
    cv2.imshow('output', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()