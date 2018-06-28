import serial
import pickle
import socket
from enum import Enum

monitor = serial.Serial('/dev/ttyS0', 9600, timeout=0.001)

UDP_IP = "10.0.0.240"
UDP_PORT = 3303
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

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

monitor.write(b'2') #Swap to 57600 baud (Command code 0000 1000)

monitor = serial.Serial('/dev/ttyS0', 57600, timeout=0.001)

def sendData(packet):
    serialized = pickle.dumps(packet)
    sock.sendto(serialized, (UDP_IP, UDP_PORT))

def bytesToInt(byteArray, isBigEndian, isSigned):
    endian = 'big' if isBigEndan else 'little'
    int.from_bytes(bytes(byteArray), byteorder=endian, signed=isSigned)

def parse_data(data):
    done = False
    i = 0

    packet = {
        "signal_quality": None,
        "heart_rate": None,
        "attention_esense": None,
        "meditation_esense": None,
        "8bit_raw_wave": None,
        "raw_marker": None,
        "raw_wave": None,
        "eeg_power": None,
        "asic_eeg_power": None,
        "rrinterval": None
    }

    while(not done):
        if(data[i] == 2): #POOR_SIGNAL Quality (0-255) 0x02
            packet["signal_quality"] = data[i+1]
            i += 2

        elif(data[i] == 3): #HEART_RATE (0-255) 0x03
            packet["heart_rate"] = data[i+1]
            i += 2

        elif(data[i] == 4): #ATTENTION eSense (0-100) 0x04
            packet["attention_esense"] = data[i+1]
            i += 2

        elif(data[i] == 5): #MEDITATION eSense (0-100) 0x05
            packet["meditation_esense"] = data[i+1]
            i += 2

        elif(data[i] == 6): #8BIT_RAW Wave Value (0-255) 0x06
            packet["8bit_raw_wave"] = data[i+1]
            i += 2

        elif(data[i] == 7): #RAW_MARKER Section (0) 0x07
            packet["raw_marker"] = data[i+1]
            i += 2

        elif(data[i] == 128): #RAW Wave Value. 2 two's-complement bytes follow (0x80)
            wave_val = bytesToInt(data[i+1:i+3], True, True)
            packet["raw_wave"] = wave_val
            i += 3

        elif(data[i] == 129): #EEG_POWER 0x81
            #do some funky IEEE 754 float conversions
            i += 9

        elif(data[i] == 131): #ASIC_EEG_POWER. 8 3-byte unsigned ints  0x83
            delta = bytesToInt(data[i+1:i+4], True, False)
            theta = bytesToInt(data[i+4:i+7], True, False)
            low_alpha = bytesToInt(data[i+7:i+10], True, False)
            high_alpha = bytesToInt(data[i+10:i+13], True, False)
            low_beta = bytesToInt(data[i+13:i+16], True, False)
            high_beta = bytesToInt(data[i+16:i+19], True, False)
            low_gamma = bytesToInt(data[i+19:i+22], True, False)
            mid_gamma = bytesToInt(data[i+22:i+25], True, False)

            packet["asic_eeg_power"] = [delta, theta, low_alpha, high_alpha, low_beta, low_gamma, mid_gamma]

        elif(data[i] == 134): #RRINTERVAL 0x86
            i += 3

        if(i == len(data)):
            done = True
    return packet

while True:
    c = monitor.read()
    if(len(c) == 0):
        continue

    c = ord(c) #Turn hex into decimal to compare against

    if(status == Status.WAITING_FOR_SYNC):
        if(c == 170):
            status = Status.CONFIRMING_SYNC
            continue

    if(status == Status.CONFIRMING_SYNC):
        if(c == 170):
            status = Status.READING_PLENGTH
            continue

    if(status == Status.READING_PLENGTH):
        plength = c
        status = Status.READING_PAYLOAD
        continue

    if(status == Status.READING_PAYLOAD):
        data.append(c)
        plength_read += 1
        chksum += c
        if(plength_read == plength):
            status = Status.CHKSUM_VERIFY
            continue

    if(status == Status.CHKSUM_VERIFY):
        #TODO: Write verification code
        verify_chksum = c

        print("Packet received, printing")
        print(data)

        parsed = parse_data(data)
        send_data(parsed)

        #Reset the packet specific variables
        plength = 0
        plength_read = 0
        data = []
        chksum = 0
        verify_chksum = 0
        status = Status.WAITING_FOR_SYNC
