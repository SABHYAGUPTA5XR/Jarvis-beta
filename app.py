import os
import uuid
import asyncio
import requests
import time
import webbrowser

import streamlit as st

# ─── Detect Local vs. Cloud ──────────────────────────────
IS_LOCAL = os.name == "nt"

# ─── Detect Local vs. Cloud ──────────────────────────────
IS_LOCAL = os.name == "nt"

# Local-only dependencies
if IS_LOCAL:
    import pyautogui
    import pywhatkit
    import speech_recognition as sr
    from dotenv import load_dotenv
    from playsound import playsound
    load_dotenv()
else:
    # No-op for local-only packages; edge_tts always available
    pyautogui = None
    pywhatkit = None
    sr = None
    load_dotenv = lambda *a, **k: None
    playsound = lambda *a, **k: None
# ─── Secrets / Config ────────────────────────────────────
MISTRAL_API_KEY = (
    st.secrets.get("MISTRAL_API_KEY") or os.getenv("MISTRAL_API_KEY")
)
SPOTIFY_PATH = (
    st.secrets.get("SPOTIFY_PATH") or os.getenv("SPOTIFY_PATH")
)

# ─── TTS helper for cloud and local ───────────────────────
async def _tts_to_file(text: str) -> str:
    """Generate an MP3 via edge-tts and return its filename."""
    fname = f"tts_{uuid.uuid4()}.mp3"
    await edge_tts.Communicate(text, voice="en-US-GuyNeural").save(fname)
    return fname

# ─── Speak helper ─────────────────────────────────────────
def speak(text: str):
    st.markdown(f"**🤖 Jarvis:** {text}")
    # generate TTS file
    if IS_LOCAL:
        fname = asyncio.run(_tts_to_file(text))
        playsound(fname)
        os.remove(fname)
    else:
        fname = asyncio.run(_tts_to_file(text))
        st.audio(fname, format="audio/mp3")
        os.remove(fname)

# ─── Transcribe audio ────────────────────────────────────
def transcribe_audio(file_bytes):
    if not IS_LOCAL:
        return None
    r = sr.Recognizer()
    with sr.AudioFile(file_bytes) as src:
        audio = r.record(src)
    try:
        return r.recognize_google(audio)
    except:
        return None

# ─── Mistral LLM Call ─────────────────────────────────────
def ask_mistral(prompt: str) -> str:
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mistral-tiny",
        "messages": [
            {"role": "system", "content": "You are Jarvis, a futuristic AI assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1
    }
    try:
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error(f"⚠️ Mistral error: {e}")
        return "Sorry, I can’t think right now…"

# ─── Play music helper ────────────────────────────────────
def play_on_spotify(song: str):
    if not IS_LOCAL:
        # Cloud fallback: search on YouTube
        speak(f"Playing {song} on YouTube")
        query = song.replace(' ', '+')
        webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return
    try:
        speak(f"Searching for {song} on Spotify")
        os.startfile(SPOTIFY_PATH)
        time.sleep(5)
        pyautogui.hotkey("ctrl", "l")
        pyautogui.write(song)
        pyautogui.press("enter"); time.sleep(2)
        pyautogui.press("tab", presses=1, interval=0.2)
        pyautogui.press("enter"); time.sleep(2)
        pyautogui.press("enter")
    except Exception:
        speak(f"Could not play on Spotify, falling back to YouTube")
        pywhatkit.playonyt(song)

# ─── Command routing ─────────────────────────────────────
def handle_command(cmd: str):
    cmd = cmd.lower().strip()
    if not cmd:
        speak("…I heard nothing.")
        return
    st.markdown(f"**🗣️ You:** {cmd}")
    # Play on YouTube explicitly
    if cmd.startswith("play") and " on youtube" in cmd:
        song = cmd.removeprefix("play").removesuffix("on youtube").strip()
        speak(f"Playing {song} on YouTube")
        if IS_LOCAL:
            pywhatkit.playonyt(song)
        else:
            query = song.replace(' ', '+')
            webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
        return
    # Play on Spotify or fallback
    if cmd.startswith("play"):
        song = cmd.removeprefix("play").strip()
        play_on_spotify(song)
        return
    # Open Spotify app
    if "open spotify" in cmd:
        if IS_LOCAL:
            speak("Opening Spotify")
            os.startfile(SPOTIFY_PATH)
        else:
            speak("Spotify controls unavailable in cloud.")
        return
    # Open YouTube homepage
    if "open youtube" in cmd:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
        return
    # Fallback: ask LLM
    speak("Let me think…")
    answer = ask_mistral(cmd)
    speak(answer)

# ─── CSS and UI Setup ────────────────────────────────────
st.set_page_config(
    page_title="🧠 Jarvis AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

COMMON_CSS = """
<style>
.stButton>button { background-color:#1a1a1a; color:#0ff; border-radius:8px; }
.stTextInput>div>div>input { background:#1a1a1a; color:#0ff; border-radius:4px; }
.sidebar .sidebar-content { background:#111; }
.stFileUploader>div>div>input { background:#1a1a1a; color:#0ff; }
</style>
"""

scanlines = """
<style>
[data-testid="stApp"]::before {
  content: "";
  position: absolute; top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(transparent 95%, rgba(0,255,255,0.05) 40%);
  background-size: 100% 2px;
  pointer-events: none; z-index: 10;
}
h1, h2, .stButton>button {
  text-shadow: 0 0 4px #0ff, 0 0 8px #0ff, 0 0 16px #0ff;
}
</style>
"""

typewriter_css = """
<style>
@keyframes typing { from { width:0; } to { width:100%; } }
@keyframes blink-caret { 50% { border-color:transparent; } }
.typewriter {
  font-family:'Courier New', monospace; overflow:hidden; white-space:nowrap;
  border-right:.2em solid #0ff; width:0;
  animation: typing 2s steps(40,end), blink-caret .75s step-end infinite;
  color:#0ff; text-shadow:0 0 4px #0ff,0 0 8px #0ff;
}
</style>
"""

st.markdown(scanlines, unsafe_allow_html=True)
st.markdown(COMMON_CSS, unsafe_allow_html=True)
st.markdown(typewriter_css, unsafe_allow_html=True)

THEMES = {
    "Dark":    "<style>html, body, [data-testid='stApp']{background:#0d0d0d;color:#e6e6e6;}</style>",
    "Neon Blue":    "<style>html, body, [data-testid='stApp']{background:#001f3f;color:#7fdbff;}</style>",
    "Matrix Green":"<style>html, body, [data-testid='stApp']{background:#001100;color:#00ff00;}</style>"
}

st.sidebar.title("⚙️ Settings")
theme = st.sidebar.selectbox("Theme", list(THEMES.keys()))
st.markdown(THEMES[theme], unsafe_allow_html=True)

# ─── Main UI ────────────────────────────────────────────
st.title("🧠 **Jarvis AI**")
st.write("Your futuristic assistant. 🔮")

cmd_txt = st.text_input("💬 Type a command…")
if st.button("🚀 Send"):
    handle_command(cmd_txt)

audio_file = st.file_uploader("🎙️ Upload a WAV/MP3 clip", type=["wav","mp3"])
if audio_file:
    st.info("Transcribing…")
    cmd = transcribe_audio(audio_file)
    if cmd:
        handle_command(cmd)
    else:
        speak("Sorry, I couldn’t understand the audio.")

st.caption("📌 To speak live: record locally, then upload above.")
st.markdown("---")
st.write("Built with ❤️ by _Sabhya_")
