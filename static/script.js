const socket = io.connect('http://localhost:5000');

const grid = document.getElementById('grid');
const resetBtn = document.getElementById('resetBtn');
const probContainer = document.getElementById('probabilities');
const weightContainer = document.getElementById('weights-b1');

const GRID_SIZE = 28;
const CELL_SIZE = 10;

let isDrawing = false;

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

// Draw a cell
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
    sendGridData();
}

function handleCellInteraction(e) {
    if (e.target.classList.contains('cell')) {
        const index = Array.from(grid.children).indexOf(e.target);
        const row = Math.floor(index / GRID_SIZE);
        const col = index % GRID_SIZE;
        drawOnCell(row, col);
    }
}

// Send grid data to the server
function sendGridData() {
    const gridData = Array.from(grid.children).map(cell => parseFloat(cell.dataset.intensity));
    socket.emit('user_interaction', { input: gridData });
}

function on_label_press(label) {
    socket.emit('get_rand_image', { label: label });
}

// Update probabilities
function updateProbabilities(probabilities) {
    const maxProb = Math.max(...probabilities);
    const maxIndex = probabilities.indexOf(maxProb);

    probabilities.forEach((prob, index) => {
        const bar = document.getElementById(`prob-bar-${index}`);
        const number = bar.previousElementSibling;

        const intensity = Math.round((1 - prob) * 255);
        bar.style.backgroundColor = `rgb(${intensity}, ${intensity}, ${intensity})`;

        if (index === maxIndex) {
            number.style.color = 'white';
            number.style.backgroundColor = `rgba(0, 255, 0, ${prob})`;
            number.style.border = `2px solid rgba(0, 255, 0, ${prob})`;
        } else {
            const textIntensity = prob > 0.9 ? 255 : 0;
            number.style.color = `rgb(${textIntensity}, ${textIntensity}, ${textIntensity})`;
            number.style.backgroundColor = `rgba(${255 - textIntensity}, ${255 - textIntensity}, ${255 - textIntensity}, ${prob})`;
            number.style.border = `2px solid rgba(${255 - textIntensity}, ${255 - textIntensity}, ${255 - textIntensity}, ${prob})`;
        }
    });
}

// Update weights
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
    handleCellInteraction(e);
});

grid.addEventListener('mousemove', (e) => {
    if (isDrawing) {
        handleCellInteraction(e);
    }
});

grid.addEventListener('mouseup', () => {
    isDrawing = false;
    sendGridData();
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
