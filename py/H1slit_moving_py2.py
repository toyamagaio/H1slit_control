import numpy as np
import time
import serial
import subprocess
import sys

filepath='pos.curr'


PORT = "/dev/ttyUSB0"  # Linux device name (Windows: "COM3", etc.)
#PORT = "/dev/ttyACM0"  # Linux device name (Windows: "COM3", etc.)

BAUDRATE = 115200  #dip switch 4
#BAUDRATE = 38400 #dip switch 2

#client = serial.Serial("/dev/ttyACM0",115200,
client = serial.Serial(PORT,BAUDRATE,
                       timeout=0.05,write_timeout=0.01,
                       parity=serial.PARITY_EVEN,
                       stopbits=serial.STOPBITS_ONE)


def execute(com,PRINT=True):
    #    print com.encode('hex')
    com += crc16(com)
    if PRINT:
        print com.encode('hex')
    client.write(com)
    time.sleep(0.5)
    size = 16
    result = client.read(size)
    if PRINT:
	    print result.encode('hex')    
    return int(result.encode('hex'),16)

def to_bytes(n, length, endianess='big'):
    h = '%x' % n
    s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
    return s if endianess != 'big' else s[::-1]

def s32(val):
    return -(val & 0x80000000) | (val & 0x7fffffff)

def tohex(val, nbits=32):
  return hex((val + (1 << nbits)) % (1 << nbits))

def crc16(data):
    data = bytearray(data)
    poly = 0xA001
    crc = 0xFFFF
    for b in data:
        crc ^= (0xFF & b)
        for _ in range(0, 8):
            if (crc & 0x0001):
                crc = ((crc >> 1) & 0xFFFF) ^ poly
            else:
                crc = ((crc >> 1) & 0xFFFF)
#    print hex(crc)
    return to_bytes(crc,2)

#def read(address,register,nbyte):
def read(seg,register,n):
    tmp = bytearray.fromhex('%02x'%seg)
    #tmp = bytearray.fromhex('%02d'%seg) #original
    tmp.extend('\x03')
    tmp.extend(bytearray.fromhex('%04x'%register))
    tmp.extend(bytearray.fromhex('%04x'%n))
    command=bytes(tmp)
    return execute(command)
    #return execute(command,False) #original
 #   print type(command),command.encode('hex')

# address: x=1, y=2
# function: read:03h, write:06h, writemulti:10h

def write(seg,register,nreg,nbyte,data):
    tmp = bytearray.fromhex('%02d'%seg)
    tmp.extend('\x10')
    tmp.extend(bytearray.fromhex('%04x'%register))
    tmp.extend(bytearray.fromhex('%04x'%nreg))
    tmp.extend(bytearray.fromhex('%02x'%nbyte))
    for d in data:
        tmp.extend(bytearray.fromhex('%08x'%d))
    command=bytes(tmp)
    execute(command)
#    print type(command),command,command.encode('hex')

def home_all(trig=False):
    if trig:
        cmd ='trgON 0'
        subprocess.call(cmd.split())
    for seg in [1,2]:
        if polling(seg):
            set_zhome(seg,10000,1500,1000)
            write(seg,0x7c,2,4,[0x10])
            time.sleep(0.1)
            off(seg)
    get_position(1)
    get_position(2)
    save_seg()
    if trig:
        cmd ='trgON 1'
        subprocess.call(cmd.split())
        
def home(seg):    
    if polling(seg):
        write(seg,0x7c,2,4,[0x10])
        time.sleep(0.1)
        off(seg)
    get_position(seg)
    save_seg()

def off(seg):
    write(seg,0x7c,2,4,[0x00])

def start(seg):    
    if polling(seg):
        write(seg,0x7c,2,4,[0x08])
        time.sleep(0.1)
        off(seg)
    
def set_params(seg,channel,mode,pos,speed=5000,rate1=1000,rate2=1000):
    #mode: 1 absolute, 2 relative
    #base=6144+64*channel #original
    base=1024+channel
    #if polling(seg):        
        #write(seg,base + 0,2,4,[mode])
        #write(seg,base + 2,2,4,[pos])
        #write(seg,base + 4,2,4,[speed])
        #write(seg,base + 6,2,4,[rate1])
        #write(seg,base + 8,2,4,[rate2])
    write(seg,base + 0*128,2,4,[pos])
    write(seg,base + 1*128,2,4,[speed])
    write(seg,base + 2*128,2,4,[mode])
    write(seg,base + 4*128,2,4,[rate1])
    write(seg,base + 5*128,2,4,[rate2])

