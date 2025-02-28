import os

PREDEFINED_TYPES = {
    '1': 'flux',
    '2': 'illustrious',
    '3': 'pony',
    '4': 'sd.15',
    '5': 'sd_1.4',
    '6': 'sdxl',
    '7': 'all',
    '8': 'custom'
}

def get_log_file_path(type_name):
    """Get the path for a specific type's log file"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, f"{type_name}.txt")

def get_lora_folder_path(type_name):
    """Get the path for a specific type's lora folder"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "loras", type_name)

def check_duplicates(log_file_path, folder_path):
    # Read the log file and extract filenames
    log_filenames = set()
    encodings = ['utf-8', 'utf-8-sig', 'cp1252', 'iso-8859-1']
    
    # Try different encodings
    for encoding in encodings:
        try:
            with open(log_file_path, 'r', encoding=encoding) as log_file:
                for line in log_file:
                    # Extract just the filename from the full path
                    filename = os.path.basename(line.strip())
                    log_filenames.add(filename)
            break  # If successful, break the loop
        except UnicodeDecodeError:
            if encoding == encodings[-1]:  # If this was the last encoding to try
                print(f"Error: Unable to read log file {log_file_path} with any supported encoding")
                return
            continue
        except FileNotFoundError:
            print(f"Error: Log file not found at {log_file_path}")
            return
    
    # Check if folder exists
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found at {folder_path}")
        return
    
    # Get all files from the specified folder
    folder_files = set()
    duplicate_paths = []  # Store full paths of duplicates
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) and filename in log_filenames:
            folder_files.add(filename)
            duplicate_paths.append(file_path)
    
    # Find duplicates
    duplicates = log_filenames.intersection(folder_files)
    
    # Print results
    if duplicates:
        print("\nFound duplicate files:")
        for i, path in enumerate(duplicate_paths, 1):
            print(f"{i}. {path}")
        print(f"\nTotal duplicates found: {len(duplicates)}")
        
        # Ask user if they want to delete the files
        response = input("\nDo you want to delete these duplicate files? (yes/no): ").lower()
        if response == 'yes':
            confirm = input("Are you sure? This cannot be undone! (yes/no): ").lower()
            if confirm == 'yes':
                deleted_count = 0
                for path in duplicate_paths:
                    try:
                        os.remove(path)
                        print(f"Deleted: {path}")
                        deleted_count += 1
                    except Exception as e:
                        print(f"Error deleting {path}: {e}")
                print(f"\nSuccessfully deleted {deleted_count} files")
            else:
                print("Deletion cancelled")
        else:
            print("No files were deleted")
    else:
        print("No duplicates found.")

def process_type(type_name):
    log_file_path = get_log_file_path(type_name)
    folder_path = get_lora_folder_path(type_name)
    
    print(f"\nProcessing {type_name.upper()} models...")
    print("-" * 30)
    
    if not os.path.exists(log_file_path):
        print(f"Error: Log file not found for {type_name}")
        return
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder not found for {type_name}")
        return
        
    check_duplicates(log_file_path, folder_path)

def main():
    print("Duplicate File Checker and Remover")
    print("=" * 30)
    print("\nAvailable options:")
    for key, value in PREDEFINED_TYPES.items():
        print(f"{key}. {value}")
    
    choice = input("\nSelect option (1-8): ").strip()
    
    if choice == '8':  # Custom paths
        log_file_path = input("Enter the path to your log file: ").strip('"')
        folder_path = input("Enter the path to the folder to check: ").strip('"')
        check_duplicates(log_file_path, folder_path)
    elif choice in PREDEFINED_TYPES:
        if choice == '7':  # Process all types
            for type_name in list(PREDEFINED_TYPES.values())[:-2]:  # Exclude 'all' and 'custom'
                process_type(type_name)
        else:
            process_type(PREDEFINED_TYPES[choice])
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()