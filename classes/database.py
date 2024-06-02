from abc import ABC, abstractmethod

class Database(ABC):
    @abstractmethod
    def create_database(self, database_name: str, username: str, password: str) -> bool:
        pass

    @abstractmethod
    def delete_database(self, database_name: str, username: str) -> bool:
        pass

    @abstractmethod
    def test_database_connection(self) -> str:
        pass