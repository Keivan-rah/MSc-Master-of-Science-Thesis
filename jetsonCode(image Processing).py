import cv2
import numpy as np
import serial
import time

def empty():
    pass

def gstreamer_pipeline(
    sensor_id=0,
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=60,
    flip_method=0,
):
    return (
        "nvarguscamerasrc sensor-id=%d !"
        "video/x-raw(memory:NVMM), width=(int)%d, height=(int)%d, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            sensor_id,
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )


def position():
    arduino = serial.Serial(
    port = '/dev/ttyACM0',
    baudrate = 19200,
    bytesize = serial.EIGHTBITS,
    parity = serial.PARITY_NONE,
    stopbits = serial.STOPBITS_ONE,
    timeout = 0.025,
    xonxoff = False,
    rtscts = False,
    dsrdtr = False,
    writeTimeout = 0.025)

    i=0
    time.sleep(1)
    window_title = "CSI Camera"

    hmin=50
    hmax=90
    smin=50
    smax=200
    vmin=70
    vmax=185
    lower=np.array([hmin,smin,vmin])
    upper=np.array([hmax,smax,vmax])

    print(gstreamer_pipeline(flip_method=0))
    video_capture = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)

    if video_capture.isOpened():
        try:
            window_handle = cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            while True:
                i=i+1
                _, frame = video_capture.read()
                img=frame[int(frame.shape[0]/1.75):int(frame.shape[0]/1.49),int(frame.shape[1]/3.8):int(frame.shape[1]/2),:]
                img=cv2.GaussianBlur(img,(3,3),1)
                img=cv2.GaussianBlur(img,(3,3),1)
                imgHSV=cv2.cvtColor(img,cv2.COLOR_BGR2HSV)

                mask=cv2.inRange(imgHSV,lower,upper)
                kernel_erode=np.ones((3,3),'uint8')
                mask=cv2.erode(mask,kernel_erode,iterations=2)
                kernel_dilate=np.ones((7,7),'uint8')
                mask=cv2.dilate(mask,kernel_dilate,iterations=2)
                contours, hierarchy=cv2.findContours(mask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                for cnt in contours:
                    M=cv2.moments(cnt)
                    cX=int(M["m10"]/M["m00"])
                    cY=int(M["m01"]/M["m00"])
                    cv2.circle(img, (cX,cY), 3, (255,255,255), -1)
                 #   print('x='+str(cX)+'  y='+str(cY))
                 #   cv2.drawContours(img,cnt,-1,(0,0,255),2)
                    position_actual= max(-0.142948*cX+38.5546,0.0)
                    print('position_actual ='+str("{:.1f}".format(position_actual))+'mm\t'+str(i))
                    pos =str(int(position_actual))

                    txt=str(position_actual*1000)+"z"
                    arduino.write(txt.encode())
                    time.sleep(0.0005)

                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, img)
                else:
                    break 

                keyCode = cv2.waitKey(10) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break
        finally:
            video_capture.release()
            cv2.destroyAllWindows()
    else:
        print("Error: Unable to open camera")

if __name__ == "__main__":
    position()
