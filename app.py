import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# CONFIGURATION
# In a real production env, use environment variables: os.getenv("GEMINI_API_KEY")
# For this personal project, you can paste your key here OR set it in your terminal.
API_KEY = os.getenv("GEMINI_API_KEY") 

if not API_KEY:
    print("WARNING: API Key not found. Please set GEMINI_API_KEY environment variable.")

# Configure the AI
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate_question', methods=['POST'])
def generate_question():
    try:
        data = request.json
        domain = data.get('domain', 'General CISSP')
        
        # Prompt Engineering: instructing the AI to act as a CISSP exam creator
        prompt = f"""
        Act as a senior CISSP exam proctor. Generate a difficult, scenario-based multiple-choice question 
        focusing on the domain: {domain}.
        
        Format the response strictly as valid JSON with the following keys:
        - "question": The scenario text.
        - "options": A list of 4 options (A, B, C, D).
        - "correct_answer": The correct option letter.
        - "explanation": A detailed explanation referencing specific NIST or ISO standards where applicable.
        
        Do not include markdown formatting (like ```json), just the raw JSON string.
        """
        
        response = model.generate_content(prompt)
        
        # Clean up response if AI adds markdown ticks
        clean_text = response.text.replace('```json', '').replace('```', '').strip()
        
        return clean_text, 200, {'Content-Type': 'application/json'}

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
