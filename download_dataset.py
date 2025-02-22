import kagglehub
import shutil
import os

custom_path = "./dataset"

# Default download path
default_path = kagglehub.dataset_download("hojjatk/mnist-dataset", force_download=True)

if os.path.exists(custom_path):
    shutil.rmtree(custom_path)

# Move files to custom path
shutil.move(default_path, custom_path)
