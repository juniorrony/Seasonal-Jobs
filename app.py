import json
from flask import Flask, render_template

app = Flask(__name__)

# Load JSON data
with open("case.json", "r", encoding="utf-8") as file:
    data = json.load(file)

@app.route("/")
def index():
    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)