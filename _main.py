import cv2, threading, time, os, datetime
import numpy as np

"""
    NEURAL NETWORK FRAMEWORK: YOLO DARKNET [GOOGLE COLAB (FREE GPU)]
    OBJECT DETECTION ALGORITHM: YOLO (YOU ONLY LOOK ONCE)
    LIBRARIES USED:
        - cv2
        - threading
        - time
        - os
        - dateime
        - numpy
"""

os.system("color a")

# Object Detection using YOLO class
class yolo_objection_detection (object):

    # Constructor
    def __init__(self, weights, cfg, names, delaySeconds):
        self.stop = False
        self.detected = []
        self.delaySeconds = delaySeconds
        self.weights = weights
        self.cfg = cfg
        self.names = names

    # Method for time thread
    def time_thread(self, timeInit):
        n = 0

        while True:
            current_time = time.perf_counter() - timeInit

            if int(current_time) != int(n):
                n = current_time
                print(".", end="", flush=True)

            if current_time > self.delaySeconds:
                self.stop = True
                break

        return

    # Main Object Detection Processing Method
    def obj_detection(self):

        # Setup the algorithm, trained model, names and configurations
        net = cv2.dnn.readNet(self.weights, self.cfg)
        classes = []

        with open(self.names, "r") as f:
            classes = [line.strip() for line in f.readlines()]

        # Setup layer names
        layer_names = net.getLayerNames()
        outputLayers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        try:
            capture = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        except:
            print("Error intializing video capture")
            return
        
        if not capture.isOpened():
            print("Can't initialize using internal camera\nInitializing using external camera...")
            capture = cv2.VideoCapture(1, cv2.CAP_DSHOW)
            if not capture.isOpened():
                print("")
                return
            else:
                print("Success initialization using external camera")
        else:
            print("Success initialization using internal camera")

        print("> [Point the objects to camera for {} seconds]\n> Detecting Objects ".format(self.delaySeconds), end="", flush=True)

        init_time = time.perf_counter()
        y = threading.Thread(target=self.time_thread, args=(init_time,))
        y.start()

        # Setup Video Capture
        while True:
            ret, image = capture.read()
            height, width, channels = image.shape

            blob = cv2.dnn.blobFromImage(image, 0.00392, (416, 416), (0, 0, 0), True, crop=False)

            net.setInput(blob)
            del blob
            
            outs = net.forward(outputLayers)

            class_ids = []
            confidences = []
            square = []

            for out in outs:
                for detection in out:
                    scores = detection[5:]
                    class_id = np.argmax(scores)
                    confidence = scores[class_id]
                    del scores
                    if confidence > 0.5:
                        center_x = int(detection[0] * width)
                        center_y = int(detection[1] * height)
                        w = int(detection[2] * width)
                        h = int(detection[3] * height)
                        x = int(center_x - w/2)
                        y = int(center_y - h/2)
                        square.append([x, y, w, h])
                        del center_x, center_y, w, h, x, y
                        confidences.append(float(confidence))
                        class_ids.append(class_id)
                    del confidence, class_id
            del outs

            indexes = cv2.dnn.NMSBoxes(square, confidences, 0.5, 0.5)
            font = cv2.FONT_HERSHEY_PLAIN
            tempDetected = []

            for  i in range(len(square)):
                if i in indexes:
                    x, y, w, h = square[i]
                    label = classes[class_ids[i]]
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                    cv2.putText(image, label, (x, y), font, 2, (0, 255, 0), 1)
                    tempDetected.append(label)
                    del x, y, w, h

            self.detected = tempDetected
            
            del tempDetected, confidences, class_ids, square, ret

            if self.stop:
                if not os.path.exists("images"):
                    os.mkdir("images")
                now = datetime.datetime.now()
                img_info = "images\\{}.jpg".format(now.strftime("%Y-%m-%d-%H-%M-%S"))
                cv2.imwrite(img_info, image)
                print("\n> {} was saved in the images directory".format(img_info))
                del image
                break

        y.join()
        capture.release()    
        cv2.destroyAllWindows()
        return

    # Initializes Detection Method
    def init_detection(self):
        self.stop = False
        x = threading.Thread(target=self.obj_detection)
        x.start()
        x.join()
        print("> Detection Done!\n> Objects Detected:", self.detected)

    # Props for the hardware
    def transfer_objects(self):
        print("> Transferring Objects ({})".format(len(self.detected)))
        """
            This area is for coding the hardware
        """
        for obj in range(len(self.detected)):
            time.sleep(5)
            print("> {} Done".format(self.detected[obj]))

    # Verify if the files exist
    def verifyFiles(self):
        if os.path.exists(self.weights) and os.path.exists(self.cfg) and os.path.exists(self.names):
            return True
        return False

if __name__=="__main__":

    if not os.path.exists("config.txt"):
        print("> config.txt is missing!")
        os.system("pause")
        exit()

    with open("config.txt", "r") as file:
        args = [f.strip() for f in file.readlines()]

    if len(args) < 3:
        print("> cfg.txt is either empty or has missing argument\\s!\n> It needs 3 argument files (in order):\n> .weights\n> .names\n> .cfg")
        os.system("pause")
        exit()
    
    # Object for the object detection class with few necessary parameters
    # Parameters: weights, cfg, names, delayTime
    objDetection = yolo_objection_detection(args[0], args[1], args[2], 8)

    while True:
        
        if not objDetection.verifyFiles():
            print("> Invalid or missing files!")
            os.system("pause")
            break
        
        objDetection.init_detection()
        objDetection.transfer_objects()
        time.sleep(2)
        os.system("pause")
