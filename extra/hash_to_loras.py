import os
import hashlib
import requests

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

def create_urls(model_id, version_id):
    base_url = f"https://civitai.com/models/{model_id}"
    version_url = f"{base_url}?modelVersionId={version_id}"
    return base_url, version_url  # Return both URLs

if __name__ == "__main__":
    folder_path = get_folder_path()
    if folder_path is None:
        print("Exiting the script due to invalid input.")
    else:
        # Create or open both files for writing
        with open("loras_download.txt", "w", encoding="utf-8") as url_file, \
             open("loras_hash_not_found.txt", "w", encoding="utf-8") as not_found_file:
            
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.endswith(".safetensors"):
                        file_path = os.path.join(root, file)
                        print(f"Processing: {file}")
                        
                        file_hash = get_file_hash(file_path)
                        data = check_civitai(file_hash)
                        
                        if data and "id" in data and "modelId" in data:
                            version_id = data["id"]
                            model_id = data["modelId"]
                            base_url, version_url = create_urls(model_id, version_id)
                            url_file.write(f"{base_url}\n{version_url}\n")
                        else:
                            rel_path = os.path.relpath(file_path, folder_path)
                            not_found_file.write(f"{rel_path}\n")

    print("Done. URLs saved to loras_download.txt")
    print("Files not found saved to hash_not_found.txt")