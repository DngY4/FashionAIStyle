document.addEventListener('DOMContentLoaded', function() {
    const updateKnowledgeBaseForm = document.getElementById('updateKnowledgeBase');

    updateKnowledgeBaseForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData(this);
        const newData = {};

        for (let [key, value] of formData.entries()) {
            if (key.includes('[')) {
                const [mainKey, subKey] = key.split('[');
                if (!newData[mainKey]) newData[mainKey] = {};
                newData[mainKey][subKey.replace(']', '')] = value;
            } else {
                newData[key] = value.split(',').map(item => item.trim());
            }
        }

        try {
            const response = await fetch('/api/train_ai', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ new_data: newData }),
            });
            const data = await response.json();
            alert(data.message);
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while updating the knowledge base.');
        }
    });
});