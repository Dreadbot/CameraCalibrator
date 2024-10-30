import cv2

def set_camera_prop(cap, prop_id, value):
    for _ in range (0, 10):
        cap.set(prop_id, value)
        if cap.get(prop_id) != value:
            continue
        else: 
            return
    raise Error()
    
def set_auto_exposure(cap, value):
    try:
        set_camera_prop(cap, cv2.CAP_PROP_AUTO_EXPOSURE, value)
    except ValueError:
        raise Error("Failed to set AUTO EXPOSURE to %d", value)
