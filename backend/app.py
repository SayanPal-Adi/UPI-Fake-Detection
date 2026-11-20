
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Enable API communication with the Android frontend
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "project": "UPI Shield",
        "description": "Fake UPI Payment Screenshot Detector",
        "status": "Running"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "backend": "operational"
    })


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=2807,
        debug=True
    )
