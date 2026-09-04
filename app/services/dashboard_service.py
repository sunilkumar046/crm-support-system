from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.dashboard_repository import (
    DashboardRepository
)


class DashboardService:

    @staticmethod
    def get_admin_dashboard(
        db: Session,
        current_user
    ):

        if current_user.role.value != "admin":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can access the admin dashboard"
            )

        return {
            "total_customers":
                DashboardRepository.count_customers(db),

            "total_support_agents":
                DashboardRepository.count_support_agents(db),

            "total_tickets":
                DashboardRepository.count_tickets(db),

            "open_tickets":
                DashboardRepository.count_by_status(
                    db,
                    "open"
                ),

            "in_progress_tickets":
                DashboardRepository.count_by_status(
                    db,
                    "in_progress"
                ),

            "resolved_tickets":
                DashboardRepository.count_by_status(
                    db,
                    "resolved"
                ),

            "closed_tickets":
                DashboardRepository.count_by_status(
                    db,
                    "closed"
                ),

            "critical_tickets":
                DashboardRepository.count_by_priority(
                    db,
                    "critical"
                ),

            "sla_breached_tickets":
                DashboardRepository.count_sla_breached(
                    db
                ),

            "average_resolution_hours":
                DashboardRepository.get_average_resolution_hours(
                    db
                )
        }

    @staticmethod
    def get_agent_dashboard(
        db: Session,
        current_user
    ):

        if current_user.role.value != "support_agent":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only support agents can access this dashboard"
            )

        agent_id = current_user.id

        return {
            "assigned_tickets":
                DashboardRepository.count_agent_tickets(
                    db,
                    agent_id
                ),

            "open_tickets":
                DashboardRepository.count_agent_status(
                    db,
                    agent_id,
                    "open"
                ),

            "in_progress_tickets":
                DashboardRepository.count_agent_status(
                    db,
                    agent_id,
                    "in_progress"
                ),

            "waiting_for_customer_tickets":
                DashboardRepository.count_agent_status(
                    db,
                    agent_id,
                    "waiting_for_customer"
                ),

            "resolved_tickets":
                DashboardRepository.count_agent_status(
                    db,
                    agent_id,
                    "resolved"
                ),

            "critical_tickets":
                DashboardRepository.count_agent_priority(
                    db,
                    agent_id,
                    "critical"
                ),

            "sla_breached_tickets":
                DashboardRepository.count_agent_sla_breached(
                    db,
                    agent_id
                )
        }

    @staticmethod
    def get_customer_dashboard(
        db: Session,
        current_user
    ):

        if current_user.role.value != "customer":

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only customers can access this dashboard"
            )

        customer_id = current_user.id

        return {
            "total_tickets":
                DashboardRepository.count_customer_tickets(
                    db,
                    customer_id
                ),

            "open_tickets":
                DashboardRepository.count_customer_status(
                    db,
                    customer_id,
                    "open"
                ),

            "in_progress_tickets":
                DashboardRepository.count_customer_status(
                    db,
                    customer_id,
                    "in_progress"
                ),

            "waiting_for_customer_tickets":
                DashboardRepository.count_customer_status(
                    db,
                    customer_id,
                    "waiting_for_customer"
                ),

            "resolved_tickets":
                DashboardRepository.count_customer_status(
                    db,
                    customer_id,
                    "resolved"
                ),

            "closed_tickets":
                DashboardRepository.count_customer_status(
                    db,
                    customer_id,
                    "closed"
                ),

            "recent_tickets":
                DashboardRepository.get_recent_customer_tickets(
                    db,
                    customer_id
                )
        }