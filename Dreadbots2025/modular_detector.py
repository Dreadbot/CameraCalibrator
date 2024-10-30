from dt_apriltags import Detector
import numpy as np
import argparse
import pathlib
import yaml
import math
import cv2
import os
import ntcore
import time
import dataclasses
import wpiutil
from wpiutil import wpistruct
from camera_utils import set_auto_exposure
from camera_utils import set_camera_prop
from calculate_pose import calculate_world_pose

CAM_MOUNT_PITCH = 30
CAM_ID = -1
CAMERA_TO_ROBOT_OFFSET = 0.3937

INCHES_TO_METERS = 0.0254
CAMERA_PITCH = math.radians(90 - CAM_MOUNT_PITCH)

def main():
    cap = cv2.VideoCapture(CAM_ID)
    try:
        set_auto_exposure(cap, 1)
    except Error:
        set_auto_exposure(cap, 0.25)

    set_camera_prop(cap, cv2.CAP_PROP_EXPOSURE, 500)
    set_camera_prop(cap, cv2.CAP_PROP_BRIGHTNESS, 0)
    
    while True:
        ret, frame = cap.read()
        cv2.imshow("frame", frame)

        if cv2.waitKey(1) == ord('q') & 0xff:
            break

if __name__ == "__main__":
    main()
