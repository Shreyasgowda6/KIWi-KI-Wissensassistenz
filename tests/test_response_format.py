import unittest

from response_format import prepare_response, conversational_reply


class ResponseFormatTests(unittest.TestCase):
    def test_social_messages_have_no_sources(self):
        for message in ["How are you?", "Hi KIWi, how are you?", "Wie geht es dir?", "Thanks!", "Hi!"]:
            with self.subTest(message=message):
                reply = conversational_reply(message)
                self.assertIsNotNone(reply)
                self.assertEqual(reply["sources"], [])
                self.assertNotIn("https://", reply["content"])

    def test_social_prefix_does_not_swallow_real_question(self):
        self.assertIsNone(conversational_reply("Hi, how do I register for exams?"))
        self.assertIsNone(conversational_reply("How are you funded by THWS?"))

    def test_model_link_and_sources_removed_from_no_answer(self):
        text = ('I could not find information about dekant in the provided context. '
                'Please clarify the office. [1]\n\n'
                '[Advisory Services](https://example.org/advice)')
        clean, sources = prepare_response(text, [{"source": "Advice"}])
        self.assertNotIn("https://", clean)
        self.assertNotIn("Advisory Services", clean)
        self.assertNotIn("[1]", clean)
        self.assertIn("Please clarify", clean)
        self.assertEqual(sources, [])

    def test_supported_answer_unchanged(self):
        text = 'The office is in room 12 [1]. [Contact](https://example.org/contact)'
        hits = [{"source": "Contact"}]
        self.assertEqual(prepare_response(text, hits), (text, hits))

    def test_german_abstention(self):
        text = 'Ich konnte keine Informationen dazu finden. https://example.org'
        clean, hits = prepare_response(text, [{"source": "Other"}])
        self.assertNotIn("https://", clean)
        self.assertEqual(hits, [])

    def test_clarification_has_no_source_panel(self):
        text = "Which faculty's dean's office do you mean?"
        self.assertEqual(prepare_response(text, [{"source": "Unrelated"}]), (text, []))
