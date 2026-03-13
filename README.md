# 🩺 AuraClean: Medical Voice-AI Pipeline

**AuraClean** is a high-integrity data transformation pipeline designed for medical operating room environments. It solves the **"Dirty Data"** problem inherent in Speech-to-Text (STT) medical transcriptions by applying phonetic normalization and strict schema validation.

---

## 🏗️ Architectural Overview

This project is built using a **Modular Layered Architecture** to ensure separation of concerns and a HIPAA-ready audit trail.

```
┌─────────────────────────────────────────────────────────────┐
│                     AuraClean Pipeline                      │
├───────────────┬──────────────────┬─────────────┬───────────┤
│  Ingestion    │   Logic Layer    │  Validation │Persistence│
│    Layer      │   ("The Brain")  │    Layer    │   Layer   │
│               │                  │             │           │
│  RawData      │  PhoneticMapper  │  Pydantic   │  MongoDB  │
│  Loader       │  (Metaphone +    │  Medical    │  Atlas    │
│  (JSON/STT)   │   RapidFuzz)     │  Record     │  Cluster  │
└───────────────┴──────────────────┴─────────────┴───────────┘
```

### 1. Ingestion Layer
- **Purpose:** Asynchronous intake of raw STT JSON logs.
- **Resilience:** Implements graceful error handling for malformed files to prevent pipeline downtime.

### 2. Logic Layer (The "Brain")
- **Phonetic Normalization:** Uses a hybrid approach combining **Jellyfish** (Metaphone) for sound-based indexing and **RapidFuzz** for character distance.
- **Safety Trigger:** Implements a **Confidence Threshold (85%)** — any match below this score is flagged for mandatory manual review to prevent medical errors.

### 3. Validation Layer
- **Strict Typing:** Powered by **Pydantic**. Data is forced into a `MedicalRecord` model, ensuring all entries have valid timestamps, IDs, and cleaned terms before hitting the database.

### 4. Persistence Layer (Repository Pattern)
- **Design Pattern:** Implements the **Repository Pattern** via an Abstract Base Class (`BaseRepository`).
- **Implementation:** Currently uses **MongoDB Atlas** for high-availability cloud storage.
- **Scalability:** Decoupled architecture allows for swapping to SQL or other cloud-native stores with zero changes to the core logic.

---

## 📂 Project Structure

```
AuraClean-Pipeline/
├── src/
│   ├── ingestion/
│   │   └── loader.py              # RawDataLoader — reads & validates JSON STT logs
│   ├── logic/
│   │   ├── phonetic_mapper.py     # PhoneticMapper — Metaphone + RapidFuzz matching
│   │   └── models/
│   │       └── medical_record.py  # Pydantic MedicalRecord schema
│   └── persistence/
│       ├── base_repository.py     # Abstract BaseRepository (interface)
│       └── mongo_repository.py    # MongoRepository — MongoDB Atlas implementation
├── tests/
│   └── test_phonetic_mapper.py    # Unit tests for the PhoneticMapper
├── data/
│   └── raw/
│       └── stt_logs.json          # Sample STT input data
├── main.py                        # Pipeline orchestrator
├── requirements.txt
├── .env.template
└── README.md
```

---

## 🛠️ Tech Stack

