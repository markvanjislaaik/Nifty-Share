import zipfile
import os

class FileZipper:
    def create_zip(self, path: str, zip_path: str) -> str:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            base_dir = os.path.basename(path)
            for root, dirs, files in os.walk(path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, path)
                    zip_file.write(file_path, os.path.join(base_dir, rel_path))
        return zip_path

    def remove(self, zip_path: str) -> None:
        os.remove(zip_path)

if __name__ == '__main__':
    
    zipper = FileZipper()
    input_path = "C:/Users/user1/Desktop/HolidayPhotos"
    result = zipper.create_zip(input_path, f"{os.path.basename(input_path)}.zip")
    print(result)