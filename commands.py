import os
import requests
from halo import Halo
from rich.console import Console
from rich.markdown import Markdown
from serpapi import GoogleSearch

console = Console(width=100)

def search():
    response = requests.get('http://ip-api.com/json/')
    data = response.json()
    users_location = f"{data['city']}, {data['regionName']}, {data['country']}"

    # Get the SerpAPI key
    SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

    print("Sure, let me google that for you.")

    search_query = input("\nEnter your search query: ")

    params = {
        "q": search_query,
        "location": users_location,
        "hl": "en",
        "gl": "us",
        "google_domain": "google.com",
        "api_key": SERPAPI_API_KEY
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    
    search_results_as_str = ""
    if 'answer_box' in results:
        answer_box = results['answer_box']
        title = answer_box.get('title', 'No title available')
        url = answer_box.get('link', 'No URL available')
        snippet = answer_box.get('snippet', 'No snippet available')
        search_results_as_str += f"\nAnswer Box:\nTitle: {title}\nURL: {url}\nSnippet: {snippet}\n"

    for i, result in enumerate(results['organic_results'], start=1):
        title = result.get('title', 'No title available')
        url = result.get('link', 'No URL available')
        snippet = result.get('snippet', 'No snippet available')
        search_results_as_str += f"\nResult {i}:\nTitle: {title}\nURL: {url}\nSnippet: {snippet}\n"

    intro_message = f"Pretend you are Google. The user has just asked you to google the following search terms or question '{search_query}'. Given the following context, which is actual Google search result snippets, please respond to the user's search. At the end of your response, return the URL or URLs in standard markdown format that were most useful to you in answering the user's search."
    search_results = intro_message + search_results_as_str

    return search_results