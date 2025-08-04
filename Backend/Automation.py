import os
import subprocess
import asyncio
import keyboard
import requests
import webbrowser
from bs4 import BeautifulSoup
from pywhatkit import search, playonyt
from dotenv import dotenv_values
from AppOpener import close, open as appopen
from webbrowser import open as webopen
from groq import Groq
from rich import print

# Load environment variables
env_vars = dotenv_values(".env")
GroqAPIKey = env_vars.get("GroqAPIKey")
GroqModel = env_vars.get("GroqModel", "llama3-70b-8192")  # Default if not in .env

# Setup Groq API client
client = Groq(api_key=GroqAPIKey)

# System prompt
SystemChatBot = [{
    "role": "system",
    "content": "You are a professional content writer. Write clearly and engagingly."
}]

# List to store conversation history
messages = []

# Predefined classes for parsing (currently unused)
classes = [
    "zCubwf", "hgKElc", "LTK00 sY7ric", "Z0LcW", "gsrt vk_bk FzvWSb YwPhnf",
    "pclqee", "tw-Data-text tw-text-small tw-ta", "IZ6rdc", "05uR6d LTK00", "vlzY6d",
    "webanswers-webanswers table webanswers-table", "dDoNo ikb4Bb gsrt", "sXLa0e",
    "LWkfKe", "VQF4g", "qv3Wpe", "kno-rdesc", "SPZz6b"
]
useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'

client = Groq(api_key=GroqAPIKey)

professional_responses = [
    "Your satisfaction is my top priority; feel free to reach out if there's anything else I can help you with.",
      "I'm at your service for any additional questions or support you may need-don't hesitate to ask."
]
# --- Features ---

def GoogleSearch(Topic):
    search(Topic)
    return True


def Content(topic):

    def ContentWriterAI(prompt):
        messages.append({"role": "user", "content": prompt})

        completion = client.chat.completions.create(
            model=GroqModel,  # ✅ Updated model from .env
            messages=SystemChatBot + messages,
            max_tokens=2048,
            temperature=0.7,
            top_p=1,
            stream=True
        )

        answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                answer += chunk.choices[0].delta.content

        answer = answer.replace("</s>", "")
        messages.append({"role": "assistant", "content": answer})
        return answer

    topic_clean = topic.replace("content", "").strip()
    ai_content = ContentWriterAI(topic_clean)

    os.makedirs("Data", exist_ok=True)
    file_path = rf"Data\{topic_clean.lower().replace(' ', '')}.txt"
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(ai_content)

    OpenNotepad(file_path)
    return True


def OpenNotepad(file_path):
    try:
        os.startfile(file_path)
    except Exception as e:
        print(f"[red]Error opening file: {e}[/red]")


def YouTubeSearch(Topic):
    url = f"https://www.youtube.com/results?search_query={Topic}"
    webbrowser.open(url)
    return True


def PlayYoutube(query):
    playonyt(query)
    return True


def OpenApp(app, sees=requests.session()):
    try:
        appopen(app, match_closest=True, output=True, throw_error=True)
        return True
    except Exception:
        def extract_links(html):
            if html is None:
                return []
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', {'jsname': 'UWckNb'})
            return [link.get('href') for link in links if link.get('href')]

        def search_google(query):
            url = f"https://www.google.com/search?q={query}"
            headers = {"User-Agent": useragent}
            response = sees.get(url, headers=headers)
            return response.text if response.status_code == 200 else None

        html = search_google(app)
        if html:
            links = extract_links(html)
            if links:
                webopen(f"https://www.google.com{links[0]}")
        return True


def CloseApp(app):
    try:
        if "chrome" in app.lower():
            return True
        else:
            close(app, match_closest=True, output=True, throw_error=True)
            return True
    except Exception:
        return False


def System(command):
    def mute(): keyboard.press_and_release("volume mute")
    def unmute(): keyboard.press_and_release("volume mute")
    def volume_up(): keyboard.press_and_release("volume up")
    def volume_down(): keyboard.press_and_release("volume down")

    commands_map = {
        "mute": mute,
        "unmute": unmute,
        "volume up": volume_up,
        "volume down": volume_down,
    }

    if command in commands_map:
        commands_map[command]()
        return True

    return False


# --- Core Interpreter ---

async def TranslateAndExecute(commands: list[str]):
    funcs = []
    for command in commands:
        command = command.lower().strip()

        if command.startswith("open "):
            funcs.append(asyncio.to_thread(OpenApp, command.removeprefix("open ")))

        elif command.startswith("close "):
            funcs.append(asyncio.to_thread(CloseApp, command.removeprefix("close ")))

        elif command.startswith("play "):
            funcs.append(asyncio.to_thread(PlayYoutube, command.removeprefix("play ")))

        elif command.startswith("content "):
            funcs.append(asyncio.to_thread(Content, command.removeprefix("content ")))

        elif command.startswith("google search "):
            funcs.append(asyncio.to_thread(GoogleSearch, command.removeprefix("google search ")))

        elif command.startswith("youtube search "):
            funcs.append(asyncio.to_thread(YouTubeSearch, command.removeprefix("youtube search ")))

        elif command.startswith("system "):
            funcs.append(asyncio.to_thread(System, command.removeprefix("system ")))

        else:
            print(f"[red]No function found for command:[/red] {command}")

    results = await asyncio.gather(*funcs)
    for result in results:
        yield result


async def Automation(commands: list[str]):
    async for result in TranslateAndExecute(commands):
        pass
    return True


# Test it directly (optional)
if __name__ == "__main__":
    OpenApp("Open camera")
