function createEmptyForm() {
    const form = document.createElement('form');
    form.className = 'exam-form';

    form.innerHTML = `
        <div class="grid-for-9-sign_up specification-for-grid-8 margin-top-10">
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
                <input type="text" name="adress" id="adress" placeholder="Adresa" required>
            </div>
            <div class="form-group">
                <input type="text" name="drivers_license" id="drivers_license" placeholder="Číslo ř. p.">
            </div>
            <div class="form-group">
                <input class="input-box3" type="text" name="license_category" id="license_category" placeholder="A, B, B+E" required title="Zadej skupiny ŘP oddělené čárkou (např. B, B+E)">
            </div>
            <div class="form-group">
                <input type="date" name="first_try" id="first_try" placeholder="První pokus">
            </div>
            <div class="form-group">
                <select name="type-of-teaching" id="type-of-teaching">
                    <option value="základní-výuka-a-výcvik" selected>Základní výuka a výcvik</option>
                    <option value="opakovaná-výuka">Opakovaná výuka</option>
                    <option value="opakovaný-výcvik">Opakovaný výcvik</option>
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
        if (!form.querySelector('#license_category').value.trim()) {
            isValid = false;
            errorMessage += `Řádek ${index + 1}: Pole "Druh řidičského průkazu" musí být vyplněno.\n`;
        }
        // Číslo řidičského průkazu není povinné
    });

    if (!isValid) {
        alert(errorMessage);
    }
    return isValid;
}

document.getElementById('submit-forms').addEventListener('click', function(event) {
    event.preventDefault(); // Zabráníme defaultnímu odeslání formuláře

    if (!validateForms()) {
        return;
    }

    // Shromáždění údajů z hlavního formuláře
    const mainForm = document.querySelector('#for-form form');
    const mainFormData = {
        driving_school_id: document.querySelector('#driving-school').value,
        adress: mainForm.querySelector('#adress').value,
        start_of_training: mainForm.querySelector('#start-of-training').value,
        vehicle_list: Array.from(mainForm.querySelector('#vehicle-list').selectedOptions).map(option => option.value),
    };

    // Shromáždění údajů ze všech formulářů žáků
    const examForms = document.querySelectorAll('.exam-form');
    const students = Array.from(examForms).map(form => {
        return {
            evidence_number: form.querySelector('#evidence_number').value,
            first_name: form.querySelector('#first_name').value,
            last_name: form.querySelector('#last_name').value,
            birth_date: form.querySelector('#birth_date').value,
            adress: form.querySelector('#adress').value,
            drivers_license: form.querySelector('#drivers_license').value || null,
            license_category: form.querySelector('#license_category').value,
            first_try: form.querySelector('#first_try').value || null,
            type_of_teaching: form.querySelector('#type-of-teaching').value
        };
    });

    // Vytvoření objektu pro odeslání na backend
    const payload = {
        main_form: mainFormData,
        students: students
    };

    // Odeslání dat na backend pomocí fetch
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

document.addEventListener('DOMContentLoaded', function () {
    // Iniciace Select2 pro druhý select
    $('#vehicle-list').select2();

    // Event listener pro první select
    document.getElementById('driving-school').addEventListener('change', function () {
        const selectedValue = this.value;

        // Pokud není vybrána žádná hodnota, vyprázdníme druhý select
        if (!selectedValue) {
            $('#vehicle-list').empty();
            return;
        }

        // API request
        fetch(`/api/get_vehicles?value=${selectedValue}`)
            .then(response => response.json())
            .then(data => {
                // Vyprázdnit stávající možnosti ve druhém selectu
                $('#vehicle-list').empty();

                // Naplnit druhý select novými daty
                data.forEach(vozidlo => {
                    const optionText = `${vozidlo.znacka} ${vozidlo.model} ${vozidlo.RZ}`;
                    const newOption = new Option(optionText, vozidlo.id, false, false);
                    $('#vehicle-list').append(newOption).trigger('change');
                });
            })
            .catch(error => {
                console.error('Error fetching options:', error);
            });
    });
});

