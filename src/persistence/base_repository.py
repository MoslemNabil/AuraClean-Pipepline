from abc import ABC, abstractmethod
from models.medical_record import MedicalRecord


class BaseRepository(ABC):
    """
    Abstract Base Class for the AuraClean persistence layer.
    Defines the contract for saving medical records to any storage backend.
    """

    @abstractmethod
    def save(self, record: MedicalRecord) -> None:
        """
        Saves a single MedicalRecord to the persistence store.

        Args:
            record (MedicalRecord): The validated medical record to persist.
        """
        pass
