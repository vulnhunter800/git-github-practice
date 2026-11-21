import unittest

from recon.analysis import find_candidate_ai_urls, is_candidate_ai_url


class AnalysisTests(unittest.TestCase):
    def test_ai_route_keyword_matches(self):
        self.assertTrue(is_candidate_ai_url("https://example.com/api/v1/chat/completions"))

    def test_normal_route_does_not_match(self):
        self.assertFalse(is_candidate_ai_url("https://example.com/about"))

    def test_unique_results_preserve_order(self):
        urls = [
            "https://example.com/api/chat",
            "https://example.com/about",
            "https://example.com/api/chat",
        ]
        self.assertEqual(
            find_candidate_ai_urls(urls),
            ["https://example.com/api/chat"],
        )


if __name__ == "__main__":
    unittest.main()