| Component       | Technology                          |
|-----------------|-------------------------------------|
| **Language**    | Python 3.11+ (Strict Type Hinting)  |
| **Database**    | MongoDB Atlas (Dedicated Cluster)   |
| **Validation**  | Pydantic v2                         |
| **Phonetics**   | Jellyfish (Metaphone algorithm)     |
| **Fuzzy Match** | RapidFuzz                           |
| **Data**        | Pandas                              |
| **Security**    | python-dotenv + IP Whitelisting     |
| **Testing**     | Pytest / Unittest                   |

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.11+
- A [MongoDB Atlas](https://www.mongodb.com/atlas) Cluster (or local MongoDB instance)

### 2. Installation

```bash
git clone https://github.com/moslemnabil/auraclean-pipeline.git
cd auraclean-pipeline
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the root directory based on `.env.template`:

```plaintext
MONGO_URI="mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority&appName=AuraClean"
```

> **Security Note:** Never commit your `.env` file. It is already included in `.gitignore`.
> Ensure your current IP address is whitelisted in your MongoDB Atlas **Network Access** settings.

### 4. Prepare Input Data

Place your STT JSON logs in `data/raw/stt_logs.json`. The expected format is:

```json
[
  {
    "patient_id": "PAT-12345",
    "physician_id": "PHY-67890",
    "transcript": "Metforman"
  }
]
```

### 5. Run the Pipeline

```bash
python main.py
```

**Sample Output:**

```
======================================================================
 AURACLEAN PIPELINE: INITIALIZING
======================================================================
[INFO] Connecting to MongoDB Atlas...
[SUCCESS] Connected to MongoDB Atlas!
----------------------------------------------------------------------
 STARTING PIPELINE PROCESSING
----------------------------------------------------------------------

TRANSCRIPT      | CLEANED      | CONF | REVIEW REQUIRED?
----------------------------------------------------------------------
Metforman       | Metformin    | 0.88 | No
Asprin          | Aspirin      | 0.91 | No
Amoxacilin      | Amoxicillin  | 0.86 | No
Ibuprofin       | Ibuprofen    | 0.89 | No
----------------------------------------------------------------------
Successfully persisted 4 records to MongoDB.
======================================================================
 PIPELINE FINISHED
======================================================================
```

---

## 🧠 Matching Logic

The `PhoneticMapper` applies a **three-step matching cascade**:

```
Input Transcript
       │
       ▼
┌─────────────────┐     Match found     ┌────────────────────────┐
│  Step A: Exact  │ ──────────────────► │  confidence = 1.0      │
│    Match        │                     │  review_required = False│
└─────────────────┘                     └────────────────────────┘
       │ No match
       ▼
┌─────────────────┐     Match found     ┌────────────────────────┐
│  Step B:        │ ──────────────────► │  confidence ≥ 0.85 →   │
│  Metaphone +    │                     │    review_required=False│
│  RapidFuzz      │                     │  confidence < 0.85 →   │
└─────────────────┘                     │    review_required=True │
       │ No match                       └────────────────────────┘
       ▼
┌─────────────────┐     Match found     ┌────────────────────────┐
│  Step C: Global │ ──────────────────► │  review_required = True│
│  Fuzzy Fallback │                     │  (always flagged)      │
└─────────────────┘                     └────────────────────────┘
       │ No match
       ▼
  cleaned_term = "UNKNOWN"
  review_required = True
```

---

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

**Test Coverage:**

| Test Case                                          | Description                                          |
|----------------------------------------------------|------------------------------------------------------|
| `test_exact_match`                                 | Exact match returns 1.0 confidence, no review        |
| `test_phonetic_match_high_confidence`              | Metaphone + RapidFuzz match ≥ 85% confidence         |
| `test_phonetic_match_low_confidence_review_required` | Low confidence triggers `review_required`          |
| `test_fuzzy_fallback`                              | Fuzzy fallback always sets `review_required = True`  |
| `test_no_match`                                    | Unrecognized input returns `UNKNOWN`                 |

---

## �� Security & Compliance

- **Secret Management:** All credentials managed via `python-dotenv` — no secrets in source code.
- **Network Security:** MongoDB Atlas IP Whitelisting restricts database access.
- **Audit Trail:** Every `MedicalRecord` includes `match_method`, `audit_log`, and `confidence_score` fields for full traceability.
- **Human-in-the-Loop:** The `review_required` flag ensures low-confidence matches are never auto-applied to patient records without manual verification.

---

## 📋 MedicalRecord Schema

```python
class MedicalRecord(BaseModel):
    timestamp:        datetime  # UTC timestamp of the event
    patient_id:       str       # Unique patient identifier
    physician_id:     str       # Unique physician identifier
    transcript:       str       # Raw voice-to-text phonetic input
    cleaned_term:     str       # Normalized medical term
    confidence_score: float     # Match confidence: 0.0 – 1.0
    review_required:  bool      # True if manual verification needed
    match_method:     str       # "Exact" | "Phonetic" | "Fuzzy" | "None"
    audit_log:        str       # Rationale summary for the match
```

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add your feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

*Built with ❤️ for medical data integrity.*
