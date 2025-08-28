import face_recognition
import os
from flask import Flask, request, jsonify, send_from_directory, render_template_string
from werkzeug.utils import secure_filename
from PIL import Image

PHOTOS_ROOT = r"C:\Users\User1\Desktop\face recognition - v3\photos"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'images')
os.makedirs(OUTPUT_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png'}

app = Flask(__name__)

def allowed_file(filename):
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)

def get_all_image_paths(folder):
    img_files = []
    for root, _, files in os.walk(folder):
        for file in files:
            if allowed_file(file):
                img_files.append(os.path.join(root, file))
    return img_files

@app.route('/')
def index():
    # Serve the HTML file
    with open(os.path.join(os.path.dirname(__file__), 'index.html'), encoding='utf-8') as f:
        return render_template_string(f.read())

@app.route('/upload', methods=['POST'])
def upload():
    if 'image' not in request.files:
        return jsonify({'success': False, 'error': 'No file part'})
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No selected file'})
    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': 'Invalid file type'})

    filename = secure_filename(file.filename)
    upload_path = os.path.join(OUTPUT_DIR, filename)
    file.save(upload_path)

    # Face search logic
    try:
        image = face_recognition.load_image_file(upload_path)
        encodings = face_recognition.face_encodings(image)
        if not encodings:
            return jsonify({'success': False, 'error': 'No face found in uploaded image!'})
        query_encoding = encodings[0]
        matches = []
        for img_path in get_all_image_paths(PHOTOS_ROOT):
            gallery_image = face_recognition.load_image_file(img_path)
            gallery_encodings = face_recognition.face_encodings(gallery_image)
            for face_encoding in gallery_encodings:
                if face_recognition.compare_faces([query_encoding], face_encoding, tolerance=0.35)[0]:
                    matches.append(img_path)
                    break
        # Save the first match as output (or all matches if you want)
        if matches:
            match_img_path = matches[0]
            out_img = Image.open(match_img_path)
            out_name = f"result_{filename}"
            out_path = os.path.join(OUTPUT_DIR, out_name)
            out_img.save(out_path)
            image_url = f"/images/{out_name}"
            return jsonify({'success': True, 'image_url': image_url})
        else:
            return jsonify({'success': False, 'error': 'No matching faces found.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)