// frontend/js/main.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('uploadForm');
    if (!form) {
        console.warn('uploadForm not found in DOM');
        return;
    }

    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const resultSection = document.getElementById('result');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Show filename when a file is selected
    const resumeInput = document.getElementById('resume');
    const fileNameEl = document.getElementById('fileName');
    if (resumeInput && fileNameEl) {
        resumeInput.addEventListener('change', () => {
            if (resumeInput.files[0]) {
                fileNameEl.textContent = '📎 ' + resumeInput.files[0].name;
                fileNameEl.style.display = 'block';
            } else {
                fileNameEl.style.display = 'none';
            }
        });
    }

    function showError(msg) {
        if (errorAlert) {
            errorMessage.textContent = msg;
            errorAlert.style.display = 'flex';
        }
    }

    function hideError() {
        if (errorAlert) errorAlert.style.display = 'none';
    }

    function setLoading(loading) {
        if (loading) {
            submitBtn.disabled = true;
            btnText.textContent = 'Analyzing…';
            btnSpinner.style.display = 'inline-block';
        } else {
            submitBtn.disabled = false;
            btnText.textContent = 'Analyze Resume';
            btnSpinner.style.display = 'none';
        }
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const resumeFile = document.getElementById('resume').files[0];
        const jdText = document.getElementById('job_description').value;

        if (!resumeFile) {
            showError('Please upload a resume file (PDF or DOCX).');
            return;
        }
        if (!jdText.trim()) {
            showError('Please paste the job description text.');
            return;
        }

        const formData = new FormData();
        formData.append('resume', resumeFile);
        formData.append('job_description', jdText);

        // Include CSRF token so Flask-WTF accepts the request
        const csrfToken = document.getElementById('csrf_token');
        if (csrfToken) formData.append('csrf_token', csrfToken.value);

        if (resultSection) resultSection.style.display = 'none';
        setLoading(true);

        try {
            const response = await fetch('/process_resume', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (!response.ok) {
                showError(data.error || 'An unexpected error occurred.');
                return;
            }

            // Populate score
            const scoreValue = document.getElementById('scoreValue');
            const scoreRing = document.getElementById('scoreRing');
            const score = parseFloat(data.score) || 0;
            if (scoreValue) scoreValue.textContent = score.toFixed(1);
            if (scoreRing) {
                // SVG circle: circumference = 2 * pi * r = 2 * pi * 45 ≈ 283
                const circumference = 283;
                const offset = circumference - (score / 100) * circumference;
                scoreRing.style.strokeDashoffset = offset;
                // Colour by score
                if (score >= 70) scoreRing.style.stroke = '#10b981';
                else if (score >= 40) scoreRing.style.stroke = '#f59e0b';
                else scoreRing.style.stroke = '#ef4444';
            }

            // Populate tips
            const tipsList = document.getElementById('tipsList');
            if (tipsList) {
                tipsList.innerHTML = '';
                const tips = data.retrieved_tips || [];
                if (tips.length === 0) {
                    tipsList.innerHTML = '<li class="tip-item">No specific tips retrieved.</li>';
                } else {
                    tips.forEach(tip => {
                        const li = document.createElement('li');
                        li.className = 'tip-item';
                        li.textContent = tip;
                        tipsList.appendChild(li);
                    });
                }
            }

            // Populate AI suggestions
            const aiEl = document.getElementById('aiSuggestions');
            if (aiEl) {
                const raw = data.ai_suggestions || 'No suggestions returned.';
                // Convert numbered list lines to styled HTML
                aiEl.innerHTML = raw
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/^(\d+)\.\s+/gm, '<span class="suggestion-number">$1</span> ')
                    .replace(/\n/g, '<br>');
            }

            if (resultSection) {
                resultSection.style.display = 'block';
                resultSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        } catch (err) {
            showError('Network error — make sure the backend server is running at http://127.0.0.1:5000');
            console.error(err);
        } finally {
            setLoading(false);
        }
    });
});
