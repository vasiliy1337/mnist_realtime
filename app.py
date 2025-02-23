from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS

import numpy as np

from nnmodel import NNModel
from utils.dataset_loader import DatasetLoader
from utils import weights_manager

app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_key_noone_knows_about'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# load model
model = NNModel(weights_manager)
# You can use a custom checkpoint; by default, the best checkpoint is used.
# checkpoint_path = weights_manager.get_checkpoint_with_best_accuracy()
# if checkpoint_path == "":
#     raise FileNotFoundError("Looks like you didn't have any checkpoints for model. Run 'train_model.py'")
model.init_weights(from_checkpoint=True)

# load dataset
dl = DatasetLoader()
X_train_path = './dataset/train-images.idx3-ubyte'
y_train_path = './dataset/train-labels.idx1-ubyte'
X_test_path = './dataset/t10k-images.idx3-ubyte'
y_test_path = './dataset/t10k-labels.idx1-ubyte'
res = dl.load_dataset(X_train_path, y_train_path, X_test_path, y_test_path)
dl.compute_cache()

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('user_interaction')
def handle_input(data):
    input_data = np.array(data['input']).reshape(28, 28)
    res = model.predict_single_image_with_probs_and_weights(input_data)
    weights = res[1]
    output = res[0]
    emit('update_data', {
        'weights': weights,
        'probabilities': output
    })

@socketio.on('get_rand_image')
def handle_get_rand(data):
    label_str = data.get("label")  # Use .get() to avoid KeyError

    try:
        label = int(label_str)
    except (ValueError, TypeError):
        emit('error', {'error': 'Label must be an integer between 0 and 9'})
        return

    if label < 0 or label > 9:
        emit('error', {'error': 'Probably label not in [0,9] (just my guess, ok?)'})
        return

    board = dl.get_rand(label)
    output, weights = model.predict_single_image_with_probs_and_weights(board)

    emit('update_data', {
        'data': list(board),
        'weights': weights,
        'probabilities': output
    })


if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
