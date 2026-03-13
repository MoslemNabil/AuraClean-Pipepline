from datetime import datetime
from pydantic import BaseModel, Field


class MedicalRecord(BaseModel):
    """
    Pydantic BaseModel for a medical event representing a transformed phonetic transcript.
    Includes audit trail fields for medical data integrity.

    Attributes:
        timestamp (datetime): The UTC timestamp of the medical event.
        patient_id (str): Unique identifier for the patient.
        physician_id (str): Unique identifier for the physician.
        transcript (str): The raw, phonetic voice-to-text transcript.
        cleaned_term (str): The normalized term after phonetic mapping.
        confidence_score (float): A value between 0.0 and 1.0 representing mapping accuracy.
        review_required (bool): Flag indicating if manual verification is needed.
        match_method (str): The strategy used for mapping (e.g., 'Exact', 'Phonetic').
        audit_log (str): A summary of the mapping rationale.
    """

    timestamp: datetime = Field(default_factory=datetime.utcnow, description="The UTC timestamp of the event")
    patient_id: str = Field(..., description="Unique identifier for the patient")
    physician_id: str = Field(..., description="Unique identifier for the physician")
    transcript: str = Field(..., description="The raw voice-to-text phonetic input")
    cleaned_term: str = Field(..., description="The normalized medical term")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score from 0.0 to 1.0")
    review_required: bool = Field(default=False, description="True if the match needs manual review")
    match_method: str = Field(..., description="Method used: Exact, Phonetic, or Fuzzy")
    audit_log: str = Field(..., description="Summary of why the match was made")

    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "timestamp": "2026-03-13T10:00:00Z",
                "patient_id": "PAT-12345",
                "physician_id": "PHY-67890",
                "transcript": "Metforman",
                "cleaned_term": "Metformin",
                "confidence_score": 0.88,
                "review_required": False,
                "match_method": "Phonetic",
                "audit_log": "Metaphone match found with 88% confidence via RapidFuzz"
            }
        }
