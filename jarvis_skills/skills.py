import datetime
import webbrowser
import urllib.parse

def get_current_time(params: dict) -> str:
    """
    Retrieves the current time and formats it into a user-friendly string.
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
        # In a real scenario, this might involve OS-specific commands.
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
    # Default to YouTube search
    search_url = f"https://www.youtube.com/results?search_query={encoded_media_title}"

    if media_service_input:
        service_lower = media_service_input.lower()
        if "youtube" in service_lower:
            service_name_for_message = "YouTube"
            # URL already set by default for YouTube
        elif "spotify" in service_lower:
            service_name_for_message = "Spotify"
            search_url = f"https://open.spotify.com/search/{encoded_media_title}"
        # else, it uses the YouTube default set above for other service names

    try:
        webbrowser.open_new_tab(search_url)
        return f"Searching for '{media_title}' on {service_name_for_message}..."
    except Exception as e:
        print(f"Error opening web browser for media: {e}")
        return f"Sorry, I encountered an error trying to play '{media_title}' on {service_name_for_message}."

SKILL_REGISTRY = {
    "getTime": get_current_time,
    "openApp": open_application, # This function is now enhanced
    "searchWeb": search_web,
    "checkWeather": check_weather_skill,
    "playMedia": play_media,
}
