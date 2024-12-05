// script.js

// Log a message to the console when the script is loaded
console.log("JavaScript file loaded successfully.");

// Example function to show an alert when a button is clicked
// function showAlert() {
//     alert("Button clicked!");
// }

// // Add event listeners to buttons if needed
// document.addEventListener("DOMContentLoaded", function() {
//     const buttons = document.querySelectorAll("button");
//     buttons.forEach(button => {
//         button.addEventListener("click", showAlert);
//     });
// });

let activeTimers = {};

function toggleTimer(taskId) {
    const button = document.querySelector(`[data-task-id="${taskId}"]`);
    const timerDisplay = document.getElementById(`timer-${taskId}`);
    
    // Log the current button state
    console.log('Current button text:', button.textContent.trim());

    if (button.textContent.trim() === 'Start') {
        console.log('Starting timer for task:', taskId);
        // Start timer
        fetch(`/start_timer/${taskId}`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Start timer response:', data);
            if (data.status === 'success') {
                button.textContent = 'Stop';
                startTimerDisplay(taskId);
            }
        })
        .catch(error => {
            console.error('Error starting timer:', error);
        });
    } else {
        console.log('Stopping timer for task:', taskId);
        // Stop timer
        fetch(`/stop_timer/${taskId}`, { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Stop timer response:', data);
            if (data.status === 'success') {
                button.textContent = 'Start';
                stopTimerDisplay(taskId);
            }
        })
        .catch(error => {
            console.error('Error stopping timer:', error);
        });
    }
}

function startTimerDisplay(taskId) {
    let seconds = 0;
    const display = document.querySelector(`#timer-${taskId} .timer-count`);
    
    // If the timer is already running, calculate the elapsed time
    if (display.dataset.startTime) {
        const startTime = new Date(display.dataset.startTime);
        const now = new Date();
        seconds = Math.floor((now - startTime) / 1000);
    } else {
        // Set the start time if not already set
        display.dataset.startTime = new Date().toISOString();
    }

    activeTimers[taskId] = setInterval(() => {
        seconds++;
        display.textContent = formatTime(seconds);
    }, 1000);
}

function stopTimerDisplay(taskId) {
    if (activeTimers[taskId]) {
        clearInterval(activeTimers[taskId]);
        delete activeTimers[taskId];
    }
    const display = document.querySelector(`#timer-${taskId} .timer-count`);
    delete display.dataset.startTime; // Clear the start time
}

function formatTime(seconds) {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    return `${pad(h)}:${pad(m)}:${pad(s)}`;
}

function pad(num) {
    return num.toString().padStart(2, '0');
}

// Add this function to initialize the button states when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get all timer buttons
    const timerButtons = document.querySelectorAll('.timer-btn');
    
    // Initialize each button's state based on the task's timer_start value
    timerButtons.forEach(button => {
        const taskId = button.getAttribute('data-task-id');
        // You can add a data attribute to the button to store the initial timer state
        const isTimerRunning = button.getAttribute('data-timer-running') === 'true';
        button.textContent = isTimerRunning ? 'Stop' : 'Start';
        console.log(`Initialized button for task ${taskId} with state: ${button.textContent}`);
    });
});

function toggleTimeHistory(taskId) {
    const historyDiv = document.getElementById(`time-history-${taskId}`);
    const button = historyDiv.previousElementSibling;
    
    if (historyDiv.style.display === 'none') {
        historyDiv.style.display = 'block';
        button.textContent = 'Hide Time History';
    } else {
        historyDiv.style.display = 'none';
        button.textContent = 'Show Time History';
    }
}