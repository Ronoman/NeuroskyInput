import serial, Enum

monitor = serial.Serial('/dev/ttyS0', 9600, timeout=0.001)

class Status(Enum):
    WAITING_FOR_SYNC = 1 #Waiting for first 0xAA
    CONFIRMING_SYNC = 2  #Waiting for second 0xAA
    READING_PLENGTH = 3  #Getting the data packet length
    READING_PAYLOAD = 4  #Counting PLENGTH bytes
    CHKSUM_VERIFY = 5    #Confirming data packet with CHKSUM

status = Status.WAITING_FOR_SYNC

plength = 0 #Length of the packet to be read
plength_read = 0 #Number of bytes read so far
data = []
chksum = 0
verify_chksum = 0

while True:
    c = monitor.read()
    if(len(c) == 0):
        break

    if(status == Status.WAITING_FOR_SYNC):
        if(ord(c) == 170):
            status = Status.CONFIRMING_SYNC
            print("sync 1")

    if(status == Status.CONFIRMING_SYNC):
        if(c == 0xAA):
            status == Status.READING_PLENGTH
            print("synced")

    if(status == Status.READING_PLENGTH):
        plength = ord(c)
        status == Status.READING_PAYLOAD
        print("Length is " + str(ord(c)))

    if(status == Status.READING_PAYLOAD):
        data.append(ord(c))
        plength_read += 1
        chksum += c
        if(plength_read == plength):
            status = Status.CHKSUM_VERIFY
            print("Done reading packet")

    if(status == Status.CHKSUM_VERIFY):
        #TODO: Write verification code
        verify_chksum = ord(c)

        print("Packet received, printing")
        print(data)

        plength = 0
        plength_read = 0
        data = []
        chksum = 0
        verify_chksum = 0
