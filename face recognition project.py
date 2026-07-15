import os
import csv
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import Label, Button
import cv2
import face_recognition
from PIL import Image, ImageTk
import numpy as np

# ==========================================
# CONFIGURATION MODULE: Set Cooldown Here
# ==========================================
# 60 seconds for live interview testing. Change to 3600 for a 1-hour interval.
COOLDOWN_SECONDS = 60 

# --- STEP 1: EXTRACT FACE SIGNATURE ---
def get_face_encoding(image_path):
    """Loads an image file and extracts its mathematical face signature."""
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    return encodings[0] if encodings else None


# --- STEP 2: INITIALIZE DATABASE & LOG FILE ---
script_dir = os.path.dirname(os.path.abspath(__file__))
persons_folder = os.path.join(script_dir, "persons")

known_face_encodings = []
person_ids = []

# Load image database
if os.path.exists(persons_folder):
    for filename in os.listdir(persons_folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(persons_folder, filename)
            name = os.path.splitext(filename)[0]
            encoding = get_face_encoding(path)
            
            if encoding is not None:
                known_face_encodings.append(encoding)
                person_ids.append(name)

# Initialize Excel/CSV logger file
log_file_path = os.path.join(script_dir, "attendance_log.csv")
if not os.path.exists(log_file_path):
    with open(log_file_path, mode='w', newline='') as f:
        csv.writer(f).writerow(["Name", "Date", "Time"])

# DYNAMIC COOLDOWN TRACKER: Stores last recognized time as a Python datetime object
# Format mapping structure: {"name": datetime_object}
last_logged_cache = {}
current_date_str = datetime.now().strftime("%Y-%m-%d")

# Pre-load logs from history to reconstruct system cache state on startup
if os.path.exists(log_file_path):
    with open(log_file_path, mode='r') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip CSV Header
        for row in reader:
            if len(row) >= 3 and row[1] == current_date_str:
                name_entry = row[0]
                time_str = row[2]
                try:
                    # Combine today's date and log string to rebuild object array reference
                    full_datetime = datetime.strptime(f"{current_date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                    # Keep the latest time parsed sequentially from storage
                    last_logged_cache[name_entry] = full_datetime
                except ValueError:
                    continue


# --- STEP 3: APPLICATION ACTIONS ---
video_capture = cv2.VideoCapture(0)

def log_attendance(name):
    """Logs name to Excel dynamically if the timestamp bypasses the set cooldown duration."""
    if name == "Unknown":
        return

    now = datetime.now()
    
    # LINE: Check if name exists in tracking dictionary cache
    if name in last_logged_cache:
        last_time = last_logged_cache[name]
        elapsed_time = (now - last_time).total_seconds()
        
        # LINE: If elapsed seconds are less than threshold parameter loop breaks
        if elapsed_time < COOLDOWN_SECONDS:
            remaining = int(COOLDOWN_SECONDS - elapsed_time)
            # Optional console print to track math operations
            # print(f"[COOLDOWN] {name} locked out for another {remaining} seconds.")
            return 

    # Cooldown verification passed: Register entry
    current_time_str = now.strftime("%H:%M:%S")
    with open(log_file_path, mode='a', newline='') as f:
        csv.writer(f).writerow([name, current_date_str, current_time_str])
        
    # Update localized processing memory index
    last_logged_cache[name] = now
    print(f"[SYSTEM MASTER] Logged attendance for: {name} at {current_time_str}")

def close_application():
    """Safely releases physical hardware assets and kills the window execution loop."""
    video_capture.release()
    cv2.destroyAllWindows()
    window.quit()


# Execution cycle bounds setup
frame_counter = 0
cached_face_locations = []
cached_face_names = []

# --- STEP 4: LIVE CAMERA UPDATE LOOP ---
def update_video_stream():
    """Captures frames, shifts arrays, drops process frame overhead to balance execution threads."""
    global frame_counter, cached_face_locations, cached_face_names
    
    ret, frame = video_capture.read()
    if not ret or frame is None:
        window.after(10, update_video_stream)
        return

    frame = cv2.flip(frame, 1)
    
    # Matrix performance optimization passing boundary mapping calculations every 4th frame
    if frame_counter % 4 == 0:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        cached_face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, cached_face_locations)

        cached_face_names = []
        for face_encoding in face_encodings:
            name = "Unknown"
            if known_face_encodings:
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                if True in matches:
                    name = person_ids[matches.index(True)]
                    log_attendance(name)
            cached_face_names.append(name)

    frame_counter += 1
    current_frame_names = []

    # Graphics overlay parsing layer
    for (top, right, bottom, left), name in zip(cached_face_locations, cached_face_names):
        if name != "Unknown":
            current_frame_names.append(name)
            
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1)

    # Frame delivery to Tkinter
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(img))
    video_label.config(image=img_tk)
    video_label.image = img_tk

    # Update GUI list box text
    live_listbox.delete(0, tk.END)
    for entry in set(current_frame_names):
        live_listbox.insert(tk.END, entry)

    window.after(10, update_video_stream)


# --- STEP 5: GRAPHICAL USER INTERFACE (GUI) ---
window = tk.Tk()
window.title("Smart Attendance System with Cooldown")
window.geometry("950x600")

# Setup layout blocks
video_label = Label(window)
video_label.pack(side="left", fill="both", expand=True, padx=10, pady=10)

sidebar = tk.Frame(window)
sidebar.pack(side="right", fill="y", padx=20, pady=20)

Label(sidebar, text="IN FRAME FACES", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
live_listbox = tk.Listbox(sidebar, font=("Arial", 11), bg="white", width=25, height=12)
live_listbox.pack(pady=5)

Button(sidebar, text="Stop & Close", command=close_application, bg="#ff4d4d", fg="white", font=("Arial", 11, "bold")).pack(fill="x", pady=30)

# Hardware closure protocol handling bound interfaces
window.protocol("WM_DELETE_WINDOW", close_application)

# Kickoff processing runtime execution loops
update_video_stream()
window.mainloop()