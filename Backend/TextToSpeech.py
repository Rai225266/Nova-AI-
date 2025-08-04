import pygame
import random
import asyncio
import edge_tts
import os
from dotenv import dotenv_values

# Load environment variables
env_vars = dotenv_values(".env")
AssistantVoice = env_vars.get("AssistanceVoice")

# Ensure Data directory exists
os.makedirs("Data", exist_ok=True)

# Asynchronous function to convert text to audio file
async def TextToAudioFile(text) -> None:
    file_path = r"Data/speech.mp3"

    # Remove existing file to avoid overwrite issues
    if os.path.exists(file_path):
        os.remove(file_path)

    # Generate speech with Edge TTS
    communicate = edge_tts.Communicate(text, AssistantVoice, pitch='+5Hz', rate='+13%')
    await communicate.save(file_path)

# Function to play TTS using pygame
def TTS(Text, func=lambda r=None: True):
    try:
        # Run the async function synchronously
        asyncio.run(TextToAudioFile(Text))

        pygame.mixer.init()
        pygame.mixer.music.load("Data/speech.mp3")
        pygame.mixer.music.play()

        # Loop while audio is playing
        while pygame.mixer.music.get_busy():
            if not func():
                break
            pygame.time.Clock().tick(10)
        return True

    except Exception as e:
        print(f"Error in TTS: {e}")
        return False

    finally:
        try:
            func(False)
            pygame.mixer.music.stop()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error in finally block: {e}")

# Function to split and optionally summarize long text
def TextToSpeech(Text, func=lambda r=None: True):
    Data = str(Text).split(".")

    # Customize this with actual fallback responses if needed
    responses = [
        "The rest of the result has been printed to the chat screen, kindly check it out sir.",
        "The rest of the text is now on the chat screen, sir, please check it.",
        "You can see the rest of the text on the chat screen, sir.",
        "The remaining part of the text is now on the chat screen, sir.",
        "Sir, you'll find more text on the chat screen for you to see.",
        "The rest of the answer is now on the chat screen, sir.",
        "Sir, please look at the chat screen, the rest of the answer is there.",
        "You'll find the complete answer on the chat screen, sir.",
        "The next part of the text is on the chat screen, sir.",
        "Sir, please check the chat screen for more information.",
        "There's more text on the chat screen for you, sir.",
        "Sir, take a look at the chat screen for additional text.",
        "You'll find more to read on the chat screen, sir.",
        "Sir, check the chat screen for the rest of the text.",
        "The chat screen has the rest of the text, sir.",
        "There's more to see on the chat screen, sir, please look.",
        "Sir, the chat screen holds the continuation of the text.",
        "You'll find the complete answer on the chat screen, kindly check it out sir.",
        "Please review the chat screen for the rest of the text, sir.",
        "Sir, look at the chat screen for the complete answer."
    ]
    if len(Data) > 4 and len(Text) > 250:
        summary = " ".join(Data[:2]) + ". " + random.choice(responses)
        TTS(summary, func)
    else:
        TTS(Text, func)

# CLI Entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter the text: ")
        if user_input.strip().lower() in ["exit", "quit"]:
            break
        TextToSpeech(user_input)
