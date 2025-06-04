from abc import ABC, abstractmethod


class DataSetInterface(ABC):
    @abstractmethod
    def read_all_repositories(self):
        pass

    @abstractmethod
    def filter_repositories(self, filter_strategy):
        pass
