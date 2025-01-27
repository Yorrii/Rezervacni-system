function successStudent(id) {
    // Definujte endpoint pro schválení studenta
    const endpoint = `/api/success`;
    const potvrzeni = confirm('Jste si jistý? Akce smaže studenta ze systému.')
    // Proveďte API volání pomocí fetch
    if(potvrzeni){
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
            window.location.reload()
        })
        .catch(error => {
            // Zpracujte chybu
            console.error('Error:', error);
        });
    }
}

function rejectStudent(id) {
    // Definujte endpoint pro odmítnutí studenta
    const endpoint = `/api/reject`;

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
        window.location.reload()
    })
    .catch(error => {
        // Zpracujte chybu
        console.error('Error:', error);
    });
}

async function makeDocument(nazev, datum) {
    const name = nazev;
    const date = datum;

    try {
        const response = await fetch('/api/generate_doc', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name, date })
        });
        
        if (response.ok) {
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${name}_${date}_document.docx`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } else {
            alert("Došlo k chybě při generování dokumentu.");
        }
    } catch (error) {
        console.error("Chyba:", error);
    }
}