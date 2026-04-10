// Voice Assistant JavaScript
class VoiceAssistant {
  constructor() {
    this.recognition = null;
    this.synthesis = window.speechSynthesis;
    this.isListening = false;
    this.isSpeaking = false;
    this.currentLanguage = 'auto'; // 'auto', 'en-US', 'hi-IN'
    this.conversationHistory = [];
    
    this.initializeElements();
    this.initializeSpeechRecognition();
    this.bindEvents();
  }

  initializeElements() {
    this.voiceButton = document.getElementById('voice-button');
    this.buttonIcon = document.getElementById('button-icon');
    this.buttonText = document.getElementById('button-text');
    this.statusText = document.getElementById('status-text');
    this.statusIcon = document.getElementById('status-icon');
    this.detectedLanguage = document.getElementById('detected-language');
    this.currentLanguageDisplay = document.getElementById('current-language');
    this.conversationContainer = document.getElementById('conversation-container');
    this.errorDisplay = document.getElementById('error-display');
    this.errorMessage = document.getElementById('error-message');
    this.clearButton = document.getElementById('clear-button');
    this.languageToggle = document.getElementById('language-toggle');
  }

  initializeSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      this.showError('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.recognition = new SpeechRecognition();
    
    // Configure recognition
    this.recognition.continuous = false;
    this.recognition.interimResults = false;
    this.recognition.maxAlternatives = 1;
    this.recognition.lang = this.getRecognitionLanguage();

    // Event handlers
    this.recognition.onstart = () => {
      console.log('Speech recognition started');
      this.updateStatus('listening', 'Listening...');
      this.voiceButton.classList.add('listening-animation');
      this.hideError();
    };

    this.recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      const confidence = event.results[0][0].confidence;
      
      console.log('Speech recognized:', transcript, 'Confidence:', confidence);
      
      // Detect language
      this.detectLanguage(transcript);
      
      // Add user message
      this.addMessage(transcript, 'user');
      
      // Process the request
      this.processVoiceRequest(transcript);
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      let errorMessage = 'Speech recognition failed.';
      
      switch(event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone access denied. Please allow microphone access.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please check your browser settings.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your internet connection.';
          break;
        default:
          errorMessage = `Speech recognition error: ${event.error}`;
      }
      
      this.showError(errorMessage);
      this.resetUI();
    };

