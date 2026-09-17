"""Abstract object storage interface for Coordin8."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import BinaryIO


class ObjectStore(ABC):
    """Abstract object storage interface for raw and derived files."""

    @abstractmethod
    def put_object(self, key: str, data: bytes | BinaryIO) -> str:
        """Store an object under key and return URI."""
        pass

    @abstractmethod
    def get_object(self, key: str) -> bytes:
        """Retrieve bytes of an object."""
        pass

    @abstractmethod
    def delete_object(self, key: str) -> bool:
        """Delete an object."""
        pass


class LocalFileSystemObjectStore(ObjectStore):
    """Local filesystem implementation of ObjectStore."""

    def __init__(self, root_dir: str | Path) -> None:
        self.root = Path(root_dir)
        self.root.mkdir(parents=True, exist_ok=True)

    def put_object(self, key: str, data: bytes | BinaryIO) -> str:
        target = self.root / key
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(data, bytes):
            target.write_bytes(data)
        else:
            with target.open("wb") as f:
                f.write(data.read())
        return str(target)

    def get_object(self, key: str) -> bytes:
        target = self.root / key
        return target.read_bytes()

    def delete_object(self, key: str) -> bool:
        target = self.root / key
        if target.exists():
            target.unlink()
            return True
        return False
