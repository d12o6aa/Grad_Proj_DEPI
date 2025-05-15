# app/routes/employee_routes.py
from flask import Blueprint, request, render_template
import os
import base64
from use_cases.add_employee import extract_and_store_vectors

employee_routes = Blueprint('employee_routes', __name__)
UPLOAD_FOLDER = "your_app/static/images"

@employee_routes.route('/add_employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        folder = os.path.join(UPLOAD_FOLDER, name)
        os.makedirs(folder, exist_ok=True)

        image_paths = []
        for i in range(1, 4):
            img_data = request.form.get(f'image{i}')
            if img_data:
                img_data = img_data.split(',')[1]
                img_bytes = base64.b64decode(img_data)
                path = os.path.join(folder, f'{name}_{i}.jpg')
                with open(path, 'wb') as f:
                    f.write(img_bytes)
                image_paths.append(path)

        extract_and_store_vectors(name, image_paths)
        return f"✔️ تم تسجيل الموظف {name} بنجاح."
    return render_template('add_employee.html')
