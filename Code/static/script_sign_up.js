function createEmptyForm() {
    const form = document.createElement('form');
    form.className = 'exam-form';

    form.innerHTML = `
        <div class="form-group">
            <input type="text" name="evidence_number" id="evidence_number" placeholder="Evidenční číslo" required>
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
            <input type="text" name="drivers_license" id="drivers_license" placeholder="Číslo řidičského průkazu-Nepoviné">
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
    `;
    return form;
}

document.getElementById('add-form').addEventListener('click', function() {
    const formList = document.getElementById('form-list');

    const newForm = createEmptyForm();
    formList.appendChild(newForm); 
});

document.getElementById('submit-forms').addEventListener('click', function(event) {
    event.preventDefault(); // Zabráníme defaultnímu odeslání formuláře

    // Shromáždění údajů z hlavního formuláře
    const mainForm = document.querySelector('.term-container form');
    const mainFormData = {
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
