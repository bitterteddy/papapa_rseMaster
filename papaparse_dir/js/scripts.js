function showFieldsByType() {
    const taskType = document.getElementById('task-type').value;
    document.getElementById('css-fields').classList.toggle('d-none', taskType !== 'parse');
    document.getElementById('regex-fields').classList.toggle('d-none', taskType !== 'regex_parse');
}

function addCSSField() {
    const container = document.getElementById('css-parameters-container');
    const field = `
        <div class="parameter-group mb-3">
            <div class="row g-2">
                <div class="col-md-4">
                    <label class="form-label">Name:</label>
                    <input type="text" name="name" class="form-control" placeholder="Name">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Selector:</label>
                    <input type="text" name="selector" class="form-control" placeholder="CSS Selector">
                </div>
                <div class="col-md-4">
                    <label class="form-label">Attribute:</label>
                    <select name="attribute" class="form-select">
                        <option value="text">Text</option>
                        <option value="href">Href</option>
                        <option value="src">Src</option>
                        <option value="alt">Alt</option>
                        <option value="title">Title</option>
                        <option value="id">ID</option>
                        <option value="class">Class</option>
                        <option value="">None</option>
                    </select>
                </div>
                <div class="col-md-2 mt-2">
                    <label class="form-label">Multiple:</label>
                    <input type="checkbox" name="multiple" class="form-check-input ms-2">
                </div>
            </div>
        </div>
    `;
    container.insertAdjacentHTML('beforeend', field);
}

function addRegexPattern() {
    const container = document.getElementById('regex-patterns');
    const field = `
        <div class="input-group mb-2">
            <input type="text" class="form-control" placeholder="Enter regex pattern" name="regex_pattern">
        </div>
    `;
    container.insertAdjacentHTML('beforeend', field);
}

async function submitTask() {
    const taskType = document.getElementById("task-type").value;
    const urls = document.getElementById("urls").value.split("\n").filter(url => url.trim());
    let parameters = {};

    if (taskType === "parse") {
        const container_selector = document.getElementById("container-selector").value
        const fields = document.querySelectorAll("#css-parameters-container .parameter-group");
        const elements = Array.from(fields).map(field => ({
            name: field.querySelector("input[name='name']").value,
            selector: field.querySelector("input[name='selector']").value,
            attribute: field.querySelector("select[name='attribute']").value,
            multiple: field.querySelector("input[name='multiple']").checked
        }));
        parameters.parse_parameters = { 
            container_selector: container_selector,
            elements 
        };
    } else if (taskType === "regex_parse") {
        const regexFields = document.querySelectorAll("#regex-fields input[name='regex_pattern']");
        const regexPatterns = Array.from(regexFields).map(input => input.value);
        parameters.regex_patterns = regexPatterns;
    }

    const response = await fetch("/tasks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            task_type: taskType,
            parameters: { urls, ...parameters }
        })
    });

    const result = await response.json();
    alert(result.message);
    // loadTasks();
}

async function loadTasks() {
    try {
        const response = await fetch('/tasks');  
        const tasks = await response.json();  

        const tasksList = document.getElementById('tasks-list');
        tasksList.innerHTML = '';  

        tasks.forEach(task => {
            const li = document.createElement('li');
            li.innerHTML = `
                <span>Task ${task.id}: ${task.status}</span>
                <div class="task-actions">
                    <button class="start" onclick="startTask(${task.id})">Start</button>
                    <button class="stop" onclick="stopTask(${task.id})">Stop</button>
                    <button class="view" onclick="viewTaskDetails(${task.id})">View Details</button>
                    <button class="view" onclick="viewTaskResult(${task.id})">View Result</button>
                </div>
            `;
            tasksList.appendChild(li);  // Добавляем задачу в список
        });
    } catch (error) {
        console.error('Error fetching tasks:', error);
    }
}

window.onload = loadTasks;

// async function loadTasks() {
//     const response = await fetch("/tasks");
//     const tasks = await response.json();
//     const taskList = document.getElementById("task-list");
//     taskList.innerHTML = "";
//     for (const [taskId, task] of Object.entries(tasks)) {
//         const li = document.createElement("li");
//         li.textContent = `Task ${taskId}: ${task.status}`;
//         taskList.appendChild(li);
//     }
// }

// async function loadTasks() {
//     const response = await fetch('/tasks');
//     const tasks = await response.json();

//     const tasksList = document.getElementById('tasks-list');
//     tasksList.innerHTML = '';

//     for (const taskId in tasks) {
//         const task = tasks[taskId];
//         const li = document.createElement('li');
//         li.innerHTML = `
//             Task ${task.task_id}: ${task.status} 
//             <button onclick="viewTaskDetails('${task.task_id}')">View Details</button>
//         `;
//         tasksList.appendChild(li);
//     }
// }

// async function viewTaskDetails(taskId) {
//     const response = await fetch(`/tasks/${taskId}`);
//     if (response.ok) {
//         const task = await response.json();
//         const taskDetails = document.getElementById('task-details');
//         const content = document.getElementById('task-details-content');
        
//         content.textContent = JSON.stringify(task, null, 2);
        
//         taskDetails.style.display = 'block';
//     } else {
//         alert('Task not found!');
//     }
// }

// document.getElementById('close-details').addEventListener('click', () => {
//     document.getElementById('task-details').style.display = 'none';
// });

loadTasks();