import sys
import logging
import os
from typing import List, Dict, Any
from datetime import datetime
from dotenv import load_dotenv

from ingestion.loader import RawDataLoader
from logic.phonetic_mapper import PhoneticMapper
from models.medical_record import MedicalRecord
from persistence.mongo_repository import MongoRepository

# Load environment variables (from .env file)
load_dotenv()

# Configure logging for the pipeline
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


def main() -> None:
    """
    Main orchestrator for the AuraClean pipeline.
    Loads raw medical data, performs phonetic cleaning, validates via Pydantic,
    and persists the results to MongoDB.
    """
    print("\n" + "=" * 70)
    print(" AURACLEAN PIPELINE: INITIALIZING")
    print("=" * 70)
    
    # 1. Dependency Setup
    SOURCE_OF_TRUTH: List[str] = ['Aspirin', 'Metformin', 'Amoxicillin', 'Ibuprofen']
    DATA_DIR: str = "data/raw"
    INPUT_FILE: str = "stt_logs.json"

    # 2. Initialize Components
    loader = RawDataLoader(data_dir=DATA_DIR)
    mapper = PhoneticMapper(source_of_truth=SOURCE_OF_TRUTH)
    
    # Initialize Persistence Layer (Dependency Inversion Principle)
    repository = None
    try:
        # Check if we should use DB at all
        mongo_uri = os.getenv('MONGO_URI')
        if not mongo_uri:
            print("[INFO] No MONGO_URI found in environment. Skipping database connection.")
        else:
            print(f"[INFO] Connecting to MongoDB Atlas...")
            repository = MongoRepository()
            print(f"[SUCCESS] Connected to MongoDB Atlas!")
            
    except Exception as e:
        logger.error("Failed to initialize persistence: %s", e)
        # Use a mock repository if DB is not available for testing
        print("\n[!] MongoDB connection failed. Continuing without persistence for demonstration.\n")
        repository = None

    print("-" * 70)
    print(" STARTING PIPELINE PROCESSING")
    print("-" * 70)

    # 3. Load Raw Data
    raw_records: List[Dict[str, Any]] = loader.load_file(INPUT_FILE)
    
    if not raw_records:
        logger.warning("No records found in %s.", INPUT_FILE)
        return

    # 4. Process and Persist
    persisted_count: int = 0
    processed_records: List[MedicalRecord] = []

    for raw in raw_records:
        transcript: str = raw.get("transcript", "UNKNOWN")
        
        # Step A: Perform Phonetic/Fuzzy Mapping
        mapping_result: Dict[str, Any] = mapper.get_best_match(transcript)
        
        # Step B: Create and Validate Pydantic Model
        record: MedicalRecord = MedicalRecord(
            patient_id=raw.get("patient_id", "UNKNOWN"),
            physician_id=raw.get("physician_id", "UNKNOWN"),
            transcript=transcript,
            cleaned_term=mapping_result["cleaned_term"],
            confidence_score=mapping_result["confidence_score"],
            match_method=mapping_result["match_method"],
            audit_log=mapping_result["audit_log"],
            review_required=mapping_result["review_required"],
            timestamp=datetime.utcnow()
        )
        
        processed_records.append(record)
        
        # Step C: Persist to MongoDB
        if repository:
            try:
                repository.save(record)
                persisted_count += 1
            except Exception as e:
                logger.error("Persistence failed for record (Patient: %s): %s", record.patient_id, e)

    # 5. Output Summary Report
    print(f"\n{'TRANSCRIPT':<15} | {'CLEANED':<12} | {'CONF':<4} | {'REVIEW REQUIRED?'}")
    print("-" * 70)

    for rec in processed_records:
        review_tag = "YES [!]" if rec.review_required else "No"
        print(f"{rec.transcript:<15} | "
              f"{rec.cleaned_term:<12} | "
              f"{rec.confidence_score:<4.2f} | "
              f"{review_tag}")

    print("-" * 70)
    if repository:
        print(f"Successfully persisted {persisted_count} records to MongoDB.")
    else:
        print("Records processed, but database persistence was skipped.")
    print("=" * 70)
    print(" PIPELINE FINISHED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
