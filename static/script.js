const socket = io.connect('http://localhost:5000');

const grid = document.getElementById('grid');
const resetBtn = document.getElementById('resetBtn');
const probContainer = document.getElementById('probabilities');
const weightContainer = document.getElementById('weights-b1');

const GRID_SIZE = 28;

let isDrawing = false;
let doDiagonals = false;

function clearGrid() {
    for (const cell of grid.children) {
        cell.dataset.intensity = '0';
        cell.style.backgroundColor = '';
    }
}

function getCell(row, col) {
    return grid.children[row * GRID_SIZE + col];
}

function setCell(row, col, intensity) {
    const cell = getCell(row, col)
    if (intensity !== 0){
        cell.dataset.intensity = intensity.toString();
        cell.style.backgroundColor = `rgba(0, 0, 0, ${intensity})`;
    }
}

function updateCell(row, col, intensity) {
    const cell = getCell(row, col)
    const currentIntensity = parseFloat(cell.dataset.intensity);
    const newIntensity = Math.max(currentIntensity, intensity);
    cell.dataset.intensity = newIntensity.toString();
    cell.style.backgroundColor = `rgba(0, 0, 0, ${newIntensity})`;
}

function drawOnCell(row, col) {
    updateCell(row, col, 1);
    const adjacentCells = [
        [row - 1, col], [row + 1, col],
        [row, col - 1], [row, col + 1]
    ];
    adjacentCells.forEach(([r, c]) => {
        if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
            updateCell(r, c, 0.5);
        }
    });
    if (doDiagonals) {
        const diagonalCells = [
            [row - 1, col - 1], [row + 1, col + 1],
            [row + 1, col - 1], [row - 1, col + 1]
        ];
        diagonalCells.forEach(([r, c]) => {
            if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
                updateCell(r, c, 0.2);
            }
        });
    }
    

    sendGridData();
}

function handleCellInteraction(e) {
    const index = Array.from(grid.children).indexOf(e.target);
    const row = Math.floor(index / GRID_SIZE);
    const col = index % GRID_SIZE;
    drawOnCell(row, col);
}

function sendGridData() {
    const gridData = Array.from(grid.children).map(cell => parseFloat(cell.dataset.intensity));
    socket.emit('user_interaction', { input: gridData });
}

function on_label_press(label) {
    socket.emit('get_rand_image', { label: label });
}

function updateProbabilities(probabilities) {
    var maxIndex = -1
    if (!probabilities.every(item => item === 0)) {
        const maxProb = Math.max(...probabilities);
        maxIndex = probabilities.indexOf(maxProb);
    }

    probabilities.forEach((prob, index) => {
        const bar = document.getElementById(`prob-bar-${index}`);
        const number = bar.previousElementSibling;

        const intensity = Math.round((1 - prob) * 255);
        bar.style.backgroundColor = `rgb(${intensity}, ${intensity}, ${intensity})`;

        if (index === maxIndex) {
            number.style.color = 'white';
            number.style.backgroundColor = `rgba(95, 191, 255, ${prob})`;
        } else {
            number.style.color = `#000000`;
            number.style.backgroundColor = `#ffffff`;
        }
    });
}

function updateWeights(weights) {
    weights.forEach((weight, index) => {
        const bar = document.getElementById(`weight-box-${index}`);
        const intensity = Math.round((1-weight) * 255);
        bar.style.backgroundColor = `rgb(${intensity}, ${intensity}, ${intensity})`;
    });
}

resetBtn.addEventListener('click', () => {
    clearGrid();
    updateProbabilities(new Array(10).fill(0));
    updateWeights(new Array(128).fill(0));
});

grid.addEventListener('mousedown', (e) => {
    e.preventDefault();
    isDrawing = true;
});

let lastHoveredCell = null;
grid.addEventListener('mousemove', (e) => {
    if (isDrawing) {
        if (e.target !== lastHoveredCell) {
            lastHoveredCell = e.target;
            if (e.target.classList.contains('cell') && getComputedStyle(e.target).backgroundColor !== `rgb(0, 0, 0)`) {
                handleCellInteraction(e);
            }
        }
    }
});

grid.addEventListener('mouseup', () => {
    isDrawing = false;
});

grid.addEventListener('mouseleave', () => {
    isDrawing = false;
});

socket.on('update_data', (data) => {
     if (data.data && data.data.length === GRID_SIZE * GRID_SIZE) {
         clearGrid();
         data.data.forEach((value, index) => {
             const x = Math.floor(index / GRID_SIZE);
             const y = index % GRID_SIZE;
             setCell(x, y, value);
         });
     }
    if (data.probabilities && data.probabilities.length === 10) {
        updateProbabilities(data.probabilities);
    }
    if (data.weights && data.weights.length === 128) {
        updateWeights(data.weights);
    }
});
