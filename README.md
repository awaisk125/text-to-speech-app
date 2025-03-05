Text-to-Speech Flask App


Purpose

This app allows users to convert text into speech using a web interface. It leverages the edge_tts library to generate speech in various languages and voices. The app is built with Flask for the backend and Bootstrap for the frontend, providing a simple and responsive user interface.
Features

    Text Input:

        Users can enter the text they want to convert into speech.

    Language Selection:

        Users can select a language from a dropdown menu. The app dynamically filters languages based on available voices.

    Voice Selection:

        Once a language is selected, users can choose from a list of available voices for that language.

    Volume Control:

        Users can adjust the volume of the generated speech using a slider.

    Audio Playback:

        The generated speech is played directly in the browser using an <audio> element.

    Save Audio:

        Users can download the generated speech as an MP3 file.

    Dynamic Voice Fetching:

        The app fetches available voices from the edge_tts library and organizes them by language.

    File Cleanup:

        Generated audio files are automatically deleted from the server after being sent to the user.

How It Works
Backend (Flask)

    Language and Voice Data:

        The app uses a predefined dictionary (LANGUAGE_NAMES) to map language codes to their friendly names.

        It fetches available voices from the edge_tts library and organizes them by language.

    Routes:

        / (Home Route):

            Renders the index.html template, passing the filtered languages and voices.

        /speak (POST Route):

            Accepts JSON input with the text, voice, and volume.

            Generates speech using the edge_tts library and saves it as an MP3 file.

            Returns the MP3 file as a response, which is played in the browser.

            Deletes the file after sending it to the user.

        /cleanup (POST Route):

            Cleans up any remaining generated audio files on the server.

    Asynchronous Tasks:

        The app uses asyncio to handle asynchronous tasks, such as fetching voices and generating speech.

Frontend (HTML + JavaScript)

    HTML Structure:

        The app uses a Bootstrap-based UI with a card layout.

        It includes a form for text input, language selection, voice selection, and volume control.

        An <audio> element is used for playback, and a "Save Audio" button allows users to download the file.

    JavaScript Functionality:

        Dynamic Voice Population:

            When the user selects a language, the corresponding voices are populated in the voice dropdown.

        Form Submission:

            When the form is submitted, the text, voice, and volume data are sent to the /speak endpoint.

        Audio Playback:

            The response from the server (an MP3 file) is played in the <audio> element.

        Save Audio:

            The "Save Audio" button allows users to download the MP3 file.

Technologies Used

    Backend:

        Flask: A lightweight Python web framework for handling HTTP requests and rendering templates.

        edge_tts: A Python library for text-to-speech synthesis using Microsoft Edge's TTS engine.

        asyncio: For handling asynchronous tasks like fetching voices and generating speech.

        uuid: For generating unique filenames for the audio files.

    Frontend:

        Bootstrap: A CSS framework for responsive and visually appealing UI components.

        JavaScript: For dynamic behavior, such as populating voices, handling form submission, and playing audio.

        HTML: For structuring the web page.

    Other Tools:

        JSON: For sending and receiving data between the frontend and backend.

        Blob URLs: For playing and downloading audio files in the browser.

Workflow

    User Interaction:

        The user opens the app in their browser.

        They enter text, select a language and voice, and adjust the volume.

    Speech Generation:

        The user clicks "Generate Speech".

        The app sends the text, voice, and volume data to the /speak endpoint.

    Backend Processing:

        The Flask backend generates speech using the edge_tts library.

        The speech is saved as an MP3 file with a unique filename.

    Audio Playback:

        The backend sends the MP3 file to the frontend.

        The frontend plays the audio using the <audio> element.

    Save Audio:

        The user clicks "Save Audio" to download the MP3 file.

    File Cleanup:

        The backend deletes the MP3 file after sending it to the user.

Code Structure
Backend (Flask)

    app.py:

        Contains the Flask app and routes.

        Handles speech generation, file management, and cleanup.

Frontend (HTML + JavaScript)

    index.html:

        Contains the HTML structure and embedded JavaScript.

        Handles dynamic voice population, form submission, and audio playback.

How to Run the App

    Install Dependencies:

    pip install Flask edge_tts

    Run the Flask App:

    python app.py

    Access the App:

        Open your browser and go to http://localhost:5000.

Example Use Case

    User Input:

        Text: "Hello, how are you?"

        Language: English (en-US)

        Voice: Jenny

        Volume: 80%

    App Behavior:

        The app generates speech using the edge_tts library.

        The speech is played in the browser.

        The user can download the speech as an MP3 file.

Limitations

    Browser Support:

        The app relies on modern browser features like fetch and Blob URLs. Older browsers may not support these features.

    File Cleanup:

        If the app crashes or is stopped abruptly, generated files may not be deleted. The /cleanup route can be used to manually clean up files.

    Voice Availability:

        The app depends on the voices available in the edge_tts library. Some languages may have limited voice options.

Future Enhancements

    Voice Preview:

        Allow users to preview a voice before generating speech.

    Advanced Controls:

        Add controls for pitch, speed, and other speech parameters.

    User Authentication:

        Add user accounts to save and manage generated audio files.

    Multi-Language Support:

        Translate the UI into multiple languages for better accessibility.
