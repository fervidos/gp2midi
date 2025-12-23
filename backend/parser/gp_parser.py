from abc import ABC, abstractmethod

from backend.models.song_model import Song


class GPParser(ABC):
    @abstractmethod
    def parse_file(self, file_path: str) -> Song:
        """
        Parses a Guitar Pro file and returns a Song model.
        """
        pass

    @abstractmethod
    def parse_bytes(self, file_content: bytes) -> Song:
        """
        Parses bytes directly (useful for API uploads).
        """
        pass
