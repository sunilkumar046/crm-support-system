from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.ticket import Ticket


class DashboardRepository:

    @staticmethod
    def count_customers(db: Session):

        return (
            db.query(User)
            .filter(
                User.role == "customer"
            )
            .count()
        )

    @staticmethod
    def count_support_agents(db: Session):

        return (
            db.query(User)
            .filter(
                User.role == "support_agent"
            )
            .count()
        )

    @staticmethod
    def count_tickets(db: Session):

        return db.query(Ticket).count()

    @staticmethod
    def count_by_status(
        db: Session,
        ticket_status: str
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.status == ticket_status
            )
            .count()
        )

    @staticmethod
    def count_by_priority(
        db: Session,
        priority: str
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.priority == priority
            )
            .count()
        )

    @staticmethod
    def count_sla_breached(
        db: Session
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.sla_status == "breached"
            )
            .count()
        )

    @staticmethod
    def get_average_resolution_hours(
        db: Session
    ):

        result = (
            db.query(
                func.avg(
                    func.extract(
                        "epoch",
                        Ticket.resolution_time
                        - Ticket.created_at
                    ) / 3600
                )
            )
            .filter(
                Ticket.resolution_time.isnot(None)
            )
            .scalar()
        )

        if result is None:
            return 0.0

        return float(result)

    @staticmethod
    def count_agent_tickets(
        db: Session,
        agent_id: int
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id
            )
            .count()
        )

    @staticmethod
    def count_agent_status(
        db: Session,
        agent_id: int,
        ticket_status: str
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id,
                Ticket.status == ticket_status
            )
            .count()
        )

    @staticmethod
    def count_agent_priority(
        db: Session,
        agent_id: int,
        priority: str
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id,
                Ticket.priority == priority
            )
            .count()
        )

    @staticmethod
    def count_agent_sla_breached(
        db: Session,
        agent_id: int
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id,
                Ticket.sla_status == "breached"
            )
            .count()
        )

    @staticmethod
    def count_customer_tickets(
        db: Session,
        customer_id: int
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.customer_id == customer_id
            )
            .count()
        )

    @staticmethod
    def count_customer_status(
        db: Session,
        customer_id: int,
        ticket_status: str
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.customer_id == customer_id,
                Ticket.status == ticket_status
            )
            .count()
        )

    @staticmethod
    def get_recent_customer_tickets(
        db: Session,
        customer_id: int,
        limit: int = 5
    ):

        return (
            db.query(Ticket)
            .filter(
                Ticket.customer_id == customer_id
            )
            .order_by(
                Ticket.created_at.desc()
            )
            .limit(limit)
            .all()
        )