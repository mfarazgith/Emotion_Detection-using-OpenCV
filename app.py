from flask import Flask, render_template, jsonify, Response
import cv2
from keras.models import model_from_json
import numpy as np

app = Flask(__name__)

json_file = open("emotiondetector.json", "r")
model_json = json_file.read()
json_file.close()
model = model_from_json(model_json)

model.load_weights("emotiondetector.h5")
haar_file = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(haar_file)

def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1, 48, 48, 1)
    return feature / 255.0

labels = {0: 'angry', 1: 'disgust', 2: 'fear', 3: 'happy', 4: 'neutral', 5: 'sad', 6: 'surprise'}

def generate_frames():
    webcam = cv2.VideoCapture(0)
    while True:
        _, frame = webcam.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame, 1.3, 5)

        try:
            for (p, q, r, s) in faces:
                face = gray[q:q+s, p:p+r]
                face = cv2.resize(face, (48, 48))
                img = extract_features(face)
                pred = model.predict(img)
                prediction_label = labels[pred.argmax()]
                cv2.putText(frame, f'Emotion: {prediction_label}', (p-10, q-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255))
        except cv2.error:
            pass

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
