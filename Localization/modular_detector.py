from dt_apriltags import Detector
import math
import cv2
import numpy as np
import ntcore
import time
import wpiutil
from wpiutil import wpistruct
from network_tables import start_network_table
from camera_utils import set_auto_exposure
from camera_utils import set_camera_prop
from camera_utils import get_parameters
from calculate_pose import calculate_tag_offset
from calculate_pose import calculate_transformation
from poseclass import Position

INCHES_TO_METERS = 0.0254                                                                                      # OFFSET FROM ROBOT-------------------------------
cams = {                                                                                                       # METERS-----------------------       RAD---------
                   # ID                                                                                        # X=+front    Y=+left     Z=+up       yaw    pitch
    cv2.VideoCapture(-1): {"Parameters": get_parameters("front_camera.yaml"), "Matrix": calculate_transformation(0, 0, 0, 0, 0)},
    #cv2.VideoCapture(-1): {"Parameters": get_parameters("back_camera.yaml"),  "Matrix": calculate_transformation(X OFFSET, Y OFFSET, Z OFFSET, YAW, PITCH)}
}
ACCEPTABLE_TAG_ERROR_LIMIT = 5.0e-7 # Ask Calvin why this is the value, and why we toss even though we have a kalman filter

def main():
    # Initialize Network Table
    tagSeenPub, latencyPub, positionPub = start_network_table()
    
    # Initialize Detector. https://github.com/duckietown/lib-dt-apriltags
    at_detector = Detector(searchpath=['apriltags'],
                           nthreads=2,        # Ask Calvin why we use 2 threads
                           quad_decimate=1.0) # use high res 1.0, low res 2.0
    
    for cam in cams:
        # We get 100fps on MJPG compared to YUY2
        cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))

        # DO NOT USE TRY EXCEPT IN FINAL CODE. IF MULTIPLE CAMERAS USE DIFFERENT VALUES FOR THIS, INITIALIZE PRIOR
        try:
            # Our Cameras use 1 as the manual. run v4l2-ctl -d /dev/videoX -L to see
            set_auto_exposure(cam, 1)
        except ValueError:
            set_auto_exposure(cam, 0.25)
        
        # Set Exposure and Brightness to reasonable values. Tweak if necessary.
        set_camera_prop(cam, cv2.CAP_PROP_EXPOSURE, 10)
        set_camera_prop(cam, cv2.CAP_PROP_BRIGHTNESS, 0)
    
    while True:
        # Initialize NT values
        visionOffsets = []
        seen_tag = False
        frame_start = time.process_time()
        #if cv2.waitKey(1) == ord('q') & 0xff:
            #break
        for cam in cams: 
            _, frame = cam.read()
            
            # Use imshow to debug camera postions and IDs
            #cv2.imshow(str(cam), frame)
            
            grayscale = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tags = at_detector.detect(grayscale,
                                      estimate_tag_pose=True,
                                      camera_params=cams[cam]["Parameters"],
                                      tag_size=0.163525)
            
            for tag in tags:
                # We do not like tags that have much error >:(
                if tag.pose_err > ACCEPTABLE_TAG_ERROR_LIMIT:
                    continue
                seen_tag = True
                
                offset = calculate_tag_offset(tag.pose_t, cams[cam]["Matrix"])
                
                xOffset = offset[0][0][0]
                yOffset = offset[1][0][0]
                tagID = tag.tag_id
                
                visionPositions.append(Position(xOffset, yOffset, tagID))
        # Publish all positions and values to be interpreted on the RIO
        positionPub.set(visionOffsets)
        latencyPub.set(time.process_time() - frame_start)
        tagSeenPub.set(seen_tag)

if __name__ == "__main__":
    main()
