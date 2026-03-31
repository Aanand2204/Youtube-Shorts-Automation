import { resetUI, handleGenerationSuccess } from './ui.js';

export async function submitGeneration(formData, elements) {
    elements.generateBtn.disabled = true;
    elements.generateBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Initializing...';
    
    elements.emptyState.classList.add('hidden');
    elements.assetsContainer.classList.add('hidden');
    elements.progressContainer.classList.remove('hidden');
    elements.progressBarFill.style.width = '5%';
    elements.progressText.innerText = 'Uploading context to server...';

    try {
        const uploadRes = await fetch('/api/upload_context', {
            method: 'POST',
            body: formData
        });

        if (!uploadRes.ok) throw new Error('Failed to upload context.');
        const uploadJSON = await uploadRes.json();
        const taskId = uploadJSON.task_id;

        connectWebSocket(taskId, elements);

    } catch (error) {
        console.error(error);
        alert('An error occurred starting generation.');
        resetUI(elements);
    }
}

function connectWebSocket(taskId, elements) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/ws/generate/${taskId}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        elements.progressText.innerText = 'Connected! Starting engine...';
        elements.progressBarFill.style.width = '10%';
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.error) {
            alert('Generation Error: ' + data.error);
            ws.close();
            resetUI(elements);
            return;
        }

        if (data.progress !== undefined) {
            const percent = Math.max(10, Math.floor(data.progress * 100)); 
            elements.progressBarFill.style.width = `${percent}%`;
        }
        if (data.message) {
            elements.progressText.innerText = data.message;
        }

        if (data.progress === 1.0 && data.assets) {
            handleGenerationSuccess(data.assets, elements);
        }
    };

    ws.onerror = (error) => {
        console.error("WebSocket Error:", error);
        alert("WebSocket connection lost!");
        resetUI(elements);
    };

    ws.onclose = () => {
        elements.generateBtn.disabled = false;
        elements.generateBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate Assets';
    };
}

export async function uploadToYouTube(elements) {
    elements.uploadBtn.disabled = true;
    elements.uploadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';
    
    elements.uploadResult.className = 'hidden';
    elements.uploadResult.innerHTML = '';

    const formData = new FormData();
    formData.append('title', document.getElementById('out-title').value);
    formData.append('description', document.getElementById('out-desc').value);
    formData.append('tags', document.getElementById('out-tags').value);

    try {
        const res = await fetch('/api/upload_youtube', {
            method: 'POST',
            body: formData
        });

        const data = await res.json();
        
        if (!res.ok) throw new Error(data.error || 'Server upload failure');

        elements.uploadResult.className = 'success';
        elements.uploadResult.innerHTML = `✅ Successfully Uploaded! <br><a href="${data.url}" target="_blank">View on YouTube</a>`;
    } catch (error) {
        console.error(error);
        elements.uploadResult.className = 'error';
        elements.uploadResult.innerText = `❌ Error: ${error.message}`;
    } finally {
        elements.uploadBtn.disabled = false;
        elements.uploadBtn.innerHTML = '<i class="fa-brands fa-youtube"></i> Auto-Upload to YouTube';
    }
}
