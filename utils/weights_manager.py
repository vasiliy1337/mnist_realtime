import pickle
from datetime import datetime
from os import listdir
from os.path import isfile, join
import re

path_to_mode_cache = "./model_cache/"
# Save model weights to a file
def save_model(weights, accuracy:int, name:str='model_weights'):
    timestamp = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    filename = f"{path_to_mode_cache}checkpoint_{accuracy}_{name}_{timestamp}.plk"
    with open(filename, 'wb') as f:
        pickle.dump(weights, f)
    print(f"Model saved to {filename}")

# Load model weights from a file
def load_model(filename:str='model_weights'):
    filename = f"{path_to_mode_cache}{filename}"
    with open(filename, 'rb') as f:
        weights = pickle.load(f)
    print("loaded")
    return weights

def get_checkpoint_with_best_accuracy() -> str:
    res = ""
    pattern = r'checkpoint_([\d\.]+)_.*plk'
    only_files = [f for f in listdir(path_to_mode_cache) if isfile(join(path_to_mode_cache, f))]
    _max = -1
    for filename in only_files:
        match = re.search(pattern, filename)
        if match and float(match.group(1)) > _max:
            _max = float(match.group(1))
            res = filename
    return res