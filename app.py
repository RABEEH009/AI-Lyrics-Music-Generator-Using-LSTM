# Import necessary libraries
from flask import Flask, render_template, request, send_file  # Flask utilities
import os  # For file system operations
from generate_music import generate_sample_melody  # Function to create basic melody
from drum_and_bass import add_instruments_to_melody  # Function to add drums and bass
from lyrics_generator import generate_lyrics  # Function to generate lyrics
from dotenv import load_dotenv  # Load environment variables if needed
import logging  # For logging debug/error messages

# Set up basic logging configuration
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables from a .env file if available
load_dotenv()

# Initialize the Flask application
app = Flask(__name__)

# Route for the home page
@app.route('/')
def index():
    # Render the main index.html page
    return render_template('index.html')

# Route to handle the generation process after user submits the form
@app.route('/generate', methods=['POST'])
def generate():
    # Get the theme, mood, and style from the form input
    theme = request.form['theme']
    mood = request.form['mood']
    style = request.form['style']

    # Generate lyrics based on user input
    try:
        logger.debug(f"Generating lyrics for theme={theme}, mood={mood}, style={style}")
        lyrics = generate_lyrics(theme, mood, style)
        logger.debug("Lyrics generated successfully")
    except Exception as e:
        logger.error(f"Error generating lyrics: {e}")
        return f"Error generating lyrics: {e}", 500  # Return HTTP 500 if lyrics generation fails

    # Ensure the 'static' directory exists to save generated files
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    if not os.path.exists(static_dir):
        logger.debug(f"Creating static directory at {static_dir}")
        os.makedirs(static_dir)

    # Define file paths for the melody and full song
    melody_path = os.path.join(static_dir, 'melody.mid')
    full_song_path = os.path.join(static_dir, 'full_song.mid')

    # Generate sample melody MIDI file
    try:
        logger.debug(f"Generating melody at {melody_path} with theme={theme}, mood={mood}, style={style}")
        generate_sample_melody(melody_path, theme, mood, style)
        if not os.path.exists(melody_path):
            logger.error(f"Melody MIDI file not created at {melody_path}")
            raise Exception(f"Melody MIDI file not created at {melody_path}")
        logger.debug(f"Melody file created at {melody_path}")
    except Exception as e:
        logger.error(f"Error in generate_sample_melody: {e}")
        return f"Error in generate_sample_melody: {e}", 500  # Return error if melody generation fails

    # Add drums and bass to the generated melody
    try:
        logger.debug(f"Adding instruments, input={melody_path}, output={full_song_path}, theme={theme}, mood={mood}, style={style}")
        add_instruments_to_melody(melody_path, full_song_path, theme, mood, style)
        if not os.path.exists(full_song_path):
            logger.error(f"Full song MIDI file not created at {full_song_path}")
            raise Exception(f"Full song MIDI file not created at {full_song_path}")
        logger.debug(f"Full song file created at {full_song_path}")
    except Exception as e:
        logger.error(f"Error in add_instruments_to_melody: {e}")
        return f"Error in add_instruments_to_melody: {e}", 500  # Return error if instrument addition fails

    # Final check if the full song was created successfully
    if not os.path.exists(full_song_path):
        logger.error(f"Final check failed: Full song MIDI file not found at {full_song_path}")
        return f"Error: Final check failed, MIDI file not found at {full_song_path}", 500

    # Create a link to download the generated full song
    download_link = "static/full_song.mid"
    logger.debug(f"Returning template with download_link={download_link}")

    # Render the index.html page with lyrics and download link
    return render_template('index.html', lyrics=lyrics, download_link=download_link)

# Route to download the generated full song MIDI file
@app.route('/download')
def download():
    # Define the path for the full song
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    full_song_path = os.path.join(static_dir, 'full_song.mid')

    # Check if the file exists
    if not os.path.exists(full_song_path):
        logger.error(f"MIDI file not found for download at {full_song_path}")
        return "Error: MIDI file not found for download.", 404  # Return 404 if file missing

    logger.debug(f"Sending file for download: {full_song_path}")
    return send_file(full_song_path, as_attachment=True)  # Send the file as a download

# Main block to run the Flask app
if __name__ == '__main__':
    app.run(debug=True)  # Run in debug mode for development