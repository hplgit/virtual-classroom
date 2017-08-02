import os
import hashlib
import shutil

def find_files(extension=".png"):
    for root, dirs, files in os.walk("assignment4_solutions_late"):
        for file in files:
            if file.lower().endswith(extension):
                filepath = os.path.join(root, file)
                print(filepath)
                new_filepath = hashlib.md5(filepath).hexdigest() + extension
                new_filepath = os.path.join("challenge", new_filepath)

                shutil.copy(filepath, new_filepath)

find_files(".png")
find_files(".jpg")
find_files(".jpeg")
find_files(".eps")
find_files(".svg")
