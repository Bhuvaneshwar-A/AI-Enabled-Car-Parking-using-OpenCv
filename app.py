from flask import Flask, render_template, Response, request, session
import cv2
import pickle
import cvzone
import numpy as np
import ibm_db
import re

app = Flask(__name__)
app.secret_key='a'
app.static_folder = 'static'  # Add this line to set the static folder

conn = ibm_db.connect("XXXX", "", "")
print("connected")

@app.route('/')
def project():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def home():
    return render_template('register.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    return render_template('login.html')


@app.route('/predict', methods=['POST', 'GET'])
def predict():
    return render_template('predict.html')


@app.route("/reg", methods=['POST', 'GET'])
def signup():
    msg = ''
    if request.method == 'POST':
        name = request.form["name"]
        email = request.form["username"]
        password = request.form["password"]

        # Check if user already exists
        sql = "SELECT * FROM REGISTER WHERE name = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, name)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            return render_template('login.html', error=True)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = "Invalid Email Address!"
        else:
            # Insert new user into the database
            prep_stmt = ibm_db.prepare(conn, "INSERT INTO REGISTER (name, email, password) VALUES (?, ?, ?)")
            ibm_db.bind_param(prep_stmt, 1, name)
            ibm_db.bind_param(prep_stmt, 2, email)
            ibm_db.bind_param(prep_stmt, 3, password)
            ibm_db.execute(prep_stmt)
            msg = "You have successfully registered!"

    return render_template('login.html', msg=msg)


@app.route("/log", methods=['POST', 'GET'])
def login1():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        # Check if email and password match a user in the database
        sql = "SELECT * FROM REGISTER WHERE EMAIL=? AND PASSWORD=?"
        stmt = ibm_db.prepare(conn, sql)

        # Truncate the string values if they exceed the maximum allowed lengths
        max_email_length = 255  # Replace with the maximum allowed length for the email column
        max_password_length = 50  # Replace with the maximum allowed length for the password column
        email = email[:max_email_length] if len(email) > max_email_length else email
        password = password[:max_password_length] if len(password) > max_password_length else password

        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            # Store user information in session
            session['Loggedin'] = True
            session['id'] = account['EMAIL']
            session['email'] = account['EMAIL']
            return render_template('video.html')
        else:
            msg = "Incorrect Email/Password"
            return render_template('login.html', msg=msg)
    else:
        return render_template('login.html')


@app.route('/predict', methods=['POST', 'GET'])
def liv_pred():
    def predict():
        liv_pred_url = request.url_root + 'liv_pred'

    # Video feed
    cap = cv2.VideoCapture('Car Parking using CV/Dataset/carParkingInput.mp4')
    with open('parkingSlotPosition', 'rb') as f:
        posList = pickle.load(f)
    width, height = 107, 48

    def checkParkingSpace(imgPro, img):
        spaceCounter = 0
        for pos in posList:
            x, y = pos
            imgCrop = imgPro[y:y + height, x:x + width]
            count = cv2.countNonZero(imgCrop)
            if count < 900:
                color = (0, 255, 0)
                thickness = 5
                spaceCounter += 1
            else:
                color = (0, 0, 255)
                thickness = 2
            cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (100, 50), scale=3,
                           thickness=5, offset=20, colorR=(200, 0, 0))

    def generate_frames():
        while True:
            success, img = cap.read()
            if not success:
                break
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
            imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                 cv2.THRESH_BINARY_INV, 25, 16)
            imgMedian = cv2.medianBlur(imgThreshold, 5)
            kernel = np.ones((3, 3), np.uint8)
            imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
            checkParkingSpace(imgDilate, img)

            # Convert image to JPEG format
            ret, buffer = cv2.imencode('.jpg', img)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)