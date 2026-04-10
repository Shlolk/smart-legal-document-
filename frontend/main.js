const form = document.getElementById('problem-form');
const problemInput = document.getElementById('problem');
const resultEl = document.getElementById('result');
const submitButton = document.getElementById('submit-button');
const voiceButton = document.getElementById('voice-button');
const voiceLanguageSelect = document.getElementById('voice-language');
const resultLanguageSelect = document.getElementById('result-language');

// Speech Recognition Setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;

if (voiceButton) {
  if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      isListening = true;
      const icon = voiceButton.querySelector('span');
      if (icon) icon.textContent = 'mic_off';
      voiceButton.classList.add('text-secondary-container');
    };

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i += 1) {
        transcript += event.results[i][0].transcript;
      }
      if (event.results[event.results.length - 1].isFinal) {
        problemInput.value = transcript;
      }
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      voiceButton.classList.remove('text-secondary-container');
      alert('Voice recognition error: ' + event.error + '. Make sure your browser has microphone permission.');
    };

    recognition.onend = () => {
      isListening = false;
      const icon = voiceButton.querySelector('span');
      if (icon) icon.textContent = 'mic';
      voiceButton.classList.remove('text-secondary-container');
    };
  } else {
    voiceButton.disabled = true;
    voiceButton.title = 'Speech recognition not supported in this browser.';
  }

  voiceButton.addEventListener('click', (e) => {
    e.preventDefault();
    if (!recognition) {
      alert('Speech Recognition is not supported in your browser. Try Chrome, Edge, or Safari.');
      return;
    }

    const selectedLang = voiceLanguageSelect?.value || 'en-US';
    recognition.lang = selectedLang;

    if (isListening) {
      recognition.stop();
    } else {
      problemInput.value = '';
      try {
        recognition.start();
      } catch (error) {
        console.error('Speech recognition failed to start:', error);
        alert('Unable to start speech recognition. Check microphone permission and try again.');
      }
    }
  });
} else {
  console.warn('Voice button element not found.');
}

const renderError = (message) => {
  resultEl.className = '';
  resultEl.innerHTML = `<div class="mt-8 p-6 bg-error/10 border-l-4 border-error rounded-lg">
    <p class="text-error font-bold text-lg">${message}</p>
  </div>`;
};

const renderLoading = () => {
  resultEl.className = '';
  resultEl.innerHTML = `<div class="mt-8 p-8 text-center">
    <div class="inline-block">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-secondary-container"></div>
      <p class="text-on-surface-variant font-medium mt-4">Analyzing your problem…</p>
    </div>
  </div>`;
};

