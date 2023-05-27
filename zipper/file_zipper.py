import zipfile
import os


class FileZipper:
    def create_zip(self, files: list, zip_path: str) -> None:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for file in files:
                if os.path.exists(file):
                    zip_file.write(file, os.path.basename(file))
                else:
                    print(f"File '{file}' does not exist.")


if __name__ == '__main__':
    file_zipper = FileZipper()
    file_zipper.create_zip(['file1.txt', 'file2.png'], 'archive.zip')