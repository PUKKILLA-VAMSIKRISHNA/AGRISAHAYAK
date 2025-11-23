// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    console.log('Chat.js loaded');
    
    const messageForm = document.getElementById('message-form');
    const messageInput = document.getElementById('message-input');
    const chatContainer = document.getElementById('chat-container');
    const chatId = document.getElementById('chat-id').value;
    const languageSelect = document.getElementById('language-select');
    const typingIndicator = document.getElementById('typing-indicator');
    const translateChatButton = document.getElementById('translate-chat');
    const textToSpeechToggle = document.getElementById('text-to-speech-toggle');
    const clearChatButton = document.getElementById('clear-chat');
    const exportChatButton = document.getElementById('export-chat');
    const audioPlayer = document.getElementById('audio-player');
    
    let autoPlayAudio = false;
    let currentLanguage = languageSelect.value;
    
    console.log('Chat elements found:', {
        messageForm: !!messageForm,
        messageInput: !!messageInput,
        chatContainer: !!chatContainer,
        chatId: chatId,
        languageSelect: !!languageSelect
    });
    
    // Test API connectivity
    function testAPI() {
        console.log('Testing API connectivity...');
        fetch('/health', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        })
        .then(response => {
            console.log('Health check response status:', response.status);
            return response.json();
        })
        .then(data => {
            console.log('Health check data:', data);
            if (data.database === 'connected') {
                console.log('✅ Database is connected');
            } else {
                console.log('❌ Database is not connected');
            }
        })
        .catch(error => {
            console.error('❌ Health check failed:', error);
        });
    }
    
    // Run API test on page load
    testAPI();
    
    // Initialize chat - scroll to bottom
    scrollToBottom();
    
    // Event listeners
    if (messageForm) {
        messageForm.addEventListener('submit', sendMessage);
    }
    if (languageSelect) {
        languageSelect.addEventListener('change', changeLanguage);
    }
    if (translateChatButton) {
        translateChatButton.addEventListener('click', translateChat);
    }
    if (textToSpeechToggle) {
        textToSpeechToggle.addEventListener('click', toggleTextToSpeech);
    }
    
    // Set up play buttons for bot messages
    setupPlayButtons();
    
    function sendMessage(e) {
        e.preventDefault();
        console.log('sendMessage called');
        
        const message = messageInput.value.trim();
        if (!message) {
            console.log('Empty message, returning');
            return;
        }
        
        console.log('Message to send:', message);
        console.log('Chat ID:', chatId);
        console.log('Current language:', currentLanguage);
        
        console.log('Sending message:', message);
        
        // Clear input
        messageInput.value = '';
        
        // Add user message to UI
        addMessageToUI(message, true);
        
        // Move typing indicator to the end and show it
        chatContainer.appendChild(typingIndicator);
        typingIndicator.style.display = 'block';
        scrollToBottom();
        
        const requestData = {
            chat_id: chatId,
            message: message,
            language: currentLanguage
        };
        
        console.log('Request data:', requestData);
        
        // Send message to server
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Requested-With': 'XMLHttpRequest'
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Response data:', data);
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            // Add bot response to UI
            addMessageToUI(data.response, false, data.message_id);
            
            // Auto-play audio if enabled
            if (autoPlayAudio) {
                playMessageAudio(data.message_id);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            typingIndicator.style.display = 'none';
            showNotification('There was an error sending your message. Please try again. Error: ' + error.message, 'danger');
        });
    }
    
    function addMessageToUI(content, isUser, messageId = null) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'message-user' : 'message-bot'}`;
        
        const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        let messageContent = content;
        if (!isUser) {
            // Process links in the content
            messageContent = processMarkdown(content);
        }
        
        messageDiv.innerHTML = `
            <div class="message-content">
                ${isUser ? content : `<div class="markdown-content">${messageContent}</div>`}
            </div>
            <div class="message-time">
                ${currentTime}
                ${!isUser && messageId ? `
                    <button class="btn btn-sm btn-link text-light p-0 ms-2 play-message" data-message-id="${messageId}">
                        <i class="fas fa-volume-up"></i>
                    </button>
                ` : ''}
            </div>
        `;
        
        chatContainer.appendChild(messageDiv);
        scrollToBottom();
        
        // Set up play button for new message
        if (!isUser && messageId) {
            const playButtons = messageDiv.querySelectorAll('.play-message');
            playButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const msgId = this.getAttribute('data-message-id');
                    playMessageAudio(msgId);
                });
            });
        }
    }
    
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
    
    function setupPlayButtons() {
        const playButtons = document.querySelectorAll('.play-message');
        playButtons.forEach(button => {
            button.addEventListener('click', function() {
                const messageId = this.getAttribute('data-message-id');
                playMessageAudio(messageId);
            });
        });
    }
    
    function playMessageAudio(messageId) {
              // Find the specific message content by messageId
              const messageElement = document.querySelector(`.play-message[data-message-id="${messageId}"]`).closest('.message').querySelector('.markdown-content');
        if (!messageElement) return;
        
        const messageText = messageElement.textContent;
        
        // Convert message to speech
        fetch('/api/text_to_speech', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                text: messageText,
                language: currentLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.audio_data) {
                audioPlayer.src = `data:audio/mp3;base64,${data.audio_data}`;
                audioPlayer.play();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Failed to generate audio.', 'danger');
        });
    }
    
    function changeLanguage() {
        currentLanguage = languageSelect.value;
        showNotification(`Language changed to ${languageSelect.options[languageSelect.selectedIndex].text}`, 'info');
    }
    
    // Helper function to show notifications (copied from main.js)
    function showNotification(message, type = 'success') {
        const alertContainer = document.createElement('div');
        alertContainer.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertContainer.style.zIndex = '1050';
        alertContainer.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alertContainer);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            try {
                // Try to use Bootstrap Alert if available
                if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                    const bsAlert = new bootstrap.Alert(alertContainer);
                    bsAlert.close();
                } else {
                    // Fallback: just remove the element
                    alertContainer.remove();
                }
            } catch (error) {
                // Fallback: just remove the element
                alertContainer.remove();
            }
        }, 5000);
    }
    
    function translateChat() {
        // Get all bot messages
        const botMessages = document.querySelectorAll('.message-bot .markdown-content');
        if (botMessages.length === 0) {
            showNotification('No messages to translate.', 'info');
            return;
        }
        
        showNotification('Translating chat messages...', 'info');
        console.log('Starting translation for', botMessages.length, 'messages');
        console.log('Current language:', currentLanguage);
        
        botMessages.forEach((messageElement, index) => {
            const originalText = messageElement.textContent;
            console.log(`Translating message ${index + 1}:`, originalText);
            
            fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    text: originalText,
                    language: currentLanguage
                })
            })
            .then(response => {
                console.log(`Translation response status for message ${index + 1}:`, response.status);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log(`Translation data for message ${index + 1}:`, data);
                if (data.translated_text) {
                    messageElement.innerHTML = processMarkdown(data.translated_text);
                    console.log(`Successfully translated message ${index + 1}`);
                } else {
                    console.warn(`No translated_text received for message ${index + 1}`);
                }
            })
            .catch(error => {
                console.error(`Translation error for message ${index + 1}:`, error);
                showNotification(`Translation failed for message ${index + 1}: ${error.message}`, 'danger');
            });
        });
    }
    
    function toggleTextToSpeech() {
        autoPlayAudio = !autoPlayAudio;
        textToSpeechToggle.innerHTML = autoPlayAudio ? 
            '<i class="fas fa-volume-up text-success"></i>' : 
            '<i class="fas fa-volume-up"></i>';
        
        showNotification(
            autoPlayAudio ? 
            'Text-to-speech enabled. Responses will be read aloud.' : 
            'Text-to-speech disabled.', 
            'info'
        );
    }
    
    function processMarkdown(text) {
        // Basic Markdown processing
        // Headers
        text = text.replace(/### (.*?)(?:\n|$)/g, '<h5>$1</h5>');
        text = text.replace(/## (.*?)(?:\n|$)/g, '<h4>$1</h4>');
        text = text.replace(/# (.*?)(?:\n|$)/g, '<h3>$1</h3>');
        
        // Bold and italic
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        text = text.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Lists
        text = text.replace(/^\s*\-\s+(.*?)(?:\n|$)/gm, '<li>$1</li>');
        text = text.replace(/(<li>.*?<\/li>)/gs, '<ul>$1</ul>');
        
        // Replace multiple <ul> tags that follow each other with a single <ul>
        text = text.replace(/<\/ul>\s*<ul>/g, '');
        
        // Links
        text = text.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" class="text-success">$1</a>');
        
        // YouTube links
        const youtubeRegex = /https?:\/\/(www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]+)/g;
        const matches = text.matchAll(youtubeRegex);
        
        for (const match of matches) {
            const youtubeLink = match[0];
            const videoId = match[2];
            const youtubeEmbed = `
                <div class="youtube-preview">
                    <img src="https://img.youtube.com/vi/${videoId}/0.jpg" alt="YouTube Thumbnail">
                    <div class="youtube-preview-content">
                        <h6>YouTube Video</h6>
                        <p>Click to watch this recommended video</p>
                        <a href="${youtubeLink}" target="_blank" class="btn btn-sm btn-outline-success">Watch</a>
                    </div>
                </div>
            `;
            text = text.replace(youtubeLink, youtubeEmbed);
        }
        
        // Convert newlines to <br> for remaining text
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }
    
    // Clear chat functionality
    if (clearChatButton) {
        clearChatButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            if (confirm('Are you sure you want to clear this chat? This cannot be undone.')) {
                // Remove all messages except the typing indicator
                const messages = document.querySelectorAll('.message:not(#typing-indicator)');
                messages.forEach(message => message.remove());
                
                showNotification('Chat cleared.', 'info');
            }
        });
    }
    
    // Export chat functionality
    if (exportChatButton) {
        exportChatButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent dropdown from closing
            
            // Collect all messages
            const messages = [];
            document.querySelectorAll('.message:not(#typing-indicator)').forEach(messageEl => {
                const isUser = messageEl.classList.contains('message-user');
                const content = messageEl.querySelector('.message-content').textContent.trim();
                const time = messageEl.querySelector('.message-time').textContent.trim().split('\n')[0];
                
                if (content) {
                    messages.push({
                        sender: isUser ? 'You' : 'AgriSahayak',
                        content: content,
                        time: time
                    });
                }
            });
            
            // Create text content
            let textContent = `# Chat Export - ${new Date().toLocaleDateString()}\n\n`;
            
            messages.forEach(message => {
                textContent += `## ${message.sender} (${message.time})\n${message.content}\n\n`;
            });
            
            // Create download link
            const blob = new Blob([textContent], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat-export-${new Date().toISOString().slice(0, 10)}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            showNotification('Chat exported successfully.', 'success');
        });
    }

    // Delete chat functionality
    document.querySelectorAll('.delete-chat').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Prevent the chat link from being clicked
            
            const chatId = this.getAttribute('data-chat-id');
            
            if (confirm('Are you sure you want to delete this chat? This action cannot be undone.')) {
                fetch(`/api/delete_chat/${chatId}`, {
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Remove the chat item from the list
                        const chatItem = this.closest('.list-group-item');
                        chatItem.remove();
                        
                        // If this was the current chat, redirect to new chat
                        if (chatId === document.getElementById('chat-id').value) {
                            window.location.href = '/chat/new';
                        }
                        
                        showNotification('Chat deleted successfully.', 'success');
                    } else {
                        throw new Error('Failed to delete chat');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('There was an error deleting the chat. Please try again.', 'danger');
                });
            }
        });
    });
});
