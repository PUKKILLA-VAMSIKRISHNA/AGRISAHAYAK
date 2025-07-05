import json
from flask import render_template, redirect, url_for, flash, request, jsonify, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, Chat, Message, UserProfile
from chatbot import get_chatbot_response, get_crop_recommendations, get_youtube_videos
from utils import get_weather_data, translate_text, text_to_speech, speech_to_text
from email_utils import (
    generate_otp, generate_reset_token, send_verification_email,
    send_password_reset_email, verify_otp, verify_reset_token,
    EmailVerification, PasswordReset
)

def init_routes(app):
    # Home route
    @app.route('/')
    def index():
        return render_template('index.html')

    # Authentication routes
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                if not user.is_email_verified:
                    flash('Please verify your email before logging in.', 'warning')
                    return redirect(url_for('verify_email', email=email))
                
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
            else:
                flash('Invalid email or password', 'danger')
        
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            location = request.form.get('location', '')
            language = request.form.get('language', 'en')
            
            # Validation
            if password != confirm_password:
                flash('Passwords do not match', 'danger')
                return render_template('register.html')
            
            # Check for existing username
            existing_username = User.query.filter_by(username=username).first()
            if existing_username:
                flash('Username already taken. Please choose a different username.', 'danger')
                return render_template('register.html')
            
            # Check for existing email
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Email already registered. Please use a different email or login.', 'danger')
                return render_template('register.html')
            
            try:
                # Generate OTP first
                otp = generate_otp()
                
                # Try sending the email first before creating any database records
                send_verification_email(email, otp)
                
                # If email sends successfully, then create user and verification records
                new_user = User(
                    username=username,
                    email=email,
                    preferred_language=language,
                    location=location,
                    is_email_verified=False
                )
                new_user.set_password(password)
                
                verification = EmailVerification(email=email, otp=otp)
                
                # Start database transaction
                db.session.begin_nested()
                try:
                    db.session.add(new_user)
                    db.session.add(verification)
                    db.session.commit()
                    
                    # Create user profile
                    profile = UserProfile(user_id=new_user.id)
                    db.session.add(profile)
                    db.session.commit()
                    
                    flash('Registration successful. Please check your email for verification code.', 'success')
                    return redirect(url_for('verify_email', email=email))
                    
                except Exception as db_error:
                    db.session.rollback()
                    flash('Database error occurred. Please try again.', 'danger')
                    print(f"Database error: {str(db_error)}")
                    return render_template('register.html')
                    
            except Exception as email_error:
                flash('Failed to send verification email. Please try again or contact support.', 'danger')
                print(f"Email error: {str(email_error)}")
                return render_template('register.html')
        
        # Load available languages
        with open('static/data/languages.json', 'r', encoding='utf-8') as f:
            languages = json.load(f)
        
        return render_template('register.html', languages=languages)

    @app.route('/verify_email/<email>', methods=['GET', 'POST'])
    def verify_email(email):
        if request.method == 'POST':
            otp = request.form.get('otp')
            
            if verify_otp(email, otp):
                user = User.query.filter_by(email=email).first()
                user.is_email_verified = True
                db.session.commit()
                
                flash('Email verified successfully. Please login.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Invalid or expired OTP. Please try again.', 'danger')
        
        return render_template('verify_email.html', email=email)

    @app.route('/resend_otp/<email>')
    def resend_otp(email):
        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('Email not found.', 'danger')
            return redirect(url_for('register'))
        
        if user.is_email_verified:
            flash('Email already verified.', 'info')
            return redirect(url_for('login'))
        
        # Generate and send new OTP
        otp = generate_otp()
        verification = EmailVerification(email=email, otp=otp)
        db.session.add(verification)
        db.session.commit()
        
        try:
            send_verification_email(email, otp)
            flash('New verification code sent. Please check your email.', 'success')
        except Exception as e:
            flash('Failed to send verification email. Please try again.', 'danger')
        
        return redirect(url_for('verify_email', email=email))

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        if request.method == 'POST':
            email = request.form.get('email')
            user = User.query.filter_by(email=email).first()
            
            if user:
                token = generate_reset_token()
                reset = PasswordReset(email=email, token=token)
                db.session.add(reset)
                db.session.commit()
                
                try:
                    send_password_reset_email(email, token)
                    flash('Password reset instructions sent to your email.', 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    flash('Failed to send reset email. Please try again.', 'danger')
            else:
                flash('Email not found.', 'danger')
        
        return render_template('forgot_password.html')

    @app.route('/reset_password/<token>', methods=['GET', 'POST'])
    def reset_password(token):
        email = verify_reset_token(token)
        
        if not email:
            flash('Invalid or expired reset link.', 'danger')
            return redirect(url_for('forgot_password'))
        
        if request.method == 'POST':
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if password != confirm_password:
                flash('Passwords do not match.', 'danger')
                return render_template('reset_password.html', token=token)
            
            user = User.query.filter_by(email=email).first()
            user.set_password(password)
            
            # Mark reset token as used
            reset = PasswordReset.query.filter_by(token=token).first()
            reset.is_used = True
            db.session.commit()
            
            flash('Password reset successful. Please login with your new password.', 'success')
            return redirect(url_for('login'))
        
        return render_template('reset_password.html', token=token)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('index'))

    # Main application routes
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get user's chats
        chats = Chat.query.filter_by(user_id=current_user.id).order_by(Chat.created_at.desc()).all()
        
        # Get user profile
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # Get weather data for user's location if available
        weather_data = None
        if current_user.location:
            weather_data = get_weather_data(current_user.location)
        
        return render_template('dashboard.html', 
                               chats=chats, 
                               profile=profile, 
                               weather_data=weather_data)

    @app.route('/chat/<int:chat_id>')
    @login_required
    def chat(chat_id):
        chat = Chat.query.get_or_404(chat_id)
        
        # Ensure the chat belongs to the current user
        if chat.user_id != current_user.id:
            flash('You do not have permission to view this chat', 'danger')
            return redirect(url_for('dashboard'))
        
        messages = Message.query.filter_by(chat_id=chat.id).order_by(Message.created_at).all()
        
        # Load available languages
        with open('static/data/languages.json', 'r', encoding='utf-8') as f:
            languages = json.load(f)
        
        return render_template('chat.html', chat=chat, messages=messages, languages=languages)

    @app.route('/chat/new')
    @login_required
    def new_chat():
        chat = Chat(user_id=current_user.id, title="New Chat")
        db.session.add(chat)
        db.session.commit()
        
        return redirect(url_for('chat', chat_id=chat.id))

    @app.route('/api/send_message', methods=['POST'])
    @login_required
    def send_message():
        data = request.json
        chat_id = data.get('chat_id')
        message_content = data.get('message')
        language = data.get('language', current_user.preferred_language)
        
        # Validate chat ownership
        chat = Chat.query.get_or_404(chat_id)
        if chat.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Save user message
        user_message = Message(chat_id=chat_id, content=message_content, is_user=True)
        db.session.add(user_message)
        db.session.commit()
        
        # Get user profile for context
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        # Get response from chatbot
        response = get_chatbot_response(message_content, profile, language)
        
        # Save bot response
        bot_message = Message(chat_id=chat_id, content=response, is_user=False)
        db.session.add(bot_message)
        db.session.commit()
        
        # Update chat title if it's a new chat
        if chat.title == "New Chat":
            # Extract a title from the first user message
            title = message_content[:50] + "..." if len(message_content) > 50 else message_content
            chat.title = title
            db.session.commit()
        
        return jsonify({
            'response': response,
            'message_id': bot_message.id
        })

    @app.route('/api/delete_chat/<int:chat_id>', methods=['DELETE'])
    @login_required
    def delete_chat(chat_id):
        chat = Chat.query.get_or_404(chat_id)
        
        # Ensure the chat belongs to the current user
        if chat.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        try:
            # Delete all messages associated with the chat
            Message.query.filter_by(chat_id=chat.id).delete()
            
            # Delete the chat
            db.session.delete(chat)
            db.session.commit()
            
            return jsonify({'message': 'Chat deleted successfully'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'Failed to delete chat'}), 500

    @app.route('/api/get_crop_recommendations', methods=['POST'])
    @login_required
    def api_get_crop_recommendations():
        data = request.json
        soil_type = data.get('soil_type')
        soil_ph = data.get('soil_ph')
        location = data.get('location', current_user.location)
        language = data.get('language', current_user.preferred_language)
        
        recommendations = get_crop_recommendations(soil_type, soil_ph, location, language)
        
        return jsonify({'recommendations': recommendations})

    @app.route('/api/get_youtube_videos', methods=['POST'])
    @login_required
    def api_get_youtube_videos():
        data = request.json
        query = data.get('query')
        language = data.get('language', current_user.preferred_language)
        
        videos = get_youtube_videos(query, language)
        
        return jsonify({'videos': videos})

    @app.route('/api/translate', methods=['POST'])
    @login_required
    def api_translate():
        data = request.json
        text = data.get('text')
        target_language = data.get('language')
        
        translated_text = translate_text(text, target_language)
        
        return jsonify({'translated_text': translated_text})

    @app.route('/api/text_to_speech', methods=['POST'])
    @login_required
    def api_text_to_speech():
        data = request.json
        text = data.get('text')
        language = data.get('language', current_user.preferred_language)
        
        audio_base64 = text_to_speech(text, language)
        
        return jsonify({'audio_data': audio_base64})

    @app.route('/api/speech_to_text', methods=['POST'])
    @login_required
    def api_speech_to_text():
        data = request.json
        audio_data = data.get('audio_data')
        language = data.get('language', current_user.preferred_language)
        
        text = speech_to_text(audio_data, language)
        
        return jsonify({'text': text})

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        profile = UserProfile.query.filter_by(user_id=current_user.id).first()
        
        if request.method == 'POST':
            # Update user information
            current_user.username = request.form.get('username')
            current_user.email = request.form.get('email')
            current_user.location = request.form.get('location')
            current_user.preferred_language = request.form.get('language')
            
            # Update profile information
            profile.soil_type = request.form.get('soil_type')
            profile.soil_ph = float(request.form.get('soil_ph', 0))
            profile.farm_size = float(request.form.get('farm_size', 0))
            profile.farm_location = request.form.get('farm_location')
            profile.crops_grown = request.form.get('crops_grown')
            
            db.session.commit()
            flash('Profile updated successfully', 'success')
            return redirect(url_for('profile'))
        
        # Load available languages
        with open('static/data/languages.json', 'r', encoding='utf-8') as f:
            languages = json.load(f)
        
        return render_template('profile.html', profile=profile, languages=languages)
