function createEmptyForm() {
    const form = document.createElement('form');
    form.className = 'exam-form';

    form.innerHTML = `
        <div class="form-group">
            <label for="evidence_number">Evidenční číslo:</label>
            <input type="text" name="evidence_number" id="evidence_number" placeholder="E.č" required>
        </div>
        <div class="form-group">
            <label for="first_name">Jméno:</label>
            <input type="text" name="first_name" id="first_name" placeholder="Jméno" required>
        </div>
        <div class="form-group">
            <label for="last_name">Příjmení:</label>
            <input type="text" name="last_name" id="last_name" placeholder="Příjmení" required>
        </div>
        <div class="form-group">
            <label for="birth_date">Datum narození:</label>
            <input type="date" name="birth_date" id="birth_date" required>
        </div>
        <div class="form-group">
            <label for="license_category">Kategorie řidičského průkazu:</label>
            <select name="license_category" id="license_category">
                <option value="A">A</option>
                <option value="B" selected>B</option>
                <option value="C">C</option>
                <option value="C+E">C+E</option>
                <option value="D">D</option>
                <option value="D+E">D+E</option>
            </select>
        </div>
        <div class="form-group">
            <label for="exam_type">Typ zkoušky:</label>
            <select name="exam_type" id="exam_type">
                <option value="řádná_zkouška">Řádná zkouška</option>
                <option value="opravná_jízda_test">Opravná zkouška (jízda+test)</option>
                <option value="opravná_jízda">Opravná zkouška (jízda)</option>
                <option value="opravná_technika">Opravná zkouška (technika)</option>
                <option value="opravná_technika_jízda">Opravná zkouška (technika+jízda)</option>
                <option value="profesní_způsobilost">Profesní způsobilost</option>
            </select>
        </div>
    `;

    return form;
}

document.getElementById('add-form').addEventListener('click', function() {
    const formList = document.getElementById('form-list');
    const newForm = createEmptyForm();
    formList.appendChild(newForm);
});

document.getElementById('remove-form').addEventListener('click', function() {
    const formList = document.getElementById('form-list');
    if (formList.children.length > 1) {
        formList.removeChild(formList.lastElementChild);
    }
});

document.getElementById('submit-forms').addEventListener('click', function() {
    const forms = document.querySelectorAll('.exam-form');
    const data = Array.from(forms).map(form => {
        const formData = new FormData(form);
        return Object.fromEntries(formData.entries());
    });

    fetch('/add_drivers', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (response.ok) {
            location.reload();
        } else {
            alert('Nastala chyba při odesílání formulářů.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Nastala chyba při odesílání formulářů.');
    });
});
