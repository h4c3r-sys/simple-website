async function postData(url = '', data = {}) {
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
    return response.json();
}

function showLoading() {
    document.getElementById('resultContainer').style.display = 'block';
    document.getElementById('loadingSpinner').style.display = 'block';
    document.getElementById('results-area').innerText = 'Processing... This may take a minute while we gather data from the web and AI.';
}

function hideLoading(text) {
    document.getElementById('loadingSpinner').style.display = 'none';

    if (typeof text === 'object') {
        // Pretty print JSON
        // Check for specific keys to format nicely
        if (text.report) {
            document.getElementById('results-area').innerHTML = `
                <h5>AI Analysis Report</h5>
                <div style="white-space: pre-wrap;">${text.report}</div>
                <hr>
                <h6>Raw Data Sources</h6>
                <details>
                    <summary>Web Search</summary>
                    <pre>${JSON.stringify(text.sources.web, null, 2)}</pre>
                </details>
                <details>
                    <summary>Social Media</summary>
                    <pre>${JSON.stringify(text.sources.social, null, 2)}</pre>
                </details>
            `;
        } else if (text.proposal) {
             document.getElementById('results-area').innerHTML = `
                <h5>Business Proposal</h5>
                <div style="white-space: pre-wrap;">${text.proposal}</div>
            `;
        } else {
             document.getElementById('results-area').innerText = JSON.stringify(text, null, 2);
        }

    } else {
        document.getElementById('results-area').innerText = text;
    }
}

async function generateIdea() {
    const niche = document.getElementById('nicheInput').value;
    if (!niche) return alert('Please enter a niche');

    showLoading();
    try {
        const result = await postData('/api/generate-idea', { niche: niche });
        hideLoading(result);
    } catch (error) {
        hideLoading('Error: ' + error);
    }
}

async function analyzeMarket() {
    const idea = document.getElementById('ideaInput').value;
    if (!idea) return alert('Please enter a business idea');

    showLoading();
    try {
        const result = await postData('/api/analyze-market', { idea: idea, include_email_analysis: false });
        hideLoading(result);
    } catch (error) {
        hideLoading('Error: ' + error);
    }
}

async function sendEmail() {
    const form = document.getElementById('emailForm');
    const formData = new FormData(form);

    showLoading();
    try {
        const response = await fetch('/api/email/send', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        hideLoading(result);
    } catch (error) {
        hideLoading('Error: ' + error);
    }
}

async function checkResponses() {
    const subject = document.getElementById('responseSubject').value;
    if (!subject) return alert('Please enter a subject keyword');

    showLoading();
    try {
        const response = await fetch(`/api/email/check?subject_keyword=${encodeURIComponent(subject)}`);
        const result = await response.json();
        hideLoading(result);
    } catch (error) {
        hideLoading('Error: ' + error);
    }
}
