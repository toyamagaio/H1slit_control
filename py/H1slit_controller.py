import time
import serial
import subprocess

class H1SlitController:
    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, filepath='pos.curr'):
        self.port = port
        self.baudrate = baudrate
        self.filepath = filepath
        self.client = None

    def open_ser(self):
        self.client = serial.Serial(
            self.port,
            self.baudrate,
            timeout=0.05,
            write_timeout=0.01,
            parity=serial.PARITY_EVEN,
            stopbits=serial.STOPBITS_ONE
        )

    def close_ser(self):
        if self.client:
            self.client.close()

    def execute(self, com, PRINT=True):
        com += self.crc16(com)
        if PRINT:
            print(com.encode('hex'))
        self.client.write(com)
        time.sleep(0.5)
        result = self.client.read(16)
        if PRINT:
            print(result.encode('hex'))
        return int(result.encode('hex'), 16)

    def to_bytes(self, n, length, endianess='big'):
        h = '%x' % n
        s = ('0'*(len(h) % 2) + h).zfill(length*2).decode('hex')
        return s if endianess != 'big' else s[::-1]

    def s32(self, val):
        return -(val & 0x80000000) | (val & 0x7fffffff)

    def crc16(self, data):
        data = bytearray(data)
        poly = 0xA001
        crc = 0xFFFF
        for b in data:
            crc ^= (0xFF & b)
            for _ in range(8):
                if crc & 0x0001:
                    crc = ((crc >> 1) & 0xFFFF) ^ poly
                else:
                    crc = ((crc >> 1) & 0xFFFF)
        return self.to_bytes(crc, 2)

    def read(self, seg, register, n):
        tmp = bytearray.fromhex('%02x' % seg)
        tmp.extend('\x03')
        tmp.extend(bytearray.fromhex('%04x' % register))
        tmp.extend(bytearray.fromhex('%04x' % n))
        return self.execute(bytes(tmp))

    def write(self, seg, register, nreg, nbyte, data):
        tmp = bytearray.fromhex('%02x' % seg)
        tmp.extend('\x10')
        tmp.extend(bytearray.fromhex('%04x' % register))
        tmp.extend(bytearray.fromhex('%04x' % nreg))
        tmp.extend(bytearray.fromhex('%02x' % nbyte))
        for d in data:
            tmp.extend(bytearray.fromhex('%08x' % d))
        self.execute(bytes(tmp))

    def polling(self, seg):
        counter = 0
        while self.isready(seg) == 0:
            time.sleep(0.1)
            counter += 1
            if counter % 10 == 0:
                print('.')
            if counter > 100:
                print("timeout!!!", seg)
                return False
        return True

    def isready(self, seg):
        _ = self.read(seg, 126, 2)
        ready2 = (self.read(seg, 377, 1) >> 20) & 0x1
        return ready2

    def off(self, seg):
        self.write(seg, 0x7c, 2, 4, [0x00])

    def start(self, seg):
        if self.polling(seg):
            self.write(seg, 0x7c, 2, 4, [0x08])
            time.sleep(0.1)
            self.off(seg)

    def set_params(self, seg, channel, mode, pos, speed=5000, rate1=1000, rate2=1000):
        base = 1024 + channel
        self.write(seg, base + 0 * 128, 2, 4, [pos])
        self.write(seg, base + 1 * 128, 2, 4, [speed])
        self.write(seg, base + 2 * 128, 2, 4, [mode])
        self.write(seg, base + 4 * 128, 2, 4, [rate1])
        self.write(seg, base + 5 * 128, 2, 4, [rate2])

    def get_position(self, seg):
        if self.polling(seg):
            result = self.read(seg, 0xcc, 2)
            pos = (result >> 16) & 0xffffffff
            print(pos, hex(pos))
            return self.s32(pos)

    def save_seg(self):
        serial = 1234
        xpos = self.get_position(2)
        ypos = self.get_position(1)
        s = f"{serial} {xpos} {ypos}  fin\n"
        with open(self.filepath, 'w') as f:
            f.write(s)
        subprocess.call(['scp', '-p', self.filepath, 'vme:/tmp/daq.txt'])

    def move(self, channel):
        x = (channel - 1) % 8
        y = (channel - 1) // 8
        xpos = 25750 * x
        ypos = 25900 * y
        print(x, y, xpos, ypos)
        self.set_params(2, 0, 1, xpos)
        self.set_params(1, 0, 1, ypos)
        self.start(1)
        self.start(2)

    def step(self, seg, count):
        self.set_params(seg, 0, 2, count)
        self.start(seg)
        self.save_seg()

    def absolute(self, seg, count):
        self.set_params(seg, 0, 1, count)
        self.start(seg)
        self.save_seg()

    def home(self, seg):
        if self.polling(seg):
            self.write(seg, 0x7c, 2, 4, [0x10])
            time.sleep(0.1)
            self.off(seg)
        self.get_position(seg)
        self.save_seg()

    def read_params(self, seg, channel):
        base = 1024 + channel
        offset = [0, 128, 2 * 128, 4 * 128, 5 * 128]
        names = ['pos', 'speed', 'mode', 'rate1', 'rate2']
        print('------- seg =', seg, 'channel =', channel)
        for offs, name in zip(offset, names):
          result = self.read(seg, base + offs, 2)
          val = (result >> 16) & 0xffff
          print(name, val)

    def reset_home(self, seg):
        cpos=self.get_position(seg)
        print('cpos:',cpos, 'is new origin (0)')
        if self.polling(seg):
          val=self.read(seg,0x018A,2)
          aaa=(val>>16&0x01)
          if aaa==1:
            self.write(seg,0x018A,2,4,[0x00])
          self.write(seg,0x018A,2,4,[0x01])


if __name__ == "__main__":
    controller = H1SlitController()
    controller.open_ser()

    controller.home(1)
    controller.read_params(1, 0)

    controller.close_ser()

#if __name__ == "__main__":
#    controller = H1SlitController()
#    controller.open_ser()
#
#    controller.home(1)
#    controller.read_params(1, 0)
#
#    controller.close_ser()
