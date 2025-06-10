import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator  # For translation

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt template
BASE_PROMPT = """You are a YouTube video summarizer. You will take the transcript text 
and summarize the entire video based on the requested format and language. 
Summarize in the format: {format}. Language: {language}. Please provide the summary of the text given here: """

# Translator for language support
translator = Translator()

# Function to extract transcript details for a specific language
def extract_transcript_details(youtube_video_url, language="en"):
    try:
        video_id = youtube_video_url.split("v=")[1]
        # Fetch available transcript languages
        available_transcripts = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Check if the selected language is available, otherwise fallback to English
        transcript = None
        if language != "en" and available_transcripts.get_transcript(language):
            transcript_data = available_transcripts.find_transcript([language])
            transcript = " ".join([entry["text"] for entry in transcript_data])
        else:
            # Default to English transcript
            transcript_data = available_transcripts.find_transcript(["en"])
            transcript = " ".join([entry["text"] for entry in transcript_data])

        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {e}")
        return None

# Function to generate summary using Gemini AI
def generate_gemini_content(transcript_text, format, language):
    prompt = BASE_PROMPT.format(format=format, language=language)
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Streamlit App Title
st.title("🎥 YouTube Transcript to Multilingual Notes Converter")

# Input YouTube link
youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

# Dropdown for summary format
format_option = st.selectbox(
    "📋 Select Summary Format:",
    ["Bullet Points", "Key Points", "Short Paragraph"]
)

# Dropdown for language selection
language_option = st.selectbox(
    "🌐 Select Language for Summary:",
    ["English", "Spanish", "French", "German", "Hindi", "Chinese", "Japanese", "Arabic"]
)

# Translate language option to language code used by YouTube
language_codes = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Hindi": "hi",
    "Chinese": "zh",
    "Japanese": "ja",
    "Arabic": "ar"
}

if youtube_link:
    # Display video preview and player
    try:
        video_id = youtube_link.split("v=")[1]
        st.video(f"https://www.youtube.com/watch?v={video_id}")
        st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)
    except IndexError:
        st.error("Invalid YouTube link format. Please check and try again.")

if st.button("Generate Detailed Notes"):
    with st.spinner("Fetching transcript and generating summary..."):
        # Fetch transcript in the selected language
        transcript_text = extract_transcript_details(youtube_link, language=language_codes[language_option])

    if transcript_text:
        with st.spinner("Generating summary using Gemini AI..."):
            # Generate summary based on selected format and language
            summary = generate_gemini_content(
                transcript_text,
                format=format_option,
                language=language_option
            )

        if summary:
            st.markdown("### 📄 Detailed Notes:")
            st.write(summary)

            # Option to download the summary
            st.download_button(
                label="📥 Download Summary as Text File",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )
    else:
        st.error("Failed to retrieve transcript. Please try another video.")
