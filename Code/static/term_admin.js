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