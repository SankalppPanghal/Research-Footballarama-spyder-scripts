# -*- coding: utf-8 -*-
"""
Created on Tue Mar  9 18:00:32 2021

-------------Stiching Algorithm----------------
Send size x size crops to YOLO for detection (which was trained on 1344x1344 --down--> 672x672)
We will experiment on size from 1344 to 1344x2

@author: panghals
"""
import numpy as np
import time
import cv2
import os
import imutils

def resize(im, h):
    return imutils.resize(im,height = h)

def find_start_no(loc):
    files = sorted([int(x.split('.')[0].split('_')[1]) for x in os.listdir(loc)])
    return (files[0], len(files))

def detect_first_time():
    global image, coods
    ans = None
    for cood in coods:
        cood_row,cood_col = cood
        crop_im = image[cood_row:cood_row+size, cood_col:cood_col+size, :]
        (H, W) = crop_im.shape[:2]

        # determine only the *output* layer names that we need from YOLO
        ln = net.getLayerNames()
        ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

        # construct a blob from the input image and then perform a forward
        # pass of the YOLO object detector, giving us our bounding boxes and
        # associated probabilities
        blob = cv2.dnn.blobFromImage(crop_im, 1 / 255.0, (416, 416), swapRB=True, crop=False)
        net.setInput(blob)

        #------------------------------
        start = time.time()
        layerOutputs = net.forward(ln)
        end = time.time()
        #------------------------------
        # show timing information on YOLO
        print("YOLO took {:.6f} seconds".format(end - start))

        # initialize our lists of detected bounding boxes, confidences, and
        # class IDs, respectively
        boxes = []
        confidences = []
        classIDs = []

        # loop over each of the layer outputs
        for output in layerOutputs:
            # loop over each of the detections
            for detection in output:
                # extract the class ID and confidence (i.e., probability) of
                # the current object detection
                scores = detection[5:]
                classID = np.argmax(scores)
                confidence = scores[classID]
                # filter out weak predictions by ensuring the detected
                # probability is greater than the minimum probability
                if confidence > desired_confidence:
                    # scale the bounding box coordinates back relative to the
                    # size of the image, keeping in mind that YOLO actually
                    # returns the center (x, y)-coordinates of the bounding
                    # box followed by the boxes' width and height
                    box = detection[0:4] * np.array([W, H, W, H])
                    (centerX, centerY, width, height) = box.astype("int")

                    # use the center (x, y)-coordinates to derive the top and
                    # and left corner of the bounding box
                    x = int(centerX - (width / 2))
                    y = int(centerY - (height / 2))

                    # update our list of bounding box coordinates, confidences,
                    # and class IDs
                    boxes.append([x, y, int(width), int(height)])
                    confidences.append(float(confidence))
                    classIDs.append(classID)

        # apply non-maxima suppression to suppress weak, overlapping bounding
        # boxes
        idxs = cv2.dnn.NMSBoxes(boxes, confidences, desired_confidence, desired_threshold)

        # ensure at least one detection exists
        if len(idxs) > 0:
            # loop over the indexes we are keeping
            for i in idxs.flatten():
                # extract the bounding box coordinates
                (x, y) = (boxes[i][0], boxes[i][1])
                (w, h) = (boxes[i][2], boxes[i][3])

                # draw a bounding box rectangle and label on the image
                color = (255,0,0)
                cv2.rectangle(crop_im, (x, y), (x + w, y + h), color, 10)
                ans = (x+cood_col, y+cood_row)
                #text = "{}: {:.4f}".format(classIDs[i], confidencesqq[i])
                #cv2.putText(crop, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 3)

            image[cood_row:cood_row+size, cood_col:cood_col+size, :] = crop_im
    return ans

