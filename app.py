from flask import Flask, request, jsonify
import openai
from PyPDF2 import PdfReader
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = Flask(__name__)

# Enable CORS for cross-origin requests
from flask_cors import CORS
CORS(app)

# OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the AI Resume & Career Coach API"})

@app.route('/upload', methods=['POST'])
def upload_resume():
    # Get uploaded file
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']

    # Parse PDF content
    try:
        reader = PdfReader(file)
        text = " ".join([page.extract_text() for page in reader.pages])
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500

    # Check if resume content exceeds GPT-4's token limit
    if len(text.split()) > 7000:  # Approximate safe word limit for GPT-4
        return jsonify({"error": "Resume content is too large to process"}), 400

    # AI Analysis using GPT-4
    try:
        prompt = f"Analyze the following resume and provide improvement suggestions:\n{text}"
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        suggestions = response.choices[0].message.content.strip()
    except Exception as e:
        return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500

    # Return AI suggestions
    return jsonify({"analysis": suggestions})

if __name__ == '__main__':
    app.run(debug=True)
