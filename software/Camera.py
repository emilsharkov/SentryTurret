import cv2

class Camera:
    def __init__(self,camera_index,fov,frame_width,frame_height,frame_scale_down):
        self.fov = fov
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.scaled_width = frame_width // frame_scale_down
        self.scaled_height = frame_height // frame_scale_down
        self.video = cv2.VideoCapture(camera_index)

    def __del__(self):
        self.video.release()

    def readVideo(self):
        return self.video.read()