def detect_around_here(coody):
    global image, size, not_detect_count
    x_last,y_last = coody
    ans = coody
    cood_col,cood_row = max(int(x_last-(size/2)),0), max(int(y_last-(size/2)),0)
    crop_im = image[cood_row:cood_row+size, cood_col:cood_col+size, :]
    (H, W) = crop_im.shape[:2]

    # determine only the *output* layer names that we need from YOLO
    ln = net.getLayerNames()
    ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

    # construct a blob from the input image and then perform a forward
    # pass of the YOLO object detector, giving us our bounding boxes and
    # associated probabilities
    blob = cv2.dnn.blobFromImage(crop_im, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    net.setInput(blob)

    #------------------------------
    start = time.time()
    layerOutputs = net.forward(ln)
    end = time.time()
    #------------------------------
    # show timing information on YOLO
    print("YOLO took {:.6f} seconds".format(end - start))

    # initialize our lists of detected bounding boxes, confidences, and
    # class IDs, respectively
    boxes = []
    confidences = []
    classIDs = []

    # loop over each of the layer outputs
    for output in layerOutputs:
        # loop over each of the detections
        for detection in output:
            # extract the class ID and confidence (i.e., probability) of
            # the current object detection
            scores = detection[5:]
            classID = np.argmax(scores)
            confidence = scores[classID]
            # filter out weak predictions by ensuring the detected
            # probability is greater than the minimum probability
            if confidence > desired_confidence:
                # scale the bounding box coordinates back relative to the
                # size of the image, keeping in mind that YOLO actually
                # returns the center (x, y)-coordinates of the bounding
                # box followed by the boxes' width and height
                box = detection[0:4] * np.array([W, H, W, H])
                (centerX, centerY, width, height) = box.astype("int")

                # use the center (x, y)-coordinates to derive the top and
                # and left corner of the bounding box
                x = int(centerX - (width / 2))
                y = int(centerY - (height / 2))

                # update our list of bounding box coordinates, confidences,
                # and class IDs
                boxes.append([x, y, int(width), int(height)])
                confidences.append(float(confidence))
                classIDs.append(classID)

    # apply non-maxima suppression to suppress weak, overlapping bounding
    # boxes
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, desired_confidence, desired_threshold)

    # ensure at least one detection exists
    if len(idxs) > 0:
        # loop over the indexes we are keeping
        for i in idxs.flatten():
            # extract the bounding box coordinates
            (x, y) = (boxes[i][0], boxes[i][1])
            (w, h) = (boxes[i][2], boxes[i][3])

            # draw a bounding box rectangle and label on the image
            color = (255,0,0)
            cv2.rectangle(crop_im, (x, y), (x + w, y + h), color, 10)
            ans = (x+cood_col,y+cood_row)
            not_detect_count = 0
            #text = "{}: {:.4f}".format(classIDs[i], confidencesqq[i])
            #cv2.putText(crop, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 3)

        #STICHING BACK
        image[cood_row:cood_row+size, cood_col:cood_col+size, :] = crop_im
    if ans==coody:
        not_detect_count+=1
    if not_detect_count==not_detect_count_limit:
        ans=None

    return ans

if __name__ == "__main__":

    #-------------------Starts from here-------------------------
    desired_confidence = 0.01 #args["confidence"]
    desired_threshold = 0.1 #args["threshold"]

    yolov4_path = "D:\\SankalpStuff\\YOLO\\darknet\\build\\darknet\\x64"
    weightsPath = os.path.sep.join([yolov4_path, "models\\backup672\\yolov4-obj_best.weights"])
    configPath = os.path.sep.join([yolov4_path, "cfg\\yolov4-detect.cfg"])

    # load our YOLO object detector trained on COCO dataset (80 classes)
    print("[INFO] loading YOLO from {}".format(weightsPath))
    net = cv2.dnn.readNetFromDarknet(configPath, weightsPath)

    not_detect_count = 0
    not_detect_count_limit = 15

    for no in range(9,10):
        loc = "D:\\Sequence Data Feb\\Seq 5 shelly 020\\{}\\".format(no)
        frames_location = loc + "frames\\"
        os.chdir(loc)
        if "8k_yolo_detect_downsample_1080_frames" not in os.listdir(loc):
            os.mkdir("8k_yolo_detect_downsample_1080_frames")
        write_loc = loc + "8k_yolo_detect_downsample_1080_frames\\"

        im = cv2.imread(frames_location + "frame_{}.tiff".format(find_start_no(frames_location)[0]))
        rows,cols = im.shape[:2]

        size = 1344 #size 1344 and cfg size 2016 works very good for small ball
        rows_rem = int((rows%size)/2); #cols_rem = int((cols%size)/2);

        coods = []

        row = rows_rem;
        while row+size<=rows:
            col = 0
            while col+size<=cols:
                coods.append((row,col))
                col+=size
            row+=size

        start_no = 48527
        last_cood = None
        #start_no = 40400
        for frame_no in range(start_no,start_no+1500):
            print("frame_{}.tiff".format(frame_no))
            image = cv2.imread(frames_location + "frame_{}.tiff".format(frame_no))
            try:
                if image.any()==None:
                    break
            except:
                break
            #if last_cood == None:
            last_cood = detect_first_time()
            #else:
                #last_cood = detect_around_here(last_cood)
                # show the output image
            cv2.imshow("Image", resize(image,800) )
            #cv2.imwrite(write_loc+"frame_{}.png".format(frame_no), resize(image,1080))
            key = cv2.waitKey(1) & 0xFF
            if key==ord('q'):
                break
            if key == ord('s'):
                while True:
                    key = cv2.waitKey(0) & 0xFF
                    if key== ord('c'):
                        break


    cv2.destroyAllWindows()