##these commands were copied from the manual.

import time
import serial
#client = serial.Serial("/dev/ttyACM0",115200,
#client = serial.Serial("/dev/ttyAMA0",115200,
client = serial.Serial("/dev/ttyUSB0",115200,
                       timeout=0.15,write_timeout=0.01,
                       parity=serial.PARITY_EVEN,
                       stopbits=serial.STOPBITS_ONE)

size=32
print(client.name)
command = b"\x01\x06\x05\x01\x00\x00\xd8\xc6"
client.write(command)
result=client.read(size)
#print(command.encode('hex'))
print(result.encode('hex'))
command = b"\x01\x06\x04\x01\x21\x34\xc0\xbd"
client.write(command)
result=client.read(size)
print(result.encode('hex'))
command = b"\x01\x06\x04\x81\x07\xd0\xdb\x7e"
client.write(command)
result=client.read(size)
print(result.encode('hex'))
command = b"\x01\x06\x06\x01\x4e\x20\xec\xfa"
client.write(command)
result=client.read(size)
print(result.encode('hex'))
command = b"\x01\x06\x06\x81\x4e\x20\xed\x12"
client.write(command)
result=client.read(size)
print(result.encode('hex'))
command = b"\x01\x06\x00\x7d\x00\x08\x18\x14"
client.write(command)
result=client.read(size)
print(result.encode('hex'))
#time.sleep(1.1)
command = b"\x01\x06\x00\x7d\x00\x00\x19\xd2"
client.write(command)
result=client.read(size)
print(result.encode('hex'))
