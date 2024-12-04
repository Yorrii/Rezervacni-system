function createEmptyForm() {
    const form = document.createElement('form');
    form.className = 'exam-form';

    form.innerHTML = `
        <div class="student-line-admin-grid-8 margin-top-10">
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
                    <option value="T">T</option>
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

document.getElementById('submit-forms').addEventListener('click', function(event) {
    event.preventDefault(); // Zabráníme defaultnímu odeslání formuláře

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
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    })
    .then(response => response.json())
    .then(data => {
        console.log('Úspěch:', data);
        window.location.href = '/calendar';
    })
    .catch((error) => {
        console.error('Chyba:', error);
        window.alert(error);
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

