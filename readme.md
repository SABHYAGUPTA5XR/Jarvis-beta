# 🎙️ JARVIS - Voice Assistant (Beta)

Welcome to **JARVIS-beta**, your personalized assistant built using Python, Streamlit, and Mistral AI!  
It can understand your commands, perform tasks like playing music, opening websites, or even answering complex questions using LLMs.

---

## 🚀 Features

- 🎧 **Play Songs on Spotify or YouTube**
- 🔍 **Search and Play YouTube Videos**
- 📢 **Conversational Voice Feedback**
- 🧠 **Ask Anything via Mistral AI**
- 🌐 **Open Websites (YouTube, etc.)**
- 🎨 **Beautiful Sci-Fi Themed UI with futuristic fonts and animations (optional enhancements)**

---

## 🛠️ Tech Stack

- `Python`
- `Streamlit` (GUI)
- `SpeechRecognition`
- `pyttsx3` (Text-to-Speech)
- `pyautogui` (Keyboard automation)
- `pywhatkit` (Play YouTube videos)
- `webbrowser`
- `os` / `time`
- `dotenv` for environment variable management
- `Mistral AI` or any LLM for fallback Q&A

---

## 📦 Installation Setup

### 1. Clone the Repository

bash
git clone https://github.com/andrewheiss/MyJarvis-beta.git

### 2. Setup Environment

bash
python -m venv venv
venv\Scripts\activate   # for Windows

### 3. Install Dependencies

bash
pip install -r requirements.txt

### 4. Add Environment Variables

Create a `.env` file in the root directory:

ini
SPOTIFY_PATH=C:\\Users\\YourUsername\\AppData\\Roaming\\Spotify\\Spotify.exe

## Running the Assistant

bash
streamlit run app.py

Then click the **Start Listening** button to give a command like:

* "play Believer"
* "open YouTube"
* "play The Office intro on YouTube"
* "who is Albert Einstein?"

## Future Enhancements

* Neon Glow Effects
* 3D Sci-Fi Animations
* Voice Feedback with AI Personalization
* Secure OAuth Integration for Spotify
* Mobile-Friendly PWA Support

## Project Structure

bash
MyJarvis-beta/
├── app.py
├── utils.py
├── .env
├── requirements.txt
├── .gitignore
└── README.md

## License

MIT License. Feel free to modify and use it!

