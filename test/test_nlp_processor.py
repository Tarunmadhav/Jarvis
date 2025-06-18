import unittest
import sys
import os

# Adjust path to import NLPProcessor from jarvis_nlp directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from jarvis_nlp.nlp_processor import NLPProcessor

# Updated Test Intent Definitions to match APP_INTENT_DEFINITIONS in jarvis_app.py
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
    },
    # NEW playMedia definitions (mirrored from jarvis_app.py)
    {
        "intent_name": "playMedia",
        "regex_pattern": r"^(?:jarvis\s)?(?:please\s)?(?:play|stream)\s+(.+?)\s+on\s+([\w\s]+)",
        "entity_keys": ["mediaTitle", "mediaService"],
        "keywords": ["play on", "stream on", "listen to on"]
    },
    {
        "intent_name": "playMedia",
        "regex_pattern": r"^(?:jarvis\s)?(?:please\s)?(?:play|stream)\s+(.+)",
        "entity_keys": ["mediaTitle"],
        "keywords": ["play", "stream", "listen to"]
    },
]

class TestNLPProcessor(unittest.TestCase):

    def setUp(self):
        """Set up an NLPProcessor instance for use in tests with a default threshold."""
        self.default_threshold = 75
        self.processor = NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=self.default_threshold)
        # More lenient processor for specific keyword tests if needed
        self.lenient_processor = NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=60)


    def test_preprocess(self):
        self.assertEqual(self.processor.preprocess("  TeSt PhRaSe  "), "test phrase")
        self.assertEqual(self.processor.preprocess(123), "", "Preprocessing non-string should return empty string")

    def test_open_app_intent(self):
        passing_phrases = {
            "jarvis open Notepad.exe": {"appName": "notepad.exe"},
            "please start my app launcher": {"appName": "my app launcher"},
            "open VS Code": {"appName": "vs code"},
        }
        for phrase, expected_params in passing_phrases.items():
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result, f"Phrase '{phrase}' failed.")
                if result: # Keep linter happy
                    self.assertEqual(result["intent"], "openApp")
                    self.assertEqual(result["params"], expected_params)

    def test_get_time_intent(self):
        passing_phrases = [
            "jarvis what time is it",
            "What's the current time please?",
            "show me the time"
        ]
        for phrase in passing_phrases:
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result, f"Phrase '{phrase}' failed.")
                if result:
                    self.assertEqual(result["intent"], "getTime")
                    self.assertEqual(result["params"], {})

    def test_search_web_intent(self):
        passing_phrases = {
            "jarvis search for latest AI news": {"query": "latest ai news"},
            "look up python tutorials online": {"query": "python tutorials online"},
            "jarvis search for cats": {"query": "cats"}
        }
        for phrase, expected_params in passing_phrases.items():
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result, f"Phrase '{phrase}' failed.")
                if result:
                    self.assertEqual(result["intent"], "searchWeb")
                    self.assertEqual(result["params"], expected_params)

    def test_check_weather_intent(self):
        passing_phrases = {
            "forecast today": {},
            "show weather conditions": {}
        }
        for phrase, expected_params in passing_phrases.items():
            with self.subTest(phrase=phrase, type="passing"):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result, f"Phrase '{phrase}' failed.")
                if result:
                    self.assertEqual(result["intent"], "checkWeather")
                    self.assertEqual(result["params"], expected_params)

        self.assertIsNone(self.processor.process("jarvis weather"),
                          "Expected 'jarvis weather' to be filtered by keyword score (default threshold 75)")

    def test_play_media_intent(self):
        # Test with service
        phrases_with_service = {
            "jarvis play Hotel California on youtube": {"mediaTitle": "hotel california", "mediaService": "youtube"},
            "please stream my workout mix on spotify": {"mediaTitle": "my workout mix", "mediaService": "spotify"},
            "Play The Four Seasons on Apple Music": {"mediaTitle": "the four seasons", "mediaService": "apple music"},
        }
        for phrase, expected_params in phrases_with_service.items():
            with self.subTest(msg="Play Media with Service", phrase=phrase):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result, f"Expected intent for '{phrase}', got None")
                if result:
                    self.assertEqual(result["intent"], "playMedia", f"Incorrect intent for '{phrase}'")
                    self.assertEqual(result["params"], expected_params, f"Incorrect params for '{phrase}'")

        # Test without service (should use the second playMedia regex)
        phrases_without_service = {
            "jarvis play a good song": {"mediaTitle": "a good song"},
            "stream classical music": {"mediaTitle": "classical music"},
            "PLEASE PLAY LOUD MUSIC": {"mediaTitle": "loud music"}
        }
        for phrase, expected_params in phrases_without_service.items():
            with self.subTest(msg="Play Media without Service", phrase=phrase):
                result = self.processor.process(phrase)
                self.assertIsNotNone(result, f"Expected intent for '{phrase}', got None")
                if result:
                    self.assertEqual(result["intent"], "playMedia", f"Incorrect intent for '{phrase}'")
                    self.assertEqual(result["params"], expected_params, f"Incorrect params for '{phrase}', expected no mediaService")
                    self.assertNotIn("mediaService", result["params"], f"'mediaService' should not be present for '{phrase}'")

        # Test phrase that should be filtered by keywords
        # The regex for playMedia with service is: r"^(?:jarvis\s)?(?:please\s)?(?:play|stream)\s+(.+?)\s+on\s+([\w\s]+)"
        # Keywords: ["play on", "stream on", "listen to on"]
        # Phrase "jarvis list my songs on spotify"
        # Regex part (?:play|stream) will not match "list". So this should be None due to regex mismatch.
        phrase_weak_keyword_regex_mismatch = "jarvis list my songs on spotify"
        result_weak_keyword = self.processor.process(phrase_weak_keyword_regex_mismatch)
        self.assertIsNone(result_weak_keyword, f"Phrase '{phrase_weak_keyword_regex_mismatch}' should not match playMedia regex, but got {result_weak_keyword}")

        # Test a phrase that *matches* playMedia regex but keywords are weak for the *overall phrase*.
        # Example: "jarvis use the player for my track on my device"
        # Regex: play (.+?) on ([\w\s]+) -> title="my track", service="my device"
        # Keywords for "playMedia" with service: ["play on", "stream on", "listen to on"]
        # fuzz.token_set_ratio("jarvis use the player for my track on my device", "play on") might be low.
        phrase_matches_regex_weak_keywords = "jarvis use the player for my track on my device"
        # This test needs a processor with a higher threshold or very specific keywords to demonstrate filtering.
        # The current keywords like "play on" are quite generic.
        # Let's refine this test. If the phrase is "play my track on my device", it should pass.
        # If the phrase is "show my track on my device", it should fail keywords.

        passing_phrase_strong_keyword = "play my track on my device"
        result_strong_keyword = self.processor.process(passing_phrase_strong_keyword)
        self.assertIsNotNone(result_strong_keyword, f"Phrase '{passing_phrase_strong_keyword}' should match.")
        if result_strong_keyword:
             self.assertEqual(result_strong_keyword["params"]["mediaTitle"], "my track")
             self.assertEqual(result_strong_keyword["params"]["mediaService"], "my device")

        # This phrase *will* match the regex for playMedia (title: "my track", service: "my device")
        # but "show" is not a primary keyword for the "play" action.
        # Keywords for playMedia with service are: ["play on", "stream on", "listen to on"]
        # token_set_ratio("show my track on my device", "play on") should be < 75
        failing_phrase_weak_keywords = "show my track on my device"
        result_fail_keywords = self.processor.process(failing_phrase_weak_keywords)
        self.assertIsNone(result_fail_keywords, f"Phrase '{failing_phrase_weak_keywords}' should be filtered by keywords, got {result_fail_keywords}")


    def test_keyword_filtering_logic(self):
        processor_strict = NLPProcessor(TEST_INTENT_DEFINITIONS, keyword_threshold=90)
        # "jarvis weather" -> max score 67 for checkWeather keywords
        self.assertIsNone(processor_strict.process("jarvis weather"),
                          "'jarvis weather' should fail with threshold 90")
        result_lenient = self.lenient_processor.process("jarvis weather") # threshold 60
        self.assertIsNotNone(result_lenient, "'jarvis weather' should pass with threshold 60")
        if result_lenient:
             self.assertEqual(result_lenient["intent"], "checkWeather")

    def test_unknown_command_after_keyword_filtering(self):
        phrases = [
            "tell me a joke",
            "jarvis how are you",
            "jarvis open",
            "search",
            "what is the temperature today",
            "book a flight",
            "",
            "   "
        ]
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                result = self.processor.process(phrase)
                self.assertIsNone(result, f"Expected None for '{phrase}', got {result}")

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
