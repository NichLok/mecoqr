from collections import Counter
import cv2
import imutils
from imutils import perspective
import matplotlib.pyplot as plt
import numpy as np
from picamera import PiCamera
from scipy.spatial import distance as dist
from sklearn.cluster import KMeans
import tensorflow as tf
import time
from time import sleep



def draw_rect(image, box):
    height, width, _ = image.shape
    y_min = int(max(1, (box[0] * height)))
    x_min = int(max(1, (box[1] * width)))
    y_max = int(min(height, (box[2] * height)))
    x_max = int(min(width, (box[3] * width)))
    
    # draw a rectangle on the image
    cv2.rectangle(image, (x_min, y_min), (x_max, y_max), (255, 255, 255), 2)
    
    
def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
    
    
def RGB2HEX(color):
    return "#{:02x}{:02x}{:02x}".format(int(color[0]), int(color[1]), int(color[2]))


def get_colours_kmeans(timenow, image, colour_count, show_chart):
    ''' get colours through K-means'''
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    height, width, _ = image.shape
    modified_image = image.reshape(height*width, 3)
    
    clf = KMeans(n_clusters = colour_count)
    labels = clf.fit_predict(modified_image)
    
    counts = Counter(labels)
    # sort to ensure correct color percentage
    counts = dict(sorted(counts.items()))
    print('counts {}'.format(counts))
    
    center_colours = clf.cluster_centers_
    # We get ordered colors by iterating through the keys
    ordered_colours = [center_colours[i] for i in counts.keys()]
    hex_colours = [RGB2HEX(ordered_colours[i]) for i in counts.keys()]
    rgb_colours = [ordered_colours[i].astype(int) for i in counts.keys()]
    print('rgb_colour: {}'.format(rgb_colours))

    if (show_chart):
        plt.figure(figsize = (8, 6))
        plt.pie(counts.values(), labels = hex_colours, colors = hex_colours)
        plt.savefig("/home/pi/Desktop/Capstone_rpi_integrate/local_image/{}colour.jpg".format(timenow))
        #plt.show()
    
    return rgb_colours


