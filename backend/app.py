
import os
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename

from detection.analyzer import UPIAnalyzer

app = Flask(__name__)
CORS(app)

# Upload configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


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


@app.route("/api/analyze", methods=["POST"])
def analyze_screenshot():

    if "image" not in request.files:
        return jsonify({
            "error": "No image uploaded. Use the field name 'image'."
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "error": "No file selected."
        }), 400

    if not allowed_file(image.filename):
        return jsonify({
            "error": "Unsupported file type. Upload PNG, JPG, JPEG or WEBP."
        }), 400

    # Generate a unique filename to avoid overwriting uploads
    original_name = secure_filename(image.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{extension}"
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    try:
        image.save(image_path)

        # Run the UPI Shield analysis pipeline
        result = UPIAnalyzer.analyze_image(image_path)

        return jsonify(result), 200

    except Exception as error:
        app.logger.exception("Screenshot analysis failed")

        return jsonify({
            "error": "Screenshot analysis failed.",
            "details": str(error)
        }), 500

    finally:
        # Remove uploaded image after analysis
        if os.path.exists(image_path):
            os.remove(image_path)


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "File too large. Maximum allowed size is 10 MB."
    }), 413


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=2807,
        debug=True
    )
