document.addEventListener('DOMContentLoaded', () => {
    const skillsListContainer = document.getElementById('current-skills-list');
    const skillDeleteStatus = document.getElementById('skill-delete-status');
    const removeSkillUrlElement = document.getElementById('remove-skill-url');
    const removeSkillUrl = removeSkillUrlElement ? removeSkillUrlElement.value : null;

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

    if (!skillsListContainer || !removeSkillUrl) {
        if (!removeSkillUrl) console.error("Remove skill URL element not found.");
        if (!skillsListContainer) console.log("Skill list container not found.");
        return;
    }
     if (!csrftoken) {
        console.error("CSRF token not found. Skill deletion might fail.");
    }


    skillsListContainer.addEventListener('click', function(event) {
        if (event.target && event.target.classList.contains('delete-skill-btn')) {
            const button = event.target;
            const skillBadge = button.closest('.skill-badge-container');
            const skillId = skillBadge.getAttribute('data-skill-id');
            const skillName = skillBadge.textContent.replace('×', '').trim();

            if (!skillId) {
                console.error("Could not find skill ID for deletion.");
                return;
            }

            if (!confirm(`Are you sure you want to remove the skill "${skillName}"?`)) {
                return;
            }

            const formData = new FormData();
            formData.append('skill_id', skillId);

            button.disabled = true;
            if(skillDeleteStatus) {
                skillDeleteStatus.textContent = 'Removing skill...';
                skillDeleteStatus.className = 'mt-2 small text-info';
            }

            fetch(removeSkillUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    skillBadge.remove();
                    if(skillDeleteStatus) {
                        skillDeleteStatus.textContent = data.message || 'Skill removed successfully.';
                        skillDeleteStatus.className = 'mt-2 small text-success';
                    }
                    if (!skillsListContainer.querySelector('.skill-badge-container')) {
                        const noSkillsP = document.createElement('p');
                        noSkillsP.className = 'text-muted fst-italic';
                        noSkillsP.textContent = 'No skills added yet.';
                        skillsListContainer.appendChild(noSkillsP);
                    }
                } else {
                    if(skillDeleteStatus) {
                        skillDeleteStatus.textContent = `Error: ${data.error || 'Could not remove skill.'}`;
                        skillDeleteStatus.className = 'mt-2 small text-danger';
                    }
                    button.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error removing skill:', error);
                 if(skillDeleteStatus) {
                    skillDeleteStatus.textContent = 'Error: Could not connect to server.';
                    skillDeleteStatus.className = 'mt-2 small text-danger';
                 }
                button.disabled = false;
            });
        }
    });
});
