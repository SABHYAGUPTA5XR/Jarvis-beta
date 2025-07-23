import os, uuid, asyncio, requests, time, webbrowser, pyautogui, pywhatkit
from dotenv import load_dotenv
from playsound import playsound
import edge_tts
import streamlit as st
import speech_recognition as sr

# ─── Load secrets ───────────────────────────────────────
load_dotenv()
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# ─── Page config & custom CSS ──────────────────────────
st.set_page_config(
    page_title="🧠 Jarvis AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown(
    """
    <style>
      body { background: #0d0d0d; color: #e6e6e6; }
      .stButton>button { background-color:#1a1a1a; color:#0ff; border-radius:8px; }
      .stTextInput>div>div>input { background: #1a1a1a; color:#0ff; border-radius:4px; }
      .sidebar .sidebar-content { background: #111; }
      .stFileUploader>div>div>input { background: #1a1a1a; color:#0ff; }
    </style>
    """,
    unsafe_allow_html=True
)

# ─── Helper: Speak with Edge‑TTS ────────────────────────
async def _speak_async(text):
    fname = f"tts_{uuid.uuid4()}.mp3"
    await edge_tts.Communicate(text, voice="en-US-GuyNeural").save(fname)
    playsound(fname)
    os.remove(fname)

def speak(text):
    st.markdown(f"**🤖 Jarvis:** {text}")
    asyncio.run(_speak_async(text))

# ─── Helper: Transcribe uploaded audio ─────────────────
def transcribe_audio(file_bytes):
    r = sr.Recognizer()
    with sr.AudioFile(file_bytes) as src:
        audio = r.record(src)
    try:
        return r.recognize_google(audio)
    except:
        return None

# ─── Mistral LLM call ───────────────────────────────────
def ask_mistral(prompt):
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {MISTRAL_API_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "model":"mistral-tiny",
        "messages":[
            {"role":"system","content":"You are Jarvis, a futuristic AI assistant."},
            {"role":"user","content":prompt}
        ],
        "temperature":0.1
    }
    try:
        res = requests.post(url, headers=headers, json=body)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        st.error(f"⚠️ Mistral error: {e}")
        return "Sorry, I can’t think right now…"

# ─── Core command processing ────────────────────────────

# ─── Helper: Play a song on Spotify or fallback to YouTube ─────────────────
def play_on_spotify(song: str):
    try:
        speak(f"Searching for {song} on Spotify")
        os.startfile(os.getenv("SPOTIFY_PATH"))
        time.sleep(5)

        # focus search bar, type song, hit enter
        pyautogui.hotkey("ctrl", "l")
        pyautogui.write(song)
        pyautogui.press("enter")
        time.sleep(2)

        # navigate to first result + play
        pyautogui.press("tab", presses=1, interval=0.2)
        pyautogui.press("enter")
        time.sleep(2)
        pyautogui.press("enter")
    except Exception:
        speak(f"Could not play on Spotify, falling back to YouTube")
        pywhatkit.playonyt(song)


# ─── Command router ─────────────────────────────────────────────────────────
def handle_command(cmd: str):
    cmd = cmd.lower().strip()
    if not cmd:
        speak("…I heard nothing.")
        return

    st.markdown(f"**🗣️ You:** {cmd}")

    # 1️⃣ Play on YouTube explicitly
    if cmd.startswith("play") and " on youtube" in cmd:
        song = cmd.removeprefix("play").removesuffix("on youtube").strip()
        speak(f"Playing {song} on YouTube")
        pywhatkit.playonyt(song)
        return

    # 2️⃣ Play on Spotify (fallbacks to YouTube)
    if cmd.startswith("play"):
        song = cmd.removeprefix("play").strip()
        play_on_spotify(song)
        return

    # 3️⃣ Open Spotify app
    if "open spotify" in cmd:
        speak("Opening Spotify")
        os.startfile(os.getenv("SPOTIFY_PATH"))
        return

    # 4️⃣ Open YouTube homepage
    if "open youtube" in cmd:
        speak("Opening YouTube")
        webbrowser.open("https://youtube.com")
        return

    # 5️⃣ Fallback: query the LLM
    speak("Let me think…")
    answer = ask_mistral(cmd)
    speak(answer)


