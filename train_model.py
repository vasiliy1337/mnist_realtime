import numpy as np
from nnmodel import NNModel
from utils.dataset_loader import DatasetLoader
from utils import weights_manager

def train():
    # Paths to the MNIST dataset
    X_train_path = './dataset/train-images.idx3-ubyte'
    y_train_path = './dataset/train-labels.idx1-ubyte'
    X_test_path = './dataset/t10k-images.idx3-ubyte'
    y_test_path = './dataset/t10k-labels.idx1-ubyte'

    # initializing dataset loader
    dl = DatasetLoader()
    dl.load_dataset(X_train_path, y_train_path, X_test_path, y_test_path)

    # Proceed with training
    input_size = 784  # 28x28
    hidden_size = 128
    output_size = 10
    epochs = 500
    learning_rate = 0.1
    info = f"\nmodel initialized with params:\n{input_size=}\n{hidden_size=}\n{output_size=}\n{epochs=}\n{learning_rate=}\n"
    print(info)

    model = NNModel(weights_manager)
    weights = model.train_nn(dl.x_train.T, dl.y_train, input_size, hidden_size, output_size, epochs, learning_rate,
                             False) # change to True to continue training
    predictions = model.predict(dl.x_test.T)
    accuracy = np.mean(predictions == dl.y_test) * 100
    print(f"{accuracy=}")
    weights_manager.save_model(weights, accuracy=accuracy)


if __name__ == '__main__':
    train()