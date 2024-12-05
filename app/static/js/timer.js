let timers = {};

function startTimer(taskId) {
    fetch(`/task/${taskId}/start_timer`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const taskCard = document.querySelector(`#task-${taskId}`).closest('.task-card');
                taskCard.classList.add('timer-running');
                updateTimerDisplay(taskId);
                timers[taskId] = setInterval(() => updateTimerDisplay(taskId), 1000);
            }
        });
}

function stopTimer(taskId) {
    fetch(`/task/${taskId}/stop_timer`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const taskCard = document.querySelector(`#task-${taskId}`).closest('.task-card');
                taskCard.classList.remove('timer-running');
                clearInterval(timers[taskId]);
                delete timers[taskId];
            }
        });
}

function updateTimerDisplay(taskId) {
    fetch(`/task/${taskId}/get_time`)
        .then(response => response.json())
        .then(data => {
            document.querySelector(`#timer-${taskId}`).textContent = data.time;
        });
}

function showAddTimeModal(taskId) {
    // Implementation for add time modal
} 