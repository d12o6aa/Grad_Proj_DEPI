# Face Recognition and Liveness Detection System

## Overview

This project is an integrated identity verification system using AI technologies that:

- Detects spoofing attempts (fake photos/videos) to ensure the presented face is live and real.
- Verifies identity using DeepFace by comparing with registered face images.
- Allows employee registration with photo capture and storage.
- Provides a simple web interface to interact with the camera and display verification results.

The system uses Flask as a web server, OpenCV for image/video processing, and DeepFace for face recognition.

## Features

- Liveness detection through eye blink and head movement analysis.
- Spoofing detection to reject fake faces (printed photos, videos).
- Face recognition against stored employee images.
- Logs verification results in CSV files.
- Add new employees with live photo capture via the web interface.
- Real-time video streaming and verification.

## Requirements

- Python 3.7+
- Python libraries:
  - Flask
  - OpenCV (`opencv-python`)
  - DeepFace
  - dlib
  - scipy
  - numpy
- `shape_predictor_68_face_landmarks.dat` file for dlib face landmark detection  
  (Download from [dlib's official site](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2))
- Webcam connected to your system

## Installation

1. Clone the repository or download the source code.

2. Install dependencies:

```bash
pip install flask opencv-python deepface dlib scipy numpy

## Setup Instructions

1. Download the `shape_predictor_68_face_landmarks.dat` file and place it in the project directory.

2. Connect and test your webcam.

---

## How to Run

Run the application:

```bash
```bash
python app.py
```

## Project Structure

```
project_root/
│
├── app.py                         # Main application script
├── shape_predictor_68_face_landmarks.dat  # dlib model file
├── verified_log.csv               # Verification log file
├── verification_results.csv       # Face recognition results log
├── Data/                          # Employee images folder
│   └── [employee_name]/           # Each employee's images
├── static/
│   ├── fake_frames/               # Captured spoof frames
│   ├── verified_frames/           # Verified real frames
│   └── failed_frames/             # Failed verification frames
├── templates/
│   ├── index.html                 # Live video streaming page
│   └── add_employee.html          # Add employee page
```

## How It Works

The app captures a live video feed from your webcam.

1. **Liveness Detection**:  
    - Detects facial landmarks (e.g., eyes, mouth) to analyze blinking and head movements.  
    - These cues verify liveness, preventing spoofing attacks (e.g., photos or videos).

2. **Face Recognition**:  
    - If liveness is confirmed, the app uses DeepFace to perform face recognition.  
    - Matches the live face against stored employee images.

3. **Results and Logging**:  
    - Displays verification results (success/failure) in the browser interface.  
    - Logs all verification attempts in `.csv` files for record-keeping and auditing.

## Notes

- Use in well-lit environments for optimal accuracy.
- A high-resolution webcam improves face detection and verification quality.
- A GPU is recommended to significantly speed up face recognition via DeepFace.
- You can adjust spoof detection threshold values in the code (`app.py`) for better performance.

## Known Issues

- Low-light conditions reduce facial landmark detection accuracy.
- Performance may be slow on machines without a GPU.
- The application requires the `shape_predictor_68_face_landmarks.dat` file. Without it, the app will not run.

## Contributing

We welcome contributions to this project! You can help by:

- Reporting bugs.
- Suggesting new features.
- Submitting pull requests.

All contributions are appreciated!

## License

This project is open source and free to use, modify, and distribute under the terms of your preferred license.

Thank you for using the Face Recognition and Liveness Detection System! 😊