def read_params(seg,channel):
    #mode: 1 absolute, 2 relative
    #base=6144+64*channel #original
    #offset=[0,2,4,6,8] #original
    base=1024+channel
    offset=[0,128,2*128,4*128,5*128]
    names=['pos','speed','mode','rate1','rate2']
    print '------- seg =', seg, 'channel=',channel 
    for offs,name in zip(offset,names):
        result=read(seg,base+offs,2)
        #val=(result>>16) & 0xffffffff #original
        val=(result>>16) & 0xffff
        print name,val

def read_zhome(seg):
    address=[688,690,692]
    names=['speed','rate','rate2']
    print '------- seg =', seg, 'home'
    for ad,name in zip(address,names):
        result=read(seg,ad,2)
        val=(result>>16) & 0xffffffff
        print name,val

def set_zhome(seg,speed,rate1,rate2):
    address=[688,690,692]
    vals=[speed,rate1,rate2]
    if polling(seg):        
        for ad,val in zip(address,vals):
            write(seg,ad,2,4,[val])

def get_position(seg):
    if polling(seg):
        result=read(seg,0xcc,2)
        pos=(result>>16) & 0xffffffff
        print pos,hex(pos)
        return s32(pos)

def polling(seg):
    counter=0
    while isready(seg) == 0:
        time.sleep(0.1)
        counter+=1
        if counter%10==0:
            print '.',
        if counter > 100:
            print "timeout!!!", seg
            return False
    return True

def isready(seg):
    aaa=read(seg,126,2)
    ready=(aaa>>21 & 0x1) 
    #print hex(aaa>>16), ready
    aaa=read(seg,377,1)
    ready2=(aaa>>20 & 0x1) 
    return ready2

def save_seg():
    serial=1234
    xpos=get_position(2)
    ypos=get_position(1)
    s="%d %d %d"%(serial,xpos,ypos)    
    s+='  fin\n'
    f=open(filepath,mode='w')
    f.write(s)
    f.close()
    cmd ='scp -p '+filepath+' vme:/tmp/daq.txt'
    subprocess.call(cmd.split())

def test3():
    seg=1

    ## shindan 08h
    subfunc=0

    ###manual p146
    ##set motion type: incremental
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x05')
    tmp.extend('\x01')
    tmp.extend('\x00')
    tmp.extend('\x00')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)

    ##set motion pos: 8500 step
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x04')
    tmp.extend('\x01')
    tmp.extend('\x21')
    tmp.extend('\x34')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)

    ##set motion speed: 2000 Hz
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x04')
    tmp.extend('\x81')
    tmp.extend('\x07')
    tmp.extend('\xD0')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)

    ##set acceleration: 20 ms/kHz
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x06')
    tmp.extend('\x01')
    tmp.extend('\x4E')
    tmp.extend('\x20')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)

    ##set decceleration: 20 ms/kHz
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x06')
    tmp.extend('\x81')
    tmp.extend('\x4E')
    tmp.extend('\x20')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)

    ##start motion
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x00')
    tmp.extend('\x7D')
    tmp.extend('\x00')
    tmp.extend('\x09')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)
    
    ##stop motion
    tmp = bytearray.fromhex('%02x'%seg)
    tmp.extend('\x06')
    tmp.extend('\x00')
    tmp.extend('\x7D')
    tmp.extend('\x00')
    tmp.extend('\x00')
    command=bytes(tmp)
    result=execute(command)
    time.sleep(0.5)

    #result = client.readline()
    #print 'result2 seg%d'%seg
    #print result.encode('hex')    

    #move(1)

    #print (result)
    #print hex(result)
    client.close()

def test2():
    serial=1234
    xpos=110
    ypos=100
    s="%d %d %d"%(serial,xpos,ypos)    
    s+='  fin\n'
    print s

def test():
    seg=1
    #get_position(seg)
  
    set_params(seg,0,2,20750, speed=4000, rate1=1000,rate2=1000)

    print('===read params===')
    read_params(seg,0)
    #start(seg)
    #get_position(seg)
    #save_seg()

#def move_rel(seg,channel):
#    set_params(seg,0,2,)
#    start(1)

def move(channel):
    x=(channel-1)%8
    y=int(channel-1)/8
    xpos = 25750*x
    ypos = 25900*y
    print x,y,xpos,ypos
    set_params(2,0,1,xpos)
    set_params(1,0,1,ypos)
    start(1)
    start(2)
    #save_seg()

def step(seg, count):
    set_params(seg,0,2,count)
    start(seg)
    save_seg()

def absolute(seg, count):
    set_params(seg,0,1,count)
    start(seg)
    save_seg()

class bcolors:
    HEADER = '\033[95m'
    OKRED = '\033[91m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
