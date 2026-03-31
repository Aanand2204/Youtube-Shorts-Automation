export const getElements = () => {
    return {
        form: document.getElementById('generate-form'),
        uploadZone: document.getElementById('upload-zone'),
        imageUpload: document.getElementById('image-upload'),
        imagePreview: document.getElementById('image-preview'),
        contextInput: document.getElementById('context-input'),
        languageSelect: document.getElementById('language-select'),
        generateBtn: document.getElementById('generate-btn'),
        emptyState: document.getElementById('empty-state'),
        progressContainer: document.getElementById('progress-container'),
        progressBarFill: document.getElementById('progress-bar-fill'),
        progressText: document.getElementById('progress-text'),
        assetsContainer: document.getElementById('assets-container'),
        outputVideo: document.getElementById('output-video'),
        uploadBtn: document.getElementById('upload-btn'),
        uploadResult: document.getElementById('upload-result')
    };
};

export const resetUI = (elements) => {
    elements.progressContainer.classList.add('hidden');
    elements.emptyState.classList.remove('hidden');
    elements.generateBtn.disabled = false;
    elements.generateBtn.innerHTML = '<i class="fa-solid fa-wand-magic-sparkles"></i> Generate Assets';
};

export const handleGenerationSuccess = (assets, elements) => {
    elements.progressContainer.classList.add('hidden');
    
    document.getElementById('out-title').value = assets.title || '';
    document.getElementById('out-desc').value = assets.description || assets.script || '';
    document.getElementById('out-tags').value = assets.tags || '';
    
    elements.outputVideo.src = assets.video_url;

    elements.assetsContainer.classList.remove('hidden');
    elements.uploadResult.classList.add('hidden');
};
