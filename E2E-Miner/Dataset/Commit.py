from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from Dataset.DBconnector import Base
from Dataset.Transition import TransitionModel


class CommitModel(Base):
    __tablename__ = "commit"
    hash = Column(String(), primary_key=True)
    repository_name = Column(String(), ForeignKey("repository.name"), nullable=False)
    date = Column(DateTime, nullable=False)
    message = Column(Text, nullable=False)
    transition_id = Column(Integer, ForeignKey("transition.id"), nullable=True)

    transition = relationship(TransitionModel, back_populates="commits")
