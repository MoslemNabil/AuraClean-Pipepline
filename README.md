# **🩺 AuraClean: Medical Voice-AI Pipeline**

**AuraClean** is a high-integrity data transformation pipeline designed for medical operating room environments. It solves the "Dirty Data" problem inherent in Speech-to-Text (STT) medical transcriptions by applying **phonetic normalization** and **strict schema validation**.

## **🏗️ Architectural Overview**

The project follows a **Modular Layered Architecture** to ensure separation of concerns and a HIPAA-ready audit trail.

### **1\. Ingestion Layer**

* **Purpose:** Asynchronous intake of raw STT JSON logs.  
* **Resilience:** Implements graceful error handling for malformed or missing files to prevent pipeline downtime.

### **2\. Logic Layer (The "Brain")**

* **Phonetic Normalization:** Uses a hybrid approach combining **Jellyfish (Metaphone)** for sound-based indexing and **RapidFuzz** for character edit distance.  
* **Safety Trigger:** Implements a **Confidence Threshold (85%)**. Any match below this score is flagged for mandatory manual review to prevent medical errors.

### **3\. Validation Layer**

* **Strict Typing:** Powered by **Pydantic**. Data is forced into a MedicalRecord model, ensuring all entries have valid timestamps, IDs, and cleaned terms before persistence.

### **4\. Persistence Layer (Repository Pattern)**

* **Design Pattern:** Implements the **Repository Pattern** via an Abstract Base Class (BaseRepository).  
* **Implementation:** Currently uses **MongoDB Atlas** for high-availability cloud storage.  
* **Scalability:** Decoupled architecture allows for swapping to SQL or other cloud-native stores with zero changes to the core logic.

## **🛠️ Tech Stack**

* **Language:** Python 3.11+ (Strict Type Hinting)  
* **Database:** MongoDB Atlas (Dedicated Cluster)  
* **Key Libraries:** Pandas, Pydantic, RapidFuzz, Jellyfish, Pytest  
* **Security:** python-dotenv for secret management and IP whitelisting.

## **🚀 Quick Start**

### **1\. Prerequisites**

* Python 3.11+  
* A MongoDB Atlas Cluster (or local MongoDB instance)

### **2\. Installation**

git clone \[https://github.com/moslemnabil/auraclean-pipeline.git\](https://github.com/moslemnabil/auraclean-pipeline.git)  
cd auraclean-pipeline  
pip install \-r requirements.txt

### **3\. Environment Setup**

Create a .env file in the root directory based on the provided .env.template:

MONGO\_URI="mongodb+srv://\<user\>:\<password\>@cluster.xxxx.mongodb.net/auraclean"

### **4\. Running the Pipeline**

python \-m main

### **5\. Testing**

pytest tests/

## **👨‍💻 Foundational Principles**

* **Clean Code:** Adheres to **SOLID** principles and **Domain-Driven Design (DDD)** patterns.  
* **Test-Driven:** 100% coverage on core phonetic mapping logic.  
* **Cloud-Native:** Built for distributed environments with secure connection pooling.
