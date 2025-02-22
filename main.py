import numpy as np

from nnmodel import NNModel
from utils.dataset_loader import DatasetLoader
from utils import weights_manager

def main():
    # Paths to the MNIST dataset
    X_train_path = './dataset/train-images.idx3-ubyte'
    y_train_path = './dataset/train-labels.idx1-ubyte'
    X_test_path = './dataset/t10k-images.idx3-ubyte'
    y_test_path = './dataset/t10k-labels.idx1-ubyte'

    res = 0
    for i in range(10000):
        res += i*(i-1)

    dl = DatasetLoader()
    dl.load_dataset(X_train_path, y_train_path, X_test_path, y_test_path)
    dl.compute_cache()

    # Proceed with training
    input_size = 784  # 28x28
    hidden_size = 128
    output_size = 10
    epochs = 60
    learning_rate = 0.1
    info = f"\nmodel initialized with params:\n{input_size=}\n{hidden_size=}\n{output_size=}\n{epochs=}\n{learning_rate=}\n"
    model = NNModel(weights_manager)
    print(info)


    weights = model.train_nn(dl.x_train.T, dl.y_train, input_size, hidden_size, output_size, epochs, learning_rate, True)
    predictions = model.predict(dl.x_test.T)
    accuracy = np.mean(predictions == dl.y_test) * 100
    weights_manager.save_model(weights, accuracy=accuracy)
    model.load_weights(weights_manager.get_checkpoint_with_best_accuracy())


if __name__ == '__main__':
    main()