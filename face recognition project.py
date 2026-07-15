import os
import csv
from datetime import datetime
import tkinter as tk
from tkinter import Label, Button
import cv2
import face_recognition
from PIL import Image, ImageTk
import numpy as np

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

# DYNAMIC ADVANCEMENT: Pre-load already registered faces for today to prevent duplicates
logged_today = set()
current_date_str = datetime.now().strftime("%Y-%m-%d")

if os.path.exists(log_file_path):
    with open(log_file_path, mode='r') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip the CSV header row
        for row in reader:
            if len(row) >= 2 and row[1] == current_date_str:
                logged_today.add(row[0])


# --- STEP 3: APPLICATION ACTIONS ---
video_capture = cv2.VideoCapture(0)

def log_attendance(name):
    """Appends the recognized individual's timestamps to the CSV sheet dynamically."""
    if name not in logged_today and name != "Unknown":
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        with open(log_file_path, mode='a', newline='') as f:
            csv.writer(f).writerow([name, current_date_str, current_time])
            
        logged_today.add(name)
        print(f"[SYSTEM] Logged attendance for: {name}")

def close_application():
    """Safely releases physical hardware assets and kills the window execution loop."""
    video_capture.release()
    cv2.destroyAllWindows()
    window.quit()


# Global tracking variables for performance optimization
frame_counter = 0
cached_face_locations = []
cached_face_names = []

# --- STEP 4: LIVE CAMERA UPDATE LOOP ---
def update_video_stream():
    """Captures a frame, optimizes processing frame-skips, updates the layout interface."""
    global frame_counter, cached_face_locations, cached_face_names
    
    ret, frame = video_capture.read()
    if not ret or frame is None:
        window.after(10, update_video_stream)
        return

    # Process layout orientation
    frame = cv2.flip(frame, 1)
    
    # PERFORMANCE OPTIMIZATION: Only process face mapping calculations every 4th frame
    if frame_counter % 4 == 0:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect coordinates and faces
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

    # UI Graphics Rendering (Runs smoothly on every single frame using cached layout metrics)
    for (top, right, bottom, left), name in zip(cached_face_locations, cached_face_names):
        if name != "Unknown":
            current_frame_names.append(name)
            
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 1)

    # Render frame inside Tkinter UI frame labels safely
    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_tk = ImageTk.PhotoImage(image=Image.fromarray(img))
    video_label.config(image=img_tk)
    video_label.image = img_tk

    # Refresh the UI sidebar display box text list entries
    live_listbox.delete(0, tk.END)
    for entry in set(current_frame_names):  # Use set here to list unique faces currently visible
        live_listbox.insert(tk.END, entry)

    window.after(10, update_video_stream)


# --- STEP 5: GRAPHICAL USER INTERFACE (GUI) ---
window = tk.Tk()
window.title("Smart Attendance System")
window.geometry("950x600")

# Setup layout columns
video_label = Label(window)
video_label.pack(side="left", fill="both", expand=True, padx=10, pady=10)

sidebar = tk.Frame(window)
sidebar.pack(side="right", fill="y", padx=20, pady=20)

Label(sidebar, text="IN FRAME FACES", font=("Arial", 12, "bold")).pack(anchor="w", pady=5)
live_listbox = tk.Listbox(sidebar, font=("Arial", 11), bg="white", width=25, height=12)
live_listbox.pack(pady=5)

Button(sidebar, text="Stop & Close", command=close_application, bg="#ff4d4d", fg="white", font=("Arial", 11, "bold")).pack(fill="x", pady=30)

# Window close utility integration hook handles natural OS exit triggers cleanly
window.protocol("WM_DELETE_WINDOW", close_application)

# Launch core application loops
update_video_stream()
window.mainloop()