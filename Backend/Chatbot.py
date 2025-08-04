from groq import Groq  # Importing the Groq library
from json import load, dump
import datetime
from dotenv import dotenv_values

# Load environment variables from the .env file
env_vars = dotenv_values(".env")
Username = env_vars.get("Username")
Assistantname = env_vars.get("Assistantname")
GroqAPIKey = env_vars.get("GroqAPIKey")

# Initialize the Groq client
client = Groq(api_key=GroqAPIKey)

# System prompt
System = f"""Hello, I am {Username}, You are a very accurate and advanced AI chatbot named {Assistantname} which also has real-time up-to-date information from the internet.
*** Do not tell time until I ask, do not talk too much, just answer the question.***
*** Reply in only English, even if the question is in Hindi, reply in English.***
*** Do not provide notes in the output, just answer the question and never mention your training data. ***
"""

SystemChatBot = [
    {"role": "system", "content": System}
]

# Define chat log path
chat_log_path = r"Data\ChatLog.json"

# Try loading existing chat log, or create empty file if not found
try:
    with open(chat_log_path, "r") as f:
        messages = load(f)
except FileNotFoundError:
    with open(chat_log_path, "w") as f:
        dump([], f)

messages = []

# Function to get real-time information
def RealtimeInformation():
    current_date_time = datetime.datetime.now()
    day = current_date_time.strftime("%A")
    date = current_date_time.strftime("%d")
    month = current_date_time.strftime("%B")
    year = current_date_time.strftime("%Y")
    hour = current_date_time.strftime("%H")
    minute = current_date_time.strftime("%M")
    second = current_date_time.strftime("%S")
    data = f"Please use this real-time information if needed,\n"
    data += f"Day: {day}\nDate: {date}\nMonth: {month}\nYear: {year}\n"
    data += f"Time: {hour} hours :{minute} minutes :{second} seconds.\n"
    return data

# Function to clean up the chatbot's answer
def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

# Main chatbot function
def ChatBot(Query):
    try:
        # Special hardcoded response for "hello"
        if Query.strip().lower() == "hello":
            return f"Hi {Username}, it's nice meeting you! How can I assist you?"

        # Load existing chat log
        with open(chat_log_path, "r") as f:
            messages = load(f)

        messages.append({"role": "user", "content": Query})

        # Create completion using Groq API
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=SystemChatBot + [{"role": "system", "content": RealtimeInformation()}] + messages,
            max_tokens=1024,
            temperature=0.7,
            top_p=1,
            stream=True,
            stop=None
        )

        Answer = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                Answer += chunk.choices[0].delta.content

        Answer = Answer.replace("</s>", "").strip()
        messages.append({"role": "assistant", "content": Answer})

        # Save updated messages
        with open(chat_log_path, "w") as f:
            dump(messages, f, indent=4)

        return AnswerModifier(Answer)

    except Exception as e:
        print(f"Error: {e}")
        with open(chat_log_path, "w") as f:
            dump([], f, indent=4)
        return f"An error occurred: {e}"


# Entry point
if __name__ == "__main__":
    while True:
        user_input = input("Enter your question (or type 'exit' to quit): ")
        if user_input.lower() in ["exit", "quit"]:
            break
        print(ChatBot(user_input))
