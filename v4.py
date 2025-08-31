import os
import face_recognition
from flask import Flask, render_template, request, redirect
from werkzeug.utils import secure_filename
from PIL import Image
import uuid
import shutil
from io import BytesIO
import sqlite3
import pickle
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
import hashlib
import numpy as np
import cv2
import dlib

app = Flask(__name__)

# Paths
PHOTOS_ROOT = r"C:\Users\User1\Desktop\face recognition - v3\static\photos"  # Set your photos folder
RESULTS_FOLDER = os.path.join('static', 'results')
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Face alignment setup
face_detector = dlib.get_frontal_face_detector()
predictor_model = dlib.shape_predictor(face_recognition.api.pose_predictor_model_location())

def align_face(image):
    """Align the largest face in the image and return aligned crop."""
    try:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        rects = face_detector(gray, 1)

        if len(rects) == 0:
            return image  # fallback: no alignment

        # Pick the largest detected face
        rect = max(rects, key=lambda r: r.width() * r.height())

        # Get landmarks
        shape = predictor_model(gray, rect)
        landmarks = [(shape.part(i).x, shape.part(i).y) for i in range(68)]

        # Use eyes for alignment
        left_eye = np.mean(landmarks[36:42], axis=0)
        right_eye = np.mean(landmarks[42:48], axis=0)

        dY = right_eye[1] - left_eye[1]
        dX = right_eye[0] - left_eye[0]
        angle = np.degrees(np.arctan2(dY, dX))
        eyes_center = ((left_eye[0] + right_eye[0]) / 2, (left_eye[1] + right_eye[1]) / 2)

        M = cv2.getRotationMatrix2D(eyes_center, angle, scale=1.0)
        aligned = cv2.warpAffine(image, M, (image.shape[1], image.shape[0]), flags=cv2.INTER_CUBIC)

        return aligned
    except Exception as e:
        print(f"⚠️ Face alignment failed: {e}")
        return image  # fallback

# Caching
FACE_CACHE_DB = "face_cache.db"

