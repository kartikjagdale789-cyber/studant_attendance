# scripts/create_zip.py
import os
import zipfile
import shutil

source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
output_zip = os.path.join(r"C:\Users\Asus\Downloads", "Student_Performance_Attendance_Face_Verification_System.zip")
inside_zip = os.path.join(source_dir, "Student_Performance_Attendance_Face_Verification_System.zip")

# Remove existing zip files first
for z in [output_zip, inside_zip]:
    if os.path.exists(z):
        try:
            os.remove(z)
        except Exception:
            pass

exclude_dirs = {'.pytest_cache', '__pycache__', '.git', '.vscode', '.idea', 'data/TrainingImage'}
exclude_exts = {'.pyc', '.zip'}

with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(source_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            ext = os.path.splitext(file)[1].lower()
            if ext in exclude_exts:
                continue
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, source_dir)
            archive_name = os.path.join("Student_Performance_System", rel_path)
            zipf.write(full_path, archive_name)

shutil.copyfile(output_zip, inside_zip)
print(f"ZIP created successfully at {output_zip} and {inside_zip}")
