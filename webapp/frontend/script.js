document.getElementById('generate-button').addEventListener('click', async () => {
    const genre = document.getElementById('genre-select').value;
    const seedNotes = document.getElementById('seed-input').value;
    const temperature = parseFloat(document.getElementById('temperature-slider').value);
    const generationLength = parseInt(document.getElementById('generation-length-input').value);

    // Basic validation
    if (!seedNotes) {
        alert('Please enter some seed notes.');
        return;
    }
    if (isNaN(generationLength) || generationLength < 50 || generationLength > 2000) {
        alert('Please enter a valid generation length between 50 and 2000.');
        return;
    }

    try {
        const response = await fetch('http://localhost:8000/generate_solo', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ genre: genre, seed_notes: seedNotes, temperature: temperature, generation_length: generationLength }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const blob = await response.blob();
        const contentDisposition = response.headers.get('Content-Disposition');
        console.log('Content-Disposition header:', contentDisposition); // DEBUG
        let filename = 'generated_solo.mid';
        if (contentDisposition && contentDisposition.indexOf('attachment') !== -1) {
            const filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
            const matches = filenameRegex.exec(contentDisposition);
            if (matches != null && matches[1]) {
                filename = decodeURIComponent(matches[1].replace(/\+/g, ' '));
                if (filename.startsWith("'") || filename.startsWith("\"")) {
                    filename = filename.slice(1, -1);
                }
            }
        }
        console.log('Extracted filename:', filename); // DEBUG

        const url = URL.createObjectURL(blob);

        const downloadLink = document.getElementById('download-link');
        downloadLink.href = url;
        downloadLink.download = filename;
        downloadLink.style.display = 'block';
        downloadLink.textContent = `Download ${filename}`;

    } catch (error) {
        console.error('Error generating solo:', error);
        alert('Failed to generate solo. Check console for details.');
    }
});

// Update temperature value display
document.getElementById('temperature-slider').addEventListener('input', (event) => {
    document.getElementById('temperature-value').textContent = event.target.value;
});
