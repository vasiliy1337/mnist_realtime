const socket = io.connect('http://localhost:5000');

const grid = document.getElementById('grid');
const resetBtn = document.getElementById('resetBtn');
const probContainer = document.getElementById('probabilities');
const weightContainer = document.getElementById('weights-b1');

const GRID_SIZE = 28;
const CELL_SIZE = 10;

let isDrawing = false;

function createGrid() {
    grid.innerHTML = '';
    for (let i = 0; i < GRID_SIZE * GRID_SIZE; i++) {
        const cell = document.createElement('div');
        cell.className = 'cell';
        cell.dataset.intensity = '0';
        grid.appendChild(cell);
    }
}

function clearGrid() {
    for (const cell of grid.children) {
        cell.dataset.intensity = '0';
        cell.style.backgroundColor = ''
    }
}

function getCell(row, col) {
    return grid.children[row * GRID_SIZE + col];
}

function setCell(row, col, intensity) {
    const cell = getCell(row, col)
    if (intensity !== 0){
        console.log(intensity)
        cell.dataset.intensity = intensity.toString();
        cell.style.backgroundColor = `rgba(0, 0, 0, ${intensity})`;
    }
}

// Draw a cell
function updateCell(cell, intensity) {
    const currentIntensity = parseFloat(cell.dataset.intensity);
    const newIntensity = Math.max(currentIntensity, intensity);
    cell.dataset.intensity = newIntensity.toString();
    cell.style.backgroundColor = `rgba(0, 0, 0, ${newIntensity})`;
}
function drawOnCell(row, col) {
    const cell = getCell(row, col);
    updateCell(cell, 1);
    const adjacentCells = [
        [row - 1, col], [row + 1, col],
        [row, col - 1], [row, col + 1]
    ];
    adjacentCells.forEach(([r, c]) => {
        if (r >= 0 && r < GRID_SIZE && c >= 0 && c < GRID_SIZE) {
            updateCell(getCell(r, c), 0.5);
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
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

function createProbabilityBoxes() {
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 10; i++) {
        const boxContainer = document.createElement('div');
        boxContainer.className = 'prob-box';
        boxContainer.style.cursor = 'pointer';
        boxContainer.onclick = function() {
            on_label_press(i)
        };

        const number = document.createElement('span');
        number.className = 'prob-number';
        number.textContent = i;

        const bar = document.createElement('div');
        bar.className = 'prob-bar';
        bar.id = `prob-bar-${i}`;

        boxContainer.append(number, bar);
        fragment.appendChild(boxContainer);
    }
    probContainer.innerHTML = '';
    probContainer.appendChild(fragment);
}

function on_label_press(label) {
    socket.emit('get_rand_image', { label: label });
}

// Generate weight bars
function createWeightsBoxes() {
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 128; i++) {
        const boxContainer = document.createElement('div');
        boxContainer.className = 'weight-box';
        boxContainer.id = `weight-box-${i}`;
        fragment.appendChild(boxContainer);
    }
    weightContainer.innerHTML = '';
    weightContainer.appendChild(fragment);
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

// Reset button
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

// Socket Events
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
    //if (data.weights && data.weights.length === 128) {
        updateWeights(data.weights);
    //}
});

// Initialize
createGrid();
createProbabilityBoxes();
createWeightsBoxes();
