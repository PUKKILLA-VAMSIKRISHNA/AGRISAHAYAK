// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
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
    
    // Initialize chat - scroll to bottom
    scrollToBottom();
    
    // Event listeners
    messageForm.addEventListener('submit', sendMessage);
    languageSelect.addEventListener('change', changeLanguage);
    translateChatButton.addEventListener('click', translateChat);
    textToSpeechToggle.addEventListener('click', toggleTextToSpeech);
    
    // Set up play buttons for bot messages
    setupPlayButtons();
    
    function sendMessage(e) {
        e.preventDefault();
        
        const message = messageInput.value.trim();
        if (!message) return;
        
        // Clear input
        messageInput.value = '';
        
        // Add user message to UI
        addMessageToUI(message, true);
        
        // Move typing indicator to the end and show it
        chatContainer.appendChild(typingIndicator);
        typingIndicator.style.display = 'block';
        scrollToBottom();
        
        // Send message to server
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                chat_id: chatId,
                message: message,
                language: currentLanguage
            })
        })
        .then(response => response.json())
        .then(data => {
            // Hide typing indicator
            typingIndicator.style.display = 'none';
            
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
            showNotification('There was an error sending your message. Please try again.', 'danger');
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
    
    function translateChat() {
        // Get all bot messages
        const botMessages = document.querySelectorAll('.message-bot .markdown-content');
        if (botMessages.length === 0) return;
        
        showNotification('Translating chat messages...', 'info');
        
        botMessages.forEach(messageElement => {
            const originalText = messageElement.textContent;
            
            fetch('/api/translate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: originalText,
                    language: currentLanguage
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.translated_text) {
                    messageElement.innerHTML = processMarkdown(data.translated_text);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('Translation failed. Please try again.', 'danger');
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
