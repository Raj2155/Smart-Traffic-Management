import os
os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"
import sys
import cv2
import time
import torch
import argparse
import numpy as np
from pathlib import Path
from collections import Counter
import torch.backends.cudnn as cudnn
from base.com.dao.video_dao import VideoDAO
from base.com.vo.video_vo import VideoVO


from base.services.trackbleobject import TrackableObject
from base.services.utils.general import set_logging
from base.services.models.common import DetectMultiBackend
from base.services.utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadStreams
from base.services.utils.general import (LOGGER, Profile, check_file, check_img_size,
                            check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args,
                            scale_coords, strip_optimizer, xyxy2xywh)
from base.services.utils.plots import Annotator, colors, save_one_box
from base.services.utils.torch_utils import select_device, time_sync

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0] 
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT)) 
ROOT = Path(os.path.relpath(ROOT, Path.cwd())) 

video_dict={}
#---------------Object Tracking---------------
import skimage
from base.services.sort import *


#-----------Object Blurring-------------------
blurratio = 40


#.................. Tracker Functions .................
'''Computer Color for every box and track'''
palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

# -----------------------
trackers = []
trackableObjects = {}

totalDown = 0
totalUp = 0
# -----------------------


def compute_color_for_labels(label):
    color = [int(int(p * (label ** 2 - label + 1)) % 255) for p in palette]
    return tuple(color)


"""" Calculates the relative bounding box from absolute pixel values. """
def bbox_rel(*xyxy):
    bbox_left = min([xyxy[0].item(), xyxy[2].item()])
    bbox_top = min([xyxy[1].item(), xyxy[3].item()])
    bbox_w = abs(xyxy[0].item() - xyxy[2].item())
    bbox_h = abs(xyxy[1].item() - xyxy[3].item())
    x_c = (bbox_left + bbox_w / 2)
    y_c = (bbox_top + bbox_h / 2)
    w = bbox_w
    h = bbox_h
    return x_c, y_c, w, h


