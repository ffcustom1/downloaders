import os
import hashlib
import requests
import shutil

def get_file_hash(file_path, algo="sha256"):
    hash_func = hashlib.new(algo)
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()

def check_civitai(hash_value):
    url = f"https://civitai.com/api/v1/model-versions/by-hash/{hash_value}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def clean_filename(name):
    """Clean filename of invalid characters but keep spaces"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')
    return name.strip()

def rename_and_move_file(file_path, new_name, target_folder):
    """Rename file and move to target folder"""
    try:
        # Clean filename and keep extension
        extension = os.path.splitext(file_path)[1]
        clean_name = clean_filename(new_name)
        new_filename = f"{clean_name}{extension}"
        
        # Create target path
        target_path = os.path.join(target_folder, new_filename)
        
        # Move and rename file
        shutil.move(file_path, target_path)
        return target_path
    except Exception as e:
        print(f"Error processing file: {e}")
        return file_path

def get_folder_path():
    print("Select an option:")
    print("1. Provide a custom folder path")
    print("2. Use script directory")
    choice = input("Enter your choice (1 or 2): ")
    
    if choice == "1":
        path = input("Enter the folder path: ")
        return path if os.path.isdir(path) else None
    elif choice == "2":
        return os.path.dirname(os.path.abspath(__file__))
    return None

if __name__ == "__main__":
    # Get the current directory of the script for the "checkpoints" folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    checkpoints_base_path = os.path.join(script_dir, "checkpoints")

    # Folder path selection
    folder_path = get_folder_path()

    if folder_path is None:
        print("Exiting the script due to invalid input.")
    else:
        # Ensure the base folders for each type under "checkpoints"
        types = ["sd.15", "flux", "pony", "sdxl", "illustrious", "none"]
        for folder in types:
            os.makedirs(os.path.join(checkpoints_base_path, folder), exist_ok=True)

        # Loop through all files
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(".safetensors"):
                    file_path = os.path.join(root, file)
                    file_hash = get_file_hash(file_path)
                    print(f"Processing: {file}")
                    print(f"SHA256 Hash: {file_hash}")

                    data = check_civitai(file_hash)
                    move_to_folder = "none"  # Default folder

                    if data:
                        # Get model name for renaming
                        if "model" in data and "name" in data["model"]:
                            new_name = data["model"]["name"]
                        else:
                            new_name = os.path.splitext(file)[0]

                        # Check base model type
                        if "baseModel" in data and "baseModelType" in data:
                            base_model = data["baseModel"].lower()
                            
                            if "sd 1.5" in base_model:
                                move_to_folder = "sd.15"
                            elif "flux" in base_model:
                                move_to_folder = "flux"
                            elif "pony" in base_model:
                                move_to_folder = "pony"
                            elif "sdxl" in base_model:
                                move_to_folder = "sdxl"
                            elif "illustrious" in base_model:
                                move_to_folder = "illustrious"
                            else:
                                # For unknown models, create a folder with the base model name
                                move_to_folder = base_model
                                print(f"Base Model: {base_model.capitalize()}")
                                print(f"Base Model Type: {data.get('baseModelType', 'Unknown')}")
                    else:
                        print("Base model information not found in the API response.")
                        move_to_folder = "none"

                    # Ensure the folder exists
                    target_folder = os.path.join(checkpoints_base_path, move_to_folder)
                    os.makedirs(target_folder, exist_ok=True)
 
                    # Move and rename file
                    new_path = rename_and_move_file(file_path, new_name, target_folder)
                    print(f"Moved and renamed to: {os.path.basename(new_path)}")
                    print(f"In folder: {move_to_folder}\n")