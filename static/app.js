document.addEventListener('DOMContentLoaded', () => {
    // No file uploads in this version

    const form = document.getElementById('loanForm');
    const pipeline = document.getElementById('statusPipeline');
    const resultModal = document.getElementById('resultModal');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.querySelector('.btn-text');
    const spinner = document.getElementById('btnSpinner');

    const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    const setStage = (stageId, status, message) => {
        const stage = document.getElementById(stageId);
        const p = stage.querySelector('p');

        // Remove all classes
        stage.classList.remove('active', 'completed', 'error');
        stage.classList.add(status);
        if (message) p.textContent = message;
    };

    // Live validation
    const validateForm = () => {
        let isValid = true;
        const inputs = form.querySelectorAll('input, select');

        inputs.forEach(input => {
            if (input.required && !input.value) {
                isValid = false;
            } else if (input.type === 'number' && Number(input.value) <= 0) {
                isValid = false;
                input.style.borderColor = 'var(--error)';
            } else {
                input.style.borderColor = '';
            }
        });

        submitBtn.disabled = !isValid;
    };

    form.querySelectorAll('input, select').forEach(input => {
        input.addEventListener('input', validateForm);
        input.addEventListener('change', validateForm);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // UI Prep
        btnText.style.display = 'none';
        spinner.style.display = 'block';
        submitBtn.disabled = true;

        form.classList.add('hidden');
        pipeline.classList.remove('hidden');

        // Stage 1: Intake (Mocking delay for effect)
        setStage('stage-intake', 'active', 'Extracting and structuring data payloads...');
        await sleep(1500);

        const formData = new FormData(form);

        try {
            // Stage 2: Validation Check begins in UI, backend finishes intake fast
            setStage('stage-intake', 'completed', 'Data structured successfully.');
            setStage('stage-validation', 'active', 'Scrutinizing profile and validating fields...');

            const response = await fetch('/api/apply', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            await sleep(1500); // Visual agent delay

            if (response.status === 400 && data.stage === "Validation Agent") {
                // Validation failed
                setStage('stage-validation', 'error', 'Validation anomalies detected.');
                showResult('rejected', data.status || 'Rejected', data.remarks, data.metrics);
                return;
            }

            setStage('stage-validation', 'completed', 'All rules and profile limits verified.');
            setStage('stage-decision', 'active', 'Querying Random Forest, Gradient Boosting, and Logistic Regression ensemble...');

            await sleep(2000); // Visual agent delay

            if (response.status !== 200) {
                setStage('stage-decision', 'error', 'System Error.');
                showResult('rejected', 'Error', 'An internal error occurred: ' + data.error);
                return;
            }

            // Decision made
            if (data.status === "Approved" || data.status === "Success") {
                setStage('stage-decision', 'completed', 'Decision reached successfully.');
                showResult('success', 'Loan Approved', data.remarks, data.metrics);
            } else {
                setStage('stage-decision', 'error', 'Policy limits exceeded.');
                showResult('rejected', 'Loan Rejected', data.remarks, data.metrics);
            }

        } catch (error) {
            setStage('stage-decision', 'error', 'Network failure.');
            showResult('rejected', 'Error', 'Failed to connect to agentic backend.');
        }
    });

    const showResult = (type, title, remarks, metrics) => {
        setTimeout(() => {
            pipeline.classList.add('hidden');
            resultModal.classList.remove('hidden');
            resultModal.className = `result-modal fade-in-up ${type}`;
            document.getElementById('resultTitle').textContent = title;
            document.getElementById('resultRemarks').textContent = remarks;

            // XAI Rendering
            const metricsContainer = document.getElementById('xaiMetrics');
            const metricsList = document.getElementById('metricsList');
            metricsList.innerHTML = '';

            if (metrics && Object.keys(metrics).length > 0) {
                metricsContainer.classList.remove('hidden');

                const labels = {
                    'confidence': 'Ensemble Confidence',
                    'dti_score': 'Debt-to-Income Appropriateness',
                    'credit_score': 'Credit History Weight',
                    'employment_score': 'Employment Stability'
                };

                for (const [key, val] of Object.entries(metrics)) {
                    const percent = key === 'confidence' ? val : Math.round(val * 100);
                    const color = percent > 70 ? 'var(--success)' : percent > 40 ? 'var(--accent)' : 'var(--error)';

                    const el = document.createElement('div');
                    el.className = 'metric-row';
                    el.innerHTML = `
                        <div class="metric-label">
                            <span>${labels[key] || key}</span>
                            <span>${percent}%</span>
                        </div>
                        <div class="metric-bar-bg">
                            <div class="metric-bar-fill" style="width: 0%; background: ${color}"></div>
                        </div>
                    `;
                    metricsList.appendChild(el);

                    // Animate
                    setTimeout(() => {
                        el.querySelector('.metric-bar-fill').style.width = `${percent}%`;
                    }, 100);
                }
            } else {
                metricsContainer.classList.add('hidden');
            }

        }, 800);
    };

    document.getElementById('resetBtn').addEventListener('click', () => {
        resultModal.classList.add('hidden');
        form.classList.remove('hidden');
        form.reset();

        btnText.style.display = 'block';
        spinner.style.display = 'none';
        submitBtn.disabled = false;

        // Reset stages
        ['stage-intake', 'stage-validation', 'stage-decision'].forEach(id => {
            const el = document.getElementById(id);
            el.classList.remove('active', 'completed', 'error');
        });
        document.querySelector('#stage-intake p').textContent = 'Awaiting data ingestion...';
        document.querySelector('#stage-validation p').textContent = 'Pending profile & rule checks...';
        document.querySelector('#stage-decision p').textContent = 'Pending final model consensus...';
    });
});
