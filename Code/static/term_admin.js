function enrollStudent(zakId) {
    const studentDiv = document.getElementById(`zak_${zakId}`);

    
    const timeStart = document.getElementById(`time-zak_${zakId}`).value;
    const commissar = document.getElementById(`commissar-for-zak_${zakId}`).value;
    
    const data = {
        id: zakId, 
        time_start: timeStart,
        commissar: commissar
    };
    
    fetch('/enroll', {
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
            console.error('Failed to enroll student');
        }
    })
    .catch(error => {
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