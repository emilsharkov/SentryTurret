from Servo import Servo
from Blaster import Blaster
from Camera import Camera
import cv2
import imutils
import numpy as np

class Turret:
    def __init__(self, xServo: Servo, yServo: Servo, blaster: Blaster, camera: Camera, net: cv2.dnn_Net):
        if len({xServo.gpioPin, yServo.gpioPin, blaster.gpioPin}) != 3:
            raise ValueError('Each servo and blaster must use unique GPIO pins')
        
        self.xServo = xServo
        self.yServo = yServo
        self.blaster = blaster
        self.camera = camera
        self.net = net
    
    def __del__(self):
        cv2.destroyAllWindows()

    def calculate_turn_angles(self,targetX,targetY):
        xAngle = (targetX / self.camera.scaled_width) * (self.camera.fov / 2)
        yAngle = (targetY / self.camera.scaled_height) * (self.camera.fov / 2)
        return xAngle,yAngle

    def turn_servos(self,xAngle,yAngle):
        self.xServo.turn(xAngle)
        self.yServo.turn(yAngle)

    def toggle_shoot(self,shooting):
        self.blaster.toggle_shoot(shooting)

    def processTargets(self,frame, boxes, indices, classes, class_ids, confidences):
        frameCenterX = self.camera.scaled_width // 2
        frameCenterY = self.camera.scaled_height // 2

        for i in indices:
            # TO DO: add feature to support multiple people in frame
            if i != 0:
                return 
            
            x, y, w, h = boxes[i]
            label = classes[class_ids[i]]
            confidence = confidences[i]

            # Draw bounding box and label
            targetX = x + w//2
            targetY = y + h//2
            targetColor = (0,0,255)
            
            if frameCenterX in range(targetX - 20,targetX + 20) and frameCenterY in range(targetY - 20,targetY + 20) :
                targetColor = (0,255,0)
                # self.toggle_shoot(True)
            else:
                self.toggle_shoot(False)

            xAngle, yAngle = self.calculate_turn_angles(targetX,targetY)
            # self.turn_servos(xAngle,yAngle)
            print(xAngle,yAngle)

            cv2.circle(frame,(targetX,targetY),10, targetColor, -1)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def processFrame(self,frame,output_layers,conf_threshold,nms_threshold):
        frame = imutils.resize(frame, width=self.camera.scaled_width)
        height, width, channels = frame.shape

        # Detect objects
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (self.camera.scaled_width,self.camera.scaled_width), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(output_layers)

        # Process detections
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > conf_threshold and class_id == 0:  # Person class
                    # Scale the bounding box coordinates
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Calculate top-left corner coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-maximum suppression to eliminate redundant overlapping boxes
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        cv2.circle(frame,(width//2, height//2),10, (0,0,255), -1)

        return frame,boxes,indices,class_ids,confidences 
    
    def get_classes():
        with open("../configs/coco.names", "r") as f:
            return [line.strip() for line in f.readlines()]
        
    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i-1] for i in self.net.getUnconnectedOutLayers()]
        return output_layers
        
if __name__=='__main__':
    x_servo = Servo(
        gpioPin=17,
        servo_range=270,
        desired_servo_range=80,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )

    y_servo = Servo(
        gpioPin=24,
        servo_range=270,
        desired_servo_range=180,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )

    blaster = Blaster(
        gpioPin=23
    )

    camera = Camera(
        camera_index=0,
        fov=70,
        frame_width=1440,
        frame_height=1080,
        frame_scale_down=8
    )

    net = cv2.dnn.readNet("../configs/yolov3-tiny.weights", "../configs/yolov3-tiny.cfg")

    turret = Turret(
        xServo=x_servo,
        yServo=y_servo,
        blaster=blaster,
        camera=camera,
        net=net
    )


    output_layers = turret.get_output_layers()
    classes = Turret.get_classes()

    while True:
        ret, frame = turret.camera.video.read()
        if not ret:
            break

        frame,boxes,indices,class_ids,confidences = turret.processFrame(frame,output_layers,0.5,0.4)
        turret.processTargets(frame,boxes,indices,classes,class_ids,confidences)
        cv2.imshow("People Detection", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
