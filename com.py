import serial
import time

#arduino = serial.Serial('/dev/ttyACM0', 19200, timeout=0.02)

arduino = serial.Serial(
port = '/dev/ttyACM0',
baudrate = 19200,
bytesize = serial.EIGHTBITS,
parity = serial.PARITY_NONE,
stopbits = serial.STOPBITS_ONE,
timeout = 0.02,
xonxoff = False,
rtscts = False,
dsrdtr = False,
writeTimeout = 0.02
)

i=0

time.sleep(1)
start=time.time()
while True:
    try:

        i=i+1
        txt="Jetson command"+str(i)+"z"
      #  arduino.flush()
        arduino.write(txt.encode())
        time.sleep(0.0005)
        data = arduino.readline()
        if data:
            print(data.decode('utf-8')) # print received data from arduino to console
            print(i,time.time()-start)
      #  time.sleep(0.001)
    except Exception as e:
        
        print(e)
        arduino.close()

