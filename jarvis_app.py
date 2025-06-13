import sys
import pyttsx3

try:
    from jarvis_nlp.nlp_processor import NLPProcessor
except ImportError:
    # Fallback for running script directly from root for now
    # This assumes that the nlp_processor.py file is in a directory named "jarvis_nlp"
    # and the script is run from the parent directory of "jarvis_nlp".
    # A more robust solution would involve setting PYTHONPATH or installing as a package.
    sys.path.append('jarvis_nlp') # Temporarily add to path
    try:
        from nlp_processor import NLPProcessor
    except ImportError as e:
        print(f"Failed to import NLPProcessor even after path adjustment: {e}")
        sys.exit(1)

try:
    # Import the registry instead of individual functions
    from jarvis_skills.skills import SKILL_REGISTRY
except ImportError as e:
    print(f"Warning: Could not import SKILL_REGISTRY from jarvis_skills.skills ({e}). Skills will not work.")
    SKILL_REGISTRY = {} # Empty registry as a fallback

APP_INTENT_DEFINITIONS = [
    {
        "intent_name": "openApp",
        "regex_pattern": r"^(?:jarvis\s)?(?:please\s)?(?:open|launch|start)\s+([\w\s.-]+)",
        "entity_keys": ["appName"],
        "keywords": ["open app", "launch application", "start this app", "open"]
    },
    {
        "intent_name": "getTime",
        "regex_pattern": r"^(?:jarvis\s)?(?:.*\b(time|what time|current time)\b.*)",
        "entity_keys": [],
        "keywords": ["what time is it", "what is the current time", "tell me the time"]
    },
    {
        "intent_name": "searchWeb",
        "regex_pattern": r"^(?:jarvis\s)?(?:search for|search|find|look up)\s+(.+)",
        "entity_keys": ["query"],
        "keywords": ["search the web for", "find on internet", "look up online", "search", "find"]
    },
    {
        "intent_name": "checkWeather",
        "regex_pattern": r"^(?:jarvis\s)?(?:.*\b(weather|forecast)\b.*)",
        "entity_keys": [],
        "keywords": ["how is the weather", "weather forecast today", "is it raining", "weather conditions"]
    }
]

tts_engine = None

def speak(text_to_speak: str):
    if tts_engine:
        print(f"Jarvis (speaking): {text_to_speak}")
        tts_engine.say(text_to_speak)
        tts_engine.runAndWait()
    else:
        print(f"Jarvis (TTS not ready): {text_to_speak}")

def main():
    global tts_engine
    print("Initializing Jarvis...")
    try:
        tts_engine = pyttsx3.init()
    except Exception as e:
        print(f"Error initializing TTS engine: {e}. Jarvis will be silent.")

    speak("Jarvis initializing.")

    try:
        nlp_processor = NLPProcessor(APP_INTENT_DEFINITIONS, keyword_threshold=75)
        speak("Natural Language Processor initialized. Ready for commands.")
    except Exception as e: # Broader exception for NLP init
        error_msg = f"Critical Error initializing NLPProcessor: {e}. Jarvis cannot operate."
        print(error_msg)
        if tts_engine: speak(error_msg)
        return

    while True:
        try:
            user_input = input("You: ")
        except EOFError:
            print("\nJarvis: Exiting...")
            if tts_engine: speak("Exiting now.")
            break
        except KeyboardInterrupt:
            print("\nJarvis: Exiting...")
            if tts_engine: speak("Exiting now.")
            break

        if user_input.lower() in ["quit", "exit"]:
            goodbye_msg = "Goodbye!"
            print(f"Jarvis: {goodbye_msg}")
            if tts_engine: speak(goodbye_msg)
            break

        if not user_input:
            continue

        try:
            result = nlp_processor.process(user_input)
        except Exception as e:
            error_msg = f"An error occurred during NLP processing: {e}"
            print(f"Jarvis: {error_msg}")
            if tts_engine: speak(error_msg)
            result = None

        response_message = None
        if result:
            intent = result['intent']
            params = result['params']

            if intent in SKILL_REGISTRY:
                skill_function = SKILL_REGISTRY[intent]
                try:
                    response_message = skill_function(params)
                except Exception as e:
                    error_msg = f"Error executing skill '{intent}': {e}" # More specific error
                    print(f"Jarvis: {error_msg}") # Print the error
                    if tts_engine: speak(error_msg) # Speak the error
                    response_message = "I had trouble performing that action." # Generic user-facing message
            else:
                # Intent understood by NLP but no specific skill in registry
                response_message = f"I understood your intent is '{intent}' with parameters {params}, but I don't have a specific skill for that yet."
        else:
            response_message = "Sorry, I didn't understand that."

        # Ensure response_message is never None here to avoid issues with print/speak if logic above changes
        if response_message is None:
            response_message = "I encountered an unexpected issue." # Should not happen with current logic

        print(f"Jarvis: {response_message}")
        if tts_engine: speak(response_message)

if __name__ == '__main__':
    main()
