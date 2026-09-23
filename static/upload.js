document.addEventListener('DOMContentLoaded', function () {
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' || event.key === 'F5') {
            event.preventDefault();

            sessionStorage.removeItem('pageWasVisited');
            window.location.href = 'index.html';
        }
    });
});

document.addEventListener('DOMContentLoaded', () => {
    const fileUpload = document.getElementById('file-upload');
    const imagesButton = document.getElementById('images-tab-btn');
    const dropzone = document.querySelector('.upload__dropzone');
    const currentUploadInput = document.querySelector('.upload__input');
    const copyButton = document.querySelector('.upload__copy');

    const updateTabStyles = () => {
        const uploadTab = document.getElementById('upload-tab-btn');
        const imagesTab = document.getElementById('images-tab-btn');

        const isImagesPage = window.location.pathname.includes('images.html');

        uploadTab.classList.remove('upload__tab--active');
        imagesTab.classList.remove('upload__tab--active');

        if (isImagesPage) {
            imagesTab.classList.add('upload__tab--active');
        } else {
            uploadTab.classList.add('upload__tab--active');
        }
    };

    const handleAndStoreFiles = async (files) => {
        if (!files || files.length === 0) {
            return;
        }

        const storedFiles = JSON.parse(localStorage.getItem('uploadedImages')) || [];
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif'];
        const MAX_SIZE_MB = 5;
        const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

        const formData = new FormData();
        const fileNames = [];
        let filesAdded = false;

        for (const file of files) {
            if (!allowedTypes.includes(file.type) || file.size > MAX_SIZE_BYTES) {
                continue;
            }

            fileNames.push(file.name);
            formData.append('files', file);
            filesAdded = true;
        }

        if (!filesAdded) {
            alert('Будь ласка, оберіть коректний файл (.jpg, .png або .gif) розміром до 5 МБ.');
            return;
        }

        formData.append('names', JSON.stringify(fileNames));

        try {
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                console.error('Upload failed:', response.status);
                alert('Помилка при завантаженні файла.');
                return;
            }

            // 📩 Отримуємо JSON від сервера: { "url": "/images/uuid.gif" }
            const data = await response.json();
            console.log('Files uploaded successfully:', data);

            // 💾 Зберігаємо лише посилання (URL) від сервера
            storedFiles.push({
                name: fileNames[0],
                url: data.url
            });
            localStorage.setItem('uploadedImages', JSON.stringify(storedFiles));
            updateTabStyles();

            // 🔗 Оновлюємо поле з посиланням
            if (currentUploadInput && data.url) {
                currentUploadInput.value = window.location.origin + data.url;
            }

            alert("Файл успішно завантажено! Перейдіть на вкладку 'Images', щоб переглянути.");

        } catch (error) {
            console.error('Upload error:', error);
            alert('Помилка мережі при завантаженні.');
        }
    };

    if (copyButton && currentUploadInput) {
        copyButton.addEventListener('click', () => {
            const textToCopy = currentUploadInput.value;

            if (textToCopy && textToCopy !== 'https://') {
                navigator.clipboard.writeText(textToCopy).then(() => {
                    copyButton.textContent = 'COPIED!';

                    setTimeout(() => {
                        copyButton.textContent = 'COPY';
                    }, 2000);
                }).catch(err => {
                    console.error('Failed to copy text: ', err);
                });
            }
        });
    }

    if (imagesButton) {
        imagesButton.addEventListener('click', () => {
            window.location.href = 'images.html';
        });
    }

    if (fileUpload) {
        fileUpload.addEventListener('change', (event) => {
            handleAndStoreFiles(event.target.files);
            event.target.value = '';
        });
    }

    if (dropzone) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        dropzone.addEventListener('drop', (event) => {
            handleAndStoreFiles(event.dataTransfer.files);
        });
    }

    updateTabStyles();
});
