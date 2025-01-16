const monthNames = ["Leden", "Únor", "Březen", "Duben", "Květen", "Červen", "Červenec", "Srpen", "Září", "Říjen", "Listopad", "Prosinec"];
let currentDate = new Date();

function renderCalendar(date, events = []) {
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
        const dateString = `${year}-${String(month + 1).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
        const dayDiv = document.createElement("div");
        
        // Nastavení ID pro každý den
        dayDiv.id = `day-${dateString}`;
        dayDiv.classList.add('day')
        dayDiv.textContent = i;
        // Kontrola, zda tento den je v seznamu termínů
        const event = events.find(event => event.date === dateString);
        if (event) {
            // Nastavení barvy podle hodnoty 'ac_flag'
            if (event.ac_flag === 'R') {
                dayDiv.style.backgroundColor =  "#bcf5f1"; // Modrá pro proběhlé termíny      
            } else if (event.max_ridicu-event.zapsani_zaci <= 0) {
                dayDiv.style.backgroundColor = "#f03329"; // Červená pro plné termíny
            } else {
                dayDiv.style.backgroundColor = "#17f00c"; // Zelená pro aktivní termíny
            }
            dayDiv.classList.add("event-day"); // Přidání třídy pro další styly
                // Přidání event listeneru pro přesměrování
            dayDiv.addEventListener("click", () => {
                window.location.href = `/term/${event.id}`;
            });
        } else {
            dayDiv.id = `${dateString}`; // Nastavení unikátního ID pro den

            // Přidání event listeneru pro dny bez událostí
            dayDiv.addEventListener("click", () => {
                // Zavření menu, pokud je zobrazené pro jiný den
                const selectedDayElement = document.querySelector(".selected-day");
                if (selectedDayElement) {
                    selectedDayElement.style.backgroundColor = ""; // Vrácení původní barvy
                    selectedDayElement.classList.remove("selected-day");
                }

                // Zvýraznění aktuálně vybraného dne
                dayDiv.style.backgroundColor = "#FFD700"; // Nová barva při výběru
                dayDiv.classList.add("selected-day");

                // Zobrazení menu a uložení ID vybraného dne
                calendar_menu.style.display = "flex";
                selectedDayId = dayDiv.id;

                console.log(`Vybraný den: ${selectedDayId}`); // Pro debugování
            });
        }
        daysContainer.appendChild(dayDiv);
    }
}

// Funkce, která se spustí po kliknutí na tlačítko
document.getElementById('create_term_btn').addEventListener('click', function() {
    // Získáme hodnotu z inputu s id 'pocet_mist'
    let pocetMist = document.getElementById('pocet_mist').value;

    if(!pocetMist || pocetMist <= 0){
        alert('Zadali jste neplatné počet studentů.');
        return;
    }

    // Vytvoříme objekt s daty, které budeme odesílat
    let data = {
        dayId: selectedDayId,
        pocetMist: pocetMist
    };

    // Odeslání POST requestu na endpoint /create_termin
    fetch('/api/create_term', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data) // Převod objektu na JSON
    })
    .then(response => response.json()) // Odpověď z endpointu
    .then(data => {
        // Zpracování odpovědi
        console.log('Úspěch:', data);
    })
    .catch((error) => {
        console.error('Chyba:', error);
        alert('Nastala chyba')
    });
})

function fetchAndRenderCalendar() {
    fetch('/calendar_api')
        .then(response => response.json())
        .then(data => {
            
            renderCalendar(currentDate, data);
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

/* metoda pro skrytí menu a odbarvení vybraného dne */
document.addEventListener("click", (event) => {
    const calendar_menu = document.getElementById("calendar_menu");
    const selectedDayElement = document.querySelector(".selected-day");

    // Zkontrolujeme, zda bylo kliknuto mimo calendar_menu
    if (!calendar_menu.contains(event.target) && !event.target.classList.contains("selected-day")) {
        if (calendar_menu.style.display === "flex") {
            calendar_menu.style.display = "none"; // Zavření menu
        }

        // Vrácení původní barvy vybraného dne
        if (selectedDayElement) {
            selectedDayElement.style.backgroundColor = ""; // Reset barvy
            selectedDayElement.classList.remove("selected-day");
        }
    }
});

// Prvotní načtení kalendáře
fetchAndRenderCalendar();
