import cv2
import requests
import winsound   # for beep sound

# Flask API
SERVER_URL = "http://127.0.0.1:5000/scan_token"

# ESP32-CAM stream URL
ESP32_STREAM = "http://10.169.98.44/stream"

cap = cv2.VideoCapture(ESP32_STREAM)

detector = cv2.QRCodeDetector()

last_scanned = ""

while True:

    ret, frame = cap.read()

    if not ret:
        print("Camera not receiving frame")
        break

    data, bbox, _ = detector.detectAndDecode(frame)

    if data:

        if data != last_scanned:

            print("QR Detected:", data)

            # 🔔 Beep sound
            winsound.Beep(1200, 400)

            payload = {"patient_id": data}

            try:
                r = requests.post(SERVER_URL, json=payload)
                print("Server Response:", r.text)
            except:
                print("Server not reachable")

            last_scanned = data

    cv2.imshow("ESP32 QR Scanner", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()