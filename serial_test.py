import serial, time
ser = serial.Serial('/dev/ttyS0', 9600, timeout=0.001)

while True:
    #time.sleep(0.1)
    data = ser.readline()
    if not (data == ""):
        print(data)

ser.close()
