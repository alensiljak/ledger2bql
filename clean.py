'''
Clean up the build directories.
'''
# clean.py
import shutil
import os

for folder in ["dist", "build"]:
    shutil.rmtree(folder, ignore_errors=True)

for item in os.listdir():
    if item.endswith(".egg-info") and os.path.isdir(item):
        shutil.rmtree(item, ignore_errors=True)
