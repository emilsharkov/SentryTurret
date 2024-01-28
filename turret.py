import cv2
import numpy as np
import imutils
import Servo
import Blaster

CAMERA_FOV_DEGREES = 70
FRAME_WIDTH = 1440
FRAME_HEIGHT = 1080
FRAME_SCALE = 8
SCALED_WIDTH = int(FRAME_WIDTH/FRAME_SCALE)
SCALED_HEIGHT = int(FRAME_HEIGHT/FRAME_SCALE)

def calculateTurnAngles(targetX,targetY):
    xAngle = (targetX / SCALED_WIDTH) * (CAMERA_FOV_DEGREES / 2)
    yAngle = (targetY / SCALED_HEIGHT) * (CAMERA_FOV_DEGREES / 2)
    return xAngle,yAngle

def processTargets(frame, boxes, indices, classes, class_ids, confidences,horizontalServo,verticalServo,blaster):
    frameCenterX = SCALED_WIDTH // 2
    frameCenterY = SCALED_HEIGHT // 2

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
            blaster.toggleShoot(True)
        else:
            blaster.toggleShoot(False)

        horizontalAngle, verticalAngle = calculateTurnAngles(targetX,targetY)
        horizontalServo.turn(horizontalAngle)
        verticalServo.turn(verticalAngle)

        cv2.circle(frame,(targetX,targetY),10, targetColor, -1)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

def processFrame(frame,net,outputLayers,conf_threshold,nms_threshold):
    frame = imutils.resize(frame, width=SCALED_WIDTH)
    height, width, channels = frame.shape

    # Detect objects
    blob = cv2.dnn.blobFromImage(frame, 0.00392, (SCALED_WIDTH,SCALED_WIDTH), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(outputLayers)

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

def getClassifications():
    with open("coco.names", "r") as f:
        return [line.strip() for line in f.readlines()]

def initializeModel():
    net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
    layer_names = net.getLayerNames()
    outputlayers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]
    return net,outputlayers

def initializeBlaster():
    blaster = Blaster(gpioPin=2)
    return blaster

def initializeServos():
    horizontalServo = Servo(
        gpioPin=17,
        servo_range=270,
        desired_servo_range=270,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )
    
    verticalServo = Servo(
        gpioPin=17,
        servo_range=270,
        desired_servo_range=270,
        min_pulse_micro_seconds=500,
        max_pulse_micro_seconds=2500,
        frequency=50
    )
    
    horizontalServo.turn(horizontalServo.max_range // 2)
    verticalServo.turn(verticalServo.max_range // 2)

    return horizontalServo,verticalServo    

if __name__=='__main__':
    horizontalServo,verticalServo = initializeServos()
    blaster = initializeBlaster()
    net,outputLayers = initializeModel()
    classes = getClassifications()
    conf_threshold = 0.5
    nms_threshold = 0.4

    video = cv2.VideoCapture(1)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        frame,boxes,indices,class_ids,confidences = processFrame(frame,net,outputLayers,conf_threshold,nms_threshold)
        processTargets(frame,boxes,indices,classes,class_ids,confidences,horizontalServo,verticalServo,blaster)
        cv2.imshow("People Detection", frame)

    video.release()
    cv2.destroyAllWindows()
