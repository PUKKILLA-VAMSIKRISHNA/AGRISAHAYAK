from flask import Flask, send_from_directory
import os

app = Flask(__name__, static_folder='public', static_url_path='/static')

@app.route('/')
def index():
    return '''
    <html>
      <head>
        <title>Static File Test</title>
        <link rel="stylesheet" href="/static/css/style.css">
        <script src="/static/js/main.js"></script>
        <script src="/static/js/chat.js"></script>
        <script src="/static/js/voice.js"></script>
      </head>
      <body>
        <h1>Static File Test</h1>
        <p>If you see styles and no 404s in the console, static files work!</p>
        <div id="test-notification"></div>
        <script>
          // Test if showNotification function is available
          if (typeof showNotification === 'function') {
            showNotification('Static files are working!', 'success');
          } else {
            document.getElementById('test-notification').innerHTML = 
              '<p style="color: red;">showNotification function not found!</p>';
          }
        </script>
      </body>
    </html>
    '''

@app.route('/test-static/<path:filename>')
def test_static(filename):
    """Test endpoint to check if static files are accessible"""
    try:
        return send_from_directory('public', filename)
    except Exception as e:
        return f"Error serving {filename}: {str(e)}", 404

if __name__ == '__main__':
    app.run(debug=True) 