import speech_recognition as sr
import pyttsx3
import pyaudio
import numpy as np
import datetime
import webbrowser
import time

# Initialize TTS engine globally
def init_tts_engine():
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    for i, voice in enumerate(voices):
        print(f"[{i}] {voice.name} ({voice.languages})")
    try:
        choice = int(input("Choose a voice index: "))
        engine.setProperty("voice", voices[choice].id)
    except Exception:
        print("Invalid input. Using default voice.")
        engine.setProperty("voice", voices[0].id)
    return engine

# Text to speech
def say(text, engine):
    print(f"[Jarvis]: {text}")
    engine.say(text)
    engine.runAndWait()

# Recognize user speech
def listen():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("[Listening...]")
        try:
            audio = recognizer.listen(source, timeout=5)
            command = recognizer.recognize_google(audio)
            print(f"[User]: {command}")
            return command.lower()
        except sr.WaitTimeoutError:
            print("Timeout while listening.")
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
    return ""

# Detect clap
def detect_clap(threshold=20000):
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 2

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("[Awaiting Clap...]")

    clap_detected = False
    try:
        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = np.frombuffer(stream.read(CHUNK, exception_on_overflow=False), dtype=np.int16)
            if np.max(data) > threshold:
                print("[Clap Detected!]")
                clap_detected = True
                break
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

    return clap_detected

# Process commands
def process_command(command, tts_engine):
    if "open google" in command:
        say("Opening Google", tts_engine)
        webbrowser.open("https://www.google.com")
    elif "open youtube" in command:
        say("Opening YouTube", tts_engine)
        webbrowser.open("https://www.youtube.com")
    elif "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        say(f"The time is {now}", tts_engine)
    elif "quit" in command or "exit" in command:
        say("Goodbye!", tts_engine)
        return False
    else:
        say(f"You said: {command}", tts_engine)
    return True

# Main logic
def main():
    print("Initializing Jarvis...")
    tts_engine = init_tts_engine()

    try:
        while True:
            print("\nType 'quit' to exit.")
            text_input = input("Press Enter to wait for a clap, or type a command directly: ").strip().lower()

            if text_input == "quit":
                say("Goodbye!", tts_engine)
                break
            elif text_input != "":
                if not process_command(text_input, tts_engine):
                    break
            elif detect_clap():
                say("Yes, I'm listening...", tts_engine)
                command = listen()
                if command:
                    if not process_command(command, tts_engine):
                        break
                else:
                    say("No command detected.", tts_engine)
            else:
                print("No clap detected.")
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Exiting on user interrupt.")
        say("Shutting down. Goodbye!", tts_engine)

# Run
if __name__ == "__main__":
    main()
