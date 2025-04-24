import cv2
import pyrealsense2 as rs
import numpy as np
import pickle
import pyttsx3
import time
import random
import threading

# ====== Load Object Data ======
with open("trainedObjects.pkl", "rb") as f:
    trained_objects = pickle.load(f)

# ====== ORB Setup ======
orb = cv2.ORB_create(nfeatures=1000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

# ====== Text-to-Speech Setup ======
engine = pyttsx3.init()
def say(text):
    print(f"TTS: {text}")
    engine.say(text)
    engine.runAndWait()

# ====== RealSense Setup ======
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
pipeline.start(config)

# ====== Face Detection ======
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        if w > 100 and h > 100:
            return (x, y, w, h)
    return None

# ====== Object Recognition ======
def identify_object(frame):
    kp_frame, des_frame = orb.detectAndCompute(frame, None)
    best_match = None
    best_score = float('inf')

    for obj in trained_objects:
        matches = bf.match(des_frame, obj["descriptors"])
        matches = sorted(matches, key=lambda x: x.distance)
        score = sum([m.distance for m in matches[:20]]) if len(matches) >= 20 else float('inf')
        if score < best_score:
            best_match = obj
            best_score = score

    return best_match

# ====== ArUco Setup ======
aruco_dict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_4X4_50)
parameters = cv2.aruco.DetectorParameters_create()

# ====== Movement Placeholder Functions ======
def turn_left():
    # Should turn the robot to the left
    pass

def turn_right():
    # Should turn the robot to the right
    pass

def move_forward():
    # Should move the robot forward
    pass

def stop():
    # Should stop all robot movement
    pass

def raise_elbow():
    # Should lift the robot's elbow to perform the ring ritual
    pass

def arm_down():
    # Should lower the arm to drop the ring
    pass

def arm_up():
    # Should raise the arm back after dropping the ring
    pass

# ====== ArUco Navigation ======
def find_and_navigate_to_marker(target_id):
    say(f"Searching for box {target_id}. Let's get this over with.")
    found = False
    while not found:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        frame = np.asanyarray(color_frame.get_data())
        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        if ids is not None:
            ids = ids.flatten()
            if target_id in ids:
                say(f"There it is. Box {target_id} spotted.")
                found = True
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)
                center_x = frame.shape[1] // 2
                marker_index = list(ids).index(target_id)
                marker_center = int(np.mean(corners[marker_index][0][:, 0]))
                if marker_center < center_x - 40:
                    turn_left()
                elif marker_center > center_x + 40:
                    turn_right()
                else:
                    move_forward()
                time.sleep(1.5)
                stop()
                say("Destination reached. Time to do the bare minimum.")
                return
        cv2.imshow("Marker Scan", frame)
        if cv2.waitKey(1) == 27:
            break

# ====== Ring Drop ======
def drop_ring():
    say(random.choice([
        "Hope this lands in the box. Not my problem if it doesn’t.",
        "Done. Don’t say I never did anything.",
        "If I try any harder, I might break a sweat."
    ]))
    arm_down()
    time.sleep(1.5)
    arm_up()

# ====== Return to Center ======
def return_to_center():
    say("Heading back to the center. Cleaning complete. Barely.")
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        frame = np.asanyarray(color_frame.get_data())
        corners, ids, _ = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)
        if ids is not None and 0 in ids:
            ids = ids.flatten()
            marker_index = list(ids).index(0)
            center_x = frame.shape[1] // 2
            marker_center = int(np.mean(corners[marker_index][0][:, 0]))
            if marker_center < center_x - 40:
                turn_left()
            elif marker_center > center_x + 40:
                turn_right()
            else:
                move_forward()
            time.sleep(1.5)
            stop()
            break

# ====== Main Function with Pthreading ======
def camera_thread_routine():
    say("Scanning for signs of life...")
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        frame = np.asanyarray(color_frame.get_data())
        face = detect_face(frame)
        if face:
            x, y, w, h = face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            say(random.choice(["Ugh. What now?", "Seriously? I was in sleep mode...", "Fine. I'm awake."]))
            break
        cv2.imshow("Face Detection", frame)
        if cv2.waitKey(1) == 27:
            return

def phase2_main():
    print("[INFO] Starting Room Cleaner Phase")
    cam_thread = threading.Thread(target=camera_thread_routine)
    cam_thread.start()
    cam_thread.join()

    time.sleep(1)
    say("What am I supposed to clean up this time?")
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        frame = np.asanyarray(color_frame.get_data())
        result = identify_object(frame)
        if result:
            obj_name = result['name']
            obj_id = result['id']
            say(f"Fine. That’s the {obj_name}. Guess I will put it in box {obj_id}.")
            break
        cv2.imshow("Object Recognition", frame)
        if cv2.waitKey(1) == 27:
            return
    say("Perform the sacred ring ritual. Lift thy elbow.")
    raise_elbow()
    find_and_navigate_to_marker(obj_id)
    drop_ring()
    return_to_center()
    say("Cleaning complete. Barely.")

if __name__ == "__main__":
    phase2_main()
