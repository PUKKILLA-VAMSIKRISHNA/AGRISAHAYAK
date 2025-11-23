#!/usr/bin/env python3
"""
Static file embeddings for Vercel deployment
This module contains static files as base64 encoded strings
"""

import base64
import os

def get_static_file_content(file_path):
    """Get content of a static file, either from embedded data or from local file"""
    # In production, files will be embedded here
    # For now, try to read from local filesystem
    try:
        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                return f.read()
        return None
    except:
        return None

def get_css_style_css():
    """Get style.css content"""
    content = get_static_file_content('public/css/style.css')
    if content:
        return content.decode('utf-8')
    return """/* Fallback CSS */
body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
.container { max-width: 1200px; margin: 0 auto; }
.navbar { background: #28a745; color: white; padding: 1rem; }
.btn { padding: 0.5rem 1rem; border: none; border-radius: 4px; cursor: pointer; }
.btn-primary { background: #007bff; color: white; }
"""

def get_js_main_js():
    """Get main.js content"""
    content = get_static_file_content('public/js/main.js')
    if content:
        return content.decode('utf-8')
    return """// Fallback main.js
console.log('Main.js loaded (fallback)');
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded');
});
"""

def get_js_chat_js():
    """Get chat.js content"""
    content = get_static_file_content('public/js/chat.js')
    if content:
        return content.decode('utf-8')
    return """// Fallback chat.js
console.log('Chat.js loaded (fallback)');

function sendMessage() {
    console.log('Send message clicked');
    const messageInput = document.getElementById('message-input');
    const message = messageInput.value.trim();
    
    if (message) {
        console.log('Sending message:', message);
        messageInput.value = '';
        // Add fallback message sending logic here
    }
}

document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send-button');
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    
    const messageForm = document.getElementById('message-form');
    if (messageForm) {
        messageForm.addEventListener('submit', function(e) {
            e.preventDefault();
            sendMessage();
        });
    }
});
"""

def get_js_voice_js():
    """Get voice.js content"""
    content = get_static_file_content('public/js/voice.js')
    if content:
        return content.decode('utf-8')
    return """// Fallback voice.js
console.log('Voice.js loaded (fallback)');

function startVoiceRecording() {
    console.log('Voice recording started');
    // Add fallback voice recording logic here
}

function stopVoiceRecording() {
    console.log('Voice recording stopped');
    // Add fallback voice recording logic here
}
"""

def get_languages_json():
    """Get languages.json content"""
    content = get_static_file_content('public/data/languages.json')
    if content:
        return content.decode('utf-8')
    return """[
    {"code": "en", "name": "English", "native_name": "English"},
    {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
    {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
    {"code": "te", "name": "Telugu", "native_name": "తెలుగు"},
    {"code": "bn", "name": "Bengali", "native_name": "বাংলা"},
    {"code": "mr", "name": "Marathi", "native_name": "मराठी"},
    {"code": "gu", "name": "Gujarati", "native_name": "ગુજરાતી"},
    {"code": "kn", "name": "Kannada", "native_name": "ಕನ್ನಡ"},
    {"code": "ml", "name": "Malayalam", "native_name": "മലയാളം"},
    {"code": "pa", "name": "Punjabi", "native_name": "ਪੰਜਾਬੀ"}
]"""
