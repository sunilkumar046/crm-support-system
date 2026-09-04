from datetime import datetime, timezone

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.models.user import User
from app.models.customer import Customer

from app.schemas.ticket import (
    TicketCreate,
    TicketUpdate
)

from app.repositories.ticket_repository import (
    TicketRepository
)

from app.core.enums import (
    TicketPriority,
    TicketStatus
)

from app.services.sla_service import (
    SLAService
)

from app.services.background_service import (
    BackgroundService
)


class TicketService:

    # ========================================================
    # GET CUSTOMER USER ID
    # ========================================================

    @staticmethod
    def get_customer_user_id(
        db: Session,
        customer_id: int
    ) -> int:

        customer = (
            db.query(Customer)
            .filter(
                Customer.id == customer_id
            )
            .first()
        )

        if not customer:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Customer not found"
            )

        return customer.user_id

    # ========================================================
    # CREATE TICKET
    # ========================================================

    @staticmethod
    def create_ticket(
        db: Session,
        customer_id: int,
        data: TicketCreate,
        background_tasks: BackgroundTasks
    ) -> Ticket:

        ticket = Ticket(
            customer_id=customer_id,
            subject=data.subject,
            description=data.description,
            category_id=data.category_id,
            priority=data.priority,
            status=TicketStatus.OPEN
        )

        created_ticket = TicketRepository.create(
            db=db,
            ticket=ticket
        )

        # Initialize SLA
        SLAService.initialize_ticket_sla(
            db=db,
            ticket=created_ticket
        )

        # Get actual USER ID from CUSTOMER ID
        customer_user_id = TicketService.get_customer_user_id(
            db=db,
            customer_id=customer_id
        )

        # ====================================================
        # TICKET CREATED NOTIFICATION
        # ====================================================

        background_tasks.add_task(
            BackgroundService.create_notification_task,
            customer_user_id,
            f"Ticket #{created_ticket.id} has been created successfully",
            created_ticket.id
        )

        # ====================================================
        # CRITICAL TICKET NOTIFICATION
        # ====================================================

        if created_ticket.priority == TicketPriority.CRITICAL:

            background_tasks.add_task(
                BackgroundService.create_notification_task,
                customer_user_id,
                f"Critical ticket #{created_ticket.id} has been created",
                created_ticket.id
            )

        return created_ticket

    # ========================================================
    # GET SINGLE TICKET
    # ========================================================

    @staticmethod
    def get_ticket(
        db: Session,
        ticket_id: int,
        current_user
    ) -> Ticket:

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        role = current_user.role.value

        # ====================================================
        # ADMIN
        # ====================================================

        if role == "admin":
            return ticket

        # ====================================================
        # CUSTOMER
        # ====================================================

        if role == "customer":

            customer = (
                db.query(Customer)
                .filter(
                    Customer.user_id == current_user.id
                )
                .first()
            )

            if not customer:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer profile not found"
                )

            if ticket.customer_id != customer.id:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You do not have permission "
                        "to view this ticket"
                    )
                )

            return ticket

        # ====================================================
        # SUPPORT AGENT
        # ====================================================

        if role == "support_agent":

            if ticket.assigned_agent_id != current_user.id:

                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "You do not have permission "
                        "to view this ticket"
                    )
                )

            return ticket

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "You do not have permission "
                "to view this ticket"
            )
        )

    # ========================================================
    # GET ALL TICKETS
    # ========================================================

    @staticmethod
    def get_all_tickets(
        db: Session
    ) -> list[Ticket]:

        return TicketRepository.get_all(
            db
        )

    # ========================================================
    # GET CUSTOMER TICKETS
    # ========================================================

    @staticmethod
    def get_customer_tickets(
        db: Session,
        customer_id: int
    ) -> list[Ticket]:

        return TicketRepository.get_by_customer(
            db=db,
            customer_id=customer_id
        )

    # ========================================================
    # GET ASSIGNED TICKETS
    # ========================================================

    @staticmethod
    def get_assigned_tickets(
        db: Session,
        agent_id: int
    ) -> list[Ticket]:

        return TicketRepository.get_by_assigned_agent(
            db=db,
            agent_id=agent_id
        )

    # ========================================================
    # VALIDATE STATUS TRANSITION
    # ========================================================

    @staticmethod
    def validate_status_transition(
        current_status: TicketStatus,
        new_status: TicketStatus
    ) -> None:

        if current_status == new_status:
            return

        allowed_transitions = {

            TicketStatus.OPEN: [
                TicketStatus.IN_PROGRESS,
                TicketStatus.CANCELLED
            ],

            TicketStatus.IN_PROGRESS: [
                TicketStatus.WAITING_FOR_CUSTOMER,
                TicketStatus.RESOLVED,
                TicketStatus.CANCELLED
            ],

            TicketStatus.WAITING_FOR_CUSTOMER: [
                TicketStatus.IN_PROGRESS,
                TicketStatus.CANCELLED
            ],

            TicketStatus.RESOLVED: [
                TicketStatus.CLOSED
            ],

            TicketStatus.CLOSED: [],

            TicketStatus.CANCELLED: []
        }

        allowed_statuses = allowed_transitions.get(
            current_status,
            []
        )

        if new_status not in allowed_statuses:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid ticket status transition: "
                    f"{current_status.value} → "
                    f"{new_status.value}"
                )
            )

    # ========================================================
    # UPDATE TICKET
    # ========================================================

    @staticmethod
    def update_ticket(
        db: Session,
        ticket_id: int,
        data: TicketUpdate,
        current_user,
        background_tasks: BackgroundTasks
    ) -> Ticket:

        ticket = TicketService.get_ticket(
            db=db,
            ticket_id=ticket_id,
            current_user=current_user
        )

        # Closed/cancelled tickets cannot be modified
        if ticket.status in {
            TicketStatus.CLOSED,
            TicketStatus.CANCELLED
        }:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Closed or cancelled tickets "
                    "cannot be modified"
                )
            )

        # Store old values
        old_status = ticket.status.value
        old_priority = ticket.priority.value

        # Validate status transition
        if data.status is not None:

            TicketService.validate_status_transition(
                current_status=ticket.status,
                new_status=data.status
            )

        update_data = data.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            setattr(
                ticket,
                field,
                value
            )

        # ====================================================
        # RESOLUTION TIME
        # ====================================================

        if data.status == TicketStatus.RESOLVED:

            if ticket.resolved_at is None:

                now = datetime.now(timezone.utc)

                ticket.resolved_at = now
                ticket.resolution_time = now

        # ====================================================
        # UPDATE SLA STATUS
        # ====================================================

        if ticket.sla_deadline is not None:

            ticket.sla_status = SLAService.get_sla_status(
                ticket
            )

        updated_ticket = TicketRepository.update(
            db=db,
            ticket=ticket
        )

        # ====================================================
        # GET CUSTOMER USER ID
        # ====================================================

        customer_user_id = TicketService.get_customer_user_id(
            db=db,
            customer_id=ticket.customer_id
        )

        # ====================================================
        # STATUS CHANGE NOTIFICATION
        # ====================================================

        if data.status is not None:

            new_status = data.status.value

            if new_status != old_status:

                background_tasks.add_task(
                    BackgroundService.create_notification_task,
                    customer_user_id,
                    (
                        f"Ticket #{ticket.id} status changed "
                        f"from {old_status} to {new_status}"
                    ),
                    ticket.id
                )

        # ====================================================
        # PRIORITY CHANGE NOTIFICATION
        # ====================================================

        if data.priority is not None:

            new_priority = data.priority.value

            if new_priority != old_priority:

                background_tasks.add_task(
                    BackgroundService.create_notification_task,
                    customer_user_id,
                    (
                        f"Ticket #{ticket.id} priority changed "
                        f"from {old_priority} to {new_priority}"
                    ),
                    ticket.id
                )

        # ====================================================
        # CRITICAL TICKET ALERT
        # ====================================================

        if (
            data.priority is not None
            and data.priority == TicketPriority.CRITICAL
            and old_priority != TicketPriority.CRITICAL.value
        ):

            background_tasks.add_task(
                BackgroundService.create_notification_task,
                customer_user_id,
                f"Ticket #{ticket.id} is now marked as CRITICAL",
                ticket.id
            )

        return updated_ticket

    # ========================================================
    # DELETE TICKET
    # ========================================================

    @staticmethod
    def delete_ticket(
        db: Session,
        ticket_id: int,
        current_user
    ) -> None:

        ticket = TicketService.get_ticket(
            db=db,
            ticket_id=ticket_id,
            current_user=current_user
        )

        if ticket.status in {
            TicketStatus.CLOSED,
            TicketStatus.CANCELLED
        }:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Closed or cancelled tickets "
                    "cannot be deleted"
                )
            )

        TicketRepository.delete(
            db=db,
            ticket=ticket
        )

    # ========================================================
    # ASSIGN / REASSIGN TICKET
    # ========================================================

    @staticmethod
    def assign_ticket(
        db: Session,
        ticket_id: int,
        agent_id: int,
        background_tasks: BackgroundTasks
    ) -> Ticket:

        ticket = TicketRepository.get_by_id(
            db=db,
            ticket_id=ticket_id
        )

        if not ticket:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ticket not found"
            )

        # Closed/cancelled tickets cannot be assigned
        if ticket.status in {
            TicketStatus.CLOSED,
            TicketStatus.CANCELLED
        }:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Closed or cancelled tickets "
                    "cannot be assigned"
                )
            )

        # ====================================================
        # FIND SUPPORT AGENT
        # ====================================================

        agent = (
            db.query(User)
            .filter(
                User.id == agent_id
            )
            .first()
        )

        if not agent:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support agent not found"
            )

        # Check role
        if agent.role.value != "support_agent":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a support agent"
            )

        # Check active status
        if hasattr(agent, "is_active"):

            if not agent.is_active:

                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        "Inactive support agents "
                        "cannot be assigned tickets"
                    )
                )

        # Store previous agent
        old_agent_id = ticket.assigned_agent_id

        # ====================================================
        # GET CUSTOMER USER ID
        # ====================================================

        customer_user_id = TicketService.get_customer_user_id(
            db=db,
            customer_id=ticket.customer_id
        )

        # ====================================================
        # ASSIGN TICKET
        # ====================================================

        updated_ticket = TicketRepository.assign_agent(
            db=db,
            ticket=ticket,
            agent_id=agent_id
        )

        # ====================================================
        # NOTIFY NEW AGENT
        # ====================================================

        background_tasks.add_task(
            BackgroundService.create_notification_task,
            agent_id,
            f"Ticket #{ticket.id} has been assigned to you",
            ticket.id
        )

        # ====================================================
        # NOTIFY CUSTOMER
        # ====================================================

        background_tasks.add_task(
            BackgroundService.create_notification_task,
            customer_user_id,
            (
                f"Ticket #{ticket.id} has been assigned "
                f"to a support agent"
            ),
            ticket.id
        )

        # ====================================================
        # NOTIFY OLD AGENT
        # ====================================================

        if (
            old_agent_id is not None
            and old_agent_id != agent_id
        ):

            background_tasks.add_task(
                BackgroundService.create_notification_task,
                old_agent_id,
                (
                    f"Ticket #{ticket.id} has been "
                    f"reassigned to another agent"
                ),
                ticket.id
            )

        return updated_ticket

    # ========================================================
    # GET UNASSIGNED TICKETS
    # ========================================================

    @staticmethod
    def get_unassigned_tickets(
        db: Session
    ) -> list[Ticket]:

        return TicketRepository.get_unassigned(
            db=db
        )

    # ========================================================
    # GET SINGLE AGENT WORKLOAD
    # ========================================================

    @staticmethod
    def get_agent_workload(
        db: Session,
        agent_id: int
    ):

        agent = (
            db.query(User)
            .filter(
                User.id == agent_id
            )
            .first()
        )

        if not agent:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Support agent not found"
            )

        if agent.role.value != "support_agent":

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a support agent"
            )

        total_assigned = (
            TicketRepository.count_assigned_tickets(
                db=db,
                agent_id=agent_id
            )
        )

        open_tickets = (
            TicketRepository.count_agent_status(
                db=db,
                agent_id=agent_id,
                ticket_status=TicketStatus.OPEN
            )
        )

        in_progress_tickets = (
            TicketRepository.count_agent_status(
                db=db,
                agent_id=agent_id,
                ticket_status=TicketStatus.IN_PROGRESS
            )
        )

        waiting_for_customer_tickets = (
            TicketRepository.count_agent_status(
                db=db,
                agent_id=agent_id,
                ticket_status=TicketStatus.WAITING_FOR_CUSTOMER
            )
        )

        resolved_tickets = (
            TicketRepository.count_agent_status(
                db=db,
                agent_id=agent_id,
                ticket_status=TicketStatus.RESOLVED
            )
        )

        critical_tickets = (
            TicketRepository.count_agent_critical(
                db=db,
                agent_id=agent_id
            )
        )

        return {
            "agent_id": agent_id,
            "total_assigned": total_assigned,
            "open_tickets": open_tickets,
            "in_progress_tickets": in_progress_tickets,
            "waiting_for_customer_tickets": (
                waiting_for_customer_tickets
            ),
            "resolved_tickets": resolved_tickets,
            "critical_tickets": critical_tickets
        }

    # ========================================================
    # GET ALL AGENT WORKLOAD
    # ========================================================

    @staticmethod
    def get_all_agent_workload(
        db: Session
    ):

        agents = (
            db.query(User)
            .filter(
                User.role == "support_agent"
            )
            .all()
        )

        workload = []

        for agent in agents:

            agent_workload = (
                TicketService.get_agent_workload(
                    db=db,
                    agent_id=agent.id
                )
            )

            workload.append(
                agent_workload
            )

        return workload

    # ========================================================
    # SEARCH / FILTER / PAGINATION
    # ========================================================

    @staticmethod
    def search_tickets(
        db: Session,
        current_user,
        search: str | None = None,
        status: TicketStatus | None = None,
        priority: TicketPriority | None = None,
        category_id: int | None = None,
        assigned_agent_id: int | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20
    ):

        if page < 1:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Page must be greater than "
                    "or equal to 1"
                )
            )

        if limit < 1 or limit > 100:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit must be between 1 and 100"
            )

        allowed_sort_fields = {
            "id",
            "created_at",
            "updated_at",
            "priority",
            "status"
        }

        if sort_by not in allowed_sort_fields:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Invalid sort field. "
                    "Allowed fields: "
                    "id, created_at, updated_at, "
                    "priority, status"
                )
            )

        if sort_order not in {
            "asc",
            "desc"
        }:

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "sort_order must be "
                    "'asc' or 'desc'"
                )
            )

        # ====================================================
        # ROLE BASED FILTERING
        # ====================================================

        role = current_user.role.value

        customer_id = None

        if role == "customer":

            customer = (
                db.query(Customer)
                .filter(
                    Customer.user_id == current_user.id
                )
                .first()
            )

            if not customer:

                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer profile not found"
                )

            customer_id = customer.id

        elif role == "support_agent":

            assigned_agent_id = current_user.id

        elif role == "admin":

            pass

        else:

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "You do not have permission "
                    "to search tickets"
                )
            )

        # ====================================================
        # SEARCH DATABASE
        # ====================================================

        tickets, total = (
            TicketRepository.search_and_filter(
                db=db,
                search=search,
                status=(
                    status.value
                    if status
                    else None
                ),
                priority=(
                    priority.value
                    if priority
                    else None
                ),
                category_id=category_id,
                assigned_agent_id=assigned_agent_id,
                customer_id=customer_id,
                sort_by=sort_by,
                sort_order=sort_order,
                page=page,
                limit=limit
            )
        )

        # ====================================================
        # PAGINATION RESPONSE
        # ====================================================

        return {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (
                (total + limit - 1) // limit
            ),
            "tickets": tickets
        }