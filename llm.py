import openai
import argparse
import requests
import time
from commands import *
from email_command import send_email_report
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

def complete_conversation(user_question, conversation_mode, analyzed_google_results, snippets, search_bool=False):
    try:
        # Append the user question to the conversation history
        conversation_history.append({"role": "user", "content": user_question})

        if conversation_mode == "chat":
            messages = conversation_history
        else:
            messages = [
                {"role": "system", "content": "You are a friendly assistant who lives in the CLI. You may receive google search results and analysis from another LLM, analyze and incorporate the results to answer the user's question. Include any links in your response which were useful in answering the user's question. Always respond in well formatted Markdown."},
                {"role": "user", "content": f"User's Question: {user_question} + \nAnalyzed Google Results: {analyzed_google_results} + \nGoogle Snippets: {snippets}"}
            ]

        # pass the conversation to the GPT model
        completion = openai.ChatCompletion.create(
            model="gpt-4",
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

    if search_bool==True:
        
        # make space for search results
        console.print("\n\n\n\n===================================================================================================\n", style="#39FF14")

        # print collected_messages 
        console.print(Markdown(collected_messages))

        console.print("\n===================================================================================================", style="#39FF14")
    
    return collected_messages

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
        search_bool = True        
        while True:
            google_query = input("Enter your search query: ")
            try:
                token_count_bool = search_main(google_query)
                if token_count_bool == True:
                    break
                else:    
                    analyzed_google_results, snippets = search_main(google_query)           
                    collected_messages = complete_conversation(user_question, conversation_mode, analyzed_google_results, snippets, search_bool)
                    # ask user if they want to email the results
                    email_bool = input("Would you like to email the results? (y/n): ")
                    if email_bool.lower() == 'y':
                        user_email = input("Enter your email address: ")
                        send_email_report(user_email, collected_messages)
                        break
                    else:
                        break
            except Exception as e:
                print(f"An error occurred: {str(e)}")
    else:
        try:
            complete_conversation(user_question, conversation_mode, search_bool=False, snippets="", analyzed_google_results="")
        except Exception as e:
            print(f"An error occurred: {str(e)}")
