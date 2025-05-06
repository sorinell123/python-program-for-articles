# AI Article Generator

A Flask-based web application that leverages the Deepseek API to generate structured, SEO-friendly articles with multi-language support and template management capabilities.

## Features

- 🌐 **Multi-language Support**: Generate content in 8 languages
  - English, Spanish, French, German
  - Italian, Portuguese, Dutch, Romanian

- 📋 **Template Management**
  - Save and load article templates
  - Reuse common content structures
  - Export templates for sharing

- 🔄 **Dynamic Text Replacement**
  - Define custom placeholders
  - Automate content personalization
  - Batch content variations

- ✍️ **Content Control**
  - Set precise character counts per section
  - Specify keywords and frequency
  - Structure content with HTML formatting

- 🔍 **SEO Optimization**
  - Keyword frequency control
  - Structured HTML output
  - SEO-friendly content organization

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-article-generator.git
cd ai-article-generator
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual keys
# Make sure to update:
# - FLASK_SECRET_KEY (generate a secure random key)
# - DEEPSEEK_API_KEY (your Deepseek API key)
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Create an article:
   - Choose or create a template
   - Fill in the required fields
   - Set language and content parameters
   - Generate and preview the article

## Project Structure

```
ai-article-generator/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── templates.json      # Saved article templates
├── static/
│   └── css/           # Stylesheets
│       ├── generator.css
│       ├── index.css
├── templates/         # HTML templates
│   ├── generator.html
│   ├── index.html
│   └── result.html
└── uploads/          # Uploaded prompt files
```

## API Integration

The application uses the Deepseek API for content generation. Ensure you have:
1. A valid Deepseek API key
2. Sufficient API credits
3. Proper error handling in place

## Development

- Python 3.6+
- Flask web framework
- Deepseek API integration
- JavaScript for frontend interactivity
- HTML/CSS for interface design

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Deepseek API for content generation
- Flask framework
- Contributors and testers

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
