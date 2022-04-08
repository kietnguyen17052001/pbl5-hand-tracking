import cv2
import time
import os
import HandTrackingModule as htm
from firebase import firebase
from datetime import datetime               
################################
wCam, hCam = 640, 480
################################
firebase = firebase.FirebaseApplication("https://fir-led-f0542-default-rtdb.firebaseio.com/", None)
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
folder_path = "LedImage"
list = os.listdir(folder_path)
overlaylist = []                                                                                                                                                                                                                                                
pTime = 0
for path in list:
    image = cv2.imread(f'{folder_path}/{path}')
    overlaylist.append(image)

detector = htm.handDetector(detectionCon=0.7)
tipIds = [4,8,12,16,20]
status = 0
led = "led_livingroom"
while True:
    now = datetime.now()
    success, img = cap.read()
    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)
    mode = firebase.get("", led)
    if mode == "OFF":
        if status == 0:
            pass
        else:
            h, w, c = overlaylist[1].shape  
            img[0:h, 0:w] = overlaylist[1]
            status = 0
    if mode == "ON":
        if status == 1:
            pass
        else:
            h, w, c = overlaylist[0].shape  
            img[0:h, 0:w] = overlaylist[0]
            status = 1
    # print(lmList)
    print(status)
    if (len(lmList) != 0):
        fingers = []
        for id in range(0,5):
            if (lmList[tipIds[id]][2] < lmList[tipIds[id]-2][2]):
                fingers.append(1)
            else:
                fingers.append(0)
        # print(fingers)
        num_one = fingers.count(1)
        if num_one == 5 and mode == "OFF":
            # turn on
            h, w, c = overlaylist[0].shape
            img[0:h, 0:w] = overlaylist[0]
            firebase.put("", led, "ON")
            firebase.put("","time_on_off_led_livingroom", now.strftime("%H:%M:%S"))
            status = 1
        elif num_one !=  5 and mode == "ON":
            # turn off 
            h, w, c = overlaylist[1].shape  
            img[0:h, 0:w] = overlaylist[1]
            firebase.put("", led, "OFF")
            firebase.put("","time_on_off_led_livingroom", now.strftime("%H:%M:%S"))
            status = 0
            

    cTime = time.time()
    fps = 1/(cTime - pTime)
    pTime = cTime
    
    cv2.putText(img, f'FPS: {int(fps)}', (400, 70), cv2.FONT_HERSHEY_PLAIN,
                1, (255, 0, 0), 3)
    cv2.imshow("image", img)
    cv2.waitKey(1)
    
