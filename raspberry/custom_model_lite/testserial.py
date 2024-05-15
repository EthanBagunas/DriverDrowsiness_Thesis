import serial
import time

ser = serial.Serial('COM4', 9600, timeout=1)

data = input("Enter the number") 
ser.reset_input_buffer()
count=0
while count < 2:
    if (data == 1):
        ser.write(b"1\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
    else:
        ser.write(b"0\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        break
    time.sleep(1)
    count+=1


'''def sendYawn(x):
    ser = serial.Serial('COM4', 9600, timeout=1)
    ser.reset_input_buffer()
    count=0
    while count < 2:
        ser.write(b"5\n")
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        time.sleep(1)
        count+=1'''