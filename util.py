import cv2
from threading import Thread
from deepface import DeepFace
import numpy as np
from PIL import Image

global cam 
facecascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
global last_frame                                  
last_frame = np.zeros((480, 640, 3), dtype=np.uint8)

class LiveVedioFeed:

    def __init__(self, src=0):
        self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


class VideoCamera(object):

    def get_frame(self):
        global cam
        global emotion
        cam = LiveVedioFeed(src=0).start()
        frame = cam.read()

        result = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = facecascade.detectMultiScale(gray, 1.1, 4)

        # Draw a rectangle around the faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, result[0]['dominant_emotion'], (x+int(w/3), y), cv2.FONT_ITALIC, 1, (246, 6, 13), 2)

        global last_frame
        last_frame = frame.copy()
        img = Image.fromarray(last_frame)
        img = np.array(img)
        ret, buffer = cv2.imencode('.jpg', img)
        emotion = result[0]['dominant_emotion']
        return buffer.tobytes(), emotion
