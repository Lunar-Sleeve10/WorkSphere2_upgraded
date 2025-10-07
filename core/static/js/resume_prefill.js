// core/static/core/js/resume_prefill.js

document.addEventListener('DOMContentLoaded', () => {

    const prefillButton = document.getElementById('prefill-button');
    const fileInput = document.getElementById('resume-upload-input');
    const uploadStatus = document.getElementById('upload-status');
    const form = document.getElementById('profile-form');
    const spinner = document.getElementById('prefill-spinner');
    const buttonText = document.getElementById('prefill-button-text');
    const parseResumeUrl = document.getElementById('parse-resume-url').value;

    if (!prefillButton || !fileInput || !uploadStatus || !form || !spinner || !buttonText || !parseResumeUrl) {
        console.error("Resume pre-fill script: One or more required elements not found.");
        return;
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    const csrftoken = getCookie('csrftoken');
    if (!csrftoken) {
        console.error("CSRF token not found. File upload might fail.");
    }

    prefillButton.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', (event) => {
        const file = event.target.files[0];
        if (!file) {
            return;
        }

        uploadStatus.textContent = '';
        uploadStatus.className = 'mt-2 small';

        const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'image/jpeg', 'image/png'];
        const maxSize = 5 * 1024 * 1024; // 5MB

        if (!allowedTypes.includes(file.type)) {
            uploadStatus.textContent = 'Error: Invalid file type. Please upload PDF, DOCX, JPG, or PNG.';
            uploadStatus.classList.add('text-danger');
            fileInput.value = '';
            return;
        }

        if (file.size > maxSize) {
            uploadStatus.textContent = 'Error: File size exceeds 5MB limit.';
            uploadStatus.classList.add('text-danger');
            fileInput.value = '';
            return;
        }

        const formData = new FormData();
        formData.append('resume_file', file);

        prefillButton.disabled = true;
        spinner.classList.remove('d-none');
        buttonText.textContent = 'Processing...';
        uploadStatus.textContent = 'Uploading and processing resume...';
        uploadStatus.classList.remove('text-danger', 'text-success');
        uploadStatus.classList.add('text-info');

        fetch(parseResumeUrl, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(errData => {
                    throw new Error(errData.error || `Server error: ${response.statusText}`);
                }).catch(() => {
                    throw new Error(`Server responded with status: ${response.status}`);
                });
            }
            return response.json();
        })
        .then(result => {
            prefillButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Select Resume & Pre-fill Form';

            if (result.success && result.data) {
                uploadStatus.textContent = 'Resume processed! Please review the pre-filled fields.';
                uploadStatus.classList.add('text-success');

                const data = result.data;
                const nameParts = data.name ? data.name.split(' ') : ['', ''];
                const firstName = nameParts[0];
                const lastName = nameParts.slice(1).join(' ');

                const firstNameField = form.querySelector('#id_first_name');
                const lastNameField = form.querySelector('#id_last_name');
                const phoneField = form.querySelector('#id_phone_number');
                const skillsField = form.querySelector('#id_skills');
                const locationField = form.querySelector('#id_location');

                if (firstNameField && firstName) firstNameField.value = firstName;
                if (lastNameField && lastName) lastNameField.value = lastName;
                if (phoneField && data.mobile_number) phoneField.value = data.mobile_number;
                if (skillsField && data.skills) skillsField.value = data.skills;
                if (locationField && data.location) locationField.value = data.location;

                console.log("Form fields updated with extracted data:", data);

            } else {
                uploadStatus.textContent = `Error: ${result.error || 'Could not extract relevant data.'}`;
                uploadStatus.classList.add('text-danger');
            }
        })
        .catch(error => {
            console.error('Error during resume pre-fill request:', error);
            uploadStatus.textContent = `Error: ${error.message || 'Could not connect to server.'}`;
            uploadStatus.classList.add('text-danger');
            prefillButton.disabled = false;
            spinner.classList.add('d-none');
            buttonText.textContent = 'Select Resume & Pre-fill Form';
        })
        .finally(() => {
             fileInput.value = '';
        });
    });

});
