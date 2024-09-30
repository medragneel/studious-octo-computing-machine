import os


def create_folder_structure():
    # Define folder structure
    folders = {
        "src": "src",
        "music": "music",
        "fonts": "fonts",
        "dist": "dist",
    }

    # Create folders if they don't exist
    for folder_path in folders.values():
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder_path}")
        else:
            print(f"Folder already exists: {folder_path}")


if __name__ == "__main__":
    create_folder_structure()