const renderResponse = (data) => {
  resultEl.className = '';
  if (data.error) {
    resultEl.innerHTML = `<div class="mt-8 p-6 bg-error/10 border-l-4 border-error rounded-lg">
      <p class="text-error font-bold">${data.error}</p>
    </div>`;
    return;
  }

  const actions = Array.isArray(data.recommended_actions)
    ? data.recommended_actions.map((action) => `<li class="mb-3 text-on-surface-variant">• ${action}</li>`).join('')
    : '<li class="text-on-surface-variant">No actions available</li>';

  resultEl.innerHTML = `
    <div class="mt-8 bg-white rounded-xl shadow-lg p-8">
      <div class="flex justify-between items-start mb-6 pb-6 border-b border-on-surface/10">
        <div>
          <h2 class="text-3xl font-bold text-primary mb-2">Analysis Result</h2>
          <p class="text-on-surface-variant">Legal guidance based on your description</p>
        </div>
      </div>

      <div class="mb-6 pb-6 border-b border-on-surface/10">
        <h3 class="text-lg font-bold text-primary mb-2">Issue Type</h3>
        <p class="text-on-surface text-base">${data.issue_type || 'N/A'}</p>
      </div>

      <div class="mb-6 pb-6 border-b border-on-surface/10">
        <h3 class="text-lg font-bold text-primary mb-2">Relevant Article / Law</h3>
        <p class="text-on-surface text-base font-semibold text-secondary">${data.related_article_or_law || 'N/A'}</p>
      </div>

      <div class="mb-6 pb-6 border-b border-on-surface/10">
        <h3 class="text-lg font-bold text-primary mb-2">Explanation</h3>
        <p class="text-on-surface text-base leading-relaxed">${data.simplified_explanation || 'N/A'}</p>
      </div>

      <div>
        <h3 class="text-lg font-bold text-primary mb-4">Recommended Actions</h3>
        <ul class="space-y-2">
          ${actions}
        </ul>
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
    const resultLanguage = resultLanguageSelect?.value || 'en-US';
    const response = await fetch('http://localhost:8000/analyze-problem', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ problem, language: resultLanguage }),
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

// Legal Search Functionality
const searchForm = document.getElementById('search-form');
const searchQuery = document.getElementById('search-query');
const searchButton = document.getElementById('search-button');
const searchResults = document.getElementById('search-results');
const searchLoading = document.getElementById('search-loading');
const searchError = document.getElementById('search-error');
const errorMessage = document.getElementById('error-message');

const renderSearchResults = (data) => {
  searchResults.innerHTML = '';
  searchLoading.classList.add('hidden');
  searchError.classList.add('hidden');

  if (!data.success || !data.results || data.results.length === 0) {
    searchResults.innerHTML = `
      <div class="text-center py-8">
        <span class="material-symbols-outlined text-4xl text-slate-300 mb-4" data-icon="search_off">search_off</span>
        <p class="text-on-surface-variant">No legal information found for "${data.query}". Try different keywords.</p>
      </div>
    `;
    return;
  }

  const resultsHTML = data.results.map((result, index) => `
    <div class="bg-white rounded-xl p-6 shadow-sm border border-outline-variant hover:shadow-md transition-all duration-200 hover:-translate-y-1">
      <div class="flex items-start gap-4">
        <div class="flex-shrink-0 w-8 h-8 rounded-full bg-primary-fixed flex items-center justify-center">
          <span class="material-symbols-outlined text-primary text-sm" data-icon="description">description</span>
        </div>
        <div class="flex-grow">
          <h3 class="text-lg font-semibold text-primary mb-2">
            <a href="${result.link}" target="_blank" rel="noopener noreferrer" class="hover:text-secondary transition-colors">
              ${result.title}
            </a>
          </h3>
          <p class="text-on-surface-variant text-sm mb-3 line-clamp-2">
            ${result.snippet}
          </p>
          <div class="flex items-center gap-2">
            <span class="material-symbols-outlined text-xs text-slate-400" data-icon="link">link</span>
            <span class="text-xs text-slate-500">${result.displayLink || result.link}</span>
          </div>
        </div>
      </div>
    </div>
  `).join('');

  searchResults.innerHTML = `
    <div class="mb-4">
      <p class="text-on-surface-variant text-sm">
        Found <span class="font-semibold text-primary">${data.total_results}</span> results for "<span class="font-medium">${data.query}</span>"
      </p>
    </div>
    ${resultsHTML}
  `;
};

const renderSearchError = (message) => {
  searchLoading.classList.add('hidden');
  searchError.classList.remove('hidden');
  if (errorMessage) {
    errorMessage.textContent = message;
  }
};

if (searchForm) {
  searchForm.addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = searchQuery.value.trim();
    if (!query) return;

    searchButton.disabled = true;
    searchButton.textContent = 'Searching...';
    searchLoading.classList.remove('hidden');
    searchError.classList.add('hidden');
    searchResults.innerHTML = '';

    try {
      const response = await fetch('http://localhost:5001/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server returned ${response.status}: ${errorText}`);
      }

      const data = await response.json();
      renderSearchResults(data);
    } catch (error) {
      renderSearchError('Unable to connect to search service. Make sure the Flask search server is running on port 5001.');
      console.error('Search error:', error);
    } finally {
      searchButton.disabled = false;
      searchButton.textContent = 'Search Legal Info';
    }
  });
}