    this.recognition.onend = () => {
      console.log('Speech recognition ended');
      this.resetUI();
    };
  }

  getRecognitionLanguage() {
    switch(this.currentLanguage) {
      case 'en-US': return 'en-US';
      case 'hi-IN': return 'hi-IN';
      case 'bho-IN': return 'hi-IN'; // Use Hindi recognition for Bhojpuri
      default: return 'en-US'; // Default to English for auto-detection
    }
  }

  detectLanguage(text) {
    // Simple language detection based on characters and keywords
    const hindiRegex = /[\u0900-\u097F]/;
    
    // More specific Bhojpuri keywords that are distinct from standard Hindi
    const bhojpuriKeywords = ['baani', 'sakel', 'kar sakel', 'paana', 'baana', 'le sakela', 'maang sakel', 'zaruri ba', 'kare sakel'];
    
    // Check for Bhojpuri patterns (mix of Hindi with Bhojpuri-specific words)
    const hasBhojpuriPatterns = bhojpuriKeywords.some(keyword => 
      text.toLowerCase().includes(keyword) && hindiRegex.test(text)
    );
    
    // Only detect Bhojpuri if specific patterns are found, otherwise default to Hindi
    if (hasBhojpuriPatterns) {
      this.detectedLanguage.textContent = 'Bhojpuri detected';
      return 'bho-IN';
    } else if (hindiRegex.test(text)) {
      this.detectedLanguage.textContent = 'Hindi detected';
      return 'hi-IN';
    } else {
      this.detectedLanguage.textContent = 'English detected';
      return 'en-US';
    }
  }

  bindEvents() {
    this.voiceButton.addEventListener('click', () => this.toggleVoice());
    this.clearButton.addEventListener('click', () => this.clearConversation());
    this.languageToggle.addEventListener('click', () => this.toggleLanguage());
  }

  toggleVoice() {
    if (this.isListening) {
      this.stopListening();
    } else {
      this.startListening();
    }
  }

  startListening() {
    if (!this.recognition) {
      this.showError('Speech recognition is not available.');
      return;
    }

    if (this.isSpeaking) {
      this.synthesis.cancel();
      this.isSpeaking = false;
    }

    try {
      this.recognition.lang = this.getRecognitionLanguage();
      this.recognition.start();
      this.isListening = true;
      this.buttonIcon.textContent = 'stop';
      this.buttonText.textContent = 'Stop Listening';
    } catch (error) {
      console.error('Error starting recognition:', error);
      this.showError('Failed to start speech recognition. Please try again.');
    }
  }

  stopListening() {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  resetUI() {
    this.isListening = false;
    this.voiceButton.classList.remove('listening-animation', 'speaking-animation');
    this.buttonIcon.textContent = 'mic';
    this.buttonText.textContent = 'Start Talking';
    this.updateStatus('ready', 'Ready to assist you');
  }

  async processVoiceRequest(message) {
    this.updateStatus('processing', 'Processing...');
    
    try {
      // Determine language - use auto-detection only if currentLanguage is 'auto'
      let detectedLang = this.currentLanguage;
      if (this.currentLanguage === 'auto') {
        detectedLang = this.detectLanguage(message);
        console.log('Auto-detected language:', detectedLang);
      }
      
      const response = await fetch('http://localhost:8000/voice-ai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: message,
          language: detectedLang
        }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      const reply = data.reply || 'I apologize, but I couldn\'t process your request.';
      
      // Add assistant message
      this.addMessage(reply, 'assistant');
      
      // Speak the response
      await this.speakResponse(reply);
      
    } catch (error) {
      console.error('Voice request error:', error);
      this.showError('Failed to connect to the server. Please check if the backend is running.');
      this.resetUI();
    }
  }

  async speakResponse(text) {
    if (!this.synthesis) {
      console.error('Speech synthesis not available');
      this.resetUI();
      return;
    }

    this.updateStatus('speaking', 'Speaking...');
    this.voiceButton.classList.add('speaking-animation');
    this.buttonIcon.textContent = 'volume_up';
    this.buttonText.textContent = 'Speaking...';

    return new Promise((resolve) => {
      const utterance = new SpeechSynthesisUtterance(text);
      
      // Set language for speech
      utterance.lang = this.currentLanguage === 'auto' ? this.detectLanguage(text) : this.currentLanguage;
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;

      utterance.onstart = () => {
        this.isSpeaking = true;
      };

      utterance.onend = () => {
        this.isSpeaking = false;
        this.resetUI();
        
        // Auto-listen again after speaking (for continuous conversation)
        if (this.conversationHistory.length > 0) {
          setTimeout(() => {
            if (!this.isListening && !this.isSpeaking) {
              this.startListening();
            }
          }, 1000);
        }
        
        resolve();
      };

      utterance.onerror = (event) => {
        console.error('Speech synthesis error:', event);
        this.isSpeaking = false;
        this.resetUI();
        resolve();
      };

      this.synthesis.cancel(); // Cancel any previous speech
      this.synthesis.speak(utterance);
    });
  }

  addMessage(text, type) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message-bubble p-4 rounded-xl ${
      type === 'user' 
        ? 'bg-white/20 ml-auto max-w-[80%]' 
        : 'bg-blue-500/30 mr-auto max-w-[80%]'
    }`;
    
    const icon = type === 'user' ? 'person' : 'smart_toy';
    const label = type === 'user' ? 'You' : 'Assistant';
    
    messageDiv.innerHTML = `
      <div class="flex items-start gap-3">
        <span class="material-symbols-outlined text-lg">${icon}</span>
        <div class="flex-1">
          <div class="font-medium text-sm mb-1">${label}</div>
          <div class="text-sm">${text}</div>
        </div>
      </div>
    `;
    
    this.conversationContainer.appendChild(messageDiv);
    this.conversationContainer.scrollTop = this.conversationContainer.scrollHeight;
    
    // Add to history
    this.conversationHistory.push({ type, text, timestamp: new Date() });
  }

  clearConversation() {
    this.conversationContainer.innerHTML = '';
    this.conversationHistory = [];
    this.hideError();
    this.resetUI();
  }

  toggleLanguage() {
    const languages = ['auto', 'en-US', 'hi-IN', 'bho-IN'];
    const currentIndex = languages.indexOf(this.currentLanguage);
    this.currentLanguage = languages[(currentIndex + 1) % languages.length];
    
    const languageNames = {
      'auto': 'Auto',
      'en-US': 'English',
      'hi-IN': 'Hindi',
      'bho-IN': 'Bhojpuri'
    };
    
    this.currentLanguageDisplay.textContent = languageNames[this.currentLanguage];
    
    // Update recognition language if currently active
    if (this.recognition) {
      this.recognition.lang = this.getRecognitionLanguage();
    }
  }

  updateStatus(status, text) {
    const icons = {
      'ready': 'mic',
      'listening': 'hearing',
      'processing': 'psychology',
      'speaking': 'volume_up'
    };
    
    this.statusIcon.textContent = icons[status] || 'mic';
    this.statusText.innerHTML = `<span class="material-symbols-outlined">${icons[status] || 'mic'}</span> ${text}`;
  }

  showError(message) {
    this.errorMessage.textContent = message;
    this.errorDisplay.classList.remove('hidden');
  }

  hideError() {
    this.errorDisplay.classList.add('hidden');
  }
}

// Initialize the voice assistant when the page loads
document.addEventListener('DOMContentLoaded', () => {
  new VoiceAssistant();
});
