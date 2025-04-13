##these commands were copied from the manual.

import time
import serial
client = serial.Serial("/dev/ttyUSB0",115200,
                       timeout=0.05,
                       parity=serial.PARITY_EVEN,
                       stopbits=serial.STOPBITS_ONE)

size=16
print(client.name)
#result=client.read(size)
#print(result.encode('hex'))
#result=client.readline()
#print(result.encode('hex'))

#print(result.encode('hex'))
#print(client.name)
command = b"\x03\x08\x00\x00\x12\x34\xec\x9e"
#cmd=bytearray.fromhex('%02x')
client.write(command)
result=client.read(size)
print('commnd')
print(command.encode('hex'))
print('result')
print(result.encode('hex'))

#result=client.read(size)
#print(result.encode('hex'))
#result=client.readline()
#print(result.encode('hex'))

#command = b"\x01\x06\x05\x01\x00\x00\xd8\xc6"
#client.write(command)
#result=client.read(size)
##print(command.encode('hex'))
#print(result.encode('hex'))
#command = b"\x01\x06\x04\x01\x21\x34\xc0\xbd"
#client.write(command)
#result=client.read(size)
#print(result.encode('hex'))
#command = b"\x01\x06\x04\x81\x07\xd0\xdb\x7e"
#client.write(command)
#result=client.read(size)
#print(result.encode('hex'))
#command = b"\x01\x06\x06\x01\x4e\x20\xec\xfa"
#client.write(command)
#result=client.read(size)
#print(result.encode('hex'))
#command = b"\x01\x06\x06\x81\x4e\x20\xed\x12"
#client.write(command)
#result=client.read(size)
#print(result.encode('hex'))
#command = b"\x01\x06\x00\x7d\x00\x08\x18\x14"
#client.write(command)
#result=client.read(size)
#print(result.encode('hex'))
#time.sleep(1.1)
#command = b"\x01\x06\x00\x7d\x00\x00\x19\xd2"
##client.write(command)
#result=client.read(size)
#print(result.encode('hex'))
