const API_BASE = "https://schedulforge.onrender.com"; // Updated to deployed backend

const fileInput = document.getElementById("file");
const sheetSelect = document.getElementById("sheet_choice");
const groupSelect = document.getElementById("tutorial_group");
const form = document.getElementById("uploadForm");
const statusDiv = document.getElementById("status");
const timetableDiv = document.getElementById("timetable");

function setStatus(msg, spinner = false) {
    statusDiv.innerHTML = spinner ? `<span class="spinner"></span> ${msg}` : msg;
}

// When file is selected
fileInput.addEventListener("change", async () => {
    timetableDiv.innerHTML = "";
    groupSelect.innerHTML = "";
    setStatus("Loading sheets...", true);

    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const res = await fetch(`${API_BASE}/list_sheets/`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        sheetSelect.innerHTML = data.sheets.map(sheet =>
            `<option value="${sheet.index}">${sheet.name}</option>`
        ).join("");
        setStatus("Sheets loaded. Select a sheet.");
    } catch (err) {
        console.error(err);
        setStatus("Failed to load sheets.");
    }
});

// When sheet is selected
sheetSelect.addEventListener("change", async () => {
    timetableDiv.innerHTML = "";
    setStatus("Loading tutorial groups...", true);

    const file = fileInput.files[0];
    const sheetIndex = sheetSelect.value;
    if (!file || !sheetIndex) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("sheet_choice", sheetIndex);

    try {
        const res = await fetch(`${API_BASE}/list_tutorial_groups/`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        groupSelect.innerHTML = data.tutorial_groups.map(group =>
            `<option value="${group}">${group}</option>`
        ).join("");
        setStatus("Tutorial groups loaded.");
    } catch (err) {
        console.error(err);
        setStatus("Failed to load tutorial groups.");
    }
});

// On form submission
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    timetableDiv.innerHTML = "";
    setStatus("Generating timetable...", true);

    const file = fileInput.files[0];
    const sheetIndex = sheetSelect.value;
    const group = groupSelect.value;
    if (!file || !sheetIndex || !group) {
        setStatus("Missing input.");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("sheet_choice", sheetIndex);
    formData.append("tutorial_group", group);

    try {
        const res = await fetch(`${API_BASE}/timetable/`, {
            method: "POST",
            body: formData
        });
        const data = await res.json();
        renderTable(data);
        setStatus(`Timetable for "${data.tutorial_group}" from "${data.sheet_name}"`);
    } catch (err) {
        console.error(err);
        setStatus("Failed to generate timetable.");
    }
});

function renderTable(data) {
    const { time_slots, timetable } = data;
    let html = `<table><thead><tr><th>Time</th>`;
    for (let day of Object.keys(timetable)) {
        html += `<th>${day}</th>`;
    }
    html += `</tr></thead><tbody>`;

    for (let time of time_slots) {
        html += `<tr><td>${time}</td>`;
        for (let day of Object.keys(timetable)) {
            const code = timetable[day][time] || "";
            let cls = "";
            if (code.includes("L")) cls = "lecture";
            else if (code.includes("T")) cls = "tutorial";
            else if (code.includes("P")) cls = "practical";
            html += `<td class="${cls}">${code}</td>`;
        }
        html += `</tr>`;
    }

    html += `</tbody></table>`;
    timetableDiv.innerHTML = html;
}

// Toggle dark mode
function toggleMode() {
    document.body.classList.toggle("dark");
    const btn = document.getElementById("modeBtn");
    btn.textContent = document.body.classList.contains("dark") ? "Light Mode" : "Dark Mode";
}

// Download timetable as PDF
function downloadPDF() {
    if (!timetableDiv.innerHTML.trim()) {
        alert("No timetable to download.");
        return;
    }
    const opt = {
        margin: 0.5,
        filename: 'timetable.pdf',
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'landscape' }
    };
    html2pdf().set(opt).from(timetableDiv).save();
}

// Clear the form and reset
function clearForm() {
    fileInput.value = "";
    sheetSelect.innerHTML = "";
    groupSelect.innerHTML = "";
    timetableDiv.innerHTML = "";
    statusDiv.innerHTML = "";
}
