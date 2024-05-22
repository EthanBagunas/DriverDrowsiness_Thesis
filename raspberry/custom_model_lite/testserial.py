import serial
import time
if __name__ == '__main__':
    ser = serial.Serial('COM4', 9600, timeout=1)
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