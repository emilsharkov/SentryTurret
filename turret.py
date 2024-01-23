import cv2
import numpy as np
import imutils

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

def processTargets(frame, boxes, indices, classes, class_ids, confidences):
    frameHeight, frameWidth, frameChannels = frame.shape
    frameCenterXCoordinate = SCALED_WIDTH // 2
    frameCenterYCoordinate = SCALED_HEIGHT // 2

    for i in indices:
        x, y, w, h = boxes[i]
        label = classes[class_ids[i]]
        confidence = confidences[i]

        # Draw bounding box and label
        targetXCoordinate = x + w//2
        targetYCoordinate = y + h//2
        targetColor = (0,0,255)
        
        margin = 20
        if targetXCoordinate - 20 < frameCenterXCoordinate < targetXCoordinate + 20:
            targetColor = (0,255,0)

        # horizontalAngle, verticalAngle = calculateTurnAngles(frameCenterXCoordinate, frameCenterYCoordinate, targetXCoordinate, targetYCoordinate)

        cv2.circle(frame,(targetXCoordinate,targetYCoordinate),10, targetColor, -1) #draw circle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, f"{label} {confidence:.2f}", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

if __name__=='__main__':
    # Load YOLO
    net = cv2.dnn.readNet("yolov3-tiny.weights", "yolov3-tiny.cfg")
    layer_names = net.getLayerNames()
    outputlayers = [layer_names[i-1] for i in net.getUnconnectedOutLayers()]

    # Load classes
    with open("coco.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]

    # Set minimum confidence threshold and NMS threshold
    conf_threshold = 0.5
    nms_threshold = 0.4

    # Load video
    video = cv2.VideoCapture(0)

    while True:
        ret, frame = video.read()
        if not ret:
            break

        # Resize frame for faster processing
        frame = imutils.resize(frame, width=SCALED_WIDTH)

        height, width, channels = frame.shape

        # Detect objects
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (SCALED_WIDTH,SCALED_WIDTH), (0, 0, 0), True, crop=False)

        net.setInput(blob)
        outs = net.forward(outputlayers)

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

        cv2.circle(frame,(width//2, height//2),10, (0,0,255), -1) #draw circle

        # process targets
        processTargets(frame, boxes, indices, classes, class_ids, confidences)

        # Display output frame
        cv2.imshow("People Detection", frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) == ord('q'):
            break
    # Release resources
    video.release()
    cv2.destroyAllWindows()
