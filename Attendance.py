import cv2
import time
import datetime
import face_recognition
import os
import numpy as np
import board
import digitalio
import adafruit_character_lcd.character_lcd as character_lcd

# ======================
# Setup 16x2 LCD Display
# ======================
lcd_rs = digitalio.DigitalInOut(board.D26)
lcd_en = digitalio.DigitalInOut(board.D19)
lcd_d4 = digitalio.DigitalInOut(board.D13)
lcd_d5 = digitalio.DigitalInOut(board.D6)
lcd_d6 = digitalio.DigitalInOut(board.D5)
lcd_d7 = digitalio.DigitalInOut(board.D11)

lcd_columns = 16
lcd_rows = 2

lcd = character_lcd.Character_LCD_Mono(
    lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows
)
lcd.clear()

# ======================
# Load Known Faces
# ======================
known_face_encodings = []
known_face_names = []

faculty_names = {
    "Biology": "Maithili mam",
    "Chemistry": "Kiran sir",
    "Physics": "Kishor sir"
}

dataset_path = "dataset"
for student_name in os.listdir(dataset_path):
    student_folder = os.path.join(dataset_path, student_name)
    if os.path.isdir(student_folder):
        for image_file in os.listdir(student_folder):
            image_path = os.path.join(student_folder, image_file)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append(student_name)

# ======================
# Webcam Setup
# ======================
cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

# ======================
# Attendance Log
# ======================
attendance_log = {}
selected_subject = "Biology"
current_displayed_name = ""
lcd_display_expiry_time = float("inf")

# ======================
# Subject Button Areas
# ======================
button_areas = {
    "Biology": (10, 10, 170, 60),
    "Chemistry": (180, 10, 340, 60),
    "Physics": (350, 10, 510, 60)
}

# ======================
# Draw Buttons
# ======================
def draw_buttons(frame):
    for subject, (x1, y1, x2, y2) in button_areas.items():
        if subject == selected_subject:
            color = (0, 255, 0)
        else:
            color = (100, 100, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
        cv2.putText(frame, subject, (x1 + 15, y1 + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    total = sum(1 for k in attendance_log if k.endswith(selected_subject))
    cv2.putText(frame, f"Selected: {selected_subject}", (10, 80),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Total {selected_subject}: {total}", (10, 110),
                cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 200, 255), 2)

# ======================
# Mouse Callback
# ======================
def check_button_click(x, y):
    global selected_subject, lcd_display_expiry_time
    for subject, (x1, y1, x2, y2) in button_areas.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            selected_subject = subject
            lcd.clear()
            total_now = sum(1 for k in attendance_log if k.endswith(selected_subject))
            lcd.message = f"{selected_subject} -\n{faculty_names[selected_subject]}"
            lcd_display_expiry_time = float("inf")
            print(f"[INFO] Switched to {selected_subject}")
            break

def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        check_button_click(x, y)

cv2.namedWindow("Attendance System")
cv2.setMouseCallback("Attendance System", mouse_click)

# ======================
# Mark Attendance
# ======================
def mark_attendance(name, subject):
    key = f"{name}-{subject}"
    if key not in attendance_log:
        attendance_log[key] = datetime.datetime.now()
        print(f"[LOG] {name} marked present for {subject} at {attendance_log[key].strftime('%H:%M:%S')}")
        return True
    return False

# ======================
# Main Loop
# ======================
try:
    lcd.message = f"{selected_subject} -\n{faculty_names[selected_subject]}"
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Camera error.")
            break

        now = time.time()
        draw_buttons(frame)

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.5)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)

            if matches[best_match_index]:
                name = known_face_names[best_match_index]

                if mark_attendance(name, selected_subject):
                    total_now = sum(1 for k in attendance_log if k.endswith(selected_subject))
                    timestamp = attendance_log[f"{name}-{selected_subject}"].strftime("%H:%M:%S")
                    lcd.clear()
                    lcd.message = f"{name[:16]}-Present\n{timestamp}"
                    current_displayed_name = name
                    lcd_display_expiry_time = now + 2
                    break

        if time.time() > lcd_display_expiry_time:
            total_now = sum(1 for k in attendance_log if k.endswith(selected_subject))
            lcd.clear()
            lcd.message = f"{selected_subject} -\nTotal: {total_now}"
            current_displayed_name = ""
            lcd_display_expiry_time = float("inf")

        cv2.imshow("Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("Stopped by user")

finally:
    cap.release()
    cv2.destroyAllWindows()
    lcd.clear()
