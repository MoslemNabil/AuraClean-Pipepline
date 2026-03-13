import json
import os
import logging
from typing import List, Dict, Any

# Configure logging for the ingestion module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RawDataLoader:
    """
    A robust class for reading raw medical data from JSON files.
    Includes error handling and logging for missing or malformed files.

    Attributes:
        data_dir (str): The directory where raw JSON files are stored.
    """

    def __init__(self, data_dir: str = "data/raw"):
        """
        Initializes the RawDataLoader with the data directory path.

        Args:
            data_dir (str): Path to the directory containing raw JSON files.
        """
        self.data_dir: str = data_dir

    def load_file(self, filename: str) -> List[Dict[str, Any]]:
        """
        Loads a single JSON file from the raw data directory.
        Handles FileNotFoundError and JSONDecodeError gracefully.

        Args:
            filename (str): Name of the JSON file to load.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing raw transcript records.
                                 Returns an empty list if file is missing or invalid.
        """
        file_path: str = os.path.join(self.data_dir, filename)
        
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}. Skipping load.")
                return []

            with open(file_path, 'r', encoding='utf-8') as f:
                data: List[Dict[str, Any]] = json.load(f)
                logger.info(f"Successfully loaded {len(data)} records from {filename}")
                return data

        except json.JSONDecodeError as e:
            logger.error(f"Malformed JSON in {filename}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading {filename}: {e}")
            return []

    def list_files(self) -> List[str]:
        """
        Lists all JSON files in the raw data directory.

        Returns:
            List[str]: A list of filenames found in the data/raw directory.
        """
        if not os.path.exists(self.data_dir):
            logger.warning(f"Data directory '{self.data_dir}' does not exist.")
            return []
            
        return [f for f in os.listdir(self.data_dir) if f.endswith('.json')]
