document.addEventListener('DOMContentLoaded', () => {
    // File input label updates
    const updateFileName = (inputId, labelId) => {
        const input = document.getElementById(inputId);
        const label = document.getElementById(labelId);
        input.addEventListener('change', (e) => {
            if(e.target.files.length > 0) {
                label.textContent = e.target.files[0].name;
                label.style.color = 'var(--accent)';
            }
        });
    };

    updateFileName('identityDocument', 'idFileName');
    updateFileName('incomeProof', 'incomeFileName');

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
            setStage('stage-validation', 'active', 'Scrutinizing documents and validating fields...');
            
            const response = await fetch('/api/apply', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            await sleep(1500); // Visual agent delay

            if (response.status === 400 && data.stage === "Validation Agent") {
                // Validation failed
                setStage('stage-validation', 'error', 'Validation anomalies detected.');
                showResult('rejected', data.status || 'Rejected', data.remarks);
                return;
            }

            setStage('stage-validation', 'completed', 'All rules and documents verified.');
            setStage('stage-decision', 'active', 'Applying bank policies and calculating matrices...');

            await sleep(2000); // Visual agent delay

            if (response.status !== 200) {
                setStage('stage-decision', 'error', 'System Error.');
                showResult('rejected', 'Error', 'An internal error occurred: ' + data.error);
                return;
            }

            // Decision made
            if (data.status === "Approved" || data.status === "Success") {
                setStage('stage-decision', 'completed', 'Decision reached successfully.');
                showResult('success', 'Loan Approved', data.remarks);
            } else {
                setStage('stage-decision', 'error', 'Policy limits exceeded.');
                showResult('rejected', 'Loan Rejected', data.remarks);
            }

        } catch (error) {
            setStage('stage-decision', 'error', 'Network failure.');
            showResult('rejected', 'Error', 'Failed to connect to agentic backend.');
        }
    });

    const showResult = (type, title, remarks) => {
        setTimeout(() => {
            pipeline.classList.add('hidden');
            resultModal.classList.remove('hidden');
            resultModal.className = `result-modal fade-in-up ${type}`;
            document.getElementById('resultTitle').textContent = title;
            document.getElementById('resultRemarks').textContent = remarks;
        }, 800);
    };

    document.getElementById('resetBtn').addEventListener('click', () => {
        resultModal.classList.add('hidden');
        form.classList.remove('hidden');
        form.reset();
        document.getElementById('idFileName').textContent = 'Upload Identity Proof (PDF, PNG)';
        document.getElementById('idFileName').style.color = '';
        document.getElementById('incomeFileName').textContent = 'Upload Income Proof (PDF, PNG)';
        document.getElementById('incomeFileName').style.color = '';
        
        btnText.style.display = 'block';
        spinner.style.display = 'none';
        submitBtn.disabled = false;
        
        // Reset stages
        ['stage-intake', 'stage-validation', 'stage-decision'].forEach(id => {
            const el = document.getElementById(id);
            el.classList.remove('active', 'completed', 'error');
        });
        document.querySelector('#stage-intake p').textContent = 'Awaiting data ingestion...';
        document.querySelector('#stage-validation p').textContent = 'Pending document & rule checks...';
        document.querySelector('#stage-decision p').textContent = 'Pending final review...';
    });
});
