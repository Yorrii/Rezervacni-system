function successStudent(id) {
    // Definujte endpoint pro schválení studenta
    const endpoint = `/api/student/success/${id}`;

    // Proveďte API volání pomocí fetch
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // Případně přidejte tělo žádosti (pokud je potřeba)
         body: JSON.stringify({ 'id': id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Zpracujte úspěšnou odpověď
        console.log('Success:', data);
    })
    .catch(error => {
        // Zpracujte chybu
        console.error('Error:', error);
    });
}

function rejectStudent(id) {
    // Definujte endpoint pro odmítnutí studenta
    const endpoint = `/api/student/reject/${id}`;

    // Proveďte API volání pomocí fetch
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        // Případně přidejte tělo žádosti (pokud je potřeba)
         body: JSON.stringify({ 'id': id })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        // Zpracujte úspěšnou odpověď
        console.log('Rejected:', data);
    })
    .catch(error => {
        // Zpracujte chybu
        console.error('Error:', error);
    });
}
