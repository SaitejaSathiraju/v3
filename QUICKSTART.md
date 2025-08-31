# ⚡ Quick Start Guide

Get your Face Recognition System up and running in 5 minutes!

## 🚀 Super Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/yourusername/face-recognition-system.git
cd face-recognition-system
python setup.py
```

### 2. Add Your Photos
- Put your photos in the `static/photos/` directory
- Organize by year/month (optional but recommended):
  ```
  static/photos/
  ├── 2023/
  │   ├── 01 jan/
  │   ├── 02 feb/
  │   └── ...
  └── 2024/
  ```

### 3. Run the Application
```bash
python app.py
# or for enhanced version with face alignment:
python v4.py
```

### 4. Open Your Browser
Go to: `http://localhost:5000`

## 🎯 What You Can Do

### Face Recognition Search
1. Upload a photo with a face
2. Click "Search for Faces"
3. View matches with confidence scores

### Photo Gallery Browse
1. Use filters to find specific photos
2. Browse albums by date/event
3. View full-size images

## ⚙️ Configuration

### Change Photo Directory
Edit `PHOTOS_ROOT` in `app.py` or `v4.py`:
```python
PHOTOS_ROOT = r"C:\Your\Custom\Path\To\Photos"
```

### Performance Settings
```python
# Adjust parallel workers (default: min(CPU cores, 8))
max_workers = 4

# Face recognition thresholds
STRONG_MATCH_THRESHOLD = 0.35  # High confidence
DOUBTFUL_MATCH_THRESHOLD = 0.5  # Lower confidence
```

## 🔧 Troubleshooting

### "dlib installation failed"
```bash
# Windows: Install Visual Studio Build Tools
# Then try:
pip install dlib --no-cache-dir
```

### "No faces found"
- Ensure photos contain clear, front-facing faces
- Check image formats (JPG, PNG supported)
- Try different photos

### "Slow performance"
- Reduce `max_workers` in the code
- Use SSD storage
- Increase RAM

## 📊 Performance Tips

- **First run**: Will be slower as it builds cache
- **Subsequent runs**: Much faster with cached face encodings
- **Large collections**: Use SSD and 8GB+ RAM
- **Best accuracy**: Use well-lit, clear face photos

## 🆘 Need Help?

1. Check the full [README.md](README.md)
2. See [DEPLOYMENT.md](DEPLOYMENT.md) for advanced setup
3. Open an issue on GitHub

---

**Happy Face Recognition! 🎉**
