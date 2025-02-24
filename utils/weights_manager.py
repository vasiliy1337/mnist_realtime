import pickle
from datetime import datetime
import os
import re

path_to_mode_cache = "./model_cache/"

def save_model(weights, accuracy:int, name:str='model_weights'):
    """
    Saves weights using pickle (I know that this is dumb)
    :param weights: weights of model
    :param accuracy: accuracy for filename
    :param name: name of model
    :return: None
    """
    timestamp = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
    filename = f"{path_to_mode_cache}checkpoint_{accuracy}_{name}_{timestamp}.plk"
    with open(filename, 'wb') as f:
        pickle.dump(weights, f)
    print(f"Model saved to {filename}")

def load_model(filename:str='model_weights'):
    """
    Loads weights from giving filename
    :param filename: name of file
    :return: weights or None
    """
    filename = f"{path_to_mode_cache}{filename}"
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return None
    with open(filename, 'rb') as f:
        weights = pickle.load(f)
    return weights

def get_checkpoint_with_best_accuracy() -> str:
    """
    Returns filename of checkpoint with the best accuracy
    :return: str
    """
    res = ""
    pattern = r'checkpoint_([\d\.]+)_.*plk'
    only_files = [f for f in os.listdir(path_to_mode_cache) if os.path.isfile(os.path.join(path_to_mode_cache, f))]
    _max = -1
    for filename in only_files:
        match = re.search(pattern, filename)
        if match and float(match.group(1)) > _max:
            _max = float(match.group(1))
            res = filename
    return res