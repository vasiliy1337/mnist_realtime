import numpy as np

class NNModel:
    def __init__(self, wl):
        self.weights_loader = wl
        self.weights = None

    def load_weights(self, weights_path):
        self.weights = self.weights_loader.load_model(weights_path)

    def set_weights(self, weights):
        self.weights = weights

    def get_weights(self):
        return self.weights

    def get_normalized_weights(self, layer = 'b1', min_val=0, max_val=1):
        data = np.array(self.weights[layer])
        scaled = ((data - np.min(data)) / (np.max(data) - np.min(data))) * (max_val - min_val) + min_val
        return scaled

    # --- Activation Functions ---
    def _relu(self, Z):
        return np.maximum(0, Z)

    def _softmax(self, Z):
        exp_Z = np.exp(Z - np.max(Z, axis=0, keepdims=True))
        return exp_Z / np.sum(exp_Z, axis=0, keepdims=True)

    # --- Forward Propagation ---
    def _forward_propagation(self, X):
        if self.weights is None:
            raise ValueError("Weights have not been initialized. Load or set weights before prediction.")
        Z1 = np.dot(self.weights['W1'], X) + self.weights['b1']
        A1 = self._relu(Z1)
        Z2 = np.dot(self.weights['W2'], A1) + self.weights['b2']
        A2 = self._softmax(Z2)
        return Z1, A1, Z2, A2

    # --- Predict ---
    def predict(self, X):
        _, _, _, A2 = self._forward_propagation(X)
        return np.argmax(A2, axis=0)

    # --- Predict Single Image ---
    def predict_single_image(self, image):
        image = image.reshape(-1, 1)
        _, _, _, A2 = self._forward_propagation(image)
        return np.argmax(A2, axis=0)[0]

    def predict_single_image_with_probs(self, image):
        image = image.reshape(-1, 1)
        _, _, _, A2 = self._forward_propagation(image)
        return self._get_normalized_dict(A2)

    def predict_single_image_with_probs_and_weights(self, image):
        image = image.reshape(-1, 1)
        _, A1, _, A2 = self._forward_propagation(image)
        return [self._get_normalized_arr(A2), self._get_normalized_arr(A1)]

    def _get_normalized_dict(self, arr, min_val=0, max_val=1):
        data = np.array(arr)
        scaled = ((data - np.min(data)) / (np.max(data) - np.min(data))) * (max_val - min_val) + min_val
        return {i: round(num[0], 4) for i, num in enumerate(scaled.tolist())}

    def _get_normalized_arr(self, arr, min_val=0, max_val=1):
        data = np.array(arr)
        scaled = ((data - np.min(data)) / (np.max(data) - np.min(data))) * (max_val - min_val) + min_val
        return [round(num[0], 4) for num in scaled.tolist()]

    def _get_normalized_dict_v2(self, arr, min_val=0, max_val=1):
        arr = np.array(arr)

        arr_min = np.min(arr)
        arr_max = np.max(arr)

        if arr_max == arr_min:
            normalized = np.full_like(arr, (min_val + max_val) / 2)
        else:
            normalized = ((arr - arr_min) / (arr_max - arr_min)) * (max_val - min_val) + min_val
        return {i: round(prob[0], 4) for i, prob in enumerate(normalized.tolist())}

    # --- Train Neural Network ---

    def _relu_derivative(self, Z):
        return Z > 0

    # --- Loss Function ---
    def _compute_loss(self, Y, A2):
        m = Y.shape[0]
        log_probs = -np.log(A2[Y, range(m)])
        return np.sum(log_probs) / m

    # --- Initialize Parameters ---
    def _initialize_parameters(self, input_size, hidden_size, output_size):
        weights = {
            'W1': np.random.randn(hidden_size, input_size) * 0.01,
            'b1': np.zeros((hidden_size, 1)),
            'W2': np.random.randn(output_size, hidden_size) * 0.01,
            'b2': np.zeros((output_size, 1)),
        }
        return weights

    # --- Update Parameters ---
    def _update_parameters(self, weights, grads, learning_rate):
        weights['W1'] -= learning_rate * grads['dW1']
        weights['b1'] -= learning_rate * grads['db1']
        weights['W2'] -= learning_rate * grads['dW2']
        weights['b2'] -= learning_rate * grads['db2']
        return weights

    # --- Backward Propagation ---
    def _backward_propagation(self, X, Y, weights, Z1, A1, A2):
        m = X.shape[1]
        dZ2 = A2
        dZ2[Y, range(m)] -= 1
        dZ2 /= m

        dW2 = np.dot(dZ2, A1.T)
        db2 = np.sum(dZ2, axis=1, keepdims=True)
        dA1 = np.dot(weights['W2'].T, dZ2)
        dZ1 = dA1 * self._relu_derivative(Z1)

        dW1 = np.dot(dZ1, X.T)
        db1 = np.sum(dZ1, axis=1, keepdims=True)

        grads = {'dW1': dW1, 'db1': db1, 'dW2': dW2, 'db2': db2}
        return grads

    def train_nn(self, X, Y, input_size, hidden_size, output_size, epochs, learning_rate, from_checkpoint=False,
                 checkpoint_path=""):

        if from_checkpoint:
            checkpoint_path = checkpoint_path or self.weights_loader.get_checkpoint_with_best_accuracy()
            if not checkpoint_path:
                print("Checkpoints not found.")
                self.weights = self._initialize_parameters(input_size, hidden_size, output_size)
            else:
                print(f"Loading from '{checkpoint_path}'")
                self.weights = self.weights_loader.load_model(checkpoint_path)
        else:
            self.weights = self._initialize_parameters(input_size, hidden_size, output_size)

        for epoch in range(epochs):
            Z1, A1, Z2, A2 = self._forward_propagation(X)
            loss = self._compute_loss(Y, A2)
            grads = self._backward_propagation(X, Y, self.weights, Z1, A1, A2)
            self.weights = self._update_parameters(self.weights, grads, learning_rate)
            if epoch % 10 == 0:
                print(f"Epoch {epoch}, Loss: {loss}")
        return self.weights