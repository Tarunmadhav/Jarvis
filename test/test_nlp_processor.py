import unittest
import sys
import os

# Adjust path to import NLPProcessor from jarvis_nlp directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jarvis_nlp.nlp_processor import NLPProcessor

# Updated Test Intent Definitions to match the latest version in nlp_processor.py
# These include 'keywords' and the 'checkWeather' intent.
TEST_INTENT_DEFINITIONS = [
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
        "keywords": ["how is the weather", "weather forecast today", "is it raining outside", "temperature check", "weather conditions"]
    }
]

class TestNLPProcessor(unittest.TestCase):

    def setUp(self):
        """Set up an NLPProcessor instance for use in tests with a default threshold."""
        # Using a threshold that was found to work well in manual testing.
        self.default_threshold = 75
        self.processor = NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=self.default_threshold)

    def test_preprocess(self):
        self.assertEqual(self.processor.preprocess("  TeSt PhRaSe  "), "test phrase")
        self.assertEqual(self.processor.preprocess(123), "", "Preprocessing non-string should return empty string")

    def test_open_app_intent(self):
        # Test cases that should pass keyword validation
        passing_phrases = {
            "jarvis open Notepad.exe": {"appName": "notepad.exe"},
            "please start my app launcher": {"appName": "my app launcher"}, # "start this app" keyword helps
            "open VS Code": {"appName": "vs code"}, # "open" keyword
        }
        for phrase, expected_params in passing_phrases.items():
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result)
                self.assertEqual(result["intent"], "openApp")
                self.assertEqual(result["params"], expected_params)

    def test_get_time_intent(self):
        passing_phrases = [
            "jarvis what time is it",            # "what time is it" keyword
            "What's the current time please?",   # "what is the current time" keyword
            "show me the time"                   # "tell me the time" keyword
        ]
        for phrase in passing_phrases:
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result)
                self.assertEqual(result["intent"], "getTime")
                self.assertEqual(result["params"], {})

    def test_search_web_intent(self):
        passing_phrases = {
            "jarvis search for latest AI news": {"query": "latest ai news"}, # "search" keyword
            "look up python tutorials online": {"query": "python tutorials online"}, # "look up online" keyword
            "jarvis search for cats": {"query": "cats"} # "search" keyword
        }
        for phrase, expected_params in passing_phrases.items():
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result)
                self.assertEqual(result["intent"], "searchWeb")
                self.assertEqual(result["params"], expected_params)

    def test_check_weather_intent(self):
        passing_phrases = {
            "forecast today": {}, # "weather forecast today" keyword
            "show weather conditions": {} # "weather conditions" keyword (score 100)
        }
        for phrase, expected_params in passing_phrases.items():
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result)
                self.assertEqual(result["intent"], "checkWeather")
                self.assertEqual(result["params"], expected_params)

        # Test case that should be filtered by keyword threshold
        # "jarvis weather" has max keyword score of 67, default threshold is 75
        self.assertIsNone(self.processor.process("jarvis weather"),
                          "Expected 'jarvis weather' to be filtered by keyword score")

    def test_keyword_filtering_logic(self):
        # Test with a specific threshold
        processor_strict = NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=90)
        processor_lenient = NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=60)

        # This phrase matched 'checkWeather' regex, keyword "weather conditions" (score 100)
        self.assertIsNotNone(processor_strict.process("show weather conditions"))
        self.assertIsNotNone(processor_lenient.process("show weather conditions"))

        # "jarvis weather" -> max score 67 for checkWeather keywords
        self.assertIsNone(processor_strict.process("jarvis weather"),
                          "'jarvis weather' should fail with threshold 90")
        result_lenient = processor_lenient.process("jarvis weather")
        self.assertIsNotNone(result_lenient, "'jarvis weather' should pass with threshold 60")
        if result_lenient:
             self.assertEqual(result_lenient["intent"], "checkWeather")

    def test_unknown_command_after_keyword_filtering(self):
        # Phrases that might match regex but should fail keyword or are genuinely unknown
        phrases = [
            "tell me a joke",
            "jarvis how are you",
            # "jarvis weather" is handled by test_check_weather_intent with default threshold
            "jarvis open", # Fails regex (needs appName)
            "search",      # Fails regex (needs query after space)
            "what is the temperature today", # Fails all regex (no "weather" or "forecast" keyword)
            "book a flight",
            "",
            "   "
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                result = self.processor.process(phrase)
                self.assertIsNone(result, f"Expected None for '{phrase}', got {result}")

        # Case: "search for" - specific regex, specific keyword "search" or "find"
        # This phrase results in query: "for" and matches "search" keyword at 100%
        # So it should be recognized.
        result_search_for = self.processor.process("search for")
        self.assertIsNotNone(result_search_for, "'search for' should be recognized")
        if result_search_for:
            self.assertEqual(result_search_for["intent"], "searchWeb")
            self.assertEqual(result_search_for["params"], {"query": "for"})


    def test_initialization_errors(self):
        with self.assertRaisesRegex(ValueError, "Intent definitions list cannot be empty"):
            NLPProcessor([])

        with self.assertRaisesRegex(ValueError, "missing 'intent_name' or 'regex_pattern'"):
            NLPProcessor([{ "name": "test" }])

        with self.assertRaisesRegex(ValueError, "Invalid regex pattern for intent"):
            NLPProcessor([{ "intent_name": "test_invalid_regex", "regex_pattern": "[" }])

        with self.assertRaisesRegex(ValueError, "Keyword threshold must be between 0 and 100"):
            NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=-1)
        with self.assertRaisesRegex(ValueError, "Keyword threshold must be between 0 and 100"):
            NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=101)

        with self.assertRaisesRegex(ValueError, "Keywords for intent .* must be a list"):
             NLPProcessor([{
                "intent_name": "test_kw_type",
                "regex_pattern": r".",
                "keywords": "not-a-list"
            }])

if __name__ == '__main__':
    unittest.main(verbosity=2)
