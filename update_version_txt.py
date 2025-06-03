import re

def get_local_version(main_py_path):
    with open(main_py_path, "r", encoding="utf-8") as f:
        content = f.read()
    # Ищем строку вида LOCAL_VERSION = "1.1.7"
    match = re.search(r'LOCAL_VERSION\s*=\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return None

def update_version_txt(version_txt_path, new_version):
    with open(version_txt_path, "w", encoding="utf-8") as f:
        f.write(new_version + "\n")
    print(f"Updated {version_txt_path} to version {new_version}")

if __name__ == "__main__":
    main_py = "main.py"          # путь к main.py (можно изменить)
    version_txt = "version.txt"  # путь к version.txt (можно изменить)

    version = get_local_version(main_py)
    if version:
        update_version_txt(version_txt, version)
    else:
        print("LOCAL_VERSION not found in main.py")



#для обновления версии python update_version_txt.py
