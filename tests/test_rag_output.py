import unittest
from unittest.mock import Mock, patch

import chromadb

with patch.object(chromadb, "PersistentClient") as persistent_client:
    persistent_client.return_value.get_collection.return_value = Mock()
    import rag


class RagOutputTests(unittest.TestCase):
    def test_adds_relevant_source_link_to_answer(self):
        hits = [{
            "source": "THWS Faculty FIW",
            "section": "FIW studies > Programme contact",
            "source_url": "https://fiw.thws.de/en/studies/",
        }]

        answer = rag.add_source_link("The advisor is listed on the contacts page [1].", hits)

        self.assertIn(
            "[FIW studies > Programme contact](https://fiw.thws.de/en/studies/)",
            answer,
        )

    def test_does_not_duplicate_source_link_already_in_answer(self):
        url = "https://fiw.thws.de/en/studies/"
        hits = [{"source": "THWS Faculty FIW", "section": "FIW studies", "source_url": url}]

        answer = rag.add_source_link(f"See {url}", hits)

        self.assertEqual(answer, f"See {url}")

    def test_no_answer_does_not_get_unrelated_retrieval_link(self):
        text = 'I could not find information about "dekant" in the provided context.'
        hits = [{"source": "Exams", "section": "Deregistration", "source_url": "https://example.org/exams"}]
        self.assertEqual(rag.add_source_link(text, hits), text)

    def test_links_cited_passage_instead_of_first_result(self):
        hits = [
            {"source": "Wrong", "section": "", "source_url": "https://example.org/wrong"},
            {"source": "Helpdesk", "section": "", "source_url": "https://example.org/help"},
        ]
        text = rag.add_source_link("Contact the helpdesk [2].", hits)
        self.assertIn("https://example.org/help", text)
        self.assertNotIn("https://example.org/wrong", text)

    def test_invalid_citation_does_not_add_link(self):
        text = "Contact the office [9]."
        hits = [{"source": "Office", "section": "", "source_url": "https://example.org"}]
        self.assertEqual(rag.add_source_link(text, hits), text)


if __name__ == "__main__":
    unittest.main()
