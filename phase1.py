import cv2
import pyrealsense2 as rs
import pickle
import os

# Constants
MAX_OBJECTS = 3
SAVE_FILE = "trainedObjects.pkl"

# Initialize ORB detector
orb = cv2.ORB_create(nfeatures=1000)
trained_data = []

# RealSense setup
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# Mouse callback for bounding box selection
drawing = False
start_point = (-1, -1)
end_point = (-1, -1)
bounding_boxes = []
current_frame = None

def mouse_callback(event, x, y, flags, param):
    global drawing, start_point, end_point, current_frame

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        x1, y1 = start_point
        x2, y2 = end_point
        roi = current_frame[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
        if roi.size == 0:
            print("Empty ROI - try again")
            return
        keypoints, descriptors = orb.detectAndCompute(roi, None)
        if descriptors is not None:
            name = input("Enter object name: ")
            obj_id = len(trained_data) + 1
            trained_data.append({
                'id': obj_id,
                'name': name,
                'keypoints': keypoints,
                'descriptors': descriptors,
                'roi': roi
            })
            print(f"[INFO] Stored object #{obj_id} - {name}")
        else:
            print("[WARN] No descriptors found. Try again.")

# GUI setup
cv2.namedWindow("Training - Draw Box Around Object")
cv2.setMouseCallback("Training - Draw Box Around Object", mouse_callback)

try:
    print("Training mode started. Show 3 objects and draw bounding boxes.")
    while len(trained_data) < MAX_OBJECTS:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        current_frame = frame.copy()

        # Display live frame and bounding box in progress
        if drawing and start_point and end_point:
            temp_frame = frame.copy()
            cv2.rectangle(temp_frame, start_point, end_point, (0, 255, 0), 2)
            cv2.imshow("Training - Draw Box Around Object", temp_frame)
        else:
            cv2.imshow("Training - Draw Box Around Object", frame)

        key = cv2.waitKey(1)
        if key == 27:  # ESC to exit early
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()

# Save trained data
with open(SAVE_FILE, "wb") as f:
    pickle.dump(trained_data, f)
print(f"\n[INFO] Lazy teen memory activated. Object recognition enabled. Saved to {SAVE_FILE}")
