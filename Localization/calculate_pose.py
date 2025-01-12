import math
import numpy as np

# AT detector results, pitch, [x, y, z, yaw, pitch]
def calculate_tag_offset(tag_in_camera_frame, CAMERA_TO_ROBOT_OFFSET):
    sin_90 = math.sin(math.pi / 2)
    cos_90 = math.cos(math.pi / 2)

    CAMERA_X = CAMERA_TO_ROBOT_OFFSET[0]
    CAMERA_Y = CAMERA_TO_ROBOT_OFFSET[1]
    CAMERA_Z = CAMERA_TO_ROBOT_OFFSET[2]
    
    CAMERA_YAW = CAMERA_TO_ROBOT_OFFSET[3]
    CAMERA_PITCH = CAMERA_TO_ROBOT_OFFSET[4]
    
    sin_pitch = math.sin(CAMERA_PITCH)
    cos_pitch = math.cos(CAMERA_PITCH)
    
    sin_yaw = math.sin(CAMERA_YAW)
    cos_yaw = math.cos(CAMERA_YAW)

    tag_in_camera_frame = np.array([[tag_in_camera_frame[0]], [tag_in_camera_frame[1]], [tag_in_camera_frame[2]], [1]], dtype="object")

    # Camera Pitch
    pitch_rotation = np.array([
        [1, 0, 0, 0],
        [0, cos_pitch, sin_pitch, 0],
        [0, -sin_pitch, cos_pitch, 0],
        [0, 0, 0, 1]
    ], dtype="object")

    # FRC Fields use X as depth opposed to cameras
    camera_axes_to_robot_axes = np.array([
        [cos_90, sin_90, 0, 0],
        [-sin_90, cos_90, 0, 0],
        [0, 0, 1, 0],
        [0, 0, 0, 1]
    ], dtype="object")

    # Translation of Camera Origin to Robot Origin
    camera_origin_to_robot_origin = np.array([
        [cos_yaw, -sin_yaw, 0, CAMERA_X],
        [sin_yaw, cos_yaw, 0, -CAMERA_Y], # -1 due to terrible left handedness of coordinate system
        [0, 0, 1, CAMERA_Z],
        [0, 0, 0, 1]
    ], dtype="object")

    # Camera Coordinates to World Coordinates
    
    # Rotate Axes onto World Axes
    corrected_pitch = np.matmul(camera_axes_to_robot_axes, pitch_rotation)
    # Move origin
    overall_transformation = np.matmul(camera_origin_to_robot_origin, corrected_pitch)
    
    # Actual Coordinate Transform
    tag_in_robot_frame = np.matmul(overall_transformation, tag_in_camera_frame)

    ## Robot Rotation
    #tag_corrected = np.matmul(pitch_rotation, tag_in_camera_frame)
    #
    ## Rotate Axes onto World Axes
    #applied_rotation = np.matmul(camera_axes_to_robot_axes, tag_corrected)
    #
    ## Bring out Rotation Values from Matrix
    #robot_yaw_from_tag = math.acos(applied_rotation[0][0][2]) * np.sign(applied_rotation[1][0][2])
    
    return tag_in_robot_frame