document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.delete-student');

    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
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
                    location.reload(); // načte stránku
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