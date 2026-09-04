from sqlalchemy.orm import Session

from app.models.ticket import Ticket


class TicketRepository:

    # ========================================================
    # CREATE
    # ========================================================

    @staticmethod
    def create(
        db: Session,
        ticket: Ticket
    ):
        db.add(ticket)
        db.commit()
        db.refresh(ticket)

        return ticket

    # ========================================================
    # GET BY ID
    # ========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        ticket_id: int
    ):
        return (
            db.query(Ticket)
            .filter(
                Ticket.id == ticket_id
            )
            .first()
        )

    # ========================================================
    # GET ALL
    # ========================================================

    @staticmethod
    def get_all(
        db: Session
    ):
        return (
            db.query(Ticket)
            .order_by(
                Ticket.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # GET CUSTOMER TICKETS
    # ========================================================

    @staticmethod
    def get_by_customer(
        db: Session,
        customer_id: int
    ):
        return (
            db.query(Ticket)
            .filter(
                Ticket.customer_id == customer_id
            )
            .order_by(
                Ticket.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # GET ASSIGNED TICKETS
    # ========================================================

    @staticmethod
    def get_by_assigned_agent(
        db: Session,
        agent_id: int
    ):
        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id
            )
            .order_by(
                Ticket.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # GET UNASSIGNED TICKETS
    # ========================================================

    @staticmethod
    def get_unassigned(
        db: Session
    ):
        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id.is_(None)
            )
            .order_by(
                Ticket.created_at.desc()
            )
            .all()
        )

    # ========================================================
    # COUNT ASSIGNED TICKETS
    # ========================================================

    @staticmethod
    def count_assigned_tickets(
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

    # ========================================================
    # COUNT BY STATUS FOR AGENT
    # ========================================================

    @staticmethod
    def count_agent_status(
        db: Session,
        agent_id: int,
        ticket_status
    ):
        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id,
                Ticket.status == ticket_status
            )
            .count()
        )

    # ========================================================
    # COUNT CRITICAL TICKETS FOR AGENT
    # ========================================================

    @staticmethod
    def count_agent_critical(
        db: Session,
        agent_id: int
    ):
        return (
            db.query(Ticket)
            .filter(
                Ticket.assigned_agent_id == agent_id,
                Ticket.priority == "critical"
            )
            .count()
        )

    # ========================================================
    # SEARCH / FILTER
    # ========================================================

    @staticmethod
    def search_and_filter(
        db: Session,
        search: str | None = None,
        status: str | None = None,
        priority: str | None = None,
        category_id: int | None = None,
        assigned_agent_id: int | None = None,
        customer_id: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20
    ):

        query = db.query(Ticket)

        if customer_id is not None:

            query = query.filter(
                Ticket.customer_id == customer_id
            )

        if search:

            search_value = f"%{search}%"

            query = query.filter(
                Ticket.subject.ilike(search_value)
                |
                Ticket.description.ilike(search_value)
            )

        if status:

            query = query.filter(
                Ticket.status == status
            )

        if priority:

            query = query.filter(
                Ticket.priority == priority
            )

        if category_id is not None:

            query = query.filter(
                Ticket.category_id == category_id
            )

        if assigned_agent_id is not None:

            query = query.filter(
                Ticket.assigned_agent_id == assigned_agent_id
            )

        sort_column = getattr(
            Ticket,
            sort_by,
            Ticket.created_at
        )

        if sort_order == "asc":

            query = query.order_by(
                sort_column.asc()
            )

        else:

            query = query.order_by(
                sort_column.desc()
            )

        total = query.count()

        offset = (page - 1) * limit

        tickets = (
            query
            .offset(offset)
            .limit(limit)
            .all()
        )

        return tickets, total

    # ========================================================
    # UPDATE
    # ========================================================

    @staticmethod
    def update(
        db: Session,
        ticket: Ticket
    ):

        db.commit()
        db.refresh(ticket)

        return ticket

    # ========================================================
    # DELETE
    # ========================================================

    @staticmethod
    def delete(
        db: Session,
        ticket: Ticket
    ):

        db.delete(ticket)
        db.commit()

    # ========================================================
    # ASSIGN AGENT
    # ========================================================

    @staticmethod
    def assign_agent(
        db: Session,
        ticket: Ticket,
        agent_id: int
    ):

        ticket.assigned_agent_id = agent_id

        db.commit()
        db.refresh(ticket)

        return ticket