const fileInput = document.getElementById('file-input');
const previewImage = document.getElementById('preview-image');
const cameraPanel = document.getElementById('camera-panel');
const cameraVideo = document.getElementById('camera-video');
const toggleCameraButton = document.getElementById('toggle-camera-button');
const captureButton = document.getElementById('capture-button');
const scanButton = document.getElementById('scan-button');
const scanStatus = document.getElementById('scan-status');
const extractedTextEl = document.getElementById('extracted-text');
const termsList = document.getElementById('terms-list');
const listenButton = document.getElementById('listen-button');

let selectedFile = null;
let cameraStream = null;
let extractedText = '';
let detectedTerms = [];

const LEGAL_TERM_DICTIONARY = {
  petitioner: 'Person who files the case.',
  affidavit: 'A written statement given under oath.',
  injunction: 'A court order that requires or prevents an action.',
  jurisdiction: 'The authority of a court to hear a case.',
  plaintiff: 'The person who brings a lawsuit.',
  defendant: 'The person against whom a lawsuit is filed.',
  summons: 'A legal document ordering someone to appear in court.',
  arbitration: 'A private process for resolving disputes outside court.',
  notarize: 'To have a document certified by a notary public.',
  contract: 'A legally enforceable agreement between parties.'
};

const highlightText = (text, terms) => {
  let highlighted = text;
  terms.forEach(({ term }) => {
    const escaped = term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b(${escaped})\\b`, 'gi');
    highlighted = highlighted.replace(regex, '<span class="highlight-term">$1</span>');
  });
  return highlighted;
};

const showStatus = (message, isError = false) => {
  scanStatus.textContent = message;
  scanStatus.className = isError ? 'text-sm text-red-600' : 'text-sm text-slate-600';
};

const renderTerms = (terms) => {
  if (!terms?.length) {
    termsList.innerHTML = '<p class="text-slate-600">No complex legal terms were detected in the extracted text.</p>';
    return;
  }

  termsList.innerHTML = terms.map(({ term, explanation }) => `
    <div class="rounded-[1.5rem] border border-slate-200 bg-slate-50 p-5">
      <p class="text-lg font-semibold text-slate-900">${term}</p>
      <p class="mt-2 text-slate-700">${explanation}</p>
    </div>
  `).join('');
};

const detectTermsFromText = (text) => {
  const lower = text.toLowerCase();
  return Object.entries(LEGAL_TERM_DICTIONARY)
    .filter(([term]) => lower.includes(term.toLowerCase()))
    .map(([term, explanation]) => ({ term, explanation }));
};

const stopCamera = () => {
  if (cameraStream) {
    cameraStream.getTracks().forEach((track) => track.stop());
    cameraStream = null;
  }
  cameraPanel.classList.add('hidden');
  toggleCameraButton.textContent = 'Use Camera';
};

const startCamera = async () => {
  if (cameraStream) {
    stopCamera();
    return;
  }

  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
    cameraVideo.srcObject = cameraStream;
    cameraPanel.classList.remove('hidden');
    previewImage.classList.add('hidden');
    toggleCameraButton.textContent = 'Stop Camera';
  } catch (error) {
    console.error('Failed to start camera:', error);
    showStatus('Unable to access camera. Please use the file upload instead.', true);
  }
};

const captureSnapshot = () => {
  if (!cameraStream) return;
  const canvas = document.createElement('canvas');
  canvas.width = cameraVideo.videoWidth;
  canvas.height = cameraVideo.videoHeight;
  canvas.getContext('2d').drawImage(cameraVideo, 0, 0, canvas.width, canvas.height);

  canvas.toBlob((blob) => {
    if (!blob) return;
    selectedFile = new File([blob], 'document-capture.png', { type: 'image/png' });
    previewImage.src = URL.createObjectURL(selectedFile);
    previewImage.classList.remove('hidden');
    showStatus('Snapshot captured and ready to scan.');
  }, 'image/png');
};

const speakExplanation = () => {
  if (!window.speechSynthesis) {
    alert('Speech synthesis is not supported by your browser.');
    return;
  }

  const termsText = detectedTerms.length > 0
    ? detectedTerms.map((item) => `${item.term}: ${item.explanation}`).join('. ')
    : 'No specific legal terms were detected.';

  const message = `Extracted text: ${extractedText}. ${termsText}`;
  const utterance = new SpeechSynthesisUtterance(message);
  utterance.rate = 1.0;
  utterance.pitch = 1.0;
  speechSynthesis.cancel();
  speechSynthesis.speak(utterance);
};

const handleScanResponse = async (response) => {
  console.log('Handling scan response, status:', response.status);
  
  if (!response.ok) {
    const errorBody = await response.text();
    console.error('Scan response error:', errorBody);
    throw new Error(errorBody || 'Server returned an error');
  }

  const data = await response.json();
  console.log('Scan response data:', data);
  
  extractedText = data.extracted_text || '';
  const terms = Array.isArray(data.legal_terms) && data.legal_terms.length > 0
    ? data.legal_terms
    : detectTermsFromText(extractedText);

  detectedTerms = terms;
  
  if (extractedText && extractedText.trim()) {
    extractedTextEl.innerHTML = highlightText(extractedText, terms);
    showStatus('Document scanned successfully. Review the extracted content and explanations.');
  } else {
    extractedTextEl.innerHTML = '<span class="text-orange-600 font-medium">No text could be extracted from the uploaded image. Please ensure:</span><ul class="list-disc list-inside mt-2 text-sm text-slate-600"><li>The image is clear and readable</li><li>The text is in English</li><li>The image contains text (not just graphics)</li><li>Try using a higher resolution image</li></ul>';
    showStatus('No text extracted. The image may not contain readable text.', true);
  }
  
  renderTerms(terms);
};

toggleCameraButton.addEventListener('click', () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    showStatus('Camera capture is not supported in this browser.', true);
    return;
  }
  startCamera();
});

captureButton.addEventListener('click', () => {
  captureSnapshot();
});

fileInput.addEventListener('change', (event) => {
  const file = event.target.files?.[0];
  if (!file) return;
  selectedFile = file;
  previewImage.src = URL.createObjectURL(file);
  previewImage.classList.remove('hidden');
  showStatus('Document image selected. Ready to scan.');
});

scanButton.addEventListener('click', async () => {
  console.log('Scan button clicked');
  console.log('Selected file:', selectedFile);
  
  if (!selectedFile) {
    showStatus('Please upload or capture a document image first.', true);
    scanButton.classList.add('animate-pulse', 'bg-red-500');
    setTimeout(() => {
      scanButton.classList.remove('animate-pulse', 'bg-red-500');
    }, 2000);
    return;
  }

  scanButton.disabled = true;
  scanButton.textContent = 'Scanning...';
  scanButton.classList.add('opacity-75', 'cursor-not-allowed');
  showStatus('Uploading image and scanning document...');

  const formData = new FormData();
  formData.append('document_image', selectedFile);

  try {
    console.log('Sending scan request to backend...');
    const response = await fetch('http://localhost:8000/scan-document', {
      method: 'POST',
      body: formData,
    });
    console.log('Scan response status:', response.status);
    await handleScanResponse(response);
  } catch (error) {
    console.error('Scan error:', error);
    showStatus('Unable to scan document. Make sure the backend /scan-document endpoint is running.', true);
    extractedTextEl.textContent = '';
    termsList.innerHTML = '';
  } finally {
    scanButton.disabled = false;
    scanButton.textContent = 'Scan Document';
    scanButton.classList.remove('opacity-75', 'cursor-not-allowed');
  }
});

listenButton.addEventListener('click', () => {
  if (!extractedText) {
    showStatus('Scan a document before listening to the explanation.', true);
    return;
  }
  speakExplanation();
});

window.addEventListener('beforeunload', () => {
  stopCamera();
});
