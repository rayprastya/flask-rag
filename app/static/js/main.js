document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.getElementById('fileInput');
    const fileList = document.getElementById('fileList');
    const queryInput = document.getElementById('queryInput');
    const queryButton = document.getElementById('queryButton');
    const response = document.getElementById('response');
    const responseText = document.getElementById('responseText');
    const sourcesList = document.getElementById('sourcesList');

    // Handle file selection
    fileInput.addEventListener('change', function() {
        fileList.innerHTML = '';
        Array.from(this.files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'flex items-center space-x-2 text-sm text-gray-600';
            fileItem.innerHTML = `
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
                <span>${file.name}</span>
            `;
            fileList.appendChild(fileItem);
        });
    });

    // Handle file upload
    uploadForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        Array.from(fileInput.files).forEach(file => {
            formData.append('file', file);
        });

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            
            if (response.ok) {
                alert('Documents uploaded successfully!');
                fileList.innerHTML = '';
                fileInput.value = '';
            } else {
                throw new Error(result.error || 'Upload failed');
            }
        } catch (error) {
            alert('Error uploading documents: ' + error.message);
        }
    });

    // Handle query submission
    queryButton.addEventListener('click', async function() {
        const question = queryInput.value.trim();
        if (!question) return;

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    question: question,
                    chat_history: []
                })
            });

            const result = await res.json();
            
            if (res.ok) {
                response.classList.remove('hidden');
                responseText.textContent = result.answer;
                
                // Display sources
                sourcesList.innerHTML = '';
                result.sources.forEach(source => {
                    const li = document.createElement('li');
                    li.textContent = source;
                    sourcesList.appendChild(li);
                });
            } else {
                throw new Error(result.error || 'Query failed');
            }
        } catch (error) {
            alert('Error querying: ' + error.message);
        }
    });

    // Handle Enter key in query input
    queryInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            queryButton.click();
        }
    });
}); 