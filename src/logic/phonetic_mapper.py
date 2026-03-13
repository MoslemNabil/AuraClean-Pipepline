from typing import List, Tuple, Dict, Any
import jellyfish
from rapidfuzz import fuzz, process


class PhoneticMapper:
    """
    A class for normalizing medical transcripts with high integrity.
    Implements a multi-step matching process: Exact match, Metaphone phonetic matching,
    and final scoring via RapidFuzz.

    Attributes:
        source_of_truth (List[str]): Injectable list of validated medical terms.
    """

    def __init__(self, source_of_truth: List[str]):
        """
        Initializes the PhoneticMapper with an injectable Source of Truth.

        Args:
            source_of_truth (List[str]): A list of validated medical terms.
        """
        self.source_of_truth: List[str] = source_of_truth

    def get_best_match(self, transcript: str) -> Dict[str, Any]:
        """
        Implements the core matching intelligence.
        Step A: Exact Match.
        Step B: Metaphone Phonetic matching + RapidFuzz scoring.
        Step C: Assign 'review_required' for low-confidence matches.

        Args:
            transcript (str): The 'dirty' phonetic transcript.

        Returns:
            Dict[str, Any]: A dictionary containing mapping metadata (cleaned_term, confidence, 
                             match_method, audit_log, review_required).
        """
        # --- Step A: Exact Match Check ---
        for term in self.source_of_truth:
            if transcript.lower().strip() == term.lower().strip():
                return {
                    "cleaned_term": term,
                    "confidence_score": 1.0,
                    "match_method": "Exact",
                    "audit_log": f"Exact match found for '{transcript}'",
                    "review_required": False
                }

        # --- Step B: Metaphone Phonetic Matching ---
        transcript_metaphone: str = jellyfish.metaphone(transcript)
        potential_matches: List[str] = [
            term for term in self.source_of_truth 
            if jellyfish.metaphone(term) == transcript_metaphone
        ]

        if potential_matches:
            # Use RapidFuzz to find the best among metaphone matches
            best_match = process.extractOne(
                transcript, 
                potential_matches, 
                scorer=fuzz.ratio
            )
            
            if best_match:
                match_term, score, _ = best_match
                confidence: float = round(score / 100.0, 2)
                
                # --- Step C: Confidence Threshold ---
                review_required = confidence < 0.85
                
                return {
                    "cleaned_term": match_term,
                    "confidence_score": confidence,
                    "match_method": "Phonetic",
                    "audit_log": f"Metaphone match found with {score}% confidence via RapidFuzz",
                    "review_required": review_required
                }

        # --- Fallback: Global Fuzzy Search (Optional but recommended for robustness) ---
        global_match = process.extractOne(
            transcript, 
            self.source_of_truth, 
            scorer=fuzz.WRatio
        )
        
        if global_match:
            match_term, score, _ = global_match
            confidence = round(score / 100.0, 2)
            return {
                "cleaned_term": match_term,
                "confidence_score": confidence,
                "match_method": "Fuzzy",
                "audit_log": f"Fuzzy fallback match found with {score}% confidence",
                "review_required": True  # Always review fuzzy fallback
            }

        return {
            "cleaned_term": "UNKNOWN",
            "confidence_score": 0.0,
            "match_method": "None",
            "audit_log": "No match found above threshold",
            "review_required": True
        }
