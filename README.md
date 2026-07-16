# Smart Attendance System

A real-time face recognition desktop application built with Python. Uses a webcam feed to detect and identify faces against a database of known individuals — displaying live bounding boxes and logged names in an optimized GUI window with automated attendance spreadsheet sync.

**Repo:** [github.com/Prashantrwt007/Smart-Attendance-System](https://github.com/Prashantrwt007/Smart-Attendance-System)

---

## What It Does

- Opens your webcam in real time
- Detects all faces in each frame
- Compares them against a folder of known person images
- Draws a bounding box and name label on each recognized face
- Shows a live list of faces currently in frame
- Automatically logs attendance with exact name, date, and time timestamps into a local CSV spreadsheet
- Prevents duplicate logs using a smart cooldown engine

---

## Features

- Real-time Detection & Recognition via webcam
- Loads known faces from a local `persons/` folder automatically
- Horizontally flipped feed (mirror mode) for natural visual interaction
- Dynamic time-interval check (e.g., 60-second cooldown) to prevent duplicate attendance database spam
- Selective frame processing (runs heavy vector calculations every 4th frame) to reduce CPU overhead
- Records entries smoothly without duplicate rows using state recovery on startup
- Clean Tkinter GUI with responsive "Stop & Close" exit control

---

## Tech Stack

| | |
|---|---|
| Language | Python 3 |
| Face Recognition | `face_recognition` (dlib-based) |
| Computer Vision | OpenCV (`cv2`) |
| GUI | Tkinter + PIL |
| Image Processing | Pillow |

---

## Project Structure

Smart-Attendance-System/
├── face recognition project.py   # Main optimized application
├── persons/                      # Folder of known face images
│   ├── prashant.jpg
│   ├── komal.png
│   └── ...
└── README.md                     # Project documentation


> Image filename = person's ID/name shown on screen.
> Example: `prashant.jpg` → displays `prashant` when recognized.

---

## How to Run

```bash
git clone https://github.com/Prashantrwt007/Smart-Attendance-System.git
cd Smart-Attendance-System

# Install dependencies
pip install face_recognition opencv-python pillow numpy<2.0.0

# Add known face images to the persons/ folder (e.g., prashant.jpg)

# Run the application
python "face recognition project.py"
Note: face_recognition requires dlib which may need CMake and a C++ compiler on Windows. On Linux/Mac it installs cleanly.
```
How It Works
```
Webcam Frame
    ↓
Selective Frame Skip (Every 4th Frame)
    ↓
face_recognition.face_locations()   → finds all face bounding boxes
    ↓
face_recognition.face_encodings()   → converts each face to a 128-d vector
    ↓
face_recognition.compare_faces()    → compares against known encodings
    ↓
Match found & Cooldown checked      → write log to CSV & update list
    ↓
Draw box + name label (smooth rendering on all frames)
    ↓
Display in Tkinter GUI
```
Project Context
Built as part of an Artificial Intelligence / Computer Vision course to demonstrate real-time image processing, performance optimization, database synchronization, facial encoding, vector comparison, and desktop GUI integration in Python.

License
MIT
