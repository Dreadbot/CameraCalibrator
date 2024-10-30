import argparse
import json

import cv2
import numpy as np

# Parse arguments
arg_parser = argparse.ArgumentParser(prog="calibrate")
arg_parser.add_argument("cam_id", help="camera id", type=int)
arg_parser.add_argument("output_path", help="path to camera model file")

arg_parser.add_argument("square", help="width of square in mm", type=float)
arg_parser.add_argument("marker", help="width of marker in mm", type=float)
arg_parser.add_argument("width", help="width of board in squares", type=int)
arg_parser.add_argument("height", help="height of board in squares", type=int)

arg_parser.add_argument("-c", "--captures", help="number of frames to capture", default=30, required=False, type=int)

arg_parser.add_argument("--legacy", "-L", action='store_true', required=False, help="use the legacy pattern for detection")
arg_parser.add_argument("--no-ui", action='store_true', required=False, help="run without displaying the current frame")

args = arg_parser.parse_args()

dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_1000)

board = cv2.aruco.CharucoBoard((args.width, args.height), args.square / 1000, args.marker / 1000, dictionary)

if args.legacy:
    board.setLegacyPattern(True)

charuco_detector = cv2.aruco.CharucoDetector(board)

params = cv2.aruco.DetectorParameters()

# Save calibration output
def save_model(all_charuco_corners, all_charuco_ids, all_counter, frame_shape):
    # Calibrate camera
    _, camera_matrix, dist_coeffs, r_vecs, t_vecs, std_dev_intrinsics, std_dev_extrinsics, per_view_errors = cv2.aruco.calibrateCameraArucoExtended(
        np.array(all_charuco_corners),
        np.array(all_charuco_ids),
        np.array(all_counter),
        board,
        frame_shape,
        np.array([]),
        np.array([]),
        np.array([]),
        np.array([]),
        np.array([]),
        np.array([]),
        np.array([]),
        cv2.CALIB_RATIONAL_MODEL)
    
    with open(args.output_path, "w") as f:
        camera_model = {
            "camera_matrix": camera_matrix.flatten().tolist(),
            "distortion_coefficients": dist_coeffs.flatten().tolist(),
            "avg_reprojection_error": np.average(np.array(per_view_errors)),
            "num_images": len(all_counter)
        }

        f.write(json.dumps(camera_model, indent=4))

all_charuco_corners = []
all_charuco_ids = []
all_counter = []
frames = 0
captures = 0
frame_shape = (0, 0)

cap = cv2.VideoCapture(args.cam_id)


while True:
    ret, frame = cap.read()
    if not ret:
        break
    resized_frame = cv2.resize(frame, (640*2, 480*2)) 
    frames += 1
    
    if (cv2.waitKey(1) == ord("q")) or captures == args.captures:
        cap.release()
        print("Starting Calibration")
        save_model(all_charuco_corners, all_charuco_ids, all_counter, frame_shape)
    
    frame_grey = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
    frame_shape = frame_grey.shape
    
    charuco_corners, charuco_ids, marker_corners, marker_ids = charuco_detector.detectBoard(frame_grey)
 
    if charuco_ids is not None and len(charuco_ids) >= 6:
        cv2.aruco.drawDetectedMarkers(resized_frame, marker_corners, marker_ids)
        cv2.aruco.drawDetectedCornersCharuco(resized_frame, charuco_corners, charuco_ids)

        # Only use every 5 calculations, for speed
        if frames % 5 == 0:
            captures += 1
            if args.no_ui:
                print(captures)
            all_charuco_corners.extend(charuco_corners)
            all_charuco_ids.extend(charuco_ids)
            all_counter.append(len(charuco_ids))
         
    if not args.no_ui:
        cv2.imshow("frame", resized_frame)
