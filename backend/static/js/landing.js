// landing.js — ATS-only score checker on the public landing page

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('landingForm');
    if (!form) return;

    const resumeInput = document.getElementById('landingResume');
    const fileNameEl = document.getElementById('landingFileName');
    const errorAlert = document.getElementById('landingError');
    const errorMsg = document.getElementById('landingErrorMsg');
    const submitBtn = document.getElementById('landingSubmit');
    const btnText = document.getElementById('landingBtnText');
    const spinner = document.getElementById('landingSpinner');
    const resultCard = document.getElementById('landingResult');
    const upsellCard = document.getElementById('upsellCard');
    const placeholderHint = document.getElementById('placeholderHint');
    const scoreValue = document.getElementById('landingScoreValue');
    const scoreRing = document.getElementById('landingScoreRing');
    const scoreLabel = document.getElementById('landingScoreLabel');

    // File name display
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
        errorMsg.textContent = msg;
        errorAlert.style.display = 'flex';
    }
    function hideError() { errorAlert.style.display = 'none'; }

    function setLoading(loading) {
        submitBtn.disabled = loading;
        btnText.textContent = loading ? 'Analyzing…' : 'Get My Score';
        spinner.style.display = loading ? 'inline-block' : 'none';
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideError();

        const file = resumeInput?.files[0];
        const jd = document.getElementById('landingJD')?.value?.trim();

        if (!file) { showError('Please upload a resume file (PDF or DOCX).'); return; }
        if (!jd) { showError('Please paste the job description text.'); return; }

        const formData = new FormData();
        formData.append('resume', file);
        formData.append('job_description', jd);

        // Hide previous results
        if (resultCard) resultCard.style.display = 'none';
        if (upsellCard) upsellCard.style.display = 'none';
        if (placeholderHint) placeholderHint.style.display = 'none';

        setLoading(true);

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content || '';
            const res = await fetch('/ats_score', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
                body: formData
            });
            const data = await res.json();

            if (!res.ok) {
                showError(data.error || 'An unexpected error occurred.');
                setLoading(false);
                if (placeholderHint) placeholderHint.style.display = 'block';
                return;
            }

            const score = parseFloat(data.score) || 0;

            // Populate score ring (circumference = 2πr = 2π×50 ≈ 314)
            const CIRCUMFERENCE = 314;
            if (scoreValue) scoreValue.textContent = score.toFixed(1);
            if (scoreRing) {
                scoreRing.style.strokeDashoffset = CIRCUMFERENCE - (score / 100) * CIRCUMFERENCE;
                scoreRing.style.stroke =
                    score >= 70 ? '#10b981' :
                        score >= 40 ? '#f59e0b' : '#ef4444';
            }
            if (scoreLabel) {
                scoreLabel.textContent =
                    score >= 70 ? '🟢 Strong Match' :
                        score >= 40 ? '🟡 Moderate Match' : '🔴 Weak Match';
            }

            if (resultCard) resultCard.style.display = 'block';
            if (upsellCard) upsellCard.style.display = 'block';
            resultCard?.scrollIntoView({ behavior: 'smooth', block: 'start' });

        } catch (err) {
            showError('Network error — make sure the backend server is running.');
            if (placeholderHint) placeholderHint.style.display = 'block';
            console.error(err);
        } finally {
            setLoading(false);
        }
    });
});
