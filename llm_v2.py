import openai
import argparse
import requests
import time
from embedchain import App
from commands import *
from serpapi import GoogleSearch
from rich.console import Console
from rich.markdown import Markdown
from halo import Halo







console = Console(width=100)

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Ask a question to the model.")
parser.add_argument("-q", "--question", type=str, help="Question to ask.")
parser.add_argument("-m", "--mode", type=str, default=None, choices=['simple', 'chat'], help="Mode to start the model in.")
args = parser.parse_args()

# Store conversation history
conversation_history = [
    {"role": "system", "content": "You are a friendly assistant who lives in the CLI."},
]

def complete_conversation(user_question, conversation_mode):
    try:
        # Append the user question to the conversation history
        conversation_history.append({"role": "user", "content": user_question})

        if conversation_mode == "chat":
            messages = conversation_history
        else:
            messages = [
                {"role": "system", "content": "You are a friendly assistant who lives in the CLI."},
                {"role": "user", "content": user_question}
            ]

        # pass the conversation to the GPT model
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=messages,
            temperature=.5,
            stream=True
        )

        # response = completion.choices[0].message['content']

        # Print User Greeting
        console.print("LLM: ", style="#39FF14", end="")

        collected_chunks = []
        collected_messages = "" 

        for chunk in completion:
            collected_chunks.append(chunk)
            chunk_message = chunk['choices'][0]['delta']
            if "content" in chunk_message:
                message_text = chunk_message['content']
                collected_messages += message_text
                console.print(message_text, end="")

        # Add the model's response to the conversation history
        if conversation_mode == "chat":
            conversation_history.append({"role": "assistant", "content": collected_messages})
              
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if args.mode is None:
    while True:
        mode = input("Please enter the mode you want to start in (simple or chat): ")
        if mode in ['simple', 'chat']:
            conversation_mode = mode
            break
        else:
            print("Invalid mode. Please choose either 'simple' or 'chat'.")
else:
    conversation_mode = args.mode

while True:
    if args.question:
        user_question = args.question
        args.question = None  # Ensure the command line argument is used only for the first iteration
    else:
        console.print("\nPlease enter your question (or 'exit' to quit): ", style="#39FF14", end="")
        user_question = input("")
    if user_question.lower() == 'exit':
        break
    elif user_question.lower() == 'search':
        user_question = search()
        try:
            complete_conversation(user_question, conversation_mode)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
    elif user_question.lower() == 'test':
        test_app = App()
        test_app.add("pdf_file", "https://www.supremecourt.gov/opinions/22pdf/21-1168_f2ah.pdf")
        user_question = input("Enter your question: ")
        print(test_app.query(user_question))
    else:
        try:
            complete_conversation(user_question, conversation_mode)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
