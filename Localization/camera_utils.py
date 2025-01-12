import cv2
import yaml

def set_camera_prop(cap, prop_id, value):
    for _ in range (0, 10):
        cap.set(prop_id, value)
        if cap.get(prop_id) != value:
            continue
        else: 
            return
    raise ValueError()
    
def set_auto_exposure(cap, value):
    try:
        set_camera_prop(cap, cv2.CAP_PROP_AUTO_EXPOSURE, value)
    except ValueError:
        raise ValueError("Failed to set AUTO EXPOSURE to %d", value)

def get_parameters(file):
    camera_params = [0] * 4
    with open(file, 'r') as f:
        params = yaml.safe_load(f)
        camera_params[0] = params["fx"]
        camera_params[1] = params["fy"]
        camera_params[2] = params["cx"]
        camera_params[3] = params["cy"]
    return camera_params
