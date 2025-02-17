function createEmptyForm() {
    const form = document.createElement('form');
    form.className = 'exam-form';

    form.innerHTML = `
        <div class="student-line-admin-grid-8 specification-for-grid-8 margin-top-10">
            <div class="form-group">
                <input type="text" name="evidence_number" id="evidence_number" placeholder="E. č." required>
            </div>
            <div class="form-group">
                <input type="text" name="first_name" id="first_name" placeholder="Jméno" required>
            </div>
            <div class="form-group">
                <input type="text" name="last_name" id="last_name" placeholder="Příjmení" required>
            </div>
            <div class="form-group">
                <input type="date" name="birth_date" id="birth_date" required>
            </div>
            <div class="form-group">
                <input type="text" name="adress" id="adress" placeholder="Adrasa" required>
            </div>
            <div class="form-group">
                <input type="text" name="drivers_license" id="drivers_license" placeholder="Číslo ř. p.">
            </div>
            <div class="form-group">
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
                <select name="type-of-teaching" id="type-of-teaching">
                    <option value="základní-výuka-a-výcvik" selected>Základní výuka a výcvik</option>
                    <option value="sdružená-výuka-a-výcvik">Sdružená výuka a výcvik</option>
                    <option value="rozšiřující-výuka-a-výcvik">Rozšiřující výuka a výcvik</option>
                    <option value="výuka-a-výcvik-podle-individuálního-plánu">Výuka a výcvik podle individuálního plánu</option>
                    <option value="doplňující-výuka-a-výcvik">Doplňující výuka a výcvik</option>
                </select>
            </div>
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

function validateForms() {
    let isValid = true;
    let errorMessage = '';

    // Ověření hlavního formuláře
    const mainForm = document.querySelector('#for-form form');
    if (!mainForm.querySelector('#adress').value.trim()) {
        isValid = false;
        errorMessage += 'Pole "Adresa" musí být vyplněno.\n';
    }
    if (!mainForm.querySelector('#start-of-training').value.trim()) {
        isValid = false;
        errorMessage += 'Pole "Datum zahájení výcviku" musí být vyplněno.\n';
    }
    if (mainForm.querySelector('#vehicle-list').selectedOptions.length === 0) {
        isValid = false;
        errorMessage += 'Musíte vybrat alespoň jedno vozidlo.\n';
    }

    // Ověření každého formuláře studenta
    const examForms = document.querySelectorAll('.exam-form');
    examForms.forEach((form, index) => {
        if (!form.querySelector('#evidence_number').value.trim()) {
            isValid = false;
            errorMessage += `Řádek ${index + 1}: Pole "E. č." musí být vyplněno.\n`;
        }
        if (!form.querySelector('#first_name').value.trim()) {
            isValid = false;
            errorMessage += `Řádek ${index + 1}: Pole "Jméno" musí být vyplněno.\n`;
        }
        if (!form.querySelector('#last_name').value.trim()) {
            isValid = false;
            errorMessage += `Řádek ${index + 1}: Pole "Příjmení" musí být vyplněno.\n`;
        }
        if (!form.querySelector('#birth_date').value.trim()) {
            isValid = false;
            errorMessage += `Řádek ${index + 1}: Pole "Datum narození" musí být vyplněno.\n`;
        }
        if (!form.querySelector('#adress').value.trim()) {
            isValid = false;
            errorMessage += `Řádek ${index + 1}: Pole "Adresa" musí být vyplněno.\n`;
        }
        // Číslo řidičského průkazu není povinné
    });

    if (!isValid) {
        alert(errorMessage);
    }
    return isValid;
}

document.getElementById('submit-forms').addEventListener('click', function(event) {
    event.preventDefault();

    if (!validateForms()) {
        return;
    }

    // Pokračování v odeslání formuláře pouze, pokud je validace úspěšná
    const mainForm = document.querySelector('#for-form form');
    const mainFormData = {
        adress: mainForm.querySelector('#adress').value,
        start_of_training: mainForm.querySelector('#start-of-training').value,
        vehicle_list: Array.from(mainForm.querySelector('#vehicle-list').selectedOptions).map(option => option.value),
    };

    const examForms = document.querySelectorAll('.exam-form');
    const students = Array.from(examForms).map(form => ({
        evidence_number: form.querySelector('#evidence_number').value,
        first_name: form.querySelector('#first_name').value,
        last_name: form.querySelector('#last_name').value,
        birth_date: form.querySelector('#birth_date').value,
        adress: form.querySelector('#adress').value,
        drivers_license: form.querySelector('#drivers_license').value || null,
        license_category: form.querySelector('#license_category').value,
        type_of_teaching: form.querySelector('#type-of-teaching').value
    }));

    const payload = {
        main_form: mainFormData,
        students: students
    };

    fetch('/api/sign_up', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            if (data.duplicate_evidence_numbers) {
                alert(`Chyba: Některá evidenční čísla již existují v systému:\n\n${data.duplicate_evidence_numbers.join(", ")}`);
            } else {
                alert(`Chyba: ${data.error}`);
            }
        } else {
            alert("Data byla úspěšně odeslána!");
            window.location.href = '/calendar';
        }
    })
    .catch((error) => {
        console.error('Chyba:', error);
        alert("Došlo k chybě při odesílání formuláře.");
    });
});
