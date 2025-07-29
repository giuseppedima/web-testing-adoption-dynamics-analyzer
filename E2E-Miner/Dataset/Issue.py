from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Computed
from sqlalchemy.orm import relationship
from Dataset.DBconnector import Base
from Dataset.Transition import TransitionModel

class IssueModel(Base):
    __tablename__ = "issue"
    number = Column(Integer, primary_key=True)
    repository_name = Column(String(), ForeignKey("repository.name"), nullable=False)
    title = Column(String(), nullable=False)
    body = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    closed_at = Column(DateTime, nullable=True)
    is_closed = Column(Boolean, Computed("closed_at IS NOT NULL"))
    transition_id = Column(Integer, ForeignKey("transition.id"), nullable=True)

    transition = relationship(TransitionModel, back_populates="issues")
