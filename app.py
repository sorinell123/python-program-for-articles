from flask import Flask, render_template, request, jsonify, send_file, flash
import json
import os
from datetime import datetime
import io
from dotenv import load_dotenv
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Load environment variables
load_dotenv()

# Set Flask secret key from environment variable
app.secret_key = os.getenv('FLASK_SECRET_KEY')
if not app.secret_key:
    raise ValueError("No FLASK_SECRET_KEY set in environment")

# Get Deepseek API key from environment variable
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("No DEEPSEEK_API_KEY set in environment")
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Language mapping for prompts
LANGUAGE_PROMPTS = {
    'en': 'Write in English',
    'es': 'Escribe en español',
    'fr': 'Écris en français',
    'de': 'Schreibe auf Deutsch',
    'it': 'Scrivi in italiano',
    'pt': 'Escreva em português',
    'nl': 'Schrijf in het Nederlands',
    'ro': 'Scrie în română'
}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def apply_replacements(text, replacements):
    if not text:
        return text
    for replacement in replacements:
        text = text.replace(replacement['key'], replacement['value'])
    return text

def generate_prompts(fields, language, replacements):
    # Process each field's requirements
    prompts = []
    for field in fields:
        # Apply replacements to topic and description
        topic = apply_replacements(field['topic'], replacements)
        description = apply_replacements(field['description'], replacements)
        character_count = field['wordCount']
        keyword = apply_replacements(field['keyword'], replacements)
        frequency = field['frequency']

        field_prompt = f"[STRICT REQUIREMENT: This section must be around {character_count} characters in length:]\n\n"
        field_prompt += f"{topic}\n"
        if description:
            field_prompt += f"{description}\n"
        if keyword:
            field_prompt += f"Include the keyword '{keyword}' approximately {frequency} times.\n"
        prompts.append(field_prompt)

    # Combine all prompts
    combined_prompt = "\n\n".join(prompts)
    language_prompt = LANGUAGE_PROMPTS.get(language, LANGUAGE_PROMPTS['en'])
    
    user_prompt = f"""{language_prompt}:

{combined_prompt}

Create an engaging and well-structured article following these requirements exactly."""

    system_prompt = """You are a professional local business content writer specializing in tech repair services. Follow these rules precisely:

1. Always start with a clear, SEO-friendly title .
2. Write in a professional but engaging tone that builds trust.
3. Maintain exact formatting from the input prompt (including bullet points).
4. Follow character count requirements strictly.
5. Keep content sales-focused while maintaining professionalism.
6. Use clear section breaks with headers.
7. Present lists and bullet points exactly as provided in the prompt."""

    return {
        'system_prompt': system_prompt,
        'user_prompt': user_prompt
    }

def generate_article(prompt):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    # Enhance the prompt to request structured content
    structured_prompt = f"""Please generate a well-structured article based on this prompt:

{prompt}

Please structure the article with:
1. A clear title (h1)
2. An introduction
3. Main sections with headings (h2)
4. Subsections where appropriate (h3)
5. Well-organized paragraphs
6. Lists where appropriate
7. A conclusion section

Format the response with proper HTML tags for structure (<h1>, <h2>, <h3>, <p>, <ul>/<ol>, etc.)"""

    data = {
        "messages": [
            {
                "role": "user",
                "content": structured_prompt
            }
        ],
        "model": "deepseek-chat",
        "temperature": 0.7,
        "max_tokens": 2000
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        json=data,
        headers=headers
    )
    
    if response.status_code == 200:
        content = response.json()['choices'][0]['message']['content']
        formatted_content = f'<article class="article-section">{content}</article>'
        return formatted_content
    else:
        raise Exception(f"API call failed with status code: {response.status_code}")

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generator')
def generator():
    return render_template('generator.html')

@app.route('/preview-prompt', methods=['POST'])
def preview_prompt():
    try:
        data = request.json
        fields = data.get('fields', [])
        language = data.get('language', 'en')
        replacements = data.get('replacements', [])

        # Generate prompts using the shared function
        prompts = generate_prompts(fields, language, replacements)
        return jsonify(prompts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-prompt', methods=['POST'])
def download_prompt():
    try:
        data = request.json
        fields = data.get('fields', [])
        language = data.get('language', 'en')
        replacements = data.get('replacements', [])

        # Get the prompts
        combined_prompts = generate_prompts(fields, language, replacements)
        
        # Format the content for the file
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
        content = f"""PROMPT GENERATOR EXPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Language: {LANGUAGE_PROMPTS.get(language, 'English')}

=== SYSTEM PROMPT ===

{combined_prompts['system_prompt']}

=== USER PROMPT ===

{combined_prompts['user_prompt']}
"""
        
        # Create in-memory file
        buffer = io.BytesIO()
        buffer.write(content.encode('utf-8'))
        buffer.seek(0)
        
        return send_file(
            buffer,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'prompt_{timestamp}.txt'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/generate-article', methods=['POST'])
def generate_article_route():
    try:
        # Check if coming from prompt generator or file upload
        if request.content_type and 'application/json' in request.content_type:
            # Direct generation from prompt generator
            data = request.json
            prompt = data.get('prompt')
            if not prompt:
                return jsonify({'error': 'No prompt provided'}), 400
        else:
            # File upload flow
            if 'file' not in request.files:
                flash('No file part')
                return render_template('index.html')
                
            file = request.files['file']
            if file.filename == '':
                flash('No selected file')
                return render_template('index.html')
                
            if not file or not allowed_file(file.filename):
                flash('Allowed file type is txt')
                return render_template('index.html')
                
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Read the prompt from the file
            with open(filepath, 'r', encoding='utf-8') as f:
                prompt = f.read()

        # Generate article using Deepseek AI
        generated_article = generate_article(prompt)
        return render_template('result.html', article=generated_article)
    except Exception as e:
        flash(f'Error generating article: {str(e)}')
        return render_template('index.html')

# Template management routes
@app.route('/save-template', methods=['POST'])
def save_template():
    try:
        data = request.json
        templates_file = 'templates.json'
        
        # Load existing templates
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                templates = json.load(f)
        else:
            templates = {}
        
        # Add new template
        template_name = data['name']
        templates[template_name] = {
            'fields': data['fields'],
            'language': data['language'],
            'replacements': data.get('replacements', [])
        }
        
        # Save updated templates
        with open(templates_file, 'w') as f:
            json.dump(templates, f, indent=2)
        
        return jsonify({'message': 'Template saved successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get-templates', methods=['GET'])
def get_templates():
    try:
        templates_file = 'templates.json'
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                templates = json.load(f)
            return jsonify(templates)
        return jsonify({})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load-template/<name>', methods=['GET'])
def load_template(name):
    try:
        templates_file = 'templates.json'
        if os.path.exists(templates_file):
            with open(templates_file, 'r') as f:
                templates = json.load(f)
            if name in templates:
                return jsonify(templates[name])
        return jsonify({'error': 'Template not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
