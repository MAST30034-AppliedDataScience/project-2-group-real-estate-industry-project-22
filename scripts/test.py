import os

file_path = '../data/raw/example.json'



# Check if the path is valid
if not os.path.exists(os.path.dirname(file_path)):
    print(f"Directory does not exist: {os.path.dirname(file_path)}")
else:
    print(f"Directory exists: {os.path.dirname(file_path)}")