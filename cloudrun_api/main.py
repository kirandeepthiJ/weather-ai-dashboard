import os
import json
import logging
import requests
from flask import Flask, jsonify, make_response
from google.cloud import storage
from vertexai.generative_models import GenerativeModel
import vertexai
import re

# ============================================================
# LOGGING
# ============================================================
logger = logging.getLogger("weather_api")
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '{"service":"weather-api","severity":"%(levelname)s","message":"%(message)s"}'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)

# ============================================================
# CORS
# ============================================================
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response

@app.after_request
def after_request(response):
    return add_cors(response)

@app.route("/ingest", methods=["OPTIONS"])
@app.route("/weather/all", methods=["OPTIONS"])
@app.route("/weather/<city>", methods=["OPTIONS"])
def cors_preflight(*args, **kwargs):
    return add_cors(make_response(jsonify({"status": "ok"}), 200))

# ============================================================
# ENVIRONMENT CONFIG
# ============================================================
BUCKET_NAME = os.getenv("BUCKET_NAME")
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("PROJECT_ID")
LOCATION = "us-central1"

storage_client = storage.Client()

# ============================================================
# VERTEX AI (Gemini 2.0 Flash)
# ============================================================
vertexai.init(project=PROJECT_ID, location=LOCATION)
model = GenerativeModel("gemini-2.0-flash")

# ============================================================
# CLEAN JSON FROM AI OUTPUT
# ============================================================
def extract_json(text):
    """Cleans markdown fences and extracts JSON from mixed LLM output."""
    text = text.strip()
    text = re.sub(r"^```json", "", text)
    text = re.sub(r"^```", "", text)
    text = re.sub(r"```$", "", text)
    text = text.strip()

    # If JSON is inside extra text → extract only JSON portion
    if not text.startswith("{"):
        first = text.find("{")
        last = text.rfind("}")
        if first != -1 and last != -1:
            text = text[first:last+1]

    return text

# ============================================================
# AI CALL — STRICT NUMERIC ENFORCEMENT
# ============================================================
def call_ai(city, temp, wind):
    prompt = f"""
You are generating structured weather text.

IMPORTANT RULES:
- DO NOT modify temperature ({temp}) or wind ({wind} km/h).
- DO NOT guess new numeric values.
- Output MUST be JSON ONLY.

Generate ONLY:

{{
  "summary": "...",
  "mood": "..."
}}

City: {city}
Temperature: {temp}
Wind Speed: {wind}
"""

    try:
        resp = model.generate_content(prompt)

        raw = extract_json(resp.text)
        data = json.loads(raw)

        return {
            "summary": data.get("summary", "AI error"),
            "mood": data.get("mood", "unknown")
        }

    except Exception as e:
        logger.error(f"AI error ({city}): {e}")
        return {"summary": "AI error", "mood": "unknown"}

# ============================================================
# STORAGE HELPERS
# ============================================================
def list_city_files():
    return [
        blob.name
        for blob in storage_client.list_blobs(BUCKET_NAME)
        if blob.name.startswith("weather_") and blob.name.endswith(".json")
    ]

def read_json(path):
    blob = storage_client.bucket(BUCKET_NAME).blob(path)
    return json.loads(blob.download_as_text())

def city_from_file(path):
    name = path.replace("weather_", "").replace(".json", "")
    return name.replace("_", " ")

# ============================================================
# AI DEBUG ENDPOINTS
# ============================================================
@app.route("/ai-test")
def ai_test():
    """Basic test: ensures your AI is returning JSON."""
    try:
        prompt = """
Generate ONLY a JSON object:
{
  "summary": "test-summary",
  "mood": "test-mood"
}
"""
        resp = model.generate_content(prompt)
        return jsonify({"raw_response": resp.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/ai-debug")
def ai_debug():
    """Full debug to inspect raw Gemini output."""
    prompt = """
Describe the weather in JSON:
{
  "summary": "...",
  "mood": "..."
}
"""
    resp = model.generate_content(prompt)
    return jsonify({"full_text": resp.text})

# ============================================================
# INGEST WEATHER + AI
# ============================================================
@app.route("/ingest", methods=["GET"])
def ingest_weather():
    cities = ["Hyderabad", "London", "New York", "Tokyo", "Sydney"]
    results = {}
    bucket = storage_client.bucket(BUCKET_NAME)

    for city in cities:
        try:
            # ✓ GEO Look-up
            geo = requests.get(
                f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
            ).json()
            lat = geo["results"][0]["latitude"]
            lon = geo["results"][0]["longitude"]

            # ✓ WEATHER Look-up
            weather = requests.get(
                f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&timezone=auto"
            ).json()

            temp = weather["current_weather"]["temperature"]
            wind = weather["current_weather"]["windspeed"]

            # ✓ AI Summary & Mood
            ai = call_ai(city, temp, wind)

            # ✓ Final JSON Output
            output = {
                "city": city,
                "temperature": temp,
                "wind_speed": wind,
                "summary": ai["summary"],
                "mood": ai["mood"]
            }

            # Store in GCS
            blob = bucket.blob(f"weather_{city.replace(' ', '_')}.json")
            blob.upload_from_string(
                json.dumps(output, indent=2),
                content_type="application/json"
            )

            results[city] = "✔ Stored"

        except Exception as e:
            logger.error(f"Error for {city}: {e}")
            results[city] = f"❌ {e}"

    return jsonify(results), 200

# ============================================================
# PUBLIC API ROUTES
# ============================================================
@app.route("/weather/all")
def get_all():
    files = list_city_files()
    data = []
    for f in files:
        obj = read_json(f)
        obj["city"] = city_from_file(f)
        data.append(obj)
    return jsonify(data)

@app.route("/weather/<city>")
def get_city(city):
    filename = f"weather_{city.replace(' ', '_')}.json"
    if filename not in list_city_files():
        return jsonify({"error": "City not found"}), 404

    obj = read_json(filename)
    obj["city"] = city_from_file(filename)
    return jsonify(obj)

@app.route("/")
def home():
    return jsonify({"message": "Weather API running"})

# ============================================================
# MAIN ENTRY
# ============================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
