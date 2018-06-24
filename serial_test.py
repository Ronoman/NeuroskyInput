import serial, time
ser = serial.Serial('/dev/ttyS0', 9600, timeout=0.001)

while True:
    #time.sleep(0.1)
    data = ser.read()
    if not (data == ""):
        print(str(ord(data)))

ser.close()
