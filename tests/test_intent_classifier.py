import unittest
from unittest.mock import Mock

from intent_classifier import classify_intent


class IntentClassifierTests(unittest.TestCase):
    def test_valid_label(self):
        client = Mock()
        client.chat.return_value = {"message": {"content": " deadline\n"}}
        self.assertEqual(classify_intent(client, "Wann endet die Frist?"),
                         ("deadline", "ok"))

    def test_invalid_label_and_service_failure(self):
        client = Mock()
        client.chat.return_value = {"message": {"content": "invented_label"}}
        self.assertEqual(classify_intent(client, "Question"),
                         ("unknown", "invalid_response"))
        client.chat.side_effect = RuntimeError("unavailable")
        self.assertEqual(classify_intent(client, "Question"),
                         ("unknown", "error"))


if __name__ == "__main__":
    unittest.main()
