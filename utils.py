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

def generate_content_with_fallback(prompt):
    """
    Generate content using Gemini API, trying multiple model names if one fails.
    Returns the response from the first successful model.
    Note: genai.configure() must be called before this function.
    """
    import google.generativeai as genai
    
    model_names = [
        'gemini-1.5-flash-latest',  # Latest flash model
        'gemini-flash-latest',       # Alternative flash model name
        'gemini-1.5-flash-002',      # Specific flash version
        'gemini-1.5-pro',            # Pro model (more stable)
        'gemini-1.5-pro-latest',     # Latest pro model
        'gemini-pro'                 # Fallback to older stable model
    ]
    
    last_error = None
    for model_name in model_names:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            current_app.logger.debug(f"Successfully used Gemini model: {model_name}")
            return response
        except Exception as e:
            error_msg = str(e)
            last_error = e
            # Check if it's a 404 or model not found error
            if '404' in error_msg or 'not found' in error_msg.lower() or 'not supported' in error_msg.lower():
                current_app.logger.debug(f"Model {model_name} not available: {error_msg}")
                continue
            else:
                # For other errors, log and re-raise
                current_app.logger.error(f"Error with model {model_name}: {error_msg}")
                raise
    
    # If all models failed, raise the last error
    if last_error:
        raise last_error
    else:
        raise Exception("No available Gemini models found")

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
        # Try static folder first (created by build.py), fallback to public
        base_folder = 'static' if os.path.exists('static') else 'public'
        json_path = os.path.join(os.path.dirname(__file__), base_folder, 'data', 'languages.json')
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                languages = json.load(f)
        except FileNotFoundError:
            # Fallback languages if file not found
            languages = [
                {"code": "en", "name": "English", "native_name": "English"},
                {"code": "hi", "name": "Hindi", "native_name": "हिन्दी"},
                {"code": "ta", "name": "Tamil", "native_name": "தமிழ்"},
                {"code": "te", "name": "Telugu", "native_name": "తెలుగు"}
            ]
        
        language_name = next((lang['name'] for lang in languages if lang['code'] == target_language), target_language)
        
        print(f"Translating to {language_name} (code: {target_language})")
        prompt = f"Translate the following text to {language_name}. Return only the translated text without any explanations:\n\n{text}"
        
        response = generate_content_with_fallback(prompt)
        
        translated_text = response.text.strip()
        print(f"Translation result: {translated_text[:100]}...")
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
