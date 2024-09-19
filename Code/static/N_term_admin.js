function createEmptyForm() {
    const form = document.createElement('form');
    form.className = 'exam-form';

    form.innerHTML = `
        <div class="form-group">
            <input type="text" name="evidence_number" id="evidence_number" placeholder="E.č" required>
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
            <select name="exam_type" id="exam_type">
                <option value="Řádná_zkouška" selected>Řádná zkouška</option>
                <option value="Opravná_zkouška-jízda+test">Opravná zkouška (jízda+test)</option>
                <option value="Opravná_zkouška-jízda">Opravná zkouška (jízda)</option>
                <option value="Opravná_zkouška-technika">Opravná zkouška (technika)</option>
                <option value="Opravná_zkouška-technika+jízda">Opravná zkouška (technika+jízda)</option>
                <option value="Profesní_způsobilost-test">Profesní způsobilost</option>
            </select>
        </div>
    `;

    return form;
}

const maxForms = document.getElementById('volna_mista').value;

document.getElementById('add-form').addEventListener('click', function() {
    const formList = document.getElementById('form-list');
    const currentForms = formList.getElementsByTagName('form').length;

    if (currentForms < maxForms) {
        const newForm = createEmptyForm();
        formList.appendChild(newForm);
    } else {
        alert(`Nelze přidat více formulářů. Je pouze ${maxForms} volných míst.`);
    }
});

document.getElementById('remove-form').addEventListener('click', function() {
    const formList = document.getElementById('form-list');
    if (formList.children.length > 1) {
        formList.removeChild(formList.lastElementChild);
    }
});

/* Nutnost předělat. Metoda volá api endpoint, který by schodil stránku */
/*document.getElementById('submit-forms').addEventListener('click', function() {
    const forms = document.querySelectorAll('.exam-form');
    const data = Array.from(forms).map(form => {
        const formData = new FormData(form);
        return Object.fromEntries(formData.entries());
    });
    console.log(data)
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
});*/

document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-student');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            alert('clicked');
            const zakId = this.getAttribute('data-zakId');
            const terminId = this.getAttribute('data-terminId');
            const studentDiv = document.getElementById(`zak_${zakId}`);

            fetch('/api/delete_student', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ zak_id: zakId, termin_id: terminId })
            })
            .then(response => {
                if (response.ok) {
                    // Úspěšné odstranění
                    studentDiv.remove();
                } else {
                    console.error('Chyba při mazání studenta');
                }
            })
            .catch(error => {
                console.error('Chyba při spojení s API:', error);
            });
        });
    });
});