# ─── Sidebar controls ───────────────────────────────────
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.selectbox("Theme", ["Dark", "Neon Blue", "Matrix Green"])

# ─── Streamlit container-level CSS for dynamic themes ──
THEMES = {
    "Dark": """
        <style>
        html, body, [data-testid="stApp"] {
            background-color: #0d0d0d;
            color: #e6e6e6;
        }
        </style>
    """,
    "Neon Blue": """
        <style>
        html, body, [data-testid="stApp"] {
            background-color: #001f3f;
            color: #7fdbff;
        }
        </style>
    """,
    "Matrix Green": """
        <style>
        html, body, [data-testid="stApp"] {
            background-color: #001100;
            color: #00ff00;
        }
        </style>
    """
}
st.markdown("""
<style>
/* Typewriter animation */
@keyframes typing {
  from { width: 0; }
  to   { width: 100%; }
}
@keyframes blink-caret {
  50% { border-color: transparent; }
}

/* Wrapper for typewriter text */
.typewriter {
  font-family: 'Courier New', monospace;
  overflow: hidden;            /* hide excess */
  white-space: nowrap;         /* no wrap */
  border-right: .2em solid #0ff;
  width: 0;                    /* start at 0 width */
  animation:
    typing 2s steps(40, end),
    blink-caret .75s step-end infinite;
}

/* Hologram glow */
.typewriter {
  color: #0ff;
  text-shadow:
    0 0 4px #0ff,
    0 0 8px #0ff;
}
</style>
""", unsafe_allow_html=True)


COMMON_CSS = """
<style>
.stButton>button {
    background-color: #1a1a1a;
    color: #0ff;
    border-radius: 8px;
}
.stTextInput>div>div>input {
    background: #1a1a1a;
    color: #0ff;
    border-radius: 4px;
}
.sidebar .sidebar-content {
    background: #111;
}
.stFileUploader>div>div>input {
    background: #1a1a1a;
    color: #0ff;
}
</style>
"""

scanlines = """
<style>
/* Scan lines */
[data-testid="stApp"]::before {
  content: "";
  position: absolute;
  top: 0; left: 0; width: 100%; height: 100%;
  background: linear-gradient(transparent 95%, rgba(0,255,255,0.05) 40%);
  background-size: 100% 2px;
  pointer-events: none;
  z-index: 10;
}
/* Neon text */
h1, h2, .stButton>button {
  text-shadow:
     0 0 4px #0ff,
     0 0 8px #0ff,
     0 0 16px #0ff;
}
"""

st.markdown(scanlines, unsafe_allow_html=True)

# Inject styles
st.markdown(COMMON_CSS, unsafe_allow_html=True)
st.markdown(THEMES[theme], unsafe_allow_html=True)


# ─── Main UI ────────────────────────────────────────────
st.title("🧠 **Jarvis AI**")
st.write("Your futuristic assistant. 🔮")
# **1. Text input**
cmd_txt = st.text_input("💬 Type a command, e.g. “Play Saiyaara song”, What is capital of india?")

if st.button("🚀 Send"):
    handle_command(cmd_txt)

# **2. Upload audio**
audio_file = st.file_uploader("🎙️ Upload a WAV/MP3 clip", type=["wav","mp3"])
if audio_file:
    st.info("Transcribing…")
    cmd = transcribe_audio(audio_file)
    if cmd:
        handle_command(cmd)
    else:
        speak("Sorry, I couldn’t understand the audio.")

# **3. (Local) Record button**  
# Note: Real‐time mic recording isn’t supported on Streamlit Cloud,
# but you can record locally then upload.
st.caption("📌 To speak live: record locally, then upload above.")

st.markdown("---")
st.write("Built with ❤️ by _Sabhya_")
st.write("_*Checkout [Github](https://github.com/SABHYAGUPTA5XR/Jarvis-2.0) for Voice assisted Jarvis-2.0!!*_")