def setup_face_cache():
    conn = sqlite3.connect(FACE_CACHE_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS face_cache (
            image_path TEXT PRIMARY KEY,
            face_encodings BLOB,
            file_hash TEXT,
            last_modified REAL,
            original_name TEXT
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_file_hash ON face_cache(file_hash)')
    conn.commit()
    conn.close()

def get_file_hash(file_path):
    try:
        stat = os.stat(file_path)
        return f"{stat.st_mtime}_{stat.st_size}"
    except:
        return "unknown"

def get_cached_face_encodings(image_path):
    try:
        conn = sqlite3.connect(FACE_CACHE_DB)
        cursor = conn.cursor()
        current_hash = get_file_hash(image_path)
        cursor.execute('''
            SELECT face_encodings, original_name FROM face_cache 
            WHERE image_path = ? AND file_hash = ?
        ''', (image_path, current_hash))
        result = cursor.fetchone()
        conn.close()
        if result:
            return pickle.loads(result[0]), result[1]
        return None, None
    except:
        return None, None

def cache_face_encodings(image_path, face_encodings, original_name):
    try:
        conn = sqlite3.connect(FACE_CACHE_DB)
        cursor = conn.cursor()
        file_hash = get_file_hash(image_path)
        encodings_blob = pickle.dumps(face_encodings)
        cursor.execute('''
            INSERT OR REPLACE INTO face_cache 
            (image_path, face_encodings, file_hash, last_modified, original_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (image_path, encodings_blob, file_hash, time.time(), original_name))
        conn.commit()
        conn.close()
    except:
        pass

def process_single_image(args):
    img_path, query_encoding = args
    try:
        cached_encodings, original_name = get_cached_face_encodings(img_path)
        if cached_encodings is None:
            gallery_img = face_recognition.load_image_file(img_path)
            gallery_img = align_face(gallery_img)
            cached_encodings = face_recognition.face_encodings(gallery_img)
            if cached_encodings:
                original_name = os.path.splitext(os.path.basename(img_path))[0]
                cache_face_encodings(img_path, cached_encodings, original_name)
        if not cached_encodings:
            return None
        best_distance = float('inf')
        for face_encoding in cached_encodings:
            dist = face_recognition.face_distance([query_encoding], face_encoding)[0]
            if dist < best_distance:
                best_distance = dist
        return {
            'path': img_path,
            'best_distance': best_distance,
            'original_name': original_name
        }
    except Exception as e:
        print(f"Error processing {img_path}: {e}")
        return None

def get_all_image_paths(folder):
    exts = ['.jpg', '.jpeg', '.png']
    img_files = []
    seen_files = set()
    for root, _, files in os.walk(folder):
        for file in files:
            if any(file.lower().endswith(ext) for ext in exts):
                full_path = os.path.join(root, file)
                normalized_path = os.path.normpath(full_path)
                if normalized_path not in seen_files:
                    seen_files.add(normalized_path)
                    img_files.append(normalized_path)
    print(f"🔍 Found {len(img_files)} unique images (filtered duplicates)")
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
    image_bytes = search_file.read()
    query_img = face_recognition.load_image_file(BytesIO(image_bytes))
    query_img = align_face(query_img)
    query_encodings = face_recognition.face_encodings(query_img)
    if not query_encodings:
        return [], []
    query_encoding = query_encodings[0]

    strong_matches = []
    doubtful_matches = []

    print(f"🚀 Starting HIGH-PERFORMANCE face search...")

    all_image_paths = get_all_image_paths(PHOTOS_ROOT)
    total_images = len(all_image_paths)
    print(f"📸 Processing {total_images} images with parallel optimization...")

    args_list = [(img_path, query_encoding) for img_path in all_image_paths]

    max_workers = min(multiprocessing.cpu_count(), 8)
    print(f"⚡ Using {max_workers} parallel workers...")

    start_time = time.time()

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(process_single_image, args_list))

    processing_time = time.time() - start_time
    print(f"⚡ Parallel processing completed in {processing_time:.2f} seconds!")

    processed_original_names = set()

    for result in results:
        if result is None:
            continue

        img_path = result['path']
        best_distance = result['best_distance']
        original_name = result['original_name']

        if original_name in processed_original_names:
            print(f"⚠️  Skipping duplicate original name: {original_name} (from {img_path})")
            continue

        processed_original_names.add(original_name)
        print(f"Processed: {img_path} (distance: {best_distance:.3f})")

        unique_id = str(uuid.uuid4())[:8]
        result_filename = f"{unique_id}_{os.path.basename(img_path)}"
        result_path = os.path.join(RESULTS_FOLDER, result_filename)
        shutil.copy2(img_path, result_path)

        print(f"  📊 Categorizing {original_name}: distance={best_distance:.3f}")

        if best_distance <= 0.35:
            strong_matches.append({
                "path": "results/" + result_filename,
                "original_name": original_name,
                "distance": best_distance
            })
            print(f"  ✅ Added to STRONG matches: {original_name} (distance: {best_distance:.3f})")
        elif 0.35 < best_distance <= 0.5:
            doubtful_matches.append({
                "path": "results/" + result_filename,
                "original_name": original_name,
                "distance": best_distance
            })
            print(f"  🟡 Added to DOUBTFUL matches: {original_name} (distance: {best_distance:.3f})")
        else:
            print(f"  ❌ Distance too high ({best_distance:.3f}), not including: {original_name}")

    print(f"Search complete. Strong matches: {len(strong_matches)}, Doubtful matches: {len(doubtful_matches)}")
    print(f"⚡ Performance: {total_images} images processed in {processing_time:.2f}s = {total_images/processing_time:.1f} images/second")

    strong_original_names = set()
    doubtful_original_names = set()

    print("\n=== DETAILED VERIFICATION ===")
    print("Strong matches:")
    for match in strong_matches:
        print(f"  - {match['path']} (original: {match['original_name']}, distance: {match['distance']:.3f})")
        strong_original_names.add(match["original_name"])

    print("\nDoubtful matches:")
    for match in doubtful_matches:
        print(f"  - {match['path']} (original: {match['original_name']}, distance: {match['distance']:.3f})")
        doubtful_original_names.add(match["original_name"])

    cross_duplicates = strong_original_names.intersection(doubtful_original_names)
    if cross_duplicates:
        print(f"\n🚨 CRITICAL ERROR: Cross-duplicates found between strong and doubtful: {cross_duplicates}")
    else:
        print(f"\n✅ SUCCESS: No cross-duplicates found")

    print(f"\nVerification complete. Total unique images: {len(strong_original_names) + len(doubtful_original_names)}")

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
    setup_face_cache()
    print("🚀 High-Performance Face Recognition System Ready!")
    print("⚡ Features: Parallel Processing + Smart Caching + Face Alignment + Zero Quality Loss")
    app.run(debug=True)
