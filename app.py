import os
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
import face_recognition
from PIL import Image
import uuid
import shutil
from io import BytesIO

app = Flask(__name__)

# Paths
PHOTOS_ROOT = r"C:\Users\User1\Desktop\face recognition - v3\static\photos"  # Set your photos folder
RESULTS_FOLDER = os.path.join('static', 'results')
os.makedirs(RESULTS_FOLDER, exist_ok=True)

def get_all_image_paths(folder):
    exts = ['.jpg', '.jpeg', '.png']
    img_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in exts):
                img_files.append(os.path.join(root, file))
    return img_files

def clear_results_folder():
    for f in os.listdir(RESULTS_FOLDER):
        file_path = os.path.join(RESULTS_FOLDER, f)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception:
            pass

def process_search(search_file):
    # Read uploaded image from memory
    image_bytes = search_file.read()
    query_img = face_recognition.load_image_file(BytesIO(image_bytes))
    query_encodings = face_recognition.face_encodings(query_img)
    if not query_encodings:
        return [], []
    query_encoding = query_encodings[0]

    strong_matches = []
    doubtful_matches = []

    for img_path in get_all_image_paths(PHOTOS_ROOT):
        gallery_img = face_recognition.load_image_file(img_path)
        gallery_encodings = face_recognition.face_encodings(gallery_img)
        for face_encoding in gallery_encodings:
            dist = face_recognition.face_distance([query_encoding], face_encoding)[0]
            
            # Get original filename and extension
            original_filename = os.path.basename(img_path)
            name, ext = os.path.splitext(original_filename)
            
            # Create unique filename for results folder
            unique_filename = str(uuid.uuid4()) + ext
            result_path = os.path.join(RESULTS_FOLDER, unique_filename)
            
            if dist <= 0.35:
                shutil.copy2(img_path, result_path)
                # Store both the file path and original filename
                strong_matches.append({
                    'path': "results/" + unique_filename,
                    'original_name': original_filename
                })
                break
            elif 0.35 < dist <= 0.5:
                shutil.copy2(img_path, result_path)
                # Store both the file path and original filename
                doubtful_matches.append({
                    'path': "results/" + unique_filename,
                    'original_name': original_filename
                })
                break

    return strong_matches, doubtful_matches

@app.route('/', methods=['GET', 'POST'])
def index():
    strong = []
    doubtful = []
    if request.method == 'POST':
        clear_results_folder()
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file and file.filename:
            strong, doubtful = process_search(file)
    return render_template('index.html', strong_images=strong, doubtful_images=doubtful)

if __name__ == '__main__':
    app.run(debug=True)