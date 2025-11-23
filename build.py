#!/usr/bin/env python3
import os
import shutil
import sys

def copy_static_files():
    """Copy static files to be included in Vercel deployment"""
    
    # Create static directory if it doesn't exist
    static_dir = 'static'
    if os.path.exists(static_dir):
        shutil.rmtree(static_dir)
    
    # Copy public folder to static
    if os.path.exists('public'):
        shutil.copytree('public', static_dir)
        print(f"Copied public folder to {static_dir}")
        
        # List what was copied
        for root, dirs, files in os.walk(static_dir):
            level = root.replace(static_dir, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files:
                print(f"{subindent}{file}")
    else:
        print("No public folder found")
        sys.exit(1)

if __name__ == '__main__':
    copy_static_files()
