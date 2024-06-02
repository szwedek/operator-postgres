from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def create(self, database_name: str, username: str, password: str) -> bool:
        pass

    @abstractmethod
    def delete(self, database_name: str, username: str) -> bool:
        pass

    @abstractmethod
    def test_connection(self, db_host: str, database_name: str, username: str, password: str) -> str:
        pass