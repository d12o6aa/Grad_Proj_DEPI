from flask import Flask, render_template, request
import os
import base64

app = Flask(__name__)
UPLOAD_FOLDER = 'Data/user1'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('camera.html')

@app.route('/save_frame', methods=['POST'])
def save_frame():
    data = request.get_json()
    img_data = data['image']
    stage = data['stage']

    img_data = img_data.split(',')[1]
    img_bytes = base64.b64decode(img_data)

    filename = ['front.jpg', 'right.jpg', 'left.jpg'][stage]
    with open(os.path.join(UPLOAD_FOLDER, filename), 'wb') as f:
        f.write(img_bytes)

    return "saved"

if __name__ == '__main__':
    app.run(debug=True)
