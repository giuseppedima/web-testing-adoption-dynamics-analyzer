from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from core.database import Base

class TaxonomyModel(Base):
    __tablename__ = "taxonomy"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(String(), nullable=False, unique=True)
    description = Column(Text(), nullable=False)

    transitions = relationship("TransitionModel", secondary="taxonomy_transition", back_populates="taxonomies")