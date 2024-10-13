document.addEventListener('DOMContentLoaded', function() {
    const styleForm = document.getElementById('styleForm');
    const trendAnalysisBtn = document.getElementById('trendAnalysis');
    const styleQuizBtn = document.getElementById('styleQuiz');
    const imageUploadForm = document.getElementById('imageUploadForm');

    styleForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const occasion = document.getElementById('occasion').value;
        const preferredColor = document.getElementById('preferredColor').value;
        const bodyType = document.getElementById('bodyType').value;

        try {
            const response = await fetch('/api/style_recommendation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ occasion, preferred_color: preferredColor, body_type: bodyType }),
            });
            const data = await response.json();
            document.getElementById('result').innerHTML = `<p>${data.message}</p>`;
        } catch (error) {
            console.error('Error:', error);
        }
    });

    trendAnalysisBtn.addEventListener('click', async function() {
        try {
            const response = await fetch('/api/trend_analysis');
            const data = await response.json();
            const trendsList = data.current_trends.map(trend => `<li>${trend}</li>`).join('');
            document.getElementById('trends').innerHTML = `<h3>Current Trends:</h3><ul>${trendsList}</ul>`;
        } catch (error) {
            console.error('Error:', error);
        }
    });

    styleQuizBtn.addEventListener('click', function() {
        // Implement style quiz logic here
        alert('Style quiz feature coming soon!');
    });

    imageUploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);

        try {
            const response = await fetch('/upload_image', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            document.getElementById('imageAnalysisResult').innerHTML = `<p>Analyzed style: ${data.style}</p>`;
        } catch (error) {
            console.error('Error:', error);
        }
    });
});