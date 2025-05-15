import os
import base64

class LocalStorage:
    def __init__(self, base_path='Data'):
        self.base_path = base_path

    def save_images(self, employee):
        folder = os.path.join(self.base_path, employee.name)
        os.makedirs(folder, exist_ok=True)

        for idx, img_data in enumerate(employee.images):
            img_bytes = base64.b64decode(img_data.split(',')[1])
            img_path = os.path.join(folder, f'{idx}.png')
            with open(img_path, 'wb') as f:
                f.write(img_bytes)
