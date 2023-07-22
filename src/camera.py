import cv2 as cv
import numpy as np

class videocapture():
    def __init__(self):
        pass
    def release(self):
        return self


class Portada():
    def __init__(self):
        self.frame = cv.imread("./img/portada.png", cv.IMREAD_COLOR)
        self.frame = cv.cvtColor(self.frame, cv.COLOR_BGR2BGRA)
        self.data = np.flip(self.frame, 2)
        self.data = self.data.ravel()
        self.data = np.asfarray(self.data, dtype='f')
        self.texture_data = np.true_divide(self.data, 255.0)
        self.vid = videocapture()
        
    def get_frame(self):
        return self


class Camera():
    def __init__(self, PASSWORD = "gesti0narc0s", USER = "admin"
                 , IP = "10.111.58.36", PORT="554"):
        self.PASSWORD = PASSWORD
        self.USER     =  USER
        self.IP       =  IP
        self.PORT     =  PORT
        self.vid = cv.VideoCapture(f"rtsp://{self.USER}:{self.PASSWORD}@{self.IP}:{self.PORT}/cam/realmonitor?channel=1&subtype=1&unicast=true")
        #self.vid = cv.VideoCapture("./sample/captured_video_20230222140050_320x240.mp4")
    
    def get_frame(self):
        self.ret, frame = self.vid.read()
        frame = cv.resize(frame,(320,240)) 
        self.frame = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)
        self.data = np.flip(self.frame, 2)
        self.data = self.data.ravel()
        self.data = np.asfarray(self.data, dtype='f')
        self.texture_data = np.true_divide(self.data, 255.0)
        return self
    
    def get_conf(self):
        # image size or you can get this from image shape
        frame_width = self.vid.get(cv.CAP_PROP_FRAME_WIDTH)
        frame_height = self.vid.get(cv.CAP_PROP_FRAME_HEIGHT)
        video_fps = self.vid.get(cv.CAP_PROP_FPS)
        print(frame_width)
        print(frame_height)
        print(video_fps)

        print("Frame Array:")
        print("Array is of type: ", type(self.frame))
        print("No. of dimensions: ", self.frame.ndim)
        print("Shape of array: ", self.frame.shape)
        print("Size of array: ", self.frame.size)
        print("Array stores elements of type: ", self.frame.dtype)
        
        print("texture_data Array:")
        print("Array is of type: ", type(self.texture_data))
        print("No. of dimensions: ", self.texture_data.ndim)
        print("Shape of array: ", self.texture_data.shape)
        print("Size of array: ", self.texture_data.size)
        print("Array stores elements of type: ", self.texture_data.dtype)
