from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.ticket import Ticket

from app.repositories.ticket_repository import (
    TicketRepository
)

from app.repositories.sla_repository import (
    SLARepository
)


class SLAService:

    SLA_HOURS = {
        "low": 48,
        "medium": 24,
        "high": 8,
        "critical": 2
    }

    @staticmethod
    def calculate_deadline(
        priority: str,
        created_at: datetime
    ):

        hours = SLAService.SLA_HOURS.get(
            priority
        )

        if hours is None:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid ticket priority"
            )

        return (
            created_at
            + timedelta(hours=hours)
        )

    @staticmethod
    def get_sla_status(
        ticket: Ticket
    ):

        if ticket.sla_deadline is None:

            return "within_sla"

        now = datetime.now(
            timezone.utc
        )

        # Already resolved/closed
        if ticket.resolved_at is not None:

            if ticket.resolved_at <= ticket.sla_deadline:
                return "within_sla"

            return "breached"

        # Deadline passed
        if now >= ticket.sla_deadline:

            return "breached"

        # At risk when less than 20% time remains
        total_seconds = (
            ticket.sla_deadline
            - ticket.created_at
        ).total_seconds()

        remaining_seconds = (
            ticket.sla_deadline
            - now
        ).total_seconds()

        if total_seconds > 0:

            remaining_percentage = (
                remaining_seconds
                / total_seconds
            )

            if remaining_percentage <= 0.20:

                return "at_risk"

        return "within_sla"

    @staticmethod
    def update_sla_status(
        db: Session,
        ticket: Ticket
    ):

        ticket.sla_status = (
            SLAService.get_sla_status(
                ticket
            )
        )

        db.commit()
        db.refresh(ticket)

        return ticket

    @staticmethod
    def initialize_ticket_sla(
        db: Session,
        ticket: Ticket
    ):

        priority = ticket.priority.value

        ticket.sla_deadline = (
            SLAService.calculate_deadline(
                priority=priority,
                created_at=ticket.created_at
            )
        )

        ticket.sla_status = "within_sla"

        db.commit()
        db.refresh(ticket)

        return ticket

    @staticmethod
    def get_ticket_sla(
        db: Session,
        ticket_id: int
    ):

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        SLAService.update_sla_status(
            db=db,
            ticket=ticket
        )

        return ticket

    @staticmethod
    def get_all_sla_tickets(
        db: Session
    ):

        tickets = TicketRepository.get_all(
            db
        )

        for ticket in tickets:

            ticket.sla_status = (
                SLAService.get_sla_status(
                    ticket
                )
            )

        db.commit()

        return tickets

    @staticmethod
    def get_breached_tickets(
        db: Session
    ):

        tickets = TicketRepository.get_all(
            db
        )

        breached = []

        for ticket in tickets:

            sla_status = (
                SLAService.get_sla_status(
                    ticket
                )
            )

            if sla_status == "breached":

                ticket.sla_status = "breached"

                breached.append(ticket)

        db.commit()

        return breached

    @staticmethod
    def get_at_risk_tickets(
        db: Session
    ):

        tickets = TicketRepository.get_all(
            db
        )

        at_risk = []

        for ticket in tickets:

            sla_status = (
                SLAService.get_sla_status(
                    ticket
                )
            )

            if sla_status == "at_risk":

                ticket.sla_status = "at_risk"

                at_risk.append(ticket)

        db.commit()

        return at_risk