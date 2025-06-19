def get_files():
    folder_path = os.getenv('INPUT_DIR')

    entries = os.listdir(folder_path)

    files = [f for f in entries if os.path.isfile(os.path.join(folder_path, f))]

    return files