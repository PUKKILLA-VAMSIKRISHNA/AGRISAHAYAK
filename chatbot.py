import os
import json
import requests
import google.generativeai as genai
from flask import current_app

# Load crop data
def load_crop_data():
    with open('public/data/crops.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_chatbot_response(message, user_profile, language='en'):
    """
    Get a response from the Gemini 2.0 Flash model
    """
    try:
        # Initialize Gemini API
        GEMINI_API_KEY = current_app.config['GEMINI_API_KEY']
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Create context from user profile
        context = "You are an agricultural assistant chatbot helping Indian farmers."
        
        if user_profile:
            context += f" The farmer is from {user_profile.farm_location or 'India'}."
            if user_profile.soil_type:
                context += f" They have {user_profile.soil_type} soil with pH {user_profile.soil_ph}."
            if user_profile.crops_grown:
                context += f" They grow {user_profile.crops_grown}."
        
        # Add instructions to provide structured advice
        instructions = """
        Based on the farmer's query, provide helpful agricultural advice.
        If they ask about crops, suggest suitable options for their conditions.
        If they ask about pests or diseases, provide identification tips and organic/chemical treatment options.
        If they ask about irrigation, provide a schedule based on crop and season.
        Structure your response clearly with headings and bullet points when appropriate.
        Make your response informative but concise and easy to understand.
        If they ask for videos, mention that you can suggest YouTube videos for them to watch.
        """
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(
            f"{context}\n\n{instructions}\n\nFarmer's query: {message}"
        )
        
        formatted_response = response.text
        
        # If the language isn't English, we'll need to translate the response
        if language != 'en':
            # Import here to avoid circular imports
            from utils import translate_text
            formatted_response = translate_text(formatted_response, language)
            
        return formatted_response
    
    except Exception as e:
        current_app.logger.error(f"Error generating chatbot response: {str(e)}")
        return "I'm sorry, I'm having trouble processing your request right now. Please try again later."

def get_crop_recommendations(soil_type, soil_ph, location, language='en'):
    """
    Get crop recommendations based on soil type, pH and location
    """
    try:
        # Initialize Gemini API
        GEMINI_API_KEY = current_app.config['GEMINI_API_KEY']
        genai.configure(api_key=GEMINI_API_KEY)
        
        crops_data = load_crop_data()
        
        # Filter crops based on soil type and pH
        suitable_crops = []
        for crop in crops_data:
            if soil_type.lower() in crop['suitable_soil_types'] and \
               float(soil_ph) >= crop['min_ph'] and float(soil_ph) <= crop['max_ph']:
                suitable_crops.append(crop)
        
        # Generate prompt for Gemini
        prompt = f"""
        Based on the following information:
        - Soil type: {soil_type}
        - Soil pH: {soil_ph}
        - Location: {location}
        
        Provide crop recommendations for an Indian farmer. For each recommended crop, include:
        1. Best planting season
        2. Water requirements
        3. Expected yield
        4. Common pests and diseases to watch for
        5. Basic care instructions
        
        Format the response in a clear, structured way.
        """
        
        # Generate response using Gemini
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        recommendations = response.text
        
        # If the language isn't English, translate the response
        if language != 'en':
            from utils import translate_text
            recommendations = translate_text(recommendations, language)
            
        return recommendations
    
    except Exception as e:
        current_app.logger.error(f"Error generating crop recommendations: {str(e)}")
        return "I'm sorry, I couldn't generate crop recommendations at this time. Please try again later."

def get_youtube_videos(query, language='en'):
    """
    Get relevant YouTube videos based on a query
    """
    try:
        # Get YouTube API key
        YOUTUBE_API_KEY = current_app.config['YOUTUBE_API_KEY']
        
        # Enhance the query for better results
        enhanced_query = f"agriculture farming {query} india tutorial"
        
        # Translate query to English if needed
        if language != 'en':
            from utils import translate_text
            enhanced_query = translate_text(enhanced_query, 'en')
        
        # Call YouTube API
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'part': 'snippet',
            'q': enhanced_query,
            'key': YOUTUBE_API_KEY,
            'maxResults': 5,
            'type': 'video',
            'relevanceLanguage': 'en'  # Default to English for wider results
        }
        
        response = requests.get(url, params=params)
        results = response.json()
        
        videos = []
        if 'items' in results:
            for item in results['items']:
                video = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                videos.append(video)
        
        # If language isn't English, translate titles and descriptions
        if language != 'en':
            from utils import translate_text
            for video in videos:
                video['title'] = translate_text(video['title'], language)
                video['description'] = translate_text(video['description'], language)
        
        return videos
    
    except Exception as e:
        current_app.logger.error(f"Error fetching YouTube videos: {str(e)}")
        return []
