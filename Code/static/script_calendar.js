const monthNames = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"];
let currentDate = new Date();

function renderCalendar(date, eventDates = []) {
    const daysContainer = document.getElementById("days");
    const monthYear = document.getElementById("monthYear");
    daysContainer.innerHTML = "";

    const month = date.getMonth();
    const year = date.getFullYear();
    const firstDayOfMonth = new Date(year, month, 1).getDay();
    const lastDateOfMonth = new Date(year, month + 1, 0).getDate();

    monthYear.textContent = `${monthNames[month]} ${year}`;

    const daysInWeek = 7;
    const paddingDays = (firstDayOfMonth + 6) % 7; // Adjusting for starting on Monday

    for (let i = 0; i < paddingDays; i++) {
        const emptyDiv = document.createElement("div");
        daysContainer.appendChild(emptyDiv);
    }

    for (let i = 1; i <= lastDateOfMonth; i++) {
        const dayDiv = document.createElement("div");
        dayDiv.textContent = i;

        // Kontrola, zda tento den je v seznamu termínů
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        if (eventDates.includes(dateString)) {
            dayDiv.style.backgroundColor = "#FFD700"; // Změna barvy pozadí pro dané termíny
        }

        daysContainer.appendChild(dayDiv);
    }
}

function fetchAndRenderCalendar() {
    fetch('/calendar_api')
        .then(response => response.json())
        .then(data => {
            const eventDates = data.map(event => event.date);
            renderCalendar(currentDate, eventDates);
        });
}

document.getElementById("prevMonth").addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() - 1);
    fetchAndRenderCalendar();
});

document.getElementById("nextMonth").addEventListener("click", () => {
    currentDate.setMonth(currentDate.getMonth() + 1);
    fetchAndRenderCalendar();
});

// Prvotní načtení kalendáře
fetchAndRenderCalendar();
