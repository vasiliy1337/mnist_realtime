from idx2numpy import convert_from_file
from collections import defaultdict
from numpy.random import choice
from numpy import divide, float32, ndarray, int64

class DatasetLoader:
    def __init__(self):
        self.x_train = None # numpy.ndarray
        self.y_train = None # numpy.ndarray
        self.x_test = None  # numpy.ndarray
        self.y_test = None  # numpy.ndarray
        self.cache = defaultdict(list)
        self.cached_train = False

    def load_dataset(self, x_train_path: str, y_train_path: str, x_test_path: str, y_test_path: str) -> bool:
        """
        Loads dataset from given path.
        :param x_train_path: Path to train images in idx3 format
        :param y_train_path: Path to train labels in idx1 format
        :param x_test_path: Path to test images in idx3 format
        :param y_test_path: Path to test labels in idx1 format
        :return: True if done else false
        """
        try:
            self.x_train = convert_from_file(x_train_path)
            self.y_train = convert_from_file(y_train_path)
            self.x_test = convert_from_file(x_test_path)
            self.y_test = convert_from_file(y_test_path)
        except FileNotFoundError as e:
            print(e)
            return False
        # Flatten the images
        self.x_train = self.x_train.reshape(-1, 28 * 28)
        self.x_test = self.x_test.reshape(-1, 28 * 28)
        # Normalize the data
        self.x_train = self.x_train / 255.0
        self.x_test = self.x_test / 255.0
        return True

    def compute_cache(self, train: bool = False):
        """
        Allows to get random image by label in constant time O(1)
        :param train: If 'False' use test part of dataset, otherwise use train part
        :return: None
        """
        data = self.y_test
        self.cached_train = False
        self.cache.clear()
        if train:
            self.cached_train = True
            data = self.y_train

        for i in range(len(data)):
            self.cache[data[i]].append(i)


    def get_rand(self, label: int) -> ndarray | None:
        """
        Get random image from dataset for given label
        :param label: int, 0 <= label <= 9
        :return: ndarray if valid label, None otherwise
        """
        if label not in self.cache:
            return None
        idx = choice(self.cache[label])

        return self.x_train[idx] if self.cached_train else self.x_test[idx]