"""Function to Draw Bounding boxes"""
def draw_boxes(img, bbox, identities=None, categories=None, 
                names=None, color_box=None,offset=(0, 0)):
    for i, box in enumerate(bbox):
        x1, y1, x2, y2 = [int(i) for i in box]
        x1 += offset[0]
        x2 += offset[0]
        y1 += offset[1]
        y2 += offset[1]
        cat = int(categories[i]) if categories is not None else 0
        id = int(identities[i]) if identities is not None else 0
        data = (int((box[0]+box[2])/2),(int((box[1]+box[3])/2)))
        label = str(id)

        if color_box:
            color = compute_color_for_labels(id)
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(img, (x1, y1), (x2, y2),color, 2)
            cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (255,191,0), -1)
            cv2.putText(img, label, (x1, y1 - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
            [255, 255, 255], 1)
            cv2.circle(img, data, 3, color,-1)
        else:
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(img, (x1, y1), (x2, y2),(255,191,0), 2)
            cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (255,191,0), -1)
            cv2.putText(img, label, (x1, y1 - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
            [255, 255, 255], 1)
            cv2.circle(img, data, 3, (255,191,0),-1)
    return img
#..............................................................................

@torch.no_grad()
def detect(source,
        weights=r'base/services/yolov5s.pt',

        data=r'base/services/data/coco128.yaml',
        imgsz=(640, 640),conf_thres=0.3,iou_thres=0.45,
        max_det=1000, device='cpu',  view_img=True,
        save_txt=False, save_conf=False, save_crop=False,
        nosave=False, classes=[2, 3, 5, 7],  agnostic_nms=False,
        augment=False, visualize=False,  update=False,
        project=r'base/static/adminResources/output_video/',
        name='',
        exist_ok=False, line_thickness=2,hide_labels=False,
        hide_conf=False,half=False,dnn=False,display_labels=False,
        blur_obj=False,color_box = False,):

    save_img = not nosave and not source.endswith('.txt')
    save_path = ""

    #.... Initialize SORT ....
    sort_max_age = 5
    sort_min_hits = 2
    sort_iou_thresh = 0.2
    sort_tracker = Sort(max_age=sort_max_age,
                       min_hits=sort_min_hits,
                       iou_threshold=sort_iou_thresh)
    track_color_id = 0
    #.........................


    webcam = source.isnumeric() or source.endswith('.txt') or source.lower().startswith(
        ('rtsp://', 'rtmp://', 'http://', 'https://'))

    # save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)
    save_dir = Path(project) / name
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)

    set_logging()
    device = select_device(device)
    half &= device.type != 'cpu'

    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data)
    stride, names, pt, jit, onnx, engine = model.stride, model.names, model.pt, model.jit, model.onnx, model.engine
    imgsz = check_img_size(imgsz, s=stride)

    half &= (pt or jit or onnx or engine) and device.type != 'cpu'
    if pt or jit:
        model.model.half() if half else model.model.float()

    if webcam:
        cudnn.benchmark = True
        dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt)
        bs = len(dataset)
    else:
        dataset = LoadImages(source, img_size=imgsz, stride=stride, auto=pt)
        bs = 1
    vid_path, vid_writer = [None] * bs, [None] * bs

    t0 = time.time()

    dt, seen = [0.0, 0.0, 0.0], 0
    # ----------------------------------
    # multi onject up down variables
    listDet = ['person', 'bicycle', 'car', 'motorcycle']
    rects = []
    labelObj = []

    #exit count-
    totalDownCar = 0
    totalDownMotor = 0
    totalDownBus = 0
    totalDownTruck = 0
    total_exit_count = 0

    #entry count
    totalDownCar1 = 0
    totalDownMotor1 = 0
    totalDownBus1 = 0
    totalDownTruck1 = 0
    total_entry_count = 0
    video_save_path = ""

    # ----------------------------------
    for path, im, im0s, vid_cap, s in dataset:

        t1 = time_sync()
        im = torch.from_numpy(im).to(device)
        im = im.half() if half else im.float()  # uint8 to fp16/32
        im /= 255  # 0 - 255 to 0.0 - 1.0
        if len(im.shape) == 3:
            im = im[None]  # expand for batch dim
        t2 = time_sync()
        dt[0] += t2 - t1

        # Inference
        visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
        pred = model(im, augment=augment, visualize=visualize)
        t3 = time_sync()
        dt[1] += t3 - t2

        # NMS
        pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)
        dt[2] += time_sync() - t3


        for i, det in enumerate(pred):  # per image
            seen += 1
            if webcam:  # batch_size >= 1
                p, im0, frame = path[i], im0s[i].copy(), dataset.count
                s += f'{i}: '
            else:
                p, im0, frame = path, im0s.copy(), getattr(dataset, 'frame', 0)

            p = Path(p)
            save_path = str(save_dir) + "/"
            txt_path = str(save_dir / 'labels' / p.stem) + ('' if dataset.mode == 'image' else f'_{frame}')  # im.txt
            s += '%gx%g ' % im.shape[2:]
            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]
            imc = im0.copy() if save_crop else im0
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))
            middle = im0.shape[0] // 2
            height = im0.shape[0]
            width = im0.shape[1]
            if len(det):
                det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()
                for c in det[:, -1].unique():
                    n = (det[:, -1] == c).sum()
                    s += f"{n} {names[int(c)]}{'s' * (n > 1)}, "

                # Write results
                for *xyxy, conf, cls in reversed(det):
                    if blur_obj:
                        crop_obj = im0[int(xyxy[1]):int(xyxy[3]),int(xyxy[0]):int(xyxy[2])]
                        blur = cv2.blur(crop_obj,(blurratio,blurratio))
                        im0[int(xyxy[1]):int(xyxy[3]),int(xyxy[0]):int(xyxy[2])] = blur
                    else:
                        continue
                #..................USE TRACK FUNCTION....................
                #pass an empty array to sort
                dets_to_sort = np.empty((0,6))

                # NOTE: We send in detected object class too
                for x1,y1,x2,y2,conf,detclass in det.cpu().detach().numpy():
                    dets_to_sort = np.vstack((dets_to_sort,
                                              np.array([x1, y1, x2, y2,
                                                        conf, detclass])))

                # Run SORT
                tracked_dets = sort_tracker.update(dets_to_sort)
                tracks =sort_tracker.getTrackers()


                # draw boxes for visualization
                if len(tracked_dets)>0:
                    bbox_xyxy = tracked_dets[:,:4]
                    identities = tracked_dets[:, 8]
                    categories = tracked_dets[:, 4]
                    for cord in tracked_dets:
                        # print("cord ->", cord)
                        x_c = (cord[0] + [2]) / 2
                        print(x_c)
                        y_c = (cord[1] + cord[3]) / 2
                        print(y_c)
                        to = trackableObjects.get(cord[8], None)
                        if to is None:
                            to = TrackableObject(cord[8], (x_c, y_c))
                            print("TOOOO", to)
                        else:
                            y = [c[1] for c in to.centroids]
                            direction = y_c - np.mean(y)
                            to.centroids.append((x_c, y_c))
                            if not to.counted:
                                idx = int(cord[4])
                                print("idx", type(idx))
                                if direction > 0 and height // 2.9 < y_c < height // 2.5:
                                    if (idx == 2):
                                        totalDownCar1 += 1
                                        to.counted = True
                                    elif (idx == 3 or idx == 1):
                                        totalDownMotor1 += 1
                                        to.counted = True
                                    elif (idx == 5):
                                        totalDownBus1 += 1
                                        to.counted = True
                                    elif (idx == 7):
                                        totalDownTruck1 += 1
                                        to.counted = True
                                    total_entry_count = totalDownCar1 + totalDownMotor1 + totalDownBus1 + totalDownTruck1

                                elif direction > 0 and height // 1.5 < y_c < height // 1.4:
                                    if (idx == 2):
                                        totalDownCar += 1
                                        to.counted = True
                                    elif (idx == 3 or idx == 1):
                                        totalDownMotor += 1
                                        to.counted = True
                                    elif (idx == 5):
                                        totalDownBus += 1
                                        to.counted = True
                                    elif (idx == 7):
                                        totalDownTruck += 1
                                        to.counted = True
                                    total_exit_count = totalDownCar + totalDownMotor + totalDownBus + totalDownTruck

                        trackableObjects[cord[8]] = to

                    draw_boxes(im0, bbox_xyxy, identities, categories, names,color_box)
            start_point_upper = (0, int(height // 2.9))
            start_point = (0, int(height // 2.5))
            start_point_middle = (0, int(height // 1.5))
            start_point_below = (0, int(height // 1.4))

            end_point_upper = (int(im0.shape[1]), int(height // 2.9))
            end_point = (int(im0.shape[1]), int(height // 2.5))
            end_point_middle = (int(im0.shape[1]), int(height // 1.5))
            end_point_below = (int(im0.shape[1]), int(height // 1.4))

            # color = (255,0,0)
            thickness = 8
            # cv2.line(im0,(0,int(height//2)),(int(width//2.4),0),thickness)
            cv2.line(im0, start_point_upper, end_point_upper, (0, 255, 0), thickness)
            cv2.line(im0, start_point, end_point,(0,255,0), thickness)
            cv2.line(im0, start_point_middle, end_point_middle,(0,255,0), thickness)
            cv2.line(im0, start_point_below, end_point_below,(0,255,0), thickness)

            color = (0, 0, 255)
            cv2.putText(im0, 'Exit car : ' + str(totalDownCar), (int(width * 0.6), int(height * 0.15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Exit motorcycle : ' + str(totalDownMotor), (int(width * 0.6), int(height * 0.2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Exit bus : ' + str(totalDownBus), (int(width * 0.6), int(height * 0.25)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Exit truck : ' + str(totalDownTruck), (int(width * 0.6), int(height * 0.3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Total Exit Count : ' + str(total_exit_count), (int(width * 0.6), int(height * 0.35)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Entry car : ' + str(totalDownCar1), (int(width * 0.02), int(height * 0.15)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Entry motorcycle : ' + str(totalDownMotor1), (int(width * 0.02), int(height * 0.2)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Entry bus : ' + str(totalDownBus1), (int(width * 0.02), int(height * 0.25)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Entry truck : ' + str(totalDownTruck1), (int(width * 0.02), int(height * 0.3)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)
            cv2.putText(im0, 'Total Entry Count : ' + str(total_entry_count), (int(width * 0.02), int(height * 0.35)),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, color, 4)

            if view_img:
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)
            if save_img:
                if dataset.mode == 'image':
                    cv2.imwrite(save_path, im0)
                else:
                    if vid_path != save_path:
                        vid_path = save_path
                        if isinstance(vid_writer, cv2.VideoWriter):
                            vid_writer.release()
                        if vid_cap:
                            print(">>>>>>>>>",vid_cap)
                            fps = vid_cap.get(cv2.CAP_PROP_FPS)
                            w = int(vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                            h = int(vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                            src = os.path.split(source)
                            ip_name = src[1].split(".")
                            video_save_path = project + str(ip_name[0]) + '.mp4'
                        else:
                            print("RTSP>>>>>>>")
                            fps, w, h = 30, im0.shape[1], im0.shape[0]
                        vid_writer = cv2.VideoWriter(video_save_path, cv2.VideoWriter_fourcc(*'h264'), fps, (w, h))
                    vid_writer.write(im0)
        print("Frame Processing!")
    print("Video Exported Success")

    if update:
        strip_optimizer(weights)

    if vid_cap :
        vid_cap.release()

    # if cv2.waitKey(1) & 0xFF == ord('q'):
    #     break

    return video_save_path,total_entry_count,total_exit_count

# def main():
#     check_requirements(exclude=('tensorboard', 'thop'))
#     detect(**vars())
#
#
# if __name__ == "__main__":
#         main()
