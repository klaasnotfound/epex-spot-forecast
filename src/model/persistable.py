import typing
from abc import ABC, abstractmethod

from duckdb import DuckDBPyConnection

T = typing.TypeVar("T", bound="Persistable")


class Persistable(ABC):
    @abstractmethod
    def init_table(con: DuckDBPyConnection):
        """Initializes the associated DB table for this class."""
