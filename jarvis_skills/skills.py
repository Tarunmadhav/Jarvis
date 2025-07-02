import datetime
import webbrowser
import urllib.parse
import openai
import os # For API key management in production

# --- IMPORTANT SECURITY NOTE ---
# The API key is hardcoded here FOR SUBTASK TESTING ONLY in an isolated environment.
# In a real application, NEVER hardcode API keys. Use environment variables
# or a secure configuration management system.
# Example for real use: OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
# The key provided by the user will be used here for this subtask.
OPENROUTER_API_KEY = "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" # Replace with your actual key if testing locally
OPENROUTER_MODEL = "mistralai/mistral-7b-instruct:free" # Or other confirmed free model like "nousresearch/nous-capybara-7b:free"

def get_current_time(params: dict) -> str:
    """
    Retrieves the current time and formats it into a user-friendly string.
    Params is unused but included for consistent skill signature.
    """
    now = datetime.datetime.now()
    formatted_time = now.strftime("%I:%M %p")
    return f"The current time is {formatted_time}."

def open_application(params: dict) -> str:
    """
    Opens specific web services (YouTube, Spotify) or returns a placeholder
    message for other application names.
    """
    app_name_original = params.get('appName') # Keep original casing for messages
    if not app_name_original:
        return "No application name specified for opening."

    app_name_lower = app_name_original.lower()
    url_to_open = None
    message = f"Attempting to open {app_name_original}..." # Default message

    if app_name_lower == "youtube":
        url_to_open = "https://www.youtube.com"
        message = "Opening YouTube..."
    elif app_name_lower == "spotify":
        url_to_open = "https://open.spotify.com"
        message = "Opening Spotify..."
    # Add other specific web services here as elif blocks if needed

    if url_to_open:
        try:
            webbrowser.open_new_tab(url_to_open)
            return message
        except Exception as e:
            print(f"Error opening web browser for {app_name_original}: {e}")
            return f"Sorry, I encountered an error trying to open {app_name_original}."
    else:
        # For non-web-service apps, this is just a placeholder
        return message


def search_web(params: dict) -> str:
    """
    Performs a web search using the default browser.
    """
    query = params.get('query')
    if not query:
        return "You didn't specify what to search for."

    try:
        encoded_query = urllib.parse.quote_plus(query)
        search_url = f"https://www.google.com/search?q={encoded_query}"
        webbrowser.open_new_tab(search_url)
        return f"Searching the web for '{query}'..."
    except Exception as e:
        print(f"Error opening web browser for search: {e}")
        return f"Sorry, I encountered an error trying to search for '{query}'."

def check_weather_skill(params: dict) -> str:
    """
    Placeholder skill for checking the weather.
    """
    return "Fetching the latest weather forecast for you."

def play_media(params: dict) -> str:
    """
    Opens a web browser to search for the specified media title on a
    streaming service (YouTube by default or Spotify if specified).
    """
    media_title = params.get('mediaTitle')
    media_service_input = params.get('mediaService')

    if not media_title:
        return "You need to specify what song or video you want to play."

    encoded_media_title = urllib.parse.quote_plus(media_title)
    service_name_for_message = "YouTube (default)"
    # Default URL for YouTube search
    search_url = f"https://www.youtube.com/results?search_query={encoded_media_title}"

    if media_service_input:
        service_lower = media_service_input.lower()
        if "youtube" in service_lower:
            service_name_for_message = "YouTube"
            # URL already set by default for YouTube
        elif "spotify" in service_lower:
            service_name_for_message = "Spotify"
            # Spotify's search URL structure
            search_url = f"https://open.spotify.com/search/{encoded_media_title}"
        # else, it uses the YouTube default set above for other service names

    try:
        webbrowser.open_new_tab(search_url)
        return f"Searching for '{media_title}' on {service_name_for_message}..."
    except Exception as e:
        print(f"Error opening web browser for media: {e}")
        return f"Sorry, I encountered an error trying to play '{media_title}' on {service_name_for_message}."

def query_text_file(params: dict) -> str:
    """
    Reads a text file and uses an LLM via OpenRouter to answer a question
    about it or summarize it.
    """
    file_path = params.get('filePath')
    query_text = params.get('queryText') # Optional

    if not file_path:
        return "You need to specify the path to the file."

    try:
        # Basic security: ensure we're only trying to read text files for now
        # This is not a foolproof security measure but a basic guardrail.
        if not file_path.lower().endswith((".txt", ".md", ".py", ".json", ".csv")): # Expanded allowed extensions
            return "Sorry, I can only analyze common text-based files (.txt, .md, .py, .json, .csv) at the moment."

        # Further path validation/sandboxing would be needed in a real-world app
        # to prevent access to arbitrary system files. For this subtask, we assume
        # file_path is relative to where the script is run or an accessible path.

        with open(file_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
    except FileNotFoundError:
        return f"Sorry, I couldn't find the file: {file_path}"
    except UnicodeDecodeError:
        return f"Sorry, I had trouble reading the file '{file_path}'. It might not be a plain text file or has an unsupported encoding."
    except IOError as e:
        return f"Sorry, I encountered an error reading the file '{file_path}': {e}"

    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY_HERE": # Check if API key is placeholder or empty
        return "API key for OpenRouter is not configured. I cannot analyze the file."

    try:
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )

        if query_text:
            prompt = f"Based on the following document content:\n\n---\n{file_content}\n---\n\nPlease answer this question: {query_text}"
        else:
            prompt = f"Please summarize the key points of the following document:\n\n---\n{file_content}\n---"

        # Basic length check to avoid overly long requests (very approximate)
        # A robust solution would use token counting specific to the model.
        MAX_CONTENT_LENGTH_FOR_PROMPT = 18000 # Approx 4k tokens (1 char ~ 4-5 bytes, 1 token ~ 4 chars)
        if len(file_content) > MAX_CONTENT_LENGTH_FOR_PROMPT:
             return f"The file '{file_path}' is too long for me to process directly ({len(file_content)} chars). Please try with a smaller file."

        completion = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant that analyzes documents and answers questions based on their content."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7, # Adjust for creativity vs. factuality
            max_tokens=300  # Max tokens for the response
        )
        llm_response = completion.choices[0].message.content
        return llm_response if llm_response else "I received an empty response from the AI."

    except openai.AuthenticationError:
        return "Sorry, there's an issue with the AI service authentication. Please check the API key."
    except openai.RateLimitError:
        return "Sorry, the AI service is busy or the rate limit was exceeded. Please try again later."
    except openai.APIConnectionError:
        return "Sorry, I couldn't connect to the AI service. Please check your internet connection."
    except openai.APIStatusError as e: # More specific error for API status issues
        print(f"OpenRouter API Status Error: {e.status_code} - {e.response}")
        return f"Sorry, the AI service reported an error: {e.status_code}."
    except openai.APIError as e:
        print(f"OpenRouter API Error: {e}")
        return f"Sorry, I encountered an error with the AI service: {e}"
    except Exception as e:
        print(f"An unexpected error occurred while querying the LLM: {e}")
        return "Sorry, an unexpected error occurred while trying to analyze the file."

SKILL_REGISTRY = {
    "getTime": get_current_time,
    "openApp": open_application,
    "searchWeb": search_web,
    "checkWeather": check_weather_skill,
    "playMedia": play_media,
    "queryFile": query_text_file, # Added new skill
}
