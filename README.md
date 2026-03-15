# Smart Attendance Board 🎓

A face recognition-based smart attendance system using Raspberry Pi with a 16x2 LCD display.

## Features
- Real-time face recognition using webcam
- Automatic attendance logging with timestamp
- Subject selection (Biology, Chemistry, Physics)
- Live attendance count display
- 16x2 LCD display shows student name + time

## Hardware Requirements
- Raspberry Pi (any model with GPIO)
- USB Webcam
- 16x2 LCD Display (connected via GPIO)

## Software Requirements
- Python 3.x
- OpenCV
- face_recognition
- adafruit_character_lcd
- NumPy

## Installation
```bash
pip install opencv-python face_recognition numpy adafruit-circuitpython-charlcd
```

## Project Structure
```
Smart-Attendance-Board/
│
├── dataset/
│   ├── Student1/
│   │   ├── img1.jpg
│   └── Student2/
│       ├── img1.jpg
│
├── attendance.py
└── README.md
```

## How to Run
1. Add student images inside the `dataset/` folder (one folder per student)
2. Connect the LCD to Raspberry Pi GPIO pins
3. Run the script:
```bash
python attendance.py
```

## GPIO Pin Configuration
| LCD Pin | Raspberry Pi GPIO |
|---------|-------------------|
| RS      | D26               |
| EN      | D19               |
| D4      | D13               |
| D5      | D6                |
| D6      | D5                |
| D7      | D11               |
```

---

## 2. Create a `.gitignore` file
```
__pycache__/
*.pyc
dataset/
.env
*.log
