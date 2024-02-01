import cv2
import imutils

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

def main():
    # Create the Camera object
    camera = Camera(
        camera_index=0,
        fov=70,
        frame_width=1440,
        frame_height=1080,
        frame_scale_down=8
    )

    while True:
        ret, frame = camera.readVideo()
        if not ret:
            break

        # Resize frame for display
        display_frame = imutils.resize(frame, width=camera.scaled_width)

        # Display the resulting frame
        cv2.imshow('Frame', display_frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything is done, release the video capture object
    camera.__del__()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()