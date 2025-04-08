// Voice functionality
document.addEventListener('DOMContentLoaded', function() {
    const voiceButton = document.getElementById('voice-btn');
    const messageInput = document.getElementById('message-input');
    const languageSelect = document.getElementById('language-select');
    
    // Check if browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (SpeechRecognition) {
        const recognition = new SpeechRecognition();
        
        // Configure recognition
        recognition.continuous = false;
        recognition.interimResults = false;
        
        let isRecording = false;
        
        voiceButton.addEventListener('click', function() {
            if (isRecording) {
                // Stop recording
                recognition.stop();
                voiceButton.classList.remove('btn-danger', 'recording');
                voiceButton.classList.add('btn-outline-success');
                voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            } else {
                // Start recording
                try {
                    // Set language based on selected option
                    const languageCode = languageSelect.value;
                    recognition.lang = getRecognitionLanguageCode(languageCode);
                    
                    recognition.start();
                    
                    voiceButton.classList.remove('btn-outline-success');
                    voiceButton.classList.add('btn-danger', 'recording');
                    voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
                    
                    messageInput.placeholder = "Listening...";
                } catch (error) {
                    console.error('Speech recognition error:', error);
                    showNotification('Could not start voice recognition. Please check your microphone permissions.', 'danger');
                }
            }
            
            isRecording = !isRecording;
        });
        
        // Recognition events
        recognition.onresult = function(event) {
            const transcript = event.results[0][0].transcript;
            messageInput.value = transcript;
            
            // Focus on input to allow easy editing if needed
            messageInput.focus();
        };
        
        recognition.onend = function() {
            // Reset button state
            isRecording = false;
            voiceButton.classList.remove('btn-danger', 'recording');
            voiceButton.classList.add('btn-outline-success');
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            messageInput.placeholder = "Type your message here...";
        };
        
        recognition.onerror = function(event) {
            console.error('Speech recognition error:', event.error);
            showNotification(`Voice recognition error: ${event.error}`, 'danger');
            
            // Reset button state
            isRecording = false;
            voiceButton.classList.remove('btn-danger', 'recording');
            voiceButton.classList.add('btn-outline-success');
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            messageInput.placeholder = "Type your message here...";
        };
    } else {
        // Browser doesn't support speech recognition
        voiceButton.disabled = true;
        voiceButton.title = "Voice recognition not supported in this browser";
        showNotification('Voice recognition is not supported in your browser. Please use Chrome for this feature.', 'warning');
    }
    
    // Map language codes to speech recognition language codes
    function getRecognitionLanguageCode(languageCode) {
        const languageMap = {
            'en': 'en-US',
            'hi': 'hi-IN',
            'ta': 'ta-IN',
            'te': 'te-IN',
            'ml': 'ml-IN',
            'kn': 'kn-IN',
            'bn': 'bn-IN',
            'gu': 'gu-IN',
            'mr': 'mr-IN',
            'pa': 'pa-IN'
        };
        
        return languageMap[languageCode] || 'en-US';
    }
    
    // Alternative: Server-side speech recognition
    // This can be used for browsers that don't support the Web Speech API
    
    let mediaRecorder;
    let audioChunks = [];
    
    function startServerSideSpeechRecognition() {
        navigator.mediaDevices.getUserMedia({ audio: true })
            .then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                audioChunks = [];
                
                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });
                
                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks);
                    sendAudioToServer(audioBlob);
                });
                
                mediaRecorder.start();
                
                // UI updates
                voiceButton.classList.remove('btn-outline-success');
                voiceButton.classList.add('btn-danger', 'recording');
                voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
                messageInput.placeholder = "Listening...";
            })
            .catch(error => {
                console.error('Microphone access error:', error);
                showNotification('Could not access microphone. Please check your permissions.', 'danger');
            });
    }
    
    function stopServerSideSpeechRecognition() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            
            // Reset UI
            voiceButton.classList.remove('btn-danger', 'recording');
            voiceButton.classList.add('btn-outline-success');
            voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
            messageInput.placeholder = "Type your message here...";
        }
    }
    
    function sendAudioToServer(audioBlob) {
        const reader = new FileReader();
        reader.readAsDataURL(audioBlob);
        reader.onloadend = () => {
            const base64Audio = reader.result.split(',')[1];
            
            fetch('/api/speech_to_text', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    audio_data: base64Audio,
                    language: languageSelect.value
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.text) {
                    messageInput.value = data.text;
                    messageInput.focus();
                } else {
                    showNotification('Could not recognize speech. Please try again.', 'warning');
                }
            })
            .catch(error => {
                console.error('Speech recognition error:', error);
                showNotification('Error processing your speech. Please try again.', 'danger');
            });
        };
    }
});
