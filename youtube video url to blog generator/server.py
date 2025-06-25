from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import logging
import requests
from urllib.parse import urlparse, parse_qs
import re

from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.youtube import YouTubeTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

def validate_youtube_url(url):
    """Validate if the URL is a proper YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )
    return bool(re.match(youtube_regex, url))

def get_video_id(youtube_url):
    """Extract the YouTube video ID from the URL."""
    if not validate_youtube_url(youtube_url):
        return None
        
    parsed_url = urlparse(youtube_url)
    hostname = parsed_url.hostname or ""
    if hostname in ('youtu.be', 'www.youtu.be'):
        return parsed_url.path[1:]
    if hostname in ('youtube.com', 'www.youtube.com'):
        if parsed_url.path == '/watch':
            query = parse_qs(parsed_url.query)
            return query.get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
    return None

def check_available_captions(youtube_url):
    """Check available caption languages for the given YouTube video."""
    video_id = get_video_id(youtube_url)
    if not video_id:
        return []

    youtube_api_key = os.getenv("GOOGLE_API_KEY")
    if not youtube_api_key:
        raise ValueError("GOOGLE_API_KEY (YouTube Data API key) not set in environment variables.")

    url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video_id}&key={youtube_api_key}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Failed to fetch captions: {response.status_code} {response.text}")
        return []

    data = response.json()
    captions = data.get('items', [])
    available_languages = []
    for caption in captions:
        lang = caption['snippet'].get('language')
        if lang and lang not in available_languages:
            available_languages.append(lang)
    return available_languages

# Initialize Gemini model with its own API key
gemini_api_key = os.getenv("GOOGLE_GEMINI_API")
if not gemini_api_key:
    raise ValueError("GOOGLE_GEMINI_API (Gemini API key) is not set in environment variables.")

gemini_model = Gemini(id="gemini-2.0-flash", api_key=gemini_api_key)

# Initialize Flask app
app = Flask(__name__)

# Create agents with their instructions
transcription_agent = Agent(
    model=gemini_model,
    tools=[YouTubeTools()],
    instructions=["Extract and transcribe audio from the provided YouTube URL in English."]
)

summarization_agent = Agent(
    model=gemini_model,
    instructions=["Summarize the provided transcription into key points in English."]
)

structuring_agent = Agent(
    model=gemini_model,
    instructions=["Organize the summary into a structured blog format with appropriate headings in English."]
)

@app.route('/generate_blog', methods=['POST'])
def generate_blog():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        youtube_url = data.get("url", "").strip()
        language = data.get("language", "en").strip().lower()

        if not youtube_url:
            return jsonify({"error": "No URL provided"}), 400

        if not validate_youtube_url(youtube_url):
            return jsonify({"error": "Invalid YouTube URL format"}), 400

        video_id = get_video_id(youtube_url)
        if not video_id:
            return jsonify({"error": "Could not extract video ID from URL"}), 400

        available_captions = check_available_captions(youtube_url)
        logger.info(f"Available captions: {available_captions}")

        # Prefer English subtitles if available, else fallback
        if 'en' in available_captions:
            language = 'en'
        elif available_captions:
            language = available_captions[0]
        else:
            language = 'en'
            logger.warning("No captions found, defaulting to English")

        # Build instructions with more context
        transcription_instruction = (
            f"Extract and transcribe audio from this YouTube URL: {youtube_url} "
            f"in {language}. Ensure to capture all important details and maintain accuracy."
        )
        
        summary_instruction = (
            "Summarize the transcription into key points, focusing on main ideas, "
            "important details, and supporting evidence. Maintain clarity and coherence."
        )
        
        structuring_instruction = (
            "Organize the summary into a well-structured blog post with:\n"
            "1. An engaging introduction\n"
            "2. Clear section headings\n"
            "3. Well-organized paragraphs\n"
            "4. A conclusion that ties everything together\n"
            "Use markdown formatting for better readability."
        )

        # Run agents sequentially with progress logging
        logger.info("Starting transcription...")
        transcription = transcription_agent.run(transcription_instruction)
        transcription = getattr(transcription, "content", transcription)
        logger.info(f"Transcription output: {transcription}")
        if not transcription:
            return jsonify({"error": "Transcription failed or returned empty result"}), 500

        logger.info("Starting summarization...")
        summary = summarization_agent.run(f"{summary_instruction}\n{transcription}")
        summary = getattr(summary, "content", summary)
        logger.info(f"Summary output: {summary}")
        if not summary:
            return jsonify({"error": "Summarization failed or returned empty result"}), 500

        logger.info("Starting blog structuring...")
        structured_blog = structuring_agent.run(f"{structuring_instruction}\n{summary}")
        blog_content = getattr(structured_blog, "content", structured_blog)
        logger.info(f"Structured blog output: {blog_content}")
        if not blog_content:
            return jsonify({"error": "Blog structuring failed or returned empty result"}), 500

        return jsonify({
            "blog_content": blog_content,
            "used_language": language,
            "video_id": video_id
        }), 200

    except Exception as e:
        logger.error(f"Error during blog generation: {str(e)}", exc_info=True)
        if "PERMISSION_DENIED" in str(e):
            return jsonify({
                "error": "Google Gemini API access denied. Please ensure the Generative Language API is enabled and your API key is correct."
            }), 500
        return jsonify({
            "error": "An unexpected error occurred",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
