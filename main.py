import os
import threading
import time
import tkinter as tk
from tkinter import ttk
import pygame
from gtts import gTTS
import speech_recognition as sr
from googletrans import LANGUAGES, Translator


isTranslateOn = False

translator = Translator()  
pygame.mixer.init()  

language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language)

def text_to_voice(text_data, to_language):
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    myobj.save("cache_file.mp3")
    audio = pygame.mixer.Sound("cache_file.mp3")  # Load a sound.
    audio.play()
    os.remove("cache_file.mp3")

def main_process(output_label, from_language, to_language):
    global isTranslateOn
    
    while isTranslateOn:
        rec = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                output_label.config(text="Listening...")
                rec.pause_threshold = 1
                audio = rec.listen(source, phrase_time_limit=10)
                output_label.config(text="Processing...")

                spoken_text = rec.recognize_google(audio, language=from_language)
                translated_text = translator_function(spoken_text, from_language, to_language)

                text_to_voice(translated_text.text, to_language)
                output_label.config(text="Translation: " + translated_text.text)
                
                time.sleep(2)  # Wait for 2 seconds before listening again

            except sr.RequestError:
                output_label.config(text="Error: Cannot access Google Speech Recognition service")
                time.sleep(2)
            except sr.UnknownValueError:
                output_label.config(text="Error: Failed to recognize speech")
                time.sleep(2)
            except Exception as e:
                output_label.config(text=f"Error: {str(e)}")
                time.sleep(2)

def start_translation():
    global isTranslateOn
    if not isTranslateOn:
        isTranslateOn = True
        from_language = get_language_code(from_language_combobox.get())
        to_language = get_language_code(to_language_combobox.get())
        threading.Thread(target=main_process, args=(output_label, from_language, to_language)).start()

def stop_translation():
    global isTranslateOn
    isTranslateOn = False

# Setup Tkinter UI
root = tk.Tk()
root.title("Language Translator")

# Source Language Dropdown
tk.Label(root, text="Select Source Language:").pack()
from_language_combobox = ttk.Combobox(root, values=list(LANGUAGES.values()))
from_language_combobox.pack()

# Target Language Dropdown
tk.Label(root, text="Select Target Language:").pack()
to_language_combobox = ttk.Combobox(root, values=list(LANGUAGES.values()))
to_language_combobox.pack()

# Start and Stop buttons
start_button = tk.Button(root, text="Start", command=start_translation)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop", command=stop_translation)
stop_button.pack(pady=10)

# Output Label
output_label = tk.Label(root, text="", wraplength=400)
output_label.pack(pady=10)

root.mainloop()
