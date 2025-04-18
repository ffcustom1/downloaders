import requests
import re
import os
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(SCRIPT_DIR, "urls.txt")
DOWNLOAD_LOG = os.path.join(SCRIPT_DIR, "processed_urls.log")

# Output files for different model types
OUTPUT_FILES = {
    "Checkpoint": os.path.join(SCRIPT_DIR, "checkpoints.txt"),
    "LORA": os.path.join(SCRIPT_DIR, "loras.txt"),
    "unknown": os.path.join(SCRIPT_DIR, "none.txt")
}

def extract_ids(url):
    """Extract model ID and version ID from Civitai URL"""
    model_match = re.search(r'models/(\d+)', url)
    version_match = re.search(r'modelVersionId=(\d+)', url)
    
    model_id = model_match.group(1) if model_match else None
    version_id = version_match.group(1) if version_match else None
    
    return model_id, version_id

def load_downloaded_urls():
    """Load already processed URLs from processed_urls.logs"""
    if os.path.exists(DOWNLOAD_LOG):
        with open(DOWNLOAD_LOG, 'r') as f:
            return set(line.strip() for line in f)
    return set()

def save_download_url(url):
    """Save original URL to processed_urls.logs"""
    with open(DOWNLOAD_LOG, 'a') as f:
        f.write(f"{url}\n")

def save_url_by_type(url, model_type, original_url):
    """Save URL to appropriate file based on model type"""
    output_file = OUTPUT_FILES.get(model_type, OUTPUT_FILES["unknown"])
    with open(output_file, 'a') as f:
        f.write(f"{url}\n")
    save_download_url(original_url)  # Save original URL instead of download URL

def process_version_api(version_id, original_url):
    """Process model version API endpoint"""
    api_url = f"https://civitai.com/api/v1/model-versions/{version_id}"
    download_url = f"https://civitai.com/api/download/models/{version_id}"
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Get model type from API response
        model_type = data.get("model", {}).get("type", "unknown")
        save_url_by_type(download_url, model_type, original_url)  # Pass original_url
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error accessing Version API: {e}")
        return False

def process_civitai_url(url, processed_urls):
    """Process a single Civitai URL and return success status"""
    if url in processed_urls:
        print(f"Skipping already processed URL: {url}")
        return True
        
    try:
        model_id, version_id = extract_ids(url)
        
        if version_id:
            # Direct version ID URL format
            return process_version_api(version_id, url)
        elif model_id:
            # Base model URL format - need to get latest version ID
            api_url = f"https://civitai.com/api/v1/models/{model_id}"
            response = requests.get(api_url)
            response.raise_for_status()
            data = response.json()
            
            if "modelVersions" in data and len(data["modelVersions"]) > 0:
                # Get the first version (index 0)
                version_data = data["modelVersions"][0]
                version_id = version_data.get("id")
                model_type = data.get("type", "unknown")
                
                if version_id:
                    download_url = f"https://civitai.com/api/download/models/{version_id}"
                    save_url_by_type(download_url, model_type, url)  # Pass original URL
                    return True
                    
            print(f"No valid version ID found for: {url}")
            return False
        else:
            print(f"Invalid URL format: {url}")
            return False
            
    except Exception as e:
        print(f"Error processing URL {url}: {str(e)}")
        return False
    
def process_links_file():
    """Process URLs from urls.txt file"""
    if not os.path.exists(INPUT_FILE):
        print("urls.txt not found!")
        return
    
    processed_urls = load_downloaded_urls()
    
    with open(INPUT_FILE, "r") as f:
        urls = [url.strip() for url in f.readlines() if url.strip()]
    
    remaining_urls = []
    processed_count = 0
    failed_count = 0
    
    # Create progress bar
    pbar = tqdm(urls, desc="Processing URLs", unit="url")
    
    for url in pbar:
        # Update progress bar description with current URL
        pbar.set_description(f"Processing: {url[:30]}...")
        
        if process_civitai_url(url, processed_urls):
            processed_count += 1
            pbar.set_postfix(processed=processed_count, failed=failed_count)
        else:
            failed_count += 1
            remaining_urls.append(url)
            pbar.set_postfix(processed=processed_count, failed=failed_count)
    
    # Close progress bar
    pbar.close()
    
    # Update urls.txt with remaining URLs
    with open(INPUT_FILE, "w") as f:
        f.writelines(f"{url}\n" for url in remaining_urls)
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed_count} URLs")
    print(f"Failed to process: {failed_count} URLs")
    print(f"Remaining URLs in urls.txt: {len(remaining_urls)}")

if __name__ == "__main__":
    process_links_file()