from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>Welcome to My Flask Backend</h1><p>This is served using Flask.</p>"

if __name__ == "__main__":
    app.run(debug=True)
