import zipfile
import os

class FileZipper:

    def list_files(self, path: str) -> list:
        files_list = []
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, path)
                files_list.append(rel_path.replace("\\", "/"))
        return files_list

    def create_zip(self, path: str, zip_path: str) -> str:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            base_dir = os.path.basename(path)
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)
                    zip_file.write(file_path, os.path.join(base_dir, rel_path))
        return zip_path
