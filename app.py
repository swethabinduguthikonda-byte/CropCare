from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import pipeline
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

MODEL_NAME = "linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification"

print("Loading CropCare AI model...")

classifier = pipeline(
    "image-classification",
    model=MODEL_NAME
)

print("CropCare AI model is ready!")


def get_treatment(disease):
    name = disease.lower()

    if "healthy" in name:
        return "The model classifies this leaf as healthy. Continue regular watering and monitor the plant."

    if "blight" in name:
        return "Remove severely affected leaves, avoid overhead watering, improve air circulation, and consult an agricultural expert."

    if "rust" in name:
        return "Remove heavily affected plant material, keep foliage dry, and seek advice about suitable disease management."

    if "mildew" in name:
        return "Improve air circulation, avoid wetting leaves, and consult an agricultural expert."

    if "spot" in name or "scab" in name:
        return "Remove affected plant material where practical, avoid overhead watering, and seek local agricultural advice."

    if "virus" in name or "mosaic" in name:
        return "Seek agricultural advice, manage insect vectors, and use healthy planting material."

    return "Monitor the crop, maintain field hygiene, and consult a local agricultural expert for suitable treatment."


@app.route("/")
def home():
    return "CropCare AI Backend is Running!"


@app.route("/predict", methods=["POST"])
def predict():

    if "file" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return jsonify({"error": "No image selected"}), 400

    try:
        image = Image.open(
            io.BytesIO(uploaded_file.read())
        ).convert("RGB")

        predictions = classifier(image, top_k=3)

        best = predictions[0]
        disease_label = best["label"]
        confidence = round(best["score"] * 100, 2)

        label = disease_label.replace("_", " ").strip()
        lower_label = label.lower()

        crop_names = {
            "bell pepper": "Bell Pepper",
            "pepper bell": "Bell Pepper",
            "pepper, bell": "Bell Pepper",
            "apple": "Apple",
            "blueberry": "Blueberry",
            "cherry": "Cherry",
            "corn": "Corn",
            "grape": "Grape",
            "orange": "Orange",
            "peach": "Peach",
            "potato": "Potato",
            "raspberry": "Raspberry",
            "soybean": "Soybean",
            "squash": "Squash",
            "strawberry": "Strawberry",
            "tomato": "Tomato"
        }

        crop = "Unknown crop"

        for key, value in crop_names.items():
            if key in lower_label:
                crop = value
                break


        if "___" in disease_label:
            disease = disease_label.split("___", 1)[1]
        else:
            disease = label

        disease = disease.replace("_", " ").strip().title()

        treatment = get_treatment(disease)

        return jsonify({
            "message": "AI analysis completed successfully!",
            "status": "REAL AI MODEL PREDICTION",
            "sample_crop": crop,
            "sample_disease": disease,
            "sample_treatment": treatment,
            "confidence": confidence,
            "top_predictions": [
                {
                    "label": item["label"].replace("___", " - ").replace("_", " "),
                    "confidence": round(item["score"] * 100, 2)
                }
                for item in predictions
            ]
        })

    except Exception as error:
        return jsonify({
            "error": "Could not analyse this image: " + str(error)
        }), 400


@app.errorhandler(413)
def file_too_large(error):
    return jsonify({
        "error": "Image is too large. Please upload an image under 10 MB."
    }), 413


if __name__ == "__main__":
    app.run(debug=True, port=5000)
