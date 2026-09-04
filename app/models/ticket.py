from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Enum as SQLEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.database.database import Base
from app.core.enums import TicketPriority, TicketStatus


class Ticket(Base):

    __tablename__ = "tickets"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    customer_id = Column(
        Integer,
        ForeignKey("customers.id"),
        nullable=False,
        index=True
    )

    subject = Column(
        String(255),
        nullable=False
    )

    description = Column(
        Text,
        nullable=False
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id"),
        nullable=False,
        index=True
    )

    priority = Column(
        SQLEnum(
            TicketPriority,
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ]
        ),
        nullable=False,
        default=TicketPriority.MEDIUM
    )

    status = Column(
        SQLEnum(
            TicketStatus,
            values_callable=lambda enum_cls: [
                member.value for member in enum_cls
            ]
        ),
        nullable=False,
        default=TicketStatus.OPEN
    )

    assigned_agent_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=True,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    resolved_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    # =========================
    # SLA FIELDS
    # =========================

    sla_deadline = Column(
        DateTime(timezone=True),
        nullable=True
    )

    first_response_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    resolution_time = Column(
        DateTime(timezone=True),
        nullable=True
    )

    sla_status = Column(
        String(20),
        nullable=True,
        default="within_sla"
    )

    # =========================
    # RELATIONSHIPS
    # =========================

    customer = relationship(
        "Customer",
        back_populates="tickets"
    )

    category = relationship(
        "Category",
        back_populates="tickets"
    )

    responses = relationship(
        "TicketResponse",
        back_populates="ticket",
        cascade="all, delete-orphan"
    )

    assigned_agent = relationship(
        "User",
        foreign_keys=[assigned_agent_id]
    )