def IoU(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou


def pill_cv():
    '''perform computer vision and
    return (shape: str, colour: tuple, size: sorted list, image: str of img_path, error: T/F)'''
    
    error = False
    timenow = time.time()
    
    ### CAPTURE IMAGE
    camera = PiCamera(resolution='2592x1700')
    camera.brightness = 60
    camera.awb_mode = 'off'
    camera.awb_gains= (2,1.5) #(red gain, blue gain)
    camera.start_preview()

    sleep(2)
    predicted_image = '/home/pi/Desktop/Capstone_rpi_integrate/local_image/{}orig.jpg'.format(timenow)
    camera.capture(predicted_image)
    camera.stop_preview()
    camera.close()
    
    ### PREDICT SHAPE
    img = cv2.imread(predicted_image)
    new_img = cv2.resize(img, (320, 320)) #resize dimension obtained from tensor input details


    interpreter.set_tensor(input_details[0]['index'], [new_img])
    interpreter.invoke()

    rects = interpreter.get_tensor(output_details[0]['index'])
    label = interpreter.get_tensor(output_details[1]['index']).tolist()
    scores = interpreter.get_tensor(output_details[2]['index'])
    score_highest = np.max(scores[0]) #get highest score
    score_highest_index = np.argwhere(scores[0]==score_highest)
    
    #get second highest score
    score_copy = scores[0].copy()

    unique, counts = np.unique(score_copy, return_counts=True)
    counts_score = dict(zip(unique, counts))
    times = counts_score[score_highest]
    
    for i in range(times):
        score_copy = np.delete(score_copy, score_highest)
    
    score_2highest = np.max(score_copy[0])
    print('score 2nd: ', score_2highest)
    

    # retrieve prediction of highest confidence score
    for index, score in enumerate(scores[0]):
        if score == score_highest:
    #     if score > 0.8:
            predicted_shape = label_names[int(label[0][index])+1] #need to +1 cos the first label is background
            box = rects[0][index]
            print('Predicted label: {}, Score: {}'.format(predicted_shape, score))
            # break

        if score == score_2highest:
            box2 = rects[0][index]

    # check IoU
    iou = IoU(box, box2)
    print('iou: ', iou)
    if iou > 0.5:
        error = True
    
    # draw bounding box and prediction in the img_shape
    img_shape = img.copy()
    draw_rect(img_shape, box)
    cv2.putText(img_shape, "{} {}".format(predicted_shape, score), (200,100), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 3)



    ### GET MASK
    # get cropped image
    height, width, _ = img.shape
    y_min = int(max(1, (box[0] * height)))
    x_min = int(max(1, (box[1] * width)))
    y_max = int(min(height, (box[2] * height)))
    x_max = int(min(width, (box[3] * width)))
    # crop_img = img[y_min:y_max, x_min:x_max]

    # get slightly larger cropped image
    cropxl_img = img[max(y_min-30, 0):min(y_max+30, height), max(x_min-30, 0):min(x_max+30, width)]
    cropxl_hsv = cv2.cvtColor(cropxl_img.copy(), cv2.COLOR_BGR2HSV)
    
    # extract saturation value and get pill mask
    _,s,_ = cv2.split(cropxl_hsv)
    _, thresh_s = cv2.threshold(s, 10, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    s_filtered = cv2.GaussianBlur(thresh_s,(5,5),11) # smoothen the edges
    
    
    ### GET COLOUR
    s_maskrgb = cv2.bitwise_and(cropxl_img.copy(),cropxl_img.copy(),mask = s_filtered)
    rgb_colours = get_colours_kmeans(timenow, s_maskrgb, colour_count=2, show_chart=True)
    # remove black
    predicted_colour = []
    for rgb in rgb_colours:
        rgb = rgb.tolist()
        if rgb != [0, 0, 0]:
            predicted_colour = predicted_colour + rgb
    print('Predicted colour: ', predicted_colour)
    

    # set threshold for the contour area
    max_thresh_contour = cropxl_img.shape[0]*cropxl_img.shape[1]*0.99
    min_thresh_contour = cropxl_img.shape[0]*cropxl_img.shape[1]*0.2
    img_s = cropxl_img.copy()
    
    # find contours
    contours_s, _ = cv2.findContours(s_filtered, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    contour_list_s = []
    area_list_s = []
    for contour in contours_s:
        area = cv2.contourArea(contour)
        if area > min_thresh_contour and area < max_thresh_contour:
            contour_list_s.append(contour)
            area_list_s.append(area)
    
    
    try:
        # draw box of the largest contour
        index_max = area_list_s.index(max(area_list_s))
        contour = contour_list_s[index_max]
        box = cv2.minAreaRect(contour)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        cv2.drawContours(img_s, [box.astype("int")], -1, (255, 0, 0), 2)
        # print(box)
        
        ### GET SIZE
        box = perspective.order_points(box)
        (tl, tr, br, bl) = box
        # print(box)
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)

        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

        # compute object size
        # pixelsPermm = 540/10.6
#         pixelsPermm = 50.9 # value obtained from experiment
        pixelsPermm = 48.71
        dimA = round(dA / pixelsPermm, 1)
        dimB = round(dB / pixelsPermm, 1)
        predicted_size = [dimA, dimB]
        predicted_size.sort()
        print("Predited size in mm: {}".format(predicted_size))
    
        # insert the object sizes on the image
        cv2.putText(img_s, "{:.1f}mm".format(dimA),
            (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (0, 0, 255), 2)
        cv2.putText(img_s, "{:.1f}mm".format(dimB),
            (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (0, 0, 255), 2)
        cv2.drawContours(img_s, contour_list_s,  -1, (20,200,0), 2) #draw contours
    
    except:
        error = True
 
    
#     img_shape_resize = cv2.resize(img_shape.copy(), (int(width*0.5), int(height*0.5)), interpolation = cv2.INTER_AREA)
    
    
    # display and save images
#     cv2.imshow('Original', img)
#     cv2.imshow('Predicted shape', img_shape)
#     sleep(3)
#     cv2.imshow('Saturation',s)
#     cv2.imshow('Threshold-saturation with smoothing', s_filtered)
#     sleep(2)
#     cv2.imshow('Pill mask', s_maskrgb)
#     sleep(2)
#     cv2.imshow('Predicted size', img_s)
    
    cv2.imwrite("/home/pi/Desktop/Capstone_rpi_integrate/local_image/{}shape.jpg".format(timenow), img_shape)
    cv2.imwrite("/home/pi/Desktop/Capstone_rpi_integrate/local_image/{}maskbw.jpg".format(timenow), s_filtered)
    cv2.imwrite("/home/pi/Desktop/Capstone_rpi_integrate/local_image/{}maskrgb.jpg".format(timenow), s_maskrgb)
    cv2.imwrite("/home/pi/Desktop/Capstone_rpi_integrate/local_image/{}size.jpg".format(timenow), img_s)

#     cv2.waitKey(300)
#     cv2.destroyAllWindows()
    
    
    # dummy: to delete
#     predicted_shape = 'round'
#     predicted_colour = [128, 128, 128]
#     predicted_size = [10, 14]
#     predicted_image = '/home/pi/Desktop/gcloud_test.jpg'
#     error = False
    
    return predicted_shape, predicted_colour, predicted_size, predicted_image, error




###########################################################################################
###########################################################################################

# Load TFLite model and allocate tensors.
interpreter = tf.lite.Interpreter(model_path="/home/pi/tflite_pill_detection_trial1/pill_detection_trial1_model-export_iod_tflite-Pill_detection_tr_20200605123101-2020-06-05T08 13 13.970Z_model.tflite")
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
interpreter.allocate_tensors()


# Read label names from label file.
with tf.io.gfile.GFile('/home/pi/tflite_pill_detection_trial1/pill_detection_trial1_model-export_iod_tflite-Pill_detection_tr_20200605123101-2020-06-05T08 13 13.970Z_dict.txt', 'r') as f:
    label_names = f.read().split('\n')


# test = pill_cv()
# print(test)