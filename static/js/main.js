import { getElements } from './ui.js';
import { initUploadLogic } from './upload.js';
import { submitGeneration, uploadToYouTube } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
    const elements = getElements();
    let selectedFile = null;

    initUploadLogic(elements, (file) => {
        selectedFile = file;
    });

    elements.form.addEventListener('submit', (e) => {
        e.preventDefault();
        
        if (!selectedFile) {
            alert('Please select an image first!');
            return;
        }

        const formData = new FormData();
        formData.append('image', selectedFile);
        formData.append('context', elements.contextInput.value);
        formData.append('language', elements.languageSelect.value);

        submitGeneration(formData, elements);
    });

    elements.uploadBtn.addEventListener('click', () => {
        uploadToYouTube(elements);
    });
});
