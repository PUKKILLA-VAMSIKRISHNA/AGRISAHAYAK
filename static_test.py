from flask import Flask

app = Flask(__name__, static_folder='static', static_url_path='/static')

@app.route('/')
def index():
    return '''
    <html>
      <head>
        <link rel="stylesheet" href="/static/css/style.css">
        <script src="/static/js/chat.js"></script>
      </head>
      <body>
        <h1>Static Test</h1>
        <p>If you see styles and no 404s in the console, static files work!</p>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run() 