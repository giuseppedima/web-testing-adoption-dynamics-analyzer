import json
from abc import ABC
import sys

sys.path.append("Dataset")
print(sys.path)
from Dataset.DataSetInterface import DataSetInterface
from Dataset.Repository import Repository
from DBconnector import Session, engine


class DataSet(DataSetInterface, ABC):

    def read_all_repositories(self):
        local_session = Session(bind=engine)
        items_list = local_session.query(Repository).all()
        for repository in items_list:
            print(repository.name)
        print(len(items_list))
        return items_list

    def filter_repositories(self, filter_strategy):
        return filter_strategy.filtering()
