import os
import re
import requests
from tqdm import tqdm
from typing import Literal

# Get script directory and set API key
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
API_KEY = "85c1a25c0653fb1e81ef01c032f684e7"

# Define constants for different model types
MODEL_TYPES = {
    'checkpoints': {
        'file': os.path.join(SCRIPT_DIR, "checkpoints.txt"),
        'folder': os.path.join(SCRIPT_DIR, "checkpoints"),
        'log': os.path.join(SCRIPT_DIR, "checkpoints_downloaded.log")
    },
    'loras': {
        'file': os.path.join(SCRIPT_DIR, "loras.txt"),
        'folder': os.path.join(SCRIPT_DIR, "loras"),
        'log': os.path.join(SCRIPT_DIR, "loras_downloaded.log")
    },
    'others': {
        'file': os.path.join(SCRIPT_DIR, "others.txt"),
        'folder': os.path.join(SCRIPT_DIR, "others"),
        'log': os.path.join(SCRIPT_DIR, "others_downloaded.log")
    }
}

def load_downloaded_urls(log_file):
    """Load already downloaded URLs from the log file."""
    if os.path.exists(log_file):
        with open(log_file, 'r') as file:
            return set(line.strip() for line in file.readlines())
    return set()

def save_downloaded_url(log_file, url):
    """Save successfully downloaded URL to the log file."""
    with open(log_file, 'a') as file:
        file.write(f"{url}\n")

def save_failed_url(url, error):
    """Save failed download URLs to failed_downloads.txt with error message."""
    with open(os.path.join(SCRIPT_DIR, "failed_downloads.txt"), 'a') as file:
        file.write(f"{url} | Error: {error}\n")

def remove_url_from_file(url, file_path):
    """Remove a URL from the source file."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
    with open(file_path, 'w') as file:
        file.writelines(line for line in lines if line.strip() != url)

def get_unique_filename(directory, filename):
    """Generate a unique filename by appending a number if the file already exists."""
    base, ext = os.path.splitext(filename)
    counter = 1
    unique_filename = filename
    while os.path.exists(os.path.join(directory, unique_filename)):
        unique_filename = f"{base}({counter}){ext}"
        counter += 1
    return unique_filename

def download_file(url, target_dir, log_file):
    """Download a file and log it if successful."""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        filename = re.findall("filename=(.+)", response.headers.get('content-disposition', ''))[0].strip('"') \
                  if 'content-disposition' in response.headers else url.split('/')[-1]
        
        filename = get_unique_filename(target_dir, filename)
        filepath = os.path.join(target_dir, filename)
        
        total_size = int(response.headers.get('content-length', 0))
        with open(filepath, 'wb') as f, tqdm(
            desc=filename,
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for data in response.iter_content(chunk_size=1024):
                size = f.write(data)
                pbar.update(size)
        
        save_downloaded_url(log_file, url)
        return True
    except Exception as e:
        error_msg = str(e)
        print(f"Error downloading {url}: {error_msg}")
        save_failed_url(url, error_msg)
        return False

def process_downloads(model_type: Literal['checkpoints', 'loras', 'others']):
    """Process downloads for specified model type."""
    config = MODEL_TYPES[model_type]
    
    os.makedirs(config['folder'], exist_ok=True)
    
    if not os.path.exists(config['file']):
        print(f"Error: {config['file']} not found")
        return
        
    downloaded = load_downloaded_urls(config['log'])
    
    with open(config['file'], 'r') as f:
        urls = [line.strip() for line in f if line.strip()]
    
    total_urls = len(urls)
    print(f"\nFound {total_urls} URLs in {os.path.basename(config['file'])}")
    
    for i, url in enumerate(urls, 1):
        if url in downloaded:
            print(f"\nSkipping {url} (already downloaded)")
            remove_url_from_file(url, config['file'])
            continue
            
        print(f"\nProcessing [{i}/{total_urls}]: {url}")
        success = download_file(url, config['folder'], config['log'])
        
        # Remove URL from source file regardless of success
        # If failed, it's already saved to failed_downloads.txt
        remove_url_from_file(url, config['file'])

if __name__ == "__main__":
    while True:
        print("\nSelect download type:")
        print("1. Checkpoints")
        print("2. Loras")
        print("3. Others")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == '4':
            break
        
        type_map = {'1': 'checkpoints', '2': 'loras', '3': 'others'}
        if choice in type_map:
            process_downloads(type_map[choice])
        else:
            print("Invalid choice. Please try again.")