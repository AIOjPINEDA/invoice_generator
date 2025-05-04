from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return """
    <html>
        <head>
            <title>Flask Test</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                }
                h1 {
                    color: #4285f4;
                }
            </style>
        </head>
        <body>
            <h1>Flask is working!</h1>
            <p>If you can see this message, your Flask installation is working correctly.</p>
            <p>Now try running the full invoice generator application.</p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Testing Flask installation...")
    print("Open your browser and go to: http://localhost:5000")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='0.0.0.0')
