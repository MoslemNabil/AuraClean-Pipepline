import logging
import os
import certifi
from typing import Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError

from models.medical_record import MedicalRecord
from persistence.base_repository import BaseRepository

# Configure logging for the persistence module
logger = logging.getLogger(__name__)


class MongoRepository(BaseRepository):
    """
    A concrete implementation of the BaseRepository for MongoDB.
    Connects to an instance and persists MedicalRecord objects.
    """

    def __init__(self, uri: str = None):
        """
        Initializes the MongoDB connection. If no URI is provided, 
        it pulls from the MONGO_URI environment variable.

        Args:
            uri (str): The MongoDB connection string (optional).
        """
        connection_uri = uri or os.getenv('MONGO_URI')
        
        if not connection_uri:
            raise ValueError("No MONGO_URI provided in environment or argument.")
            
        try:
            # serverSelectionTimeoutMS ensures we fail fast if the connection is blocked
            # tlsCAFile is crucial for Atlas connections on some systems to verify certificates
            self.client: MongoClient = MongoClient(
                connection_uri, 
                serverSelectionTimeoutMS=5000,
                tlsCAFile=certifi.where()
            )
            
            # The 'ping' command is the standard way to test a connection in MongoDB
            self.client.admin.command('ping')
            
            self.db = self.client["auraclean"]
            self.collection = self.db["medical_logs"]
            
            logger.info("Successfully connected to MongoDB Atlas.")
        except ConnectionFailure as e:
            error_msg = (
                "Could not connect to MongoDB Atlas. Please check your "
                "MONGO_URI and ensure your current IP address is Whitelisted "
                f"in the Atlas Network Access settings. Error: {e}"
            )
            logger.error(error_msg)
            raise ConnectionError(error_msg) from e

    def save(self, record: MedicalRecord) -> None:
        """
        Persists a MedicalRecord object to the 'medical_logs' collection.
        Converts the Pydantic model into a dictionary for database insertion.

        Args:
            record (MedicalRecord): The validated medical record to persist.

        Raises:
            PyMongoError: If the insertion operation fails.
        """
        try:
            # Pydantic v2 .model_dump() converts model to dictionary
            record_dict: Dict[str, Any] = record.model_dump()
            
            # MongoDB will auto-generate an _id if not provided
            self.collection.insert_one(record_dict)
            logger.debug("Record for patient %s persisted to MongoDB.", record.patient_id)
            
        except PyMongoError as e:
            logger.error("Failed to persist record for patient %s: %s", record.patient_id, e)
            raise
