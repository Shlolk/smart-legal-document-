const form = document.getElementById('problem-form');
const problemInput = document.getElementById('problem');
const resultEl = document.getElementById('result');
const submitButton = document.getElementById('submit-button');

const renderError = (message) => {
  resultEl.className = 'result';
  resultEl.innerHTML = `<div class="alert alert-error">${message}</div>`;
};

const renderLoading = () => {
  resultEl.className = 'result';
  resultEl.innerHTML = '<div class="result-card loading-card"><p class="loading">Analyzing your problem…</p></div>';
};

const renderResponse = (data) => {
  resultEl.className = 'result';
  if (data.error) {
    resultEl.innerHTML = `<div class="alert alert-error">${data.error}</div>`;
    return;
  }

  const actions = Array.isArray(data.recommended_actions)
    ? data.recommended_actions.map((action) => `<li>${action}</li>`).join('')
    : '<li>No actions available</li>';

  resultEl.innerHTML = `
    <div class="result-card">
      <div class="result-header">
        <div>
          <h2>Analysis Result</h2>
          <p class="subtitle">Legal guidance based on your description</p>
        </div>
        ${data.confidence_score ? `<span class="badge">Confidence: ${Math.round(data.confidence_score * 100)}%</span>` : ''}
      </div>

      <div class="result-block">
        <h3>Issue Type</h3>
        <p>${data.issue_type || 'N/A'}</p>
      </div>

      <div class="result-block">
        <h3>Relevant Article / Law</h3>
        <p>${data.related_article_or_law || 'N/A'}</p>
      </div>

      <div class="result-block">
        <h3>Explanation</h3>
        <p>${data.simplified_explanation || 'N/A'}</p>
      </div>

      <div class="result-block">
        <h3>Recommended Actions</h3>
        <ul>${actions}</ul>
      </div>
    </div>
  `;
};

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const problem = problemInput.value.trim();
  if (!problem) return;

  submitButton.disabled = true;
  submitButton.textContent = 'Analyzing...';
  renderLoading();

  try {
    const response = await fetch('http://localhost:8000/analyze-problem', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ problem }),
    });
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Server returned ${response.status}: ${errorText}`);
    }
    const data = await response.json();
    renderResponse(data);
  } catch (error) {
    renderError('Unable to connect to the backend. Start FastAPI on port 8000 and try again.');
    console.error(error);
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = 'Request Guidance';
  }
});
