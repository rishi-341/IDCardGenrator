import shutil
import os

imgs = [
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K510.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K511.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K320.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K321.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K322.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K323.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K324.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K863.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K864.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K865.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\K866.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\L913.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\L509.JPG",
    r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\L510.JPG"
]

# Source file to copy
photos_dir = r"C:\\Users\\ASUS\\Desktop\\git\\py\\ID_Card\\photos\\sample.png"

# Copy the sample image to all img paths
for img_path in imgs:
    shutil.copy(photos_dir, img_path)
