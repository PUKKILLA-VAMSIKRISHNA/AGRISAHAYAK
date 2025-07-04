# FarmWise Chatbot

A Flask-based web application for agricultural assistance and information.

## Features

- Interactive chatbot interface
- Agricultural information and guidance
- User-friendly web interface

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your environment variables
5. Run the application:
   ```bash
   python app.py
   ```

## Environment Variables

Create a `.env` file with the following variables:
```
FLASK_APP=app.py
FLASK_ENV=development
# Add other environment variables as needed
```

## Deployment

This application can be deployed to Render.com using the free tier.

## License

MIT License 