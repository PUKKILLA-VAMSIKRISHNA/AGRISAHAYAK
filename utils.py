import os
import base64
import requests
import json
from io import BytesIO
from gtts import gTTS
import speech_recognition as sr
from flask import current_app

def get_weather_data(location):
    """
    Get weather data using WeatherAPI.com
    """
    try:
        api_key = current_app.config['WEATHER_API_KEY']
        base_url = "http://api.weatherapi.com/v1/current.json"
        
        params = {
            'key': api_key,
            'q': location,
            'aqi': 'no'
        }
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        if response.ok:
            return {
                'temperature': data['current']['temp_c'],
                'humidity': data['current']['humidity'],
                'description': data['current']['condition']['text'],
                'wind_speed': data['current']['wind_kph'],
                'icon': data['current']['condition']['icon'],
                'location': f"{data['location']['name']}, {data['location']['region']}"
            }
        else:
            current_app.logger.error(f"Weather API error: {data.get('error', {}).get('message')}")
            return None
            
    except Exception as e:
        current_app.logger.error(f"Error fetching weather data: {str(e)}")
        return None

def translate_text(text, target_language):
    """
    Translate text to target language using Google Generative AI
    """
    try:
        # Use Gemini model for translation
        import google.generativeai as genai
        
        GEMINI_API_KEY = current_app.config['GEMINI_API_KEY']
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Load language data to get the full language name
        with open('static/data/languages.json', 'r', encoding='utf-8') as f:
            languages = json.load(f)
        
        language_name = next((lang['name'] for lang in languages if lang['code'] == target_language), target_language)
        
        prompt = f"Translate the following text to {language_name}. Return only the translated text without any explanations:\n\n{text}"
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        translated_text = response.text.strip()
        return translated_text
    
    except Exception as e:
        current_app.logger.error(f"Translation error: {str(e)}")
        return text  # Return original text if translation fails

def text_to_speech(text, language='en'):
    """
    Convert text to speech and return as base64 encoded audio
    """
    try:
        # Map language codes to gTTS language codes
        language_map = {
            'en': 'en',
            'hi': 'hi',
            'ta': 'ta',
            'te': 'te',
            'ml': 'ml',
            'kn': 'kn',
            'bn': 'bn',
            'gu': 'gu',
            'mr': 'mr',
            'pa': 'pa'
        }
        
        tts_lang = language_map.get(language, 'en')
        
        # Generate speech
        tts = gTTS(text=text, lang=tts_lang, slow=False)
        
        # Save to BytesIO object
        fp = BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        # Convert to base64
        audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
        
        return audio_base64
    
    except Exception as e:
        current_app.logger.error(f"Text-to-speech error: {str(e)}")
        return None

def speech_to_text(audio_data, language='en'):
    """
    Convert speech to text from base64 encoded audio
    """
    try:
        # Map language codes to speech recognition language codes
        language_map = {
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
        }
        
        recognition_lang = language_map.get(language, 'en-US')
        
        # Decode base64 audio
        audio_bytes = base64.b64decode(audio_data)
        
        # Save to BytesIO object
        audio_file = BytesIO(audio_bytes)
        
        # Recognize speech
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=recognition_lang)
            
        return text
    
    except Exception as e:
        current_app.logger.error(f"Speech-to-text error: {str(e)}")
        return ""
