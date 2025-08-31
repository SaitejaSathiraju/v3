#!/usr/bin/env python3
"""
Setup script for Face Recognition System
Helps users quickly configure and run the application
"""

import os
import sys
import subprocess
import platform

def print_banner():
    """Print welcome banner"""
    print("=" * 60)
    print("🔍 High-Performance Face Recognition System Setup")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "static/photos",
        "static/results", 
        "static/uploads",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created: {directory}")

def configure_photos_path():
    """Configure photos directory path"""
    print("\n📸 Configuring photos directory...")
    
    # Get current directory
    current_dir = os.getcwd()
    photos_path = os.path.join(current_dir, "static", "photos")
    
    print(f"Photos directory: {photos_path}")
    
    # Check if photos exist
    if os.path.exists(photos_path) and os.listdir(photos_path):
        print("✅ Photos directory contains files")
    else:
        print("⚠️  Photos directory is empty")
        print("Please add your photos to the static/photos directory")
    
    return photos_path

def update_config_files(photos_path):
    """Update configuration in Python files"""
    print("\n⚙️  Updating configuration files...")
    
    files_to_update = ["app.py", "v4.py"]
    
    for filename in files_to_update:
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update the PHOTOS_ROOT path
                import re
                pattern = r'PHOTOS_ROOT\s*=\s*r?"[^"]*"'
                replacement = f'PHOTOS_ROOT = r"{photos_path}"'
                
                new_content = re.sub(pattern, replacement, content)
                
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                print(f"✅ Updated: {filename}")
            except Exception as e:
                print(f"⚠️  Could not update {filename}: {e}")

def check_system_requirements():
    """Check system requirements"""
    print("\n🖥️  Checking system requirements...")
    
    # Check OS
    system = platform.system()
    print(f"Operating System: {system}")
    
    # Check memory (approximate)
    try:
        import psutil
        memory_gb = psutil.virtual_memory().total / (1024**3)
        print(f"Total Memory: {memory_gb:.1f} GB")
        
        if memory_gb < 4:
            print("⚠️  Warning: Less than 4GB RAM detected")
            print("   Performance may be limited")
        else:
            print("✅ Sufficient memory detected")
    except ImportError:
        print("⚠️  Could not check memory (psutil not installed)")
    
    # Check CPU cores
    cpu_count = os.cpu_count()
    print(f"CPU Cores: {cpu_count}")
    
    if cpu_count < 2:
        print("⚠️  Warning: Less than 2 CPU cores detected")
        print("   Parallel processing will be limited")
    else:
        print("✅ Sufficient CPU cores for parallel processing")

def run_tests():
    """Run basic tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Test imports
        import flask
        print("✅ Flask imported successfully")
        
        import face_recognition
        print("✅ face_recognition imported successfully")
        
        import cv2
        print("✅ OpenCV imported successfully")
        
        import dlib
        print("✅ dlib imported successfully")
        
        print("✅ All core dependencies working!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check system requirements
    check_system_requirements()
    
    # Install dependencies
    if not install_dependencies():
        print("\n❌ Setup failed! Please check the error messages above.")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Configure photos path
    photos_path = configure_photos_path()
    
    # Update config files
    update_config_files(photos_path)
    
    # Run tests
    if not run_tests():
        print("\n❌ Some tests failed! Please check the error messages above.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n🚀 To start the application:")
    print("   python app.py")
    print("   or")
    print("   python v4.py")
    print("\n📖 For more information, see README.md")
    print("🌐 The application will be available at: http://localhost:5000")

if __name__ == "__main__":
    main()
