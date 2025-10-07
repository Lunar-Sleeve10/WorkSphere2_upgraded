document.addEventListener('DOMContentLoaded', () => {
    // --- SKILL DELETION ---
    const skillsList = document.getElementById('current-skills-list');
    const deleteStatus = document.getElementById('skill-delete-status');
    const removeSkillUrl = document.getElementById('remove-skill-url').value;

    if (skillsList) {
        skillsList.addEventListener('click', (event) => {
            if (event.target.classList.contains('delete-skill-btn')) {
                const skillContainer = event.target.closest('.skill-badge-container');
                const skillId = skillContainer.dataset.skillId;
                
                const csrftoken = getCookie('csrftoken');

                fetch(removeSkillUrl, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrftoken,
                    },
                    body: `skill_id=${skillId}`,
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        skillContainer.remove();
                        deleteStatus.textContent = data.message;
                        deleteStatus.className = 'mt-2 small text-success';
                    } else {
                        deleteStatus.textContent = `Error: ${data.error}`;
                        deleteStatus.className = 'mt-2 small text-danger';
                    }
                })
                .catch(error => {
                    console.error('Error removing skill:', error);
                    deleteStatus.textContent = 'An unexpected error occurred.';
                    deleteStatus.className = 'mt-2 small text-danger';
                });
            }
        });
    }

    // --- SKILL ADDITION ---
    const addSkillButton = document.getElementById('add-skill-button');
    const addSkillInput = document.getElementById('add-skill-input');
    const addStatus = document.getElementById('skill-add-status');
    const addSkillUrl = document.getElementById('add-skill-url').value;

    if (addSkillButton) {
        addSkillButton.addEventListener('click', () => {
            const skillName = addSkillInput.value.trim();
            if (!skillName) {
                addStatus.textContent = 'Please enter a skill name.';
                addStatus.className = 'mt-2 small text-warning';
                return;
            }

            const csrftoken = getCookie('csrftoken');

            fetch(addSkillUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                },
                body: `skill_name=${encodeURIComponent(skillName)}`,
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addStatus.textContent = data.message;
                    addStatus.className = 'mt-2 small text-success';
                    addSkillInput.value = ''; // Clear input

                    // Add the new skill to the list without reloading
                    const newSkillBadge = document.createElement('span');
                    newSkillBadge.className = 'skill-badge-container';
                    newSkillBadge.dataset.skillId = data.skill.id;
                    newSkillBadge.innerHTML = `
                        ${data.skill.name}
                        <button type="button" class="delete-skill-btn" aria-label="Remove skill">&times;</button>
                    `;
                    skillsList.appendChild(newSkillBadge);
                    
                    // Remove the "No skills added yet." message if it exists
                    const noSkillsP = skillsList.querySelector('p');
                    if(noSkillsP) {
                        noSkillsP.remove();
                    }

                } else {
                    addStatus.textContent = `Error: ${data.error}`;
                    addStatus.className = 'mt-2 small text-danger';
                }
            })
            .catch(error => {
                console.error('Error adding skill:', error);
                addStatus.textContent = 'An unexpected error occurred.';
                addStatus.className = 'mt-2 small text-danger';
            });
        });
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
});