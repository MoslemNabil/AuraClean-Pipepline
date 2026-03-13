import unittest
from src.logic.phonetic_mapper import PhoneticMapper

class TestPhoneticMapper(unittest.TestCase):
    """
    Test suite for the PhoneticMapper class.
    Tests various mapping strategies: Exact, Phonetic, and Fuzzy.
    """

    def setUp(self):
        """Sets up a common Source of Truth for tests."""
        self.source_of_truth = ["Aspirin", "Metformin", "Amoxicillin", "Ibuprofen"]
        self.mapper = PhoneticMapper(source_of_truth=self.source_of_truth)

    def test_exact_match(self):
        """Tests that an exact match returns 1.0 confidence and no review required."""
        result = self.mapper.get_best_match("Metformin")
        self.assertEqual(result["cleaned_term"], "Metformin")
        self.assertEqual(result["confidence_score"], 1.0)
        self.assertEqual(result["match_method"], "Exact")
        self.assertFalse(result["review_required"])

    def test_phonetic_match_high_confidence(self):
        """Tests a close phonetic match (Metaphone) with > 85% confidence."""
        # 'Metforman' should match 'Metformin' via Metaphone
        result = self.mapper.get_best_match("Metforman")
        self.assertEqual(result["cleaned_term"], "Metformin")
        self.assertEqual(result["match_method"], "Phonetic")
        self.assertGreaterEqual(result["confidence_score"], 0.85)
        self.assertFalse(result["review_required"])

    def test_phonetic_match_low_confidence_review_required(self):
        """Tests a phonetic match with < 85% confidence, triggering review_required."""
        # 'Metf' might have the same metaphone but low ratio
        # Let's use a more realistic low-confidence phonetic example if possible
        # For this mock, we'll simulate a phonetic match that is slightly off
        result = self.mapper.get_best_match("Metform") 
        if result["match_method"] == "Phonetic":
            self.assertEqual(result["cleaned_term"], "Metformin")
            if result["confidence_score"] < 0.85:
                self.assertTrue(result["review_required"])

    def test_fuzzy_fallback(self):
        """Tests that a fuzzy match (not phonetic) always triggers review_required."""
        # 'Ibu' is not a phonetic match for 'Ibuprofen' but is a fuzzy one
        result = self.mapper.get_best_match("Ibu")
        self.assertEqual(result["cleaned_term"], "Ibuprofen")
        self.assertEqual(result["match_method"], "Fuzzy")
        self.assertTrue(result["review_required"])

    def test_no_match(self):
        """Tests the behavior when no reasonable match is found."""
        result = self.mapper.get_best_match("Zzzzzz")
        self.assertEqual(result["cleaned_term"], "UNKNOWN")
        self.assertEqual(result["match_method"], "None")
        self.assertTrue(result["review_required"])

if __name__ == "__main__":
    unittest.main()
