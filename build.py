#!/usr/bin/env python3
import os
import shutil
import sys

def copy_static_files():
    """Copy static files to be included in Vercel deployment"""
    
    print("Starting build process...")
    
    # Create static directory if it doesn't exist
    static_dir = 'static'
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
        print(f"Removed existing {static_dir} directory")
    
    # Copy public folder to static
    if os.path.exists('public'):
        shutil.copytree('public', static_dir)
        print(f"✓ Copied public folder to {static_dir}")
        
        # Verify key files exist
        key_files = [
            'css/style.css',
            'js/main.js',
            'js/chat.js', 
            'js/voice.js',
            'data/languages.json',
            'images/Agrisahayak_image.png'
        ]
        
        print("\nVerifying key files:")
        for file_path in key_files:
            full_path = os.path.join(static_dir, file_path)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"✓ {file_path} ({size} bytes)")
            else:
                print(f"✗ {file_path} - MISSING")
        
        # List directory structure
        print(f"\nDirectory structure of {static_dir}:")
        for root, dirs, files in os.walk(static_dir):
            level = root.replace(static_dir, '').count(os.sep)
            indent = '  ' * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = '  ' * (level + 1)
            for file in sorted(files):
                print(f"{subindent}{file}")
                
    else:
        print("✗ No public folder found")
        sys.exit(1)
        
    print("\nBuild completed successfully!")

if __name__ == '__main__':
    copy_static_files()
