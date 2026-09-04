from sqlalchemy import Column, Integer, String
from app.database.database import Base


class SLAPolicy(Base):

    __tablename__ = "sla_policies"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    priority = Column(
        String(20),
        unique=True,
        nullable=False
    )

    response_time_hours = Column(
        Integer,
        nullable=False
    )

    resolution_time_hours = Column(
        Integer,
        nullable=False
    )