from sqlalchemy import Table, Column, Integer, String, Text, ForeignKey, UniqueConstraint, Computed
from sqlalchemy.orm import relationship
from core.database import Base
from core.Dataset.Taxonomy import TaxonomyModel

taxonomy_transition = Table(
    'taxonomy_transition', Base.metadata,
    Column('taxonomy_id', Integer, ForeignKey('taxonomy.id'), primary_key=True),
    Column('transition_id', Integer, ForeignKey('transition.id'), primary_key=True),
    # Ensure the combination is unique
    UniqueConstraint('taxonomy_id', 'transition_id', name='uq_taxonomy_transition')
)

class TransitionModel(Base):
    __tablename__ = "transition"
    id = Column(Integer, primary_key=True, autoincrement=True)
    repository_name = Column(String(), ForeignKey("repository.name"), nullable=False)
    source_framework = Column(String(), nullable=True)
    target_framework = Column(String(), nullable=False)
    __table_args__ = (
        UniqueConstraint(
            "repository_name",
            "source_framework",
            "target_framework",
            "summary",
            name="uq_transition_unique_fields"
        ),
    )
    summary = Column(Text(), nullable=False)
    type = Column(String(), Computed("CASE WHEN source_framework IS NULL THEN 'adoption' ELSE 'migration' END"))

    taxonomies = relationship(TaxonomyModel, secondary=taxonomy_transition, back_populates="transitions")

    commits = relationship("CommitModel", back_populates="transition")
    issues = relationship("IssueModel", back_populates="transition")
