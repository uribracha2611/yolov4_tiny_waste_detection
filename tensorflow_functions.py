
#functions that manage interaction with images and tensorflow model for use with gui
import colorsys
import random

import tensorflow as tf
import cv2
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageColor
from tensorflow.python.saved_model import tag_constants
import sys
import os

#function that takes an image and an array of bounding boxes sized (n,5) and returns an image with bounding boxes drawn
def draw_bbox(image, bboxes, classes=["glass", "metal", "plastic", "paper", "cardboard", "biodegradable"],
             show_label=True):
   num_classes = len(classes)
   image_h, image_w, _ = image.shape
   #define colors for bounding boxes and the labels
   hsv_tuples = [(1.0 * x / num_classes, 1., 1.) for x in range(num_classes)]
   colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
   colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

   random.seed(0)#random seed for the same colors each time
   random.shuffle(colors)
   random.seed(None)

   out_boxes, out_scores, out_classes, num_boxes = bboxes
   #for loop for drawing boxes
   for i in range(num_boxes[0]):
       if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > num_classes: continue
       coor = out_boxes[0][i]
       coor[0] = int(coor[0] * image_h)
       coor[2] = int(coor[2] * image_h)
       coor[1] = int(coor[1] * image_w)
       coor[3] = int(coor[3] * image_w)

       fontScale = 0.5
       score = out_scores[0][i]
       class_ind = int(out_classes[0][i])
       bbox_color = colors[class_ind]
       bbox_thick = int(0.6 * (image_h + image_w) / 600)
       c1, c2 = (int(coor[1]), int(coor[0])), (int(coor[3]), int(coor[2]))
       cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)
       #label drawing
       if show_label:
           bbox_mess = '%s: %.2f' % (classes[class_ind], score)
           t_size = cv2.getTextSize(bbox_mess, 0, fontScale, thickness=bbox_thick // 2)[0]
           c3 = (c1[0] + t_size[0], c1[1] - t_size[1] - 3)
           cv2.rectangle(image, c1, (int(np.float32(c3[0])), int(np.float32(c3[1]))), bbox_color, -1)  # filled

           cv2.putText(image, bbox_mess, (c1[0], int(np.float32(c1[1] - 2))), cv2.FONT_HERSHEY_SIMPLEX,
                       fontScale, (0, 0, 0), bbox_thick // 2, lineType=cv2.LINE_AA)
   return image

# function that takes a file path to a single image, predicts bounding boxes inside of it saves and returns new file_path
def predict(image_path):
   model = tf.saved_model.load("model/yolov4-tiny-model", tags=[tag_constants.SERVING]) #loading model
   orig_img = cv2.imread(image_path) #loading_image
   orig_img = cv2.cvtColor(orig_img, cv2.COLOR_BGR2RGB)
   orig_width, orig_height,_ = orig_img.shape
   orig_img = cv2.resize(orig_img, (256, 256))#resizing
   img = np.array(orig_img).astype(np.float32) #copy of image so that the original image stay intact
   infer = model.signatures['serving_default']
   #data_prepration
   img = img / 255
   img = np.expand_dims(img, 0)
   img = tf.constant(img)
   #predication
   pred_bbox = infer(img)
   for key, value in pred_bbox.items():
       boxes = value[:, :, 0:4]
       pred_conf = value[:, :, 4:]

   boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
       boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
       scores=tf.reshape(
           pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
       max_output_size_per_class=50,
       max_total_size=50,
       iou_threshold=0.2,
       score_threshold=0.5
   )
   pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]
   #drawing bounding boxes and saving image
   new_img = draw_bbox(orig_img, pred_bbox, show_label=True) #new image
   new_img = Image.fromarray(new_img)#changing image to pillow format
   new_img=new_img.resize((orig_height,orig_width))
   save_name = "saves/" + str(Path(image_path).stem) + "_output.jpg"  #file name
   new_img.save(save_name) #saving
   return save_